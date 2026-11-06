## Current tracing revision: completed GPU tests

**Tested commit:** `74ba96d551640938edde68d628b36ba404a7f331`. All **15 existing logical test cases / 36 rank-case executions** passed: four standalone split W4A16 cases, four EP1 cases, and seven EP4 cases on each of four ranks. Six per-rank JUnit files report **0 failures, 0 errors, 0 skips**; all test-group commands exited successfully. These results qualify the selected tracing revision, independently of the historical performance tables below.

- **Environment:** C2/infra devbox `fi-w4a16-trace-0925`, node `hu-pdx-38`; eight NVIDIA B300 SXM6 AC (SM103), driver 590.48.01. Tests ran serially on GPU0 for split/EP1 and GPUs0–3 for EP4.
- **Image:** `nvcr.io/nvidia/pytorch:26.05-py3`, digest `sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`. The container PyTorch `2.12.0a0+5aff3928d8.nv26.05` was preserved; its runtime reports CUDA13.2. CUTLASS DSL4.8.0, cuda-python13.2.0, cuda-core1.2.1, TVM FFI0.1.14.post1 and pytest9.1.1 were installed. The NVSHMEM wheel is3.8.0; distributed test output reports the loaded runtime as3.6.5.
- **Coverage:** split 1CTA/2CTA weight-scale mapping and ordinary/fused finalization execute the shared decoder's no-op tracing hooks; MegaMoE cases cover config/runtime FP32 scales and routing, both token-return modes, activation/normalization/top-k contracts, and manual/automatic CUDA-graph replay. The graph test's historical function name says “two_rank”; this invocation ran with four ranks.

Exact setup dependencies from the recorded setup, run from a checkout of the tested commit inside the image above:

```bash
set -euxo pipefail
git checkout --detach 74ba96d551640938edde68d628b36ba404a7f331
git submodule update --init --depth 1 3rdparty/cutlass 3rdparty/cccl 3rdparty/spdlog
python -m venv --system-site-packages ../venv
source ../venv/bin/activate
unset PIP_CONSTRAINT
python -m pip install \
  'nvidia-cutlass-dsl[cu13]==4.8.0' 'cuda-python==13.2.0' 'cuda-core==1.2.1' \
  'apache-tvm-ffi==0.1.14.post1' 'nvshmem4py-cu13==0.3.1' 'nvidia-nvshmem-cu13==3.8.0' \
  'pytest==9.1.1' 'cupti-python==13.4.0' 'nvidia-cuda-cupti==13.4.92' \
  'nvidia-cuda-cccl==13.3.4.3.1' ninja einops tabulate nvidia-ml-py 'setuptools>=77' packaging
BUILD_NVEP=0 BUILD_NIXL_EP=0 BUILD_NCCL_EP=0 FLASHINFER_BUILD_NO_PIP=1 \
  python -m pip install --no-deps --no-build-isolation -e .
```

The unpinned setup utilities resolved to ninja1.13.0, einops0.8.2, tabulate0.10.0, nvidia-ml-py13.595.45, setuptools81.0.0 and packaging26.0; the complete freeze is preserved with the evidence. No replacement PyTorch wheel was installed.

Reproduction uses only existing public pytest nodes. These commands preserve the executed flags and selectors; the actual external wrapper only appended a separate JUnit filename for each rank and is unnecessary to run the tests:

```bash
unset CUTE_DSL_COMPILER_OPT MEGA_NO_DIST
export PYTHONPATH="$PWD" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTEST_ADDOPTS=''
export OMP_NUM_THREADS=1 MEGA_USE_NCU=0
export FLASHINFER_WORKSPACE_BASE="$PWD/../cache/flashinfer"
export CUTE_DSL_CACHE_DIR="$PWD/../cache/cute"
export CUDA_VISIBLE_DEVICES=0

timeout 1200 python -m pytest -q -s --maxfail=1 --confcutdir=tests/moe \
 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_weight_scale_mapping[1cta-k]' \
 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_weight_scale_mapping[2cta-k]' \
 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a16-ordinary]' \
 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a16-fused]'

timeout 1200 python -m pytest -q -s --maxfail=1 --confcutdir=tests/moe_ep \
 tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py::test_nvfp4_w4a16_fp32_scales_and_routing

export CUDA_VISIBLE_DEVICES=0,1,2,3
timeout 1800 python -m torch.distributed.run --standalone --nproc-per-node=4 -m pytest -q -s --maxfail=1 --confcutdir=tests/moe_ep \
 tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_w4a16_epilogue_contract \
 'tests/moe_ep/test_mega_cuda_graph_multirank.py::test_nvfp4_mega_two_rank_graph_replay_lockstep[w4a16-reuse_dispatch_warps-manual-False-runtime]' \
 'tests/moe_ep/test_mega_cuda_graph_multirank.py::test_nvfp4_mega_two_rank_graph_replay_lockstep[w4a16-None-auto-False-config]'
```

All parameterized cases actually reported by JUnit (full file/class selectors are in the commands above):

| Group / ranks | Existing case | Passed rank-cases |
|---|---|---:|
| split / 0 | `test_weight_scale_mapping[1cta-k]` | 1 |
| split / 0 | `test_weight_scale_mapping[2cta-k]` | 1 |
| split / 0 | `test_finalize_handles_cluster_padding_and_partial_tiles[w4a16-ordinary]` | 1 |
| split / 0 | `test_finalize_handles_cluster_padding_and_partial_tiles[w4a16-fused]` | 1 |
| ep1 / 0 | `test_nvfp4_w4a16_fp32_scales_and_routing[config-epi_warps]` | 1 |
| ep1 / 0 | `test_nvfp4_w4a16_fp32_scales_and_routing[config-reuse_dispatch_warps]` | 1 |
| ep1 / 0 | `test_nvfp4_w4a16_fp32_scales_and_routing[runtime-epi_warps]` | 1 |
| ep1 / 0 | `test_nvfp4_w4a16_fp32_scales_and_routing[runtime-reuse_dispatch_warps]` | 1 |
| ep4 / 0–3 | `test_nvfp4_w4a16_epilogue_contract[swiglu-norm]` | 4 |
| ep4 / 0–3 | `test_nvfp4_w4a16_epilogue_contract[minimax]` | 4 |
| ep4 / 0–3 | `test_nvfp4_w4a16_epilogue_contract[minimax-norm-topk]` | 4 |
| ep4 / 0–3 | `test_nvfp4_w4a16_epilogue_contract[situ-norm]` | 4 |
| ep4 / 0–3 | `test_nvfp4_w4a16_epilogue_contract[situ-linear-norm-topk]` | 4 |
| ep4 / 0–3 | `test_nvfp4_mega_two_rank_graph_replay_lockstep[w4a16-reuse_dispatch_warps-manual-False-runtime]` | 4 |
| ep4 / 0–3 | `test_nvfp4_mega_two_rank_graph_replay_lockstep[w4a16-None-auto-False-config]` | 4 |

Per-rank JUnit closure (elapsed values are test-suite wall time, not kernel benchmarks):

| Group | Rank | Cases | Failures / errors / skips | JUnit seconds |
|---|---:|---:|---|---:|
| ep1 | 0 | 4 | 0 / 0 / 0 | 57.240 |
| ep4 | 0 | 7 | 0 / 0 / 0 | 197.120 |
| ep4 | 1 | 7 | 0 / 0 / 0 | 197.116 |
| ep4 | 2 | 7 | 0 / 0 / 0 | 197.118 |
| ep4 | 3 | 7 | 0 / 0 / 0 | 197.116 |
| split | 0 | 4 | 0 / 0 / 0 | 384.661 |

Complete raw pytest summary lines follow. EP4 stdout is interleaved and does not label ranks; rank identity/counts come from the separate JUnit files above.

```text
[split]
4 passed, 368 warnings in 384.66s (0:06:24)
[ep1]
4 passed, 844 warnings in 57.54s
[ep4]
7 passed, 1546 warnings in 197.69s (0:03:17)
7 passed, 1546 warnings in 197.70s (0:03:17)
7 passed, 1546 warnings in 197.70s (0:03:17)
7 passed, 1546 warnings in 197.71s (0:03:17)
```

Warnings are preserved: deprecations, unknown pytest marks under the restricted conftest scope, and initial EP4 hostname-resolution retries. Adding the same-node mapping `127.0.0.1 hu-pdx-38` to the container's `/etc/hosts` resolved rendezvous; no repository/test change was needed. The external smoke also preserved an argument-parsing failure and an unsupported helper-keyword failure before target launch. A later E16/T4 smoke produced exact finite outputs but left the selected cluster idle on two ranks, so it was not accepted as full tracing qualification.

**Native IKET smoke: PASS.** The completed external smoke uses the same 74ba96d source and container, EP4 H1024/I1024/E256/top8, 32 tokens/rank (128 globally), and fixed M256/N64/K256, group512, epilogue token return with atomic scheduling. It performs no tuning. The thunk is compiled before the rank barrier and then launches once per rank per profiler application pass; `run-iket` performs separate tracker and collection passes. Both passes produced finite BF16 results bit-identical to the existing W4A16 independent reference, covering **32,768 output elements/rank**. The profiler and hardened structure auditor exited successfully, followed by the `IKET_PASSED` receipt.

The full native grid remains `(2,1,74)`, with 148 CTAs/GPU; `--enabled-cluster 0,0,0 --postprocess all --keep` records two CTAs and 40 warp tracks/GPU. All 16 recorded transform warps execute matching ordered FC1/FC2 work sequences. Each transform K iteration has exactly one raw-TMA wait, free-TMEM wait, NVFP4 load/decode and BF16 store/commit subsection, properly contained in its parent range. Counts below are **warp-recorded ranges/iterations**, not distinct scheduler jobs.

| Rank | Collection PID | BF16 elements | Bit mismatches / nonfinite | Profiled launches | Transform warp ranges | K iterations / each subsection | Transform warps |
|---:|---:|---:|---|---:|---:|---:|---:|
| 0 | 14359 | 32,768 | 0 / 0 | 1 | 160 | 640 | 16 |
| 1 | 14360 | 32,768 | 0 / 0 | 1 | 160 | 640 | 16 |
| 2 | 14361 | 32,768 | 0 / 0 | 1 | 176 | 704 | 16 |
| 3 | 14362 | 32,768 | 0 / 0 | 1 | 160 | 640 | 16 |

Raw smoke summaries (tracker pass, collection pass, then structure audit):

```text
FLASHINFER_IKET_SMOKE_PASS,[{"rank": 0, "pid": 13537, "elements": 32768, "passed": true, "output_sha256": "72106cbb5b2dd65ced1d71588c1aa4fef2bd3a60cd9ccd0e815971dedd6cad03"}, {"rank": 1, "pid": 13538, "elements": 32768, "passed": true, "output_sha256": "04580040bf82bb97b82a1282696944b7920c2cf70a423851bec2beabb45a47b2"}, {"rank": 2, "pid": 13539, "elements": 32768, "passed": true, "output_sha256": "6c79e7f7a96c49134628c6c2b509d756de63e55680545e59900f910d5b57e41d"}, {"rank": 3, "pid": 13540, "elements": 32768, "passed": true, "output_sha256": "e8c8da76300af77360d02baf72c426e1457f5d6b6c27325e9cb4cae71cd04059"}]
FLASHINFER_IKET_SMOKE_PASS,[{"rank": 0, "pid": 14359, "elements": 32768, "passed": true, "output_sha256": "72106cbb5b2dd65ced1d71588c1aa4fef2bd3a60cd9ccd0e815971dedd6cad03"}, {"rank": 1, "pid": 14360, "elements": 32768, "passed": true, "output_sha256": "04580040bf82bb97b82a1282696944b7920c2cf70a423851bec2beabb45a47b2"}, {"rank": 2, "pid": 14361, "elements": 32768, "passed": true, "output_sha256": "6c79e7f7a96c49134628c6c2b509d756de63e55680545e59900f910d5b57e41d"}, {"rank": 3, "pid": 14362, "elements": 32768, "passed": true, "output_sha256": "e8c8da76300af77360d02baf72c426e1457f5d6b6c27325e9cb4cae71cd04059"}]
FLASHINFER_IKET_STRUCTURE_PASS,[{"rank": 0, "recorded_launches": 1, "transform_tile_ranges": 160, "transform_k_iterations_across_warps": 640}, {"rank": 1, "recorded_launches": 1, "transform_tile_ranges": 160, "transform_k_iterations_across_warps": 640}, {"rank": 2, "recorded_launches": 1, "transform_tile_ranges": 176, "transform_k_iterations_across_warps": 704}, {"rank": 3, "recorded_launches": 1, "transform_tile_ranges": 160, "transform_k_iterations_across_warps": 640}]
```

The smoke binds the clean 74ba96d package/oracle source digest `509275ca2345933a7715d6f0830c868f4e9d09fb08a7a2c07b8e2fab2629feb3`, recorded rank/PID, configuration, outputs and native JSON/Perfetto hashes. It is native compile/execute, finite-bit-oracle and postprocessed hook-structure qualification, **not** a SASS scanner audit, time-unit/duration claim, performance result, full numerical suite, Compute Sanitizer result or older-CuTe-wheel test. The external driver/auditor and native artifacts remain outside FlashInfer; the earlier E16/T4 idle-cluster capture remains a rejected smoke qualification, separate from this successful larger run.

Evidence retained outside the repository: `tracing-sync-20260925/test-audit.json`, six rank JUnit files and raw logs under `remote-validation/validation`, `runtime-allocation.json`, `pip-freeze.txt`, `setup-c2.sh` and `test-c2.sh`; successful smoke reports in `remote-validation/validation/iket-smoke`, the `IKET_PASSED` receipt and `smoke-driver-full-fixture.log`. No test, script, documentation or protected vendor source is added to FlashInfer by this tracing port.
