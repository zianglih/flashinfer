#!/usr/bin/env bash
# Same native AUTO policies, full token grid, and split FlashInfer workspace policy.
set -euo pipefail
if [ "$#" -ne 4 ]; then
  echo "usage: $0 BASELINE_SOURCE CANDIDATE_SOURCE NEW_OUTPUT_ROOT CACHE_ROOT" >&2
  exit 2
fi
baseline_source=$1
candidate_source=$2
output_root=$3
cache_root=$4
recipe_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
[[ "$(git -C "$baseline_source" rev-parse HEAD)" == 316faec37a4706a2ecc7d46265087f8190b40baa ]]
[[ "$(git -C "$candidate_source" rev-parse HEAD)" == 3d047d3f8e7923118ffea8b8d36151504ab1fa3d ]]
[[ -z "$(git -C "$baseline_source" status --porcelain=v1 --untracked-files=normal)" ]]
[[ -z "$(git -C "$candidate_source" status --porcelain=v1 --untracked-files=normal)" ]]
export OMP_NUM_THREADS=1
tokens=1,2,4,8,16,32,64,128,256,512,4096,8192,16384
image=nvcr.io/nvidia/pytorch:26.05-py3
python3 "$recipe_dir/run.py" \
  --source "$baseline_source" --driver "$recipe_dir/benchmarks/bench_cute_dsl_moe_distributed.py" \
  --output "$output_root/baseline-full13" --cache-root "$cache_root/shared" \
  --workspace-base "$cache_root/baseline/flashinfer" \
  --arm baseline-full13 --model glm5 --policy original16-all \
  --tactic-policy all --tokens "$tokens" --variants w4a16_megamoe \
  --knobs auto --iters 100 --warmup 3 --sweeps 1 --port 29691 --image "$image"
python3 "$recipe_dir/run.py" \
  --source "$candidate_source" --driver "$recipe_dir/benchmarks/bench_cute_dsl_moe_distributed.py" \
  --output "$output_root/candidate3r-full13" --cache-root "$cache_root/shared" \
  --workspace-base "$cache_root/candidate3r/flashinfer" \
  --arm candidate3r-full13 --model glm5 --policy new18-mixed-only \
  --tactic-policy mixed-only --tokens "$tokens" --variants w4a16_megamoe \
  --knobs auto --iters 100 --warmup 3 --sweeps 1 --port 29693 --image "$image"
