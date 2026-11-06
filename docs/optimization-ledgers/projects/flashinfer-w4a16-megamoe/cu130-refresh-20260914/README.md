# CUDA 13.0 current-head performance refresh

The full 1–8192-token split/MegaMoE comparison completed successfully at `7f1a093119f12b1f5b79d50bf6d0c951069224e5`. No repository source was changed. Published to [PR #5019](https://github.com/flashinfer-ai/flashinfer/pull/5019); exact live readback passed and the PR remains ready for review. [Publication receipt](publication-check.json).

- Devbox: `fi-w4a16-cu130-0914`, C2 / `infra`, `hu-pdx-87`, eight B300 SXM6 AC / SM103 GPUs, driver590.48.01. Image `nvcr.io/nvidia/pytorch:25.11-py3`, system nvcc13.0.88, image Torch2.10.0a0+b558c986e8.nv25.11/CUDA13.0.
- Actual native compiler: DSL4.7.1 cu12, compiler12.9; direct-BF16 decoder gate false. All8 workers loaded the same native library, CUDA13.0 runtime/CUPTI, NCCL2.28.8 and NVSHMEM3.4.5. The fallback gate was not patched. Native SHA256: `77f8826afaa781db852c18fa0dc553178791a451c89338033fcf6aa5d328657d`.
- Setup preserves image Torch and library paths. Task-local `.venv-cu130` has system-site-packages and pinned no-deps helpers. nccl4py0.5.0/extensions0.1.0 satisfy the current source boundary. Auxiliary13.3 nvdisasm/CCCL packages do not establish the selected native compiler version. [Exact setup](setup.sh), [environment](environment.json), [worker maps](worker-maps.json), [runtime components](runtime-details.json).
- Numerical validation:6 exact decoder cases;8 EP1 oracle/FP32-scale-and-routing cases;6 EP2 geometry/tail cases per rank. Both returns and N64/N128 wrapping are covered. Unchanged tolerances; no full-suite/native-profile rerun. [Command](validate.sh), [raw output](validate.log), [XML](remote-logs/validation).
- Benchmark: current public harness, individually autotuned split and Mega against matching packed weights/scales/inputs/routes; EP8 H7168/I2048/E256/top-k8, global tokens1–8192, non-fused split finalize, warmup=3 and100 measured cold-L2 CUDA-graph CUPTI samples per row. Routing selection, staging, communication, compute and final reduction are timed; model router projection, preparation, compile, autotune, graph capture and L2 flush are excluded. No cross-backend refcheck; independent numerical tests remain the oracle. [Command](benchmark.sh), [raw output](benchmark.log), [measurement audit](MEASUREMENT_AUDIT.md).
- Results:28 latency rows,2800 primary samples,112 rank/token Mega tactics,14 checked speedups; all ranks agree and all winners belong to the current four-dictionary catalog. [Reader validation](parsed/validation.json), [all samples](parsed/results.json), [selected tactics](parsed/selected-tactics.json). Split's own tuner remains unchanged;112 is the Mega selection count.
- Timing utility wall sum: `14.932385` seconds across28 cases, including its capture/flush/activity processing/reduction. This is not end-to-end sweep time or a GPU latency metric. First-use support compilation dominated elapsed time; no iteration-count reduction was used.
- Closure:4896 tracked source files match the canonical local checkout; remote head/status and native hash remained unchanged; normal benchmark exit0 with `BENCHMARK_COMPLETE`; no CUPTI fallback/traceback and no remaining GPU process. Local benchmark stream matches downloaded remote log byte-for-byte after the HAI container prefix. [Download verification](download-verification.json), [closure](remote-logs/closure.json), [archive](remote-evidence.tar.gz).
- Allocation: managed `/usr/local/bin/h`, bare, no size. The initial `ziangli` request lacked quota; only its queued task resources were canceled/deleted, then `infra` succeeded. The prior CUDA13.2 devbox was untouched. [Allocation request](request.json). The current CUDA13.0 devbox remains available.
- Diagnostic note: the first optional runtime-components probe assumed `/usr/local/cuda/version.json`, absent in this image; a saved dpkg-based probe then verified CUPTI13.0.85. This metadata-only failure did not affect tests or timing. Both probe logs are retained.

| Global tokens | Split W4A16, non-fused finalize (ms) | W4A16 MegaMoE (ms) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 0.090673 | 0.081809 | 1.1083× |
| 2 | 0.117761 | 0.122049 | 0.9649× |
| 4 | 0.165169 | 0.133489 | 1.2373× |
| 8 | 0.181313 | 0.163266 | 1.1105× |
| 16 | 0.213746 | 0.185649 | 1.1513× |
| 32 | 0.251570 | 0.221602 | 1.1352× |
| 64 | 0.278898 | 0.251313 | 1.1098× |
| 128 | 0.291282 | 0.252994 | 1.1513× |
| 256 | 0.306515 | 0.247842 | 1.2367× |
| 512 | 0.295762 | 0.268978 | 1.0996× |
| 1024 | 0.313587 | 0.282274 | 1.1109× |
| 2048 | 0.359523 | 0.346067 | 1.0389× |
| 4096 | 0.551333 | 0.509108 | 1.0829× |
| 8192 | 0.982024 | 0.851399 | 1.1534× |

Over 8–8192 tokens: geometric mean speedup **1.1245×**; 11/11 rows faster.

All times are medians of 100 cold-L2 CUPTI samples, taking the maximum rank span per iteration; CUDA graphs enabled. The saved launch command must separately establish non-fused split finalization and environment provenance.


Tokens1/2/4 are displayed but excluded from retention; only token2 is slower. This is one complete sequential sweep, with no row replacement or minima from repeated runs and no confidence-interval claim. The CUDA13.2 table remains unchanged at its recorded source/environment; these results do not establish a controlled cross-stack comparison or an individual-optimization speedup.

The public before-body is preserved in `pr-before.json`, including the older CUDA13.0 table. `PR_BODY.after.md` is the reviewed and published replacement; `body-preparation.json` verifies exact preservation of the CUDA13.2 table and the existing checklist/appendix.

Remote checkout: `/workspace/flashinfer-w4a16-megamoe-cu130/flashinfer`. Run helpers through `python3 cu130-refresh-20260914/remote.py <script.sh>` from the owning project root; this invokes the managed HAI CLI from an existing HAI checkout.
