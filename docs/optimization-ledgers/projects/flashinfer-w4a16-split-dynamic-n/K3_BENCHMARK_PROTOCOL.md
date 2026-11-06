# Kimi K3 split W4A16 EP8 before/after protocol

This is a separate, native distributed benchmark of the current PR. Preserve the existing 132 medians and `BENCHMARK_SECTION.md` unchanged. Run only the split W4A16 backend with unfused finalize; no MegaMoE or fused-finalize performance measurement is part of this campaign.

## Sources and controls

- **Before:** `316faec37a4706a2ecc7d46265087f8190b40baa`.
- **After:** `6e070a25f6cdd3c07c715590dd2b0554aaecda0c`.
- **Native entry point:** `benchmarks/bench_cute_dsl_moe_distributed.py`. The entry point, imported input-generation module and timer are byte-identical between these revisions:

| Source | SHA256 in both arms |
| --- | --- |
| `benchmarks/bench_cute_dsl_moe_distributed.py` | `9f4cab8d6b105a98aaddc2d3221f2ebe42e12cfbfc17faa6494745e961cff422` |
| `benchmarks/bench_moe_deepseek.py` | `9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371` |
| `flashinfer/testing/utils.py` | `bf532ebc0b82d3551a09bea6bc96017b838bcb52d461f9a5d19573ac9766ac34` |

- **Comparison scope:** current split dynamic N, SiTU arithmetic alignment and the common deterministic-finalizer rounding change are all present in the after arm. Attribute the result to the complete current patch; this is not an isolated dynamic-N comparison.
- **Hardware/runtime:** eight NVIDIA B300 GPUs on the existing C2 `w4a16-dyn-n-1024` node; `nvcr.io/nvidia/pytorch:26.05-py3`. Reuse the established project environment: Python 3.12.3, Torch `2.12.0a0+5aff3928d8.nv26.05`, CUDA runtime 13.2/system nvcc 13.2.78, imported CuTe DSL 4.7.1, CUPTI Python 13.4.0/library package 13.4.58. Record actual imported versions and device/topology snapshots for all four runs. The separately installed compiler/NVVM packages are 13.3.73; prior emitted CuTe PTX identifies the bundled compiler as 13.3.27. Do not describe either as the system CUDA version or claim fresh PTX inspection for this campaign.
- **Run order:** before R1 → after R1 → after R2 → before R2 (ABBA), one fresh eight-rank process group per sweep. Preserve the chronological order and report logical R1/R2 pairings explicitly.
- **Normal AUTO:** each sweep performs native local-compute tuning independently. `FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0` disables loading saved selections. Native in-memory caching across token rows remains unchanged. `scripts/with_arm_cache.sh` restores each checkout's native build cache at its canonical path; it does not load another run's AUTO selections. Saved per-row, per-rank tactic caches are evidence for later analysis, not primary-run inputs.

## Exact workload

- Native `--model kimi-k3`: H3584, I3072, 896 global experts, top-k16, one group/top-group, routed scaling 1.0, SiTU gate scale 4.0 and linear scale 25.0.
- Real EP8/TP1: 112 local experts per rank, expert offset `rank * 112`; intermediate dimension is unsharded. BF16 activations/output, NVFP4 prepared weights decoded to BF16, FP32 accumulation.
- Global token grid: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Each rank starts with `T // 8 + (rank < T % 8)` tokens; T1/T2/T4 include empty input ranks. A global T is not a per-GPU token count. Native capacity is `max(4096, ceil(max_grid / 8)) = 4096` tokens/rank; each dispatch uses the current runtime token count.
- Preserve native synthetic inputs: weight seed `1000 + rank`, input seed `42 + rank`, global router-logit seed 137 and routing-bias seed 911. Native split weight preparation is used; no Mega comparison-weight path is selected.
- K3 routing is precomputed on the CPU: FP32 sigmoid, stable descending selection of score plus bias (lower expert ID breaks ties), with selected unbiased sigmoid scores normalized by their sum plus `1e-20`. The native BF16 bias is scaled by 0.01 and converted to FP32. Routing and host-to-device transfer happen before timing.
- This measures the synthetic routed-expert core. Outer latent projections, RMSNorm, shared experts, router GEMM, attention and full-model serving are outside scope.

## Timing and communication scope

- The timed call includes NVLink one-sided dispatch of BF16 tokens/routing payloads, activation packing, local split W4A16 FC1/SiTU/FC2, deterministic unfused local combine, output staging and the distributed return combine. The backend is `NVLinkOneSidedAlltoAll` configured through `TorchDistBackend(dist.group.WORLD)`.
- Precomputed CPU routing, input/weight generation, weight preparation, allocations, JIT, autotuning, graph construction and L2 flushing are outside the measured activity interval. This differs from the previous single-GPU simulated-EP8 campaign, which timed routing but excluded inter-GPU communication.
- Ten explicit native warmup calls, then CUDA synchronization and a distributed barrier; 100 native CUPTI samples, CUDA graphs enabled, cold L2 enabled. Ten warmups match the existing split methodology and the native CLI default. A three-warmup example from a different campaign is not used here.
- Native `bench_gpu_time` receives `dry_run_iters=0`, `repeat_iters=100`, `enable_cupti=True`, `use_cuda_graph=True`, `cold_l2_cache=True`, `aggregate_op=max`. Its existing untimed graph setup and overhead estimation remain unchanged. Each measured replay follows a flush using a buffer twice the device L2 size.
- One rank-local sample is the CUPTI activity span from the earliest start to the latest end of correlated kernels/memcpys/memsets for that replay. It includes gaps and overlap within that span; it is not a sum of kernel durations. The native helper gathers rank vectors and takes the elementwise rank maximum, then the benchmark reports the median: `median_i(max_rank(sample_ms[rank][i]))`. This is not the maximum of eight rank medians.
- `--log-timing-samples` retains all 100 rank-MAX samples per row. Recompute the reported median from those vectors; cross-check the native CSV median, rounded to six decimals in milliseconds. Do not use host wall time as GPU latency.
- CUPTI is required. Native CLI initialization checks CUPTI availability; the observer turns timer-fallback warnings into errors. No CUDA-event fallback is accepted.
- PDL remains enabled. All four sweeps use `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`, `TRTLLM_ENABLE_PDL=1`, `FLASHINFER_DIST_AWARE_AUTOTUNE=0`, `FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0`, `OMP_NUM_THREADS=1` and the same Python environment. The project-local NCCL 2.30.7 library directory is selected through `LD_LIBRARY_PATH`; PyTorch's compiled NCCL version is a separate fact.

## Commands and observation

The native command below reproduces the workload and timing from each correct source-arm checkout. Use a fresh process for each sweep and the ABBA order above. It is a reproduction command, not authorization to rerun existing completed observations.

```bash
project=/workspace/flashinfer-w4a16-split-dynamic-n
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1
export TORCH_EXTENSIONS_DIR="$project/caches/torch-extensions"
export FLASHINFER_WORKSPACE_BASE=/root
export LD_LIBRARY_PATH="$project/ep-nccl-2.30.7/nvidia/nccl/lib:${LD_LIBRARY_PATH:-}"
arm=baseline # use candidate for the after arm
cd "$project/$arm"
export PYTHONPATH="$PWD"
bash "$project/scripts/with_arm_cache.sh" "$arm" \
  "$project/.venv/bin/python" -m torch.distributed.run \
  --nnodes=1 --nproc-per-node=8 \
  --master-addr=127.0.0.1 --master-port=29538 \
  benchmarks/bench_cute_dsl_moe_distributed.py \
  --model kimi-k3 --num-gpus 8 --parallel-modes ep --variants w4a16 \
  --timing cupti --cuda-graph --no-fused-finalize --precomputed-routing \
  --warmup 10 --iters 100 --log-timing-samples --verbose \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384
```

The launched campaign is `scripts/run_k3_distributed_campaign.sh`. It uses the same arguments through task-local `run_k3_distributed_observed.py`, staged under remote `k3-distributed-tools/`. The observer imports the checkout's unchanged native benchmark, verifies `flashinfer.__file__`, and calls the original distributed EP function. Before/after that function, it records provenance and saves each rank's AUTO cache. It does not replace routing, compute, timer or tactic selection. Those observations are outside the native timed call.

- Remote output: `/workspace/flashinfer-w4a16-split-dynamic-n/k3-distributed-6e070a25/`.
- Arm directories: `baseline-r1`, `candidate-r1`, `candidate-r2`, `baseline-r2`.
- Each arm retains `benchmark.log`, `exitcode`, full commit, checkout status/diff, GPU/process snapshot, eight `rankN.metadata.json` files and per-rank/per-token `rankN.tT.autotune.json` caches.
- Campaign-level artifacts retain the exact observer/driver source, initial/final `nvidia-smi -q`, topology and the local driver log `evidence/k3-distributed-campaign-driver.log`.
- Metadata includes actual import paths/distributions, source hashes, full CLI/model configuration, token rows, cache hashes and completion status. Native `DISTRIBUTED_MODEL_JSON`, `DISTRIBUTED_TIMING_SAMPLES_JSON` and `DISTRIBUTED_CSV` records remain the primary timing evidence.

## Validation, reporting and retention

1. Require all four sweep exit codes zero and all eight rank metadata files complete for every sweep. Verify full expected commits, exact model/options, eight ranks, correct module imports, matching software, identical native benchmark/timer hashes, and source differences confined to the expected production files. Audit recorded checkout differences; the existing vendor-header symlinks are environment setup, not unrecorded kernel edits.
2. Require the same 13 unique token rows, variant `w4a16`, no fused or Mega measurement rows, and exactly 100 finite positive rank-MAX samples per row. Verify native timing metadata and cache hashes. Compare each reconstructed median against native CSV rounding; reject fallback/failed/incomplete runs from final aggregates while preserving their raw artifacts.
3. Publish all **52 absolute medians** in four before/after repeat columns, retaining all **5,200 rank-MAX samples** separately. These are not 41,600 independent samples: the eight rank measurements have already been reduced per iteration. Preserve observed AUTO tactics per rank; different selections prevent an isolated fixed-tactic interpretation.
4. For token T, row speedup is `sqrt((before_r1[T] * before_r2[T]) / (after_r1[T] * after_r2[T]))`. Values above one mean faster. Report both per-repeat ratios as well as the paired ratio, and flag direction disagreement.
5. **Unfused retention excludes only T1/T2. T4 is included.** The 11 retention points are `4,8,16,32,64,128,256,512,4096,8192,16384`. Overall speedup is their geometric mean. Decode is the geometric mean over `4,8,16,32,64,128,256,512`; prefill is over `4096,8192,16384`. Also report these three aggregates separately for R1 and R2. Do not select row minima, pool samples across source arms, or substitute diagnostic measurements.
6. Keep K3 EP8 results separate from the earlier H7168/SwiGLU simulated-EP8 results and finalizer-only checks. Report repeat consistency, pointwise regressions and selected-tactic changes. There is no universal percentage threshold; two sweeps do not establish statistical significance. No additional benchmark or diagnostic launch is implicit in this document.

The token/retention convention follows the already verified [FlashInfer #6277](https://github.com/flashinfer-ai/flashinfer/pull/6277) precedent. The current campaign explicitly uses ten warmups and the native K3 distributed timing scope above. Source and evidence facts in this protocol are grounded in the current checkout and campaign scripts; historical benchmark data is not relabeled as this campaign.
