#!/bin/bash

echo "- Downloading annotation files"

mkdir annotation
aws s3 cp s3://ego-edit-data/annotation/egoeditbench_data_table.csv  annotation/egoeditbench_data_table.csv
aws s3 cp s3://ego-edit-data/annotation/egoeditbench_edits_table.csv annotation/egoeditbench_edits_table.csv
aws s3 cp s3://ego-edit-data/annotation/egoeditdata_data_table.csv annotation/egoeditdata_data_table.csv
aws s3 cp s3://ego-edit-data/annotation/egoeditdata_edits_table.csv annotation/egoeditdata_edits_table.csv

echo "- Downloading EgoEditData videos"

python download_ego_edit.py \
    annotation/egoeditdata_data_table.csv \
    videos \
    annotation/local_egoeditdata_data_table.csv

echo "- Downloading EgoEditBench videos"

python download_ego_edit.py \
    annotation/egoeditbench_data_table.csv \
    videos \
    annotation/local_egoeditbench_data_table.csv
