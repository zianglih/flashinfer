#!/usr/bin/env bash
# Run inside nvcr.io/nvidia/pytorch:26.05-py3. Creates two independent checkouts.
set -euo pipefail
if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "usage: $0 NEW_WORKSPACE [CANDIDATE_REPOSITORY_URL]" >&2
  exit 2
fi
work=$1
candidate_repository=${2:-https://github.com/zianglih/flashinfer.git}
recipe_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
baseline_commit=316faec37a4706a2ecc7d46265087f8190b40baa
candidate_commit=3d047d3f8e7923118ffea8b8d36151504ab1fa3d
mkdir -p "$work"
work=$(CDPATH= cd -- "$work" && pwd)
export BUILD_NVEP=0 BUILD_NIXL_EP=0 BUILD_NCCL_EP=0
export FLASHINFER_BUILD_NO_PIP=1 MAX_JOBS=8
export CUDA_HOME=/usr/local/cuda CUDA_MODULE_LOADING=LAZY
unset PIP_CONSTRAINT
python3 - <<'PY'
import importlib.metadata as m
assert m.version('torch') == '2.12.0a0+5aff3928d8.nv26.5.50603568', 'Use the pinned PyTorch image; preserve its torch package'
PY
# New destinations only; clone/checkout fails rather than replacing existing work.
git clone --filter=blob:none --no-checkout https://github.com/flashinfer-ai/flashinfer.git "$work/baseline"
git -C "$work/baseline" fetch origin "$baseline_commit"
git -C "$work/baseline" checkout --detach "$baseline_commit"
git clone --filter=blob:none --no-checkout "$candidate_repository" "$work/candidate3r"
git -C "$work/candidate3r" fetch origin "$candidate_commit"
git -C "$work/candidate3r" checkout --detach "$candidate_commit"
for source in "$work/candidate3r" "$work/baseline"; do
  git -C "$source" submodule update --init --depth 1 --jobs 8 \
    3rdparty/cccl 3rdparty/cutlass 3rdparty/nixl 3rdparty/spdlog
  git -C "$source" submodule status --recursive
done
python3 -m pip install --disable-pip-version-check --upgrade-strategy only-if-needed \
  -c "$recipe_dir/runtime-constraints.txt" \
  'nvidia-cutlass-dsl[cu13]==4.7.1' 'cuda-python==13.2.0' 'cuda-bindings==13.2.0' \
  'cupti-python==13.2.0' 'nvidia-cuda-cupti==13.2.86' \
  'nvshmem4py-cu13==0.3.1' 'nvidia-nvshmem-cu13==3.6.5' \
  'setuptools>=77' 'packaging>=24' 'apache-tvm-ffi==0.1.14.post1'
for source in "$work/candidate3r" "$work/baseline"; do
  python3 -m pip install --disable-pip-version-check --upgrade-strategy only-if-needed \
    -c "$recipe_dir/runtime-constraints.txt" --no-build-isolation -e "$source[cu13]"
done
python3 -m pip install 'pytest==8.4.2'
python3 -m pip install --no-deps 'apache-tvm-ffi==0.1.14.post1' 'cuda-core==1.2.1' 'cuda-pathfinder==1.5.4'
python3 - <<'PY'
import importlib.metadata as m
assert m.version('torch') == '2.12.0a0+5aff3928d8.nv26.5.50603568', 'Torch was replaced'
PY
