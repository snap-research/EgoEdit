#!/usr/bin/env python3
"""
Download EgoEdit dataset from Hugging Face.

Usage:
    python download_from_huggingface.py [options]

Examples:
    # Download annotations only
    python download_from_huggingface.py --annotations-only

    # Download everything (annotations + videos)
    python download_from_huggingface.py

    # Download to a custom directory
    python download_from_huggingface.py --output-dir /path/to/data
"""

import argparse
import glob
import logging
import os
import sys
import zipfile
from pathlib import Path

from huggingface_hub import hf_hub_download, snapshot_download

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_REPO_ID = "snap-research/EgoEdit"

ANNOTATION_FILES = [
    "annotation/egoeditdata_data_table.csv",
    "annotation/egoeditdata_edits_table.csv",
    "annotation/egoeditbench_data_table.csv",
    "annotation/egoeditbench_edits_table.csv",
]


def download_annotations(repo_id: str, output_dir: str) -> None:
    """Download only the annotation CSV files."""
    logger.info("Downloading annotation files...")
    for filename in ANNOTATION_FILES:
        logger.info(f"  Downloading {filename}")
        hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="dataset",
            local_dir=output_dir,
        )
    logger.info(f"Annotations saved to {output_dir}/annotation/")


def download_all(repo_id: str, output_dir: str) -> None:
    """Download the full dataset (annotations + video zips), then extract videos."""
    logger.info(f"Downloading full dataset from {repo_id}...")
    snapshot_download(
        repo_id=repo_id,
        repo_type="dataset",
        local_dir=output_dir,
    )
    logger.info(f"Dataset downloaded to {output_dir}")

    # Extract video zip files
    videos_dir = os.path.join(output_dir, "videos")
    zip_files = sorted(glob.glob(os.path.join(videos_dir, "*.zip")))
    if zip_files:
        logger.info(f"Extracting {len(zip_files)} video zip files...")
        for i, zf_path in enumerate(zip_files, 1):
            logger.info(f"  Extracting [{i}/{len(zip_files)}]: {os.path.basename(zf_path)}")
            with zipfile.ZipFile(zf_path, "r") as zf:
                zf.extractall(videos_dir)
            os.remove(zf_path)
            logger.info(f"  Removed {os.path.basename(zf_path)}")
        logger.info("Video extraction complete.")
    else:
        logger.info("No video zip files found to extract.")


def main():
    parser = argparse.ArgumentParser(description="Download EgoEdit dataset from Hugging Face")
    parser.add_argument("--repo-id", type=str, default=DEFAULT_REPO_ID, help=f"Hugging Face dataset repo ID (default: {DEFAULT_REPO_ID})")
    parser.add_argument("--output-dir", type=str, default=".", help="Output directory (default: current directory)")
    parser.add_argument("--annotations-only", action="store_true", help="Download only annotation CSV files (skip videos)")
    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    if args.annotations_only:
        download_annotations(args.repo_id, args.output_dir)
    else:
        download_all(args.repo_id, args.output_dir)

    logger.info("Done!")


if __name__ == "__main__":
    main()
