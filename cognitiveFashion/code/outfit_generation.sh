#!/bin/bash
CHECKPOINT_DIR="model/model_final/model2K.ckpt-34865"

# Run inference on images.
python polyvore/set_generation.py \
  --checkpoint_path=${CHECKPOINT_DIR} \
  --image_dir="data/images/" \
  --feature_file="data/features/test_features_updated.pkl" \
  --query_file="query.json" \
  --word_dict_file="data/final_word_dict.txt" \
  --result_dir="results/"
