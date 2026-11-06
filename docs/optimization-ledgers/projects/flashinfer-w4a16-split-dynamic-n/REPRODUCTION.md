<details>
<summary>Benchmark environment setup and reproduction</summary>

The retained measurements compare baseline `316faec37a4706a2ecc7d46265087f8190b40baa` with measured implementation `9ec90d0696752c72ff826c8880e58515ace84e60`. Current source `ef24c9a61a00f8aae27163feddb625e895772806` keeps runtime-N helpers inside the split kernel, aligns deterministic combine and parameterized activation arithmetic with MegaMoE, and uses one shared exact reference for dense and unfused split/unified tests. The K3 EP8 campaign additionally compares the same baseline with `6e070a25f6cdd3c07c715590dd2b0554aaecda0c`; current production source is byte-identical to that measured candidate. Existing measurements are neither rerun nor relabeled.

`65a563a447eb23e55177eec907533439180d760c` is the recorded standalone-finalizer measurement head, with 16 medians and 1,600 samples. Its cited analytical signed-zero/subnormal tests are historical and are absent from the current test tree. The current activation-alignment changes affect parameterized SwiGLU and SiTU; default SwiGLU operation order, fused FC2 arithmetic and the standalone finalizer remain unchanged by this follow-up. Dynamic-N helper bodies retain their measured provenance after the documented signature normalization. With parameterized SwiGLU disabled, the active default activation and both unfused FC2 store paths match `62d4412a` at the AST level; the negative-log2e FP32 coefficient is `0xbfb8aa3b` in both. The new parameterized/SiTU branches are excluded by compile-time conditions in the earlier H7168/SwiGLU benchmark configuration; the separate K3 benchmark exercises SiTU. This is source-arithmetic equivalence, not current whole-kernel PTX equality or a new performance result. The original H7168 full-MoE measurements remain at `9ec90d0`, finalizer-only measurements remain at `65a563a4`, and the K3 EP8 full-MoE measurements are at `6e070a25`. Their separate scopes and sources are retained.

In the pinned container, run from the selected revision's checkout:

```bash
git submodule update --init --recursive 3rdparty/cutlass 3rdparty/cccl 3rdparty/spdlog
python -m venv --system-site-packages ../split-w4a16-venv
source ../split-w4a16-venv/bin/activate
python - <<'PYSETUP'
import importlib.metadata as metadata
from pathlib import Path
import sys
Path(sys.prefix, "constraints.txt").write_text(
    "torch==" + metadata.version("torch") + "\n"
)
PYSETUP
PIP_CONSTRAINT="$VIRTUAL_ENV/constraints.txt" BUILD_NVEP=0 \
python -m pip install --no-build-isolation -e '.[cu13]' \
  'nvidia-cutlass-dsl[cu13]==4.7.1' 'cupti-python==13.4.0' \
  'nvidia-cuda-cupti==13.4.58' 'pytest==9.1.1'
export TORCH_EXTENSIONS_DIR="$PWD/../split-perf-cache/torch"
export FLASHINFER_WORKSPACE_BASE=/root
```

Run this from each revision's repository root for each finalize mode. Use a fresh process for each source/finalize/repeat arm. The measured order is before/after then after/before for each finalize mode. It calls the existing benchmark's W4A16 arm directly, preserving its input generation, routing, wrapper, tuner and timer while avoiding other backends. Release inputs between token counts; both benchmarked revisions use identical code below.

```bash
CUDA_VISIBLE_DEVICES=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0 \
PYTHONPATH=.:benchmarks python - <<'PYBENCH'
import gc
import torch
from cupti import cupti
from flashinfer.autotuner import AutoTuner
import bench_moe_deepseek as bench

use_fused_finalize = False  # Repeat with True to measure fused finalize separately.
for tokens in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384):
    rows, _ = bench._benchmark_single(
        n=tokens, warmup=10, iters=100,
        num_local=32, local_offset=0,
        use_cuda_graph=True, use_cupti=True,
        use_wrapper=True, do_autotune=True,
        use_fused_finalize=use_fused_finalize,
        profile_cuda=False, profile_backend="cute-dsl-w4a16",
        backends=("cutedsl",), autotune_cache=None,
    )
    assert len(rows) == 1 and rows[0].backend == "CuteDSL W4A16"
    print(use_fused_finalize, tokens, rows[0].latency_ms * 1000, flush=True)
    gc.collect()
    torch.cuda.synchronize()
    torch.cuda.empty_cache()
PYBENCH
```

For a fixed-tactic diagnostic, save a row cache after its normal AUTO run with `AutoTuner.get().save_configs(cache_path)` and repeat the same native call on each source with `do_autotune=False, autotune_cache=cache_path`. The diagnostic harness rejects a cache miss, verifies the selected FC1/FC2 tactic and leaves the input cache unchanged. Keep these measurements separate from the normal AUTO table.

Retained numerical validation at `eb784bbb14623995c4110217c826f4b724e647bf`: 119 dense/trace CuTe DSL cases passed in 118.64s (232 unrelated cases deselected), and 149 unfused split cases passed in 203.86s (512 unrelated cases deselected), without selected skips. The 144 original-versus-shared Mega-reference configurations again match BF16 storage bits on one rank and each of four ranks. The current shared oracle lives at `tests/test_helpers/w4a16_reference.py`; dense and MoE reuse BF16 decoding, scale-layout inversion, controlled FP32 GEMM and post-GEMM alpha. The dense follow-up changes no production code. The final shared-utility relocation preserves the reference byte-for-byte and changes only seven consumers' imports; those recorded numerical tests are not relabeled as runs at `ef24c9a61a00f8aae27163feddb625e895772806`. Earlier eight unified, two W4A4 and 12 Mega kernel/reference passes remain attributed to `6e070a25f6cdd3c07c715590dd2b0554aaecda0c`. Current commands and raw summaries are in the validation section; split W4A16 fused TMA-reduce correctness is outside scope.

At `6e070a25f6cdd3c07c715590dd2b0554aaecda0c`, both unfused four-rank NCCL graph tests passed on all ranks using GPUs 4–7; both NIXL cases skipped because that backend is unavailable. The command uses a fixed loopback rendezvous and selects the project-local NCCL 2.30.7 package for transport integration. The separate K3 distributed benchmark also explicitly selects this library; earlier single-GPU timing remains unchanged. An initial missing-runner invocation exited 127 before any GPU test executed; after the runner was staged, the complete test command exited zero. To reproduce the unfused integration result, use this revision's checkout with NCCL-EP installed and the project virtual environment:

```bash
project=/workspace/flashinfer-w4a16-split-dynamic-n
cd "$project/candidate"
"$project/.venv/bin/python" -m pip install --no-deps \
  --target "$project/ep-nccl-2.30.7" 'nvidia-nccl-cu13==2.30.7'
CUDA_VISIBLE_DEVICES=4,5,6,7 TRTLLM_ENABLE_PDL=1 \
FLASHINFER_DIST_AWARE_AUTOTUNE=0 PYTHONPATH="$PWD" \
LD_LIBRARY_PATH="$project/ep-nccl-2.30.7/nvidia/nccl/lib:${LD_LIBRARY_PATH:-}" \
"$project/.venv/bin/python" -m torch.distributed.run \
  --nnodes=1 --master-addr=127.0.0.1 --master-port=29516 --nproc_per_node=4 \
  -m pytest -x -q --tb=short -ra \
  tests/moe_ep/test_split_layer_w4a16_cudagraph_multirank.py \
  -m 'nvep and gpu_4' --backend=both
```

The selected NCCL target was verified as 2.30.7 with `ctypes`/`ncclGetVersion` and its library map during environment qualification; `torch.cuda.nccl.version()` reports PyTorch's compiled 2.30.4. Retained transport logs remain under `evidence/exact-migration-6e070a25f6cdd3c07c715590dd2b0554aaecda0c/`; the missing-runner launch log is preserved separately. No sanitizer was rerun at the current head. Full-MoE timing is retained at the measured revisions above, including production-identical K3 candidate `6e070a25`; no timing is relabeled as a run at `eb784bbb` or the relocation head `ef24c9a6`. The relocation has 39 source checks, eight-file compilation and import-path/symbol validation; these are static checks only: the existing devbox was unavailable before transfer/execution, and local Python lacks Torch/pytest; no runtime import or pytest collection result is claimed.

</details>
