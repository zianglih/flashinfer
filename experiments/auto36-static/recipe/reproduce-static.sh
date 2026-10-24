#!/usr/bin/env bash
# Run inside the primary bundle's pinned image after its setup.sh creates sources.
set -euo pipefail
[[ $# == 5 ]] || { echo "usage: $0 PRIMARY_BUNDLE BASELINE_SOURCE CANDIDATE_3D_SOURCE NEW_OUTPUT_ROOT CACHE_ROOT" >&2; exit 2; }
bundle=$1 baseline=$2 candidate=$3 output=$4 cache=$5
recipe=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
[[ "$(git -C "$baseline" rev-parse HEAD)" == 316faec37a4706a2ecc7d46265087f8190b40baa ]]
[[ "$(git -C "$candidate" rev-parse HEAD)" == 3d047d3f8e7923118ffea8b8d36151504ab1fa3d ]]
[[ -z "$(git -C "$baseline" status --porcelain=v1)" ]]
[[ -z "$(git -C "$candidate" status --porcelain=v1)" ]]
git -C "$candidate" apply --check "$recipe/auto36-static-on-3d.patch"
git -C "$candidate" apply "$recipe/auto36-static-on-3d.patch"
python3 - "$candidate" <<'PY'
from pathlib import Path
import hashlib,sys
p=Path(sys.argv[1])
expected={
 'flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py':'3b14d47a8f7b45e0a022fe5d36915492da5093a1be8f008e350ffcd34534d6a6',
 'tests/moe_ep/test_w4a16_mixed_cluster_config.py':'054b4e2110d4dcb77bebd309c118edfd10153f08f632c779576a2539d41acdc6',
 'flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py':'664a74fde4f0d60957a2ddb07839c95f393d477f7ee84d5ce4415bb56bf4d939'}
for name,value in expected.items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==value
PY
export OMP_NUM_THREADS=1 FLASHINFER_MOE_EP_KNOB_CACHE=0
for arm in baseline candidate4s; do
  if [[ "$arm" == baseline ]]; then
    source=$baseline policy=all title=original16-all port=29695 modes=atomic_counter:16
  else
    source=$candidate policy=mixed-only title=static-screen-mixed36 port=29697 modes=atomic_counter:18,static:18
  fi
  python3 "$bundle/recipe/run.py" --source "$source" \
    --driver "$bundle/recipe/benchmarks/bench_cute_dsl_moe_distributed.py" \
    --output "$output/$arm" --arm "$arm-static-screen" --model glm5 \
    --policy "$title" --tactic-policy "$policy" --knobs auto \
    --cache-root "$cache/shared" --workspace-base "$cache/$arm/flashinfer" \
    --tokens 64,128,4096 --warmup 3 --iters 100 --sweeps 1 --port "$port" \
    --image nvcr.io/nvidia/pytorch:26.05-py3
  python3 "$recipe/auto_rankings.py" "$output/$arm" --output "$output/$arm/auto-rankings.json"
  python3 "$recipe/audit_scheduler_modes.py" "$output/$arm" \
    --rankings "$output/$arm/auto-rankings.json" --mode-counts "$modes" \
    --output "$output/$arm/scheduler-mode-receipts.json"
done
python3 -B "$bundle/recipe/compare.py" --baseline "$output/baseline" \
  --candidate "$output/candidate4s" --output "$output/static-screen-comparison.json"
