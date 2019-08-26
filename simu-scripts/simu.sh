#!/usr/bin/env bash

# wujian@2018

set -eu

num_spk=2
out_dir=${num_spk}spk_2s
scp_dir=2s_data

[ -d $out_dir ] && echo "clean $out_dir..." && rm -rf $out_dir

./create_dataset.py \
  $scp_dir/dev.scp \
  --num-utts 5000 \
  --simu-stats dev.stats \
  --sdr "-5, 5" \
  --num-spks $num_spk \
  --dump-dir $out_dir/dev
mv dev.stats $out_dir/dev

./create_dataset.py \
  $scp_dir/test.scp \
  --num-utts 3000 \
  --simu-stats test.stats \
  --sdr "-5, 5" \
  --num-spks $num_spk \
  --dump-dir $out_dir/test
mv test.stats $out_dir/test

./create_dataset.py \
  $scp_dir/train.scp \
  --num-utts 40000 \
  --simu-stats train.stats \
  --sdr "-5, 5" \
  --num-spks $num_spk \
  --dump-dir $out_dir/train
mv train.stats $out_dir/train
