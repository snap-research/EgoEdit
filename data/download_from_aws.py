#!/usr/bin/env python3
"""
Download EgoEdit videos from S3 URLs specified in a CSV file.

This script reads a CSV file containing data_url fields (S3 URLs),
downloads the videos in parallel, and saves them to a local directory.
Outputs an updated CSV with the same columns as the input, but with
data_url replaced by local file paths, plus a download_success column.
"""

import argparse
import logging
import os
import random
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import boto3
from tqdm import tqdm
import pandas as pd
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class DownloadError:
    """Information about a download error."""

    data_id: str
    error_message: str
    traceback_str: str
    source_url: str
    local_path: str


def parse_s3_url(url: str) -> Tuple[str, str]:
    """Parse S3 URL into bucket and key."""
    parsed = urlparse(url)
    if parsed.scheme != "s3":
        raise ValueError(f"URL must start with s3://: {url}")
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    return bucket, key


def calculate_backoff_delay(attempt: int, initial_backoff: float = 1.0, max_backoff: float = 60.0, multiplier: float = 2.0, use_jitter: bool = True) -> float:
    """
    Calculate exponential backoff delay with optional jitter.

    Args:
        attempt: Current retry attempt number (0-indexed)
        initial_backoff: Initial backoff delay in seconds
        max_backoff: Maximum backoff delay in seconds
        multiplier: Exponential multiplier for backoff
        use_jitter: Whether to add random jitter to avoid thundering herd

    Returns:
        Delay in seconds to wait before next retry
    """
    # Calculate exponential backoff: initial * (multiplier ^ attempt)
    delay = initial_backoff * (multiplier**attempt)

    # Cap at maximum backoff
    delay = min(delay, max_backoff)

    # Add jitter if enabled (randomize between 0 and delay)
    if use_jitter:
        delay = random.uniform(0, delay)

    return delay


def download_file_with_retry(data_id: str, source_url: str, local_path: str, max_retries: int = 5, initial_backoff: float = 1.0, max_backoff: float = 60.0, backoff_multiplier: float = 2.0, backoff_jitter: bool = True, s3_client=None) -> Optional[DownloadError]:
    """
    Download a file from S3 to local path with exponential backoff retries.

    Returns:
        None if successful, DownloadError if failed after all retries
    """
    if s3_client is None:
        s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED), region_name="us-east-2")

    source_bucket, source_key = parse_s3_url(source_url)

    last_error = None
    for attempt in range(max_retries):
        try:
            # Ensure parent directory exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            # Download the file
            s3_client.download_file(source_bucket, source_key, local_path)

            # Verify the file exists and has content
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Downloaded file not found at {local_path}")

            file_size = os.path.getsize(local_path)
            if file_size == 0:
                raise ValueError(f"Downloaded file is empty: {local_path}")

            logger.debug(f"Successfully downloaded {data_id}: {source_url} -> {local_path} ({file_size} bytes)")
            return None

        except ClientError as e:
            last_error = e
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                logger.warning(f"Source file not found for {data_id}: {source_url}")
                # Don't retry if file doesn't exist
                break
            else:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {data_id}: {str(e)}")
                if attempt < max_retries - 1:
                    # Calculate and apply exponential backoff
                    delay = calculate_backoff_delay(attempt, initial_backoff, max_backoff, backoff_multiplier, backoff_jitter)
                    logger.debug(f"Retrying {data_id} after {delay:.2f}s backoff")
                    time.sleep(delay)
                    continue
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {data_id}: {str(e)}")
            if attempt < max_retries - 1:
                # Calculate and apply exponential backoff
                delay = calculate_backoff_delay(attempt, initial_backoff, max_backoff, backoff_multiplier, backoff_jitter)
                logger.debug(f"Retrying {data_id} after {delay:.2f}s backoff")
                time.sleep(delay)
                continue

    # If we got here, all retries failed
    error_traceback = traceback.format_exc()
    error_message = str(last_error)
    logger.error(f"Failed to download {data_id} after {max_retries} attempts: {error_message}")

    return DownloadError(data_id=data_id, error_message=error_message, traceback_str=error_traceback, source_url=source_url, local_path=local_path)


def download_worker(task: Tuple[str, str, str, int, float, float, float, bool]) -> Tuple[str, Optional[DownloadError]]:
    """Worker function for parallel file downloads."""
    data_id, source_url, local_path, max_retries, initial_backoff, max_backoff, backoff_multiplier, backoff_jitter = task
    # Each worker gets its own S3 client
    s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED), region_name="us-east-2")
    error = download_file_with_retry(data_id, source_url, local_path, max_retries, initial_backoff, max_backoff, backoff_multiplier, backoff_jitter, s3_client)
    return data_id, error


def download_videos_parallel(df: pd.DataFrame, output_folder: str, workers: int, max_retries: int, initial_backoff: float, max_backoff: float, backoff_multiplier: float, backoff_jitter: bool, skip_existing: bool = True) -> Tuple[pd.DataFrame, int, int, List[DownloadError]]:
    """
    Download videos in parallel from S3 URLs to local folder.

    Returns:
        Tuple of (updated_dataframe, success_count, skipped_count, list of errors)
    """
    logger.info(f"Starting parallel download with {workers} workers")
    logger.info(f"Retry configuration: max_retries={max_retries}, initial_backoff={initial_backoff}s, max_backoff={max_backoff}s, multiplier={backoff_multiplier}, jitter={backoff_jitter}")
    logger.info(f"Skip existing files: {skip_existing}")

    # Create output folder
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Prepare tasks and local paths
    tasks = []
    local_paths = {}
    skipped_count = 0

    for idx, row in df.iterrows():
        data_id = row["data_id"]
        source_url = row["data_url"]

        # Extract filename from URL
        _, source_key = parse_s3_url(source_url)
        filename = os.path.basename(source_key)

        # Create local path (flat directory structure)
        local_path = os.path.join(output_folder, filename)
        local_paths[data_id] = local_path

        # Skip files that already exist locally
        if skip_existing and os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            skipped_count += 1
            continue

        tasks.append((data_id, source_url, local_path, max_retries, initial_backoff, max_backoff, backoff_multiplier, backoff_jitter))

    if skipped_count > 0:
        logger.info(f"Skipped {skipped_count} files that already exist in {output_folder}")

    total_files = len(tasks)
    logger.info(f"Downloading {total_files} videos to {output_folder}")

    errors = []
    success_count = 0
    failed_data_ids = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        future_to_data_id = {executor.submit(download_worker, task): task[0] for task in tasks}

        # Process completed tasks
        pbar = tqdm(as_completed(future_to_data_id), total=total_files, desc="Downloading", unit="file")
        for future in pbar:
            data_id, error = future.result()

            if error is None:
                success_count += 1
            else:
                errors.append(error)
                failed_data_ids.append(data_id)

            pbar.set_postfix(ok=success_count, fail=len(errors))

    logger.info("\nDownload complete:")
    logger.info(f"  Total files: {total_files}")
    logger.info(f"  Successful: {success_count}")
    logger.info(f"  Failed: {len(errors)}")

    if failed_data_ids:
        logger.error("\nFailed data IDs:")
        for data_id in failed_data_ids[:20]:  # Show first 20
            logger.error(f"  - {data_id}")
        if len(failed_data_ids) > 20:
            logger.error(f"  ... and {len(failed_data_ids) - 20} more")

    # Create updated dataframe: replace data_url with local paths
    df_updated = df.copy()
    df_updated["data_url"] = df_updated["data_id"].map(local_paths)

    # Mark failed downloads
    df_updated["download_success"] = df_updated["data_id"].apply(lambda x: x not in failed_data_ids)

    return df_updated, success_count, skipped_count, errors


def main():
    parser = argparse.ArgumentParser(description="Download EgoEdit videos from S3 URLs specified in CSV file")

    parser.add_argument("input_csv", type=str, help="Path to input CSV file with data_url column")
    parser.add_argument("output_folder", type=str, help="Path to folder where videos will be downloaded")
    parser.add_argument("output_csv", type=str, help="Path to output CSV file with data_url replaced by local paths")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel download workers (default: 4)")
    parser.add_argument("--max-retries", type=int, default=5, help="Maximum retry attempts per file (default: 5)")
    parser.add_argument("--initial-backoff", type=float, default=1.0, help="Initial backoff delay in seconds (default: 1.0)")
    parser.add_argument("--max-backoff", type=float, default=60.0, help="Maximum backoff delay in seconds (default: 60.0)")
    parser.add_argument("--backoff-multiplier", type=float, default=2.0, help="Exponential backoff multiplier (default: 2.0)")
    parser.add_argument("--no-jitter", action="store_true", help="Disable random jitter in backoff delays")
    parser.add_argument("--no-skip-existing", action="store_true", help="Re-download files that already exist in the output folder (by default existing files are skipped)")

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("EGOEDIT VIDEO DOWNLOADER")
    logger.info("=" * 80)
    logger.info(f"Input CSV: {args.input_csv}")
    logger.info(f"Output folder: {args.output_folder}")
    logger.info(f"Output CSV: {args.output_csv}")
    logger.info(f"Workers: {args.workers}")
    logger.info(f"Max retries: {args.max_retries}")
    logger.info("=" * 80)

    # Load input CSV
    logger.info("Loading input CSV...")
    try:
        df = pd.read_csv(args.input_csv)
        logger.info(f"Loaded {len(df)} records")
    except Exception as e:
        logger.error(f"Failed to load input CSV: {e}")
        sys.exit(1)

    # Validate CSV has required columns
    if "data_id" not in df.columns:
        logger.error("Input CSV must have 'data_id' column")
        sys.exit(1)
    if "data_url" not in df.columns:
        logger.error("Input CSV must have 'data_url' column")
        sys.exit(1)

    # Download videos
    skip_existing = not args.no_skip_existing
    df_updated, success_count, skipped_count, errors = download_videos_parallel(df, args.output_folder, args.workers, args.max_retries, args.initial_backoff, args.max_backoff, args.backoff_multiplier, not args.no_jitter, skip_existing)

    # Save updated CSV
    logger.info(f"Saving updated CSV to {args.output_csv}...")
    try:
        # Create parent directory if needed
        Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
        df_updated.to_csv(args.output_csv, index=False)
        logger.info(f"Saved updated CSV with {len(df_updated)} records")
    except Exception as e:
        logger.error(f"Failed to save output CSV: {e}")
        sys.exit(1)

    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("DOWNLOAD COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total records: {len(df)}")
    logger.info(f"Skipped (already exist): {skipped_count}")
    logger.info(f"Successfully downloaded: {success_count}")
    logger.info(f"Failed downloads: {len(errors)}")
    logger.info(f"Output folder: {args.output_folder}")
    logger.info(f"Output CSV: {args.output_csv}")
    logger.info("=" * 80)

    # Exit with error code if there were failures
    if errors:
        logger.warning(f"Download completed with {len(errors)} errors")
        sys.exit(1)
    else:
        logger.info("Download completed successfully with no errors")
        sys.exit(0)


if __name__ == "__main__":
    main()
