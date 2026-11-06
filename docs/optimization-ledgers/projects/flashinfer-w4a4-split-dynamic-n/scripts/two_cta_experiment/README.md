# Isolated M256 two-CTA dynamic-N experiment

Production remains untouched. `build_trial.py` copies pinned `de4f1aa4989998676d1d8a09da7c4afe1cb7c75b` and builds `two_cta_trial/core.py`; the process-local host binding is substituted by the launcher. Public logical tactics remain `(128,N)` only for this diagnostic adapter; the internal kernel is M256, cluster `(2,1)`.

## Source-traced contract

- `moe_nvfp4_swapab/kernel_fc12.py:_create_tiled_mmas`, `_setup_attributes`: group-2 main MMA M256 with per-CTA M128. `tiled_mma.partition_shape_C((256,N))` yields each CTA's accumulator `((128,N),1,1)` with rows at TMEM stride65536. Existing per-CTA up16/gate16 epilogue can be reused with channel base `tile_m*256 + cta_rank*128`.
- `dynamic_mainloop.py:compute_non_leader_cta_load_shift`: dynamic B split is `align16(valid)/2`; static TMA B partition is `allocated_N/2`. Nonleader TMA domain offset is their difference. Gather uses that dynamic start directly. B SMEM is only `allocated_N/2 × K` per CTA.
- SFB is not halved with B. `kernel_fc12.py` builds a separate one-CTA SFB TMA configuration, replicating the full SF token extent to both CTAs. Current experiment retains cp.async SFB: full N scales in each CTA, group-2 S2T.
- A/SFA use local 128-channel partitions (`tiled_mma.get_slice(cta_rank)`) of the M256 tile. Weight preparation remains up16/gate16.
- `blackwell/custom_pipeline.py`: TMA transaction count is twice the local TMA bytes, leading MMA waits for both CTA producers. Accumulator consumer arrivals count256. Pipelines receive the group-2 cluster layout. Only leader issues group-2 S2T/MMA and accumulator commits.
- TMEM alloc uses `is_two_cta=True` and a shared deallocation barrier. Initialize cluster-wide barriers before use, launch a multiple of two CTAs, and schedule tile IDs per cluster (`block//2`, `grid//2`) so paired CTAs never read divergent routing metadata.

`inspect_two_cta.py` compiles metadata only. Observed NVFP4 N256 layouts: local A16KiB, local B16KiB, SFA2KiB, SFB4KiB per stage; each CTA accumulator128×256. SFB TMEM span32 columns. All four major dtype families compiled the same geometry.

## Diagnostics

GPU0 on C1 `fi-w4a4-dyn-n-1024`, managed `/usr/local/bin/h`, image `nvcr.io/nvidia/pytorch:26.05-py3`, CuTe4.7.1. Remote sources live only in `/workspace/flashinfer-w4a4-split-dynamic-n/transfer/two-cta-experiment`.

No historical baseline campaign reruns and no retention claims. Smoke commands use a bounded timeout; phase timings are development diagnostics only. Frozen `de4f1aa4989998676d1d8a09da7c4afe1cb7c75b` one-CTA controls run on the same GPU before the variants.

## Completion relay

CuTe DSL 4.7.1 `MbarrierArray.arrive` handles remote destinations for `AsyncThread`, but its `AsyncLoad` branch calls local `arrive_cp_async_mbarrier` and ignores the destination. A single cluster CpAsync pipeline expecting 256 producer arrivals therefore deadlocks: each local barrier receives only 128 arrivals.

- V1 (`core.py`): producers explicitly commit/wait cp.async, then notify a cluster `PipelineAsyncUmma` with 256 producer arrivals. Correct smoke results, but serial producer waits make it slower than the one-CTA control.
- V2 (`relay_core.py`): retain a local CpAsync pipeline with 128 producer arrivals per CTA. Both MMA warps wait for their local CpAsync completion, acquire and commit a separate cluster `PipelineAsyncUmma` with 64 producer arrivals, and only the leader waits for both relays and issues group-2 S2T/MMA. Leader group-2 releases free both local CpAsync stages. This needs no extra relay warp and preserves asynchronous producers.
- Old split FC1 uses the same local-completion-then-cluster-relay principle, with its separate transform warp11 and `a_sync_transform_pipeline`. V2 reuses the MMA warp in each CTA.

Each CTA retains full-N SFB storage while B data is halved. Per-stage local storage is 38KiB for NVFP4 and 33.5KiB for MXFP8/mixed MXFP4×MXFP8. Five NVFP4 stages and six FP8 stages fit; six NVFP4 stages do not.

## Initial measured diagnostics

Balanced synthetic routes, 16,384 tokens/routes, 32 experts, FC1 (channels4096,K7168), FC2 (channels7168,K2048), static N256. Cold L2, CUPTI, CUDA graphs, 3 dry runs, 15 repeats, median microseconds. The control uses de4 stage policy (FC1=3, FC2=4); V2 reuses the identical harness and GPU0. These are phase development screens, not the requested full benchmark retention results.

| Mode | Kernel | Stages | FC1 us | FC2 us |
| --- | --- | ---: | ---: | ---: |
| NVFP4 | frozen de4 one-CTA | policy | 365.630 | 248.639 |
| NVFP4 | V2 two-CTA | policy | 354.591 | 239.103 |
| NVFP4 | V2 two-CTA | 5 | 304.415 | 234.720 |
| MXFP8 | frozen de4 one-CTA | policy | 481.375 | 315.552 |
| MXFP8 | V2 two-CTA | policy | 545.407 | 305.631 |
| MXFP8 | V2 two-CTA | 5 | 364.958 | 293.311 |
| MXFP8 | V2 two-CTA | 6 | 470.975 | 288.832 |
| MXFP4×MXFP8 | frozen de4 one-CTA | policy | 447.197 | 304.255 |
| MXFP4×MXFP8 | V2 two-CTA | 5 | 329.439 | 286.815 |
| MXFP4×MXFP8 | V2 two-CTA | 6 | 450.078 | 284.255 |

Repeated NVFP4 stage5 measurements were FC1 304.575us / FC2 234.368us, followed by repeated one-CTA controls 365.375us / 247.840us.

## Combined epilogue overlap

`build_overlap.py` produces frozen `overlap_core.py` from V2 and the sibling `overlap_experiment/overlap_trial/overlap2_core.py` design. It uses loader warps0–3, epilogue warps4–7, MMA/relay warp8, and two accumulator stages when N≤128. N256 retains one accumulator but permits next-tile loads while the dedicated epilogue runs. Each CTA retains its own128-row TMEM accumulator; separate512B shared epilogue scratch prevents aliasing active A loads. Dynamic accumulator offsets require explicit32-column alignment hints. Both CTA MMA producer states advance identically.

| Mode | N | Stages | FC1 us | FC2 us |
| --- | ---: | ---: | ---: | ---: |
| NVFP4 | 128 | 5 | 281.567 | 200.959 |
| NVFP4 | 256 | 5 | 286.815 | 213.216 |
| MXFP8 | 128 | 5 | 432.352 | 278.687 |
| MXFP8 | 256 | 5 | 359.262 | 271.679 |
| MXFP8 | 256 | 6 | — | 265.919 |
| MXFP4×MXFP8 | 128 | 5 | 415.999 | 269.535 |
| MXFP4×MXFP8 | 256 | 5 | 345.343 | 264.479 |

W4A8 FC1 prefers the five-warp V2 relay in this screen. NVFP4 prefers overlap N128, and FP8 FC2 prefers overlap N256. These choices still need the actual-routing benchmark and autotuning screen.

Focused V1 FC2 smoke is exact FP32 against small power-of-two scale Torch matmul for N1,17,129,255,257. V2 FC2 smoke is exact for N1,129,255,257 × K64,256,384, including K tails. V2 FC1 smoke includes per-token false/true, N1,129,255,257, and M256/K256; all finite, at least 99.9939% BF16 equality to the existing Torch activation smoke (this does not establish a bit-exact activation reference). The overlap variant has exact NVFP4 FC2 smoke at N17,129,257 with a single cluster processing multiple tiles, exercising both accumulator buffers. It also has exact MXFP8 and mixed MXFP4×MXFP8 raw FC2 smoke for N17,129,257, M384 (channel tail), K256, random signs and power-of-two block scales. Full numerical and sanitizer coverage remains deferred.

Local raw logs are collected under `artifacts/two-cta-experiment/` by `collect_logs.py`. The experiment is never synced over the production repository.

## Coherent integration screen

`build_combined.py` composes the frozen geometry/overlap prototypes with production Gather4 from `dcdcae2518767e25e4ca71d62b3749f97894ba21` and the epilogue agent's metadata-preload/256-bit-store snapshot (`69dfd49f2e1bde42b93e1d2545e8d0e0d08bc60b2220885447b3dec9e82d2d5b`). Gather4 uses `.cta_group::2` and clears the mbarrier peer bit so both CTAs signal the leader. This is supported by [PTX 9.2 cp.async.bulk.tensor](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-bulk-tensor) and follows the existing Rubin helper.

| Mode | Geometry | FC1 us | FC2 us |
| --- | --- | ---: | ---: |
| NVFP4 | M256 N128, 5 stages, separate epilogue | 270.399 | 146.304 |
| NVFP4 | M256 N256, 5 stages, separate epilogue | 266.687 | 140.191 |
| MXFP8 | M256 N256, 5 stages, separate epilogue | 353.246 | 203.997 |
| MXFP4×MXFP8 | M256 N256, 5 stages, separate epilogue | 337.760 | 195.008 |
| MXFP4×MXFP8 | M256 N256, 5 stages, inline epilogue | 324.638 | — |
| NVFP4 | M128 N128, policy stages, separate epilogue | — | 156.768 |
| NVFP4 | M128 N256, policy stages, separate epilogue | — | 144.736 |
| MXFP8 | M128 N256, policy stages, separate epilogue | — | 218.464 |
| MXFP4×MXFP8 | M128 N256, policy stages, separate epilogue | — | 207.392 |

`build_unified.py` consolidates those choices into one kernel. M128 permits N16/32/64/128/256 and cluster(1,1); M256 permits N128/256 and cluster(2,1). Channel counts remain multiples of128, with the second CTA predicated off on a128-channel tail. Two-CTA tactics use five stages. Separate epilogue warps are used for FC2 N≥128 and homogeneous two-CTA FC1; mixed-format two-CTA FC1 keeps the five-warp producer/epilogue arrangement. No new public tactic flag or backend is introduced.

The unified screen reproduces the composed results: NVFP4 M256 N256 FC1/FC2 267.169/140.287us; mixed M256 N256 324.350/194.752us. Exact focused unified smokes cover one-CTA N16/32/64 FC1 per-token and FC2 at K64, plus two-CTA MXFP8/mixed FC2 N17/129/257 at M384/K256/N256. Production core and generic wrappers were updated locally, with Ruff checks/format, Python compilation, and `git diff --check` passing. Parent owns commit, deployment, actual-routing benchmarking, and retention decisions.

The two-CTA SFB layout remains unchanged. PTX group-2 S2T copies both CTAs' local shared-memory sources; its warp-broadcast variants are intra-CTA, so removing the peer source would be incorrect. Mega's SFB TMA multicast is a possible later way to avoid duplicate global traffic while preserving full local SFB staging.

Example commands from the remote `candidate` directory:

```sh
export CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1
../.venv/bin/python ../transfer/two-cta-experiment/probe_perf.py --repo . --mode nvfp4 --tokens 16384 --tiles 256 --factors 1 --stages 0
../.venv/bin/python ../transfer/two-cta-experiment/run_trial.py --variant relay --script probe_perf.py --repo . --mode nvfp4 --tokens 16384 --tiles 256 --factors 1 --stages 5
```
