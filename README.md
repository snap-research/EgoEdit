<div align="center">

<div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
  <img src="assets/imgs/logo.png" width="120" alt="EgoEdit Logo"/>
  <h1 style="margin: 0;">EgoEdit: Dataset, Real-Time Streaming Model, and Benchmark for Egocentric Video Editing</h1>
</div>

<a href="https://snap-research.github.io/EgoEdit/"><img src="https://img.shields.io/badge/%F0%9F%8F%A0%20Project%20Page-gray.svg"></a>
<a href="https://arxiv.org/abs/2512.06065"><img src="https://img.shields.io/badge/%F0%9F%93%84%20arXiv-2512.06065-B31B1B.svg"></a>
<a href="https://huggingface.co/datasets/liguang0115/EgoEdit"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-yellow.svg"></a>

[Runjia Li](https://runjiali-rl.github.io/)<sup>1,3</sup>,
[Moayed Haji Ali](https://moayedha.com/)<sup>1,2</sup>,
[Ashkan Mirzaei](https://ashmrz.github.io/)<sup>1</sup>,
[Chaoyang Wang](https://mightychaos.github.io/)<sup>1</sup>,
[Arpit Sahni](https://scholar.google.com/citations?user=IK3yBTYAAAAJ&hl=en)<sup>1</sup>,
[Ivan Skorokhodov](https://skor.sh/)<sup>1</sup>,
[Aliaksandr Siarohin](https://aliaksandrsiarohin.github.io/aliaksandr-siarohin-website/)<sup>1</sup>,
[Tomas Jakab](https://www.robots.ox.ac.uk/~tomj/)<sup>3</sup>,
[Junlin Han](https://junlinhan.github.io/)<sup>3</sup>,
[Sergey Tulyakov](https://stulyakov.com/)<sup>1</sup>,
[Philip Torr](https://www.robots.ox.ac.uk/~phst/)<sup>3</sup>,
[Willi Menapace](https://www.willimenapace.com/)<sup>1</sup>
<br>
<br>
<sup>1</sup>Snap Research, <sup>2</sup>Rice University, <sup>3</sup>University of Oxford

<img src="assets/imgs/teaser.gif" alt="EgoEdit Teaser" style="width: 100%; max-width: 900px; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.5);"/>

</div>

## Release Schedule

| Status | Timeline | Milestone |
|:------:|:--------:|:----------|
| :white_check_mark: | **December 2025** | Final review completed |
| :white_check_mark: | **March 2026** | Initial release of **EgoEditData** and **EgoEditBench** |
| :arrows_counterclockwise: | **TBD (soon)** | Code for **EgoEditBench** |

## Overview

We propose a framework for real-time egocentric video editing. Our system is composed of three main components:

- **EgoEditData**: A manually curated dataset of 100k video editing pairs focusing on the egocentric case. It features object substitution and removal under challenging hand occlusions, interactions, and large egomotion.
- **EgoEdit**: The first real-time autoregressive model for egocentric video editing. It runs in real time on a single H100 with **855ms first-frame latency**, enabling live augmented reality (AR) interactions.
- **EgoEditBench**: A comprehensive benchmark for the evaluation of egocentric video editing systems.

## Features

- **Real-Time Performance**: Designed to run efficiently on modern hardware (single H100) with low latency.
- **Challenging Scenarios**: Handles complex egocentric video challenges such as hand occlusions, object interactions, and significant camera motion.
- **High Fidelity**: Surpasses state of the art models like Editverse in editing faithfulness (via VLM evaluation) and aligns better with human judgment.

## EgoEditData & EgoEditBench

### Option A: Download from Hugging Face (Recommended)

The easiest way to get the data:

```bash
pip install -r data/requirements_download.txt

# Download annotations only
python data/download_from_huggingface.py --annotations-only

# Download everything (annotations + videos)
python data/download_from_huggingface.py
```

You can also specify a custom output directory:

```bash
python data/download_from_huggingface.py --output-dir /path/to/data
```

Videos are stored as zip archives on Hugging Face. The download script automatically extracts them and removes the zip files, leaving individual `.mp4` files in the `videos/` directory.

### Option B: Download from S3

<details>
<summary>Click to expand S3 download instructions</summary>

#### TL;DR

```bash
cd data
pip install -r requirements_download.txt
bash download_from_aws.sh
```

#### 1. Setup Environment

```bash
pip install -r data/requirements_download.txt
```

#### 2. Configure AWS Credentials

Ensure you have AWS credentials configured. Choose one method:

**Option A: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-2  # or your region
```

**Option B: AWS Credentials File**
```bash
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
EOF
```

#### 3. Download Annotations

```bash
mkdir -p data/annotation
aws s3 cp s3://ego-edit-data/annotation/egoeditbench_data_table.csv  data/annotation/egoeditbench_data_table.csv
aws s3 cp s3://ego-edit-data/annotation/egoeditbench_edits_table.csv data/annotation/egoeditbench_edits_table.csv
aws s3 cp s3://ego-edit-data/annotation/egoeditdata_data_table.csv   data/annotation/egoeditdata_data_table.csv
aws s3 cp s3://ego-edit-data/annotation/egoeditdata_edits_table.csv  data/annotation/egoeditdata_edits_table.csv
```

#### 4. Download Videos

```bash
cd data

# Download EgoEditData videos
python download_from_aws.py \
    annotation/egoeditdata_data_table.csv \
    videos \
    annotation/local_egoeditdata_data_table.csv

# Download EgoEditBench videos
python download_from_aws.py \
    annotation/egoeditbench_data_table.csv \
    videos \
    annotation/local_egoeditbench_data_table.csv
```

#### Command Line Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `input_csv` | Yes | Path to CSV file with `data_id` and `data_url` columns |
| `output_folder` | Yes | Directory where videos will be saved |
| `output_csv` | Yes | Path for output CSV with local paths and `download_success` column |
| `--workers N` | No | Number of parallel downloads (default: 4) |
| `--max-retries N` | No | Maximum retry attempts per file (default: 5) |
| `--initial-backoff S` | No | Initial backoff delay in seconds (default: 1.0) |
| `--max-backoff S` | No | Maximum backoff delay in seconds (default: 60.0) |
| `--backoff-multiplier M` | No | Exponential backoff multiplier (default: 2.0) |
| `--no-jitter` | No | Disable random jitter in backoff (not recommended) |

#### High-Performance Download

Use more workers for faster downloads:

```bash
python download_from_aws.py \
    annotation/egoeditdata_data_table.csv \
    videos \
    annotation/local_egoeditdata_data_table.csv \
    --workers 16
```

#### Troubleshooting

- **"Access Denied" Error**: Check AWS credentials are configured correctly.
- **"No module named 'boto3'"**: Run `pip install -r data/requirements_download.txt`.
- **Downloads Are Slow**: Increase `--workers` (try 8, 16, or 32), check network bandwidth, or verify S3 bucket region matches your location.
- **Frequent Failures**: Reduce workers and increase backoff: `--workers 1 --max-retries 10 --initial-backoff 2.0 --max-backoff 120.0`.

</details>

## Data Format

EgoEdit annotation is provided as two sets of CSV files — one for **EgoEditData** and one for **EgoEditBench**. Each set consists of a **data table** and an **edits table**.

### Data Tables

Each data table maps a unique data identifier to the corresponding video URL.

| Column | Description |
|---|---|
| `data_id` | Unique identifier for a video data point |
| `data_url` | URL of the video file |

### Edits Tables

Each edits table describes editing pairs: a source video and the editing instruction. In **EgoEditData** a target video is also provided; in **EgoEditBench** only the source video and the instruction are available.

| Column | Description |
|---|---|
| `data_id` | Unique identifier for the edit |
| `source_data_id` | References `data_id` in the corresponding data table (source video) |
| `target_data_id` | References `data_id` in the corresponding data table (target video). **Only present in EgoEditData** |
| `source_to_target_edit_prompt` | Natural language editing instruction |

The **EgoEditBench** edits table includes two additional columns:

| Column | Description |
|---|---|
| `edit_task` | High-level editing category |
| `sub_edit_task` | Fine-grained editing sub-category |

### Joining Tables

To obtain the full table with video URLs and editing prompts, join the data table with the edits table.

**EgoEditData** (join twice for source and target):

```python
import pandas as pd

data = pd.read_csv("egoeditdata_data_table.csv")
edits = pd.read_csv("egoeditdata_edits_table.csv")

full = (
    edits
    .merge(data, left_on="source_data_id", right_on="data_id", suffixes=("", "_source"))
    .merge(data, left_on="target_data_id", right_on="data_id", suffixes=("", "_target"))
)
```

**EgoEditBench** (single join on source):

```python
import pandas as pd

data = pd.read_csv("egoeditbench_data_table.csv")
edits = pd.read_csv("egoeditbench_edits_table.csv")

full = edits.merge(data, left_on="source_data_id", right_on="data_id")
```

## License

This project is licensed under the Snap Inc. Non-Commercial License. See [LICENSE](LICENSE) for details.

## :books: Citing

If you find this repository useful, please consider giving a star :star: and citation.

```
@article{li2025egoedit,
  title={EgoEdit: Dataset, Real-Time Streaming Model, and Benchmark for Egocentric Video Editing},
  author={Li, Runjia and Haji-Ali, Moayed and Mirzaei, Ashkan and Wang, Chaoyang and Sahni, Arpit and Skorokhodov, Ivan and Siarohin, Aliaksandr and Jakab, Tomas and Han, Junlin and Tulyakov, Sergey and others},
  journal={arXiv preprint arXiv:2512.06065},
  year={2025}
}
```
