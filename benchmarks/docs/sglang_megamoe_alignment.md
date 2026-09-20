# Investigating MegaMoE versus Split in GLM-5.2 serving

This draft investigates why an end-to-end GLM-5.2 run can rank W4A16 MegaMoE below W4A16 Split even though [FlashInfer PR5019](https://github.com/flashinfer-ai/flashinfer/pull/5019) reports a faster MegaMoE microbenchmark. It adds controlled benchmark modes, not a kernel optimization or a demonstrated root-cause fix. Existing end-to-end runs are not repeated.

## Measured serving snapshot

These are the completed **8k1k** pairs, with identical input/output length arrays for each matched pair. Every point measures `10 × concurrency` requests; all 5,120 requests per arm succeeded. The complete three-arm 8k1k/1k1k sweep is a separate [InferenceX experiment](https://github.com/zianglih/InferenceX/pull/1), still running at this snapshot.

- Output throughput/GPU is `total_output_tokens / benchmark_duration / GPU_count`. Its numerator counts generated tokens only, while its denominator includes the end-to-end workload's prefill and decode work.
- Per-request interactivity is `1000 / median_tpot_ms` in tokens/s/user. The saved result contains the reported median, not individual latency arrays; no independent median reconstruction is claimed.
- Signed change is `100 × (Mega / Split - 1)`. These are matched concurrency comparisons, not comparisons at equal interactivity. Single runs do not establish statistical significance.
- Raw result files are unchanged copies in [`../results/glm52_sglang_20260920`](../results/glm52_sglang_20260920). `snapshot.json` contains hashes, exact values, configuration provenance and the arithmetic.

| TP=DP=EP | C | Requests/arm | Split output tok/s/GPU | Mega output tok/s/GPU | Mega change | Split interactivity | Mega interactivity | Mega change |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 4 | 40 | 107.988076 | 107.459001 | -0.4899% | 124.468965 | 120.773982 | -2.9686% |
| 4 | 8 | 80 | 171.711571 | 162.419426 | -5.4115% | 97.038671 | 93.224222 | -3.9309% |
| 4 | 16 | 160 | 227.676571 | 222.771697 | -2.1543% | 65.858361 | 63.508029 | -3.5688% |
| 4 | 32 | 320 | 334.263405 | 304.208853 | -8.9913% | 46.116767 | 41.147211 | -10.7760% |
| 4 | 64 | 640 | 418.559512 | 391.166091 | -6.5447% | 27.337966 | 25.671804 | -6.0947% |
| 4 | 128 | 1280 | 509.863807 | 470.624529 | -7.6960% | 16.455060 | 15.073434 | -8.3964% |
| 4 | 256 | 2560 | 584.828149 | 550.248568 | -5.9128% | 9.303878 | 8.757005 | -5.8779% |
| 8 | 4 | 40 | 53.237445 | 56.231134 | +5.6233% | 116.316665 | 121.960400 | +4.8520% |

The seven TP4 points favor Split in both metrics; TP8/C4 favors Mega. Consequently there is no uniform end-to-end ordering across the completed matrix. No individual-kernel speedup or regression is inferred from these serving results.

### Fixed serving configuration

| Field | Value |
|---|---|
| Hardware | NVIDIA B300, 4 or 8 GPUs in one node |
| Image | `lmsysorg/sglang:nightly-dev-cu13-20260918-20518d85` |
| Image index / amd64 digest | `sha256:d46a59f4b98658f728a1e006c003ad5ee0628e999fd8b2bef71ac1bb61b814da` / `sha256:b518f4f8cd15664cf0f733e9bf4fd2105c9c994882a369b247364394db99f596` |
| Model | `nvidia/GLM-5.2-NVFP4`, revision `53e0691e21895a3863a606dfd12910c69eba94ab` |
| SGLang source | PR39210 head `50eeb742961908afa68f4f523a1a19c5de6eb0b3` |
| Mega FlashInfer | PR5019 head `ad0a5e5e78e57070ec7c582efe733cb55cd8839f` |
| Split FlashInfer | PR5319 head `f9dd3c10541e087b716772245a9d033499745048` |
| Runtime | Torch `2.13.0+cu130`, CUDA 13.0, driver `590.48.01`; all five CuTe DSL providers `4.7.1` |
| Precision | Routed experts NVFP4 weights / BF16 activations; KV cache FP8 E4M3 |
| Topology | TP=DP=EP, DP attention enabled; Mega runner/A2A `flashinfer_megamoe`/`flashinfer_megamoe`; Split `flashinfer_cutedsl`/`none` |
| MTP | Both use `flashinfer_trtllm` / `none`; EAGLE steps=3, topk=1, draft tokens=4 |
| Memory / graphs | `mem_fraction_static=0.80`; prefill CUDA graphs disabled; decode graphs enabled |
| Target max prefill | 32768; chunked prefill global 32768 before DP normalization |
| Workload | Random nominal 8192 input / 1024 output, range ratio 0.8, unlimited arrival rate, `10C` measured / `2C` warmup requests |
| Per-DP capacity | TP4: `C/4`; TP8/C4: 1 per DP (global server capacity 8, client concurrency 4) |
| Mega switches | `SGLANG_FLASHINFER_CUTEDSL_NVFP4_W4A16=1`, `SGLANG_FLASHINFER_MEGAMOE_COMBINE_DTYPE=bf16`, `SGLANG_FLASHINFER_MEGAMOE_IN_KERNEL_FC2_REDUCE=0`, per-token activation quantization=0 |
| Split switches | `SGLANG_FLASHINFER_CUTEDSL_NVFP4_W4A16=1`, `SGLANG_FLASHINFER_MOE_FUSED_FINALIZE=0`, per-token activation quantization=0 |

The recorded W4A16 environment and fixed source dispatch select BF16 activations with NVFP4 routed-expert weights for Mega. This is not an independent GPU kernel trace. The shared/dense experts and native BF16 TRT-LLM MTP work must not be described as W4A16 routed-expert work. Existing package metadata conflicts are retained in the serving experiment; its environment is not claimed to be resolver-clean.

## Why PR5019 is not the same experiment

| Dimension | Published PR5019 microbenchmark | This serving experiment |
|---|---|---|
| Workload | One synthetic distributed routed-expert MoE | Full model, attention, shared experts, MTP, scheduling and prefill/decode mix |
| Split communication | Routed `MoeAlltoAll.dispatch/combine` | CuTe/none: replicated global input, expert-sharded local compute, output reduce-scatter |
| Shape | H7168 / I2048 / E256 / topk8 / groups8, selected4 | H6144 / I2048 / E256 / topk8 / groups1, selected1 |
| Routing input | Random pre-generated FP32 logits; published timing uses precomputed routes | Real router GEMM and routing, with actual model activations |
| Token count | Global MoE token rows (uneven partitions allowed) | Request concurrency is not MoE token rows; graph padding and MTP expansion matter |
| Mega capacity | `ceil(global_tokens / EP)` | Source-derived 32768 per rank in the recorded environment, including small decode batches |
| Versions | The PR's final performance table cites source `7100e0d16dd306e6fd2a8d734bdb03981d477901` | Mega `ad0a5e5e`; Split `f9dd3c10` includes later Split optimization |
| Environment | PyTorch NGC `26.05-py3`, CUDA13.2, Torch2.12 nightly, CuTe4.7.1 | SGLang nightly image, CUDA13.0, Torch2.13, CuTe4.7.1 |
| Timing | Cold-L2 CUDA graph CUPTI first-to-last GPU activity span; max rank per sample, 2×100 samples; precomputed routing excluded | Serving benchmark duration and reported TPOT; no per-layer span saved |

The old benchmark's TP mode is not a substitute: it replicates all experts and shards each expert's intermediate dimension. The required comparison retains expert sharding and each expert's full intermediate dimension.

## What is established and what still needs measurement

1. **Communication mismatch is established.** The original EP Split path uses all-to-all. Fixed SGLang CuTe/none chooses the full MLP token layout and gathers before the router, then reduce-scatters to the attention shards. SGLang's gather is semantic: its SUM_LEN path can be zero/copy/all-reduce; its MAX_LEN path uses padded all-gather. Replacing it with a single generic all-gather is not exact kernel-level replay.
2. **Capacity mismatch is established from code plus runtime inputs.** Serving constructs Mega with max(32768 prefill tokens, graph/decode capacity × draft tokens); DP normalization divides chunked-prefill size, not this max-prefill input. W4A16 staging loops over the allocated capacity, including clearing inactive route IDs, and capacity participates in tactic-cache lookup. The serving post-run cache archive is empty; the fixed constructor omits `knobs`, selecting the W4A16 built-in fallback when no entry exists. At this revision that fallback dictionary is independent of capacity. Thus capacity-sized staging/compiled geometry and default-versus-`auto` tuning must be measured separately; a capacity-driven change of the fallback tactic is not established. The post-run cache alone cannot exclude a transient earlier entry; no per-layer resolved-tactic trace was saved.
3. **Split version is a confound.** PR5319 changes the Split finalizer/PDL path. It does not contain this PR5019 W4A16 Mega backend. A same-revision comparison cannot be created by just copying the benchmark into that source tree. Keep communication and version ablations separate or explicitly pin a combined source revision.
4. **Integration remains a hypothesis.** Mega stages two FP32 alpha vectors with device-to-device `copy_` each forward. Their cost and whether they appear as memcpy nodes or copy kernels require a trace. The experimental `IN_KERNEL_FC2_REDUCE=0` path does **not** take the conditional extra `y.copy_` output path; it is not valid to blame that copy for these results.
5. **Whole-layer geometry differs despite matched DP flags.** Split routes gathered rows on each rank and runs a TP-sharded shared expert; Mega routes local rows and uses a TP1 shared expert. Graph capture can overlap shared-expert work on an alternate stream. A routed-expert-only speedup excludes these effects.
6. **Decode batch mapping remains a profiling requirement.** Capture the actual per-layer live rows, graph-padded rows, DP distribution, MTP acceptance and prefill/decode activity before mapping a concurrency point to a microbenchmark token count. With this EAGLE setup, target verification uses four rows per captured request; for example TP4/C128 capture bucket32 can mean128 target rows/rank, not32. Scheduler-padded rows are distinct from the inactive capacity tail.

### Fixed source references

- [Original Split EP A2A](https://github.com/flashinfer-ai/flashinfer/blob/ad0a5e5e78e57070ec7c582efe733cb55cd8839f/benchmarks/bench_cute_dsl_moe_distributed.py#L945-L1162), [old expert-replicated TP geometry](https://github.com/flashinfer-ai/flashinfer/blob/ad0a5e5e78e57070ec7c582efe733cb55cd8839f/benchmarks/bench_cute_dsl_moe_distributed.py#L1502-L1625).
- [SGLang FULL/SCATTERED selection](https://github.com/sgl-project/sglang/blob/50eeb742961908afa68f4f523a1a19c5de6eb0b3/python/sglang/srt/layers/communicator.py#L423-L438), [physical gather selector](https://github.com/sgl-project/sglang/blob/50eeb742961908afa68f4f523a1a19c5de6eb0b3/python/sglang/srt/layers/dp_attention.py#L829-L885), [output reduce-scatter](https://github.com/sgl-project/sglang/blob/50eeb742961908afa68f4f523a1a19c5de6eb0b3/python/sglang/srt/layers/communicator.py#L1498-L1524).
- [Serving capacity derivation](https://github.com/sgl-project/sglang/blob/50eeb742961908afa68f4f523a1a19c5de6eb0b3/python/sglang/srt/runtime_context.py#L2081-L2101), [Mega override](https://github.com/sgl-project/sglang/blob/50eeb742961908afa68f4f523a1a19c5de6eb0b3/python/sglang/srt/layers/moe/flashinfer_megamoe.py#L151-L165), [capacity-sized staging](https://github.com/flashinfer-ai/flashinfer/blob/ad0a5e5e78e57070ec7c582efe733cb55cd8839f/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/token_comm.py#L76-L102), [capacity-keyed tactics](https://github.com/flashinfer-ai/flashinfer/blob/ad0a5e5e78e57070ec7c582efe733cb55cd8839f/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py#L668-L681).
- [W4A16 fixed fallback](https://github.com/flashinfer-ai/flashinfer/blob/ad0a5e5e78e57070ec7c582efe733cb55cd8839f/flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/tuner.py#L270-L301), [default versus auto selection](https://github.com/flashinfer-ai/flashinfer/blob/ad0a5e5e78e57070ec7c582efe733cb55cd8839f/flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py#L235-L255).
- [Two CUDA alpha copies](https://github.com/flashinfer-ai/flashinfer/blob/ad0a5e5e78e57070ec7c582efe733cb55cd8839f/flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py#L171-L223), [conditional output copy/sync](https://github.com/flashinfer-ai/flashinfer/blob/ad0a5e5e78e57070ec7c582efe733cb55cd8839f/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py#L742-L785).
- [Shared-expert TP selection](https://github.com/sgl-project/sglang/blob/50eeb742961908afa68f4f523a1a19c5de6eb0b3/python/sglang/srt/models/deepseek_v2.py#L699-L734), [shared branch overlap](https://github.com/sgl-project/sglang/blob/50eeb742961908afa68f4f523a1a19c5de6eb0b3/python/sglang/srt/models/deepseek_v2.py#L948-L1037), [EAGLE verify width](https://github.com/sgl-project/sglang/blob/50eeb742961908afa68f4f523a1a19c5de6eb0b3/python/sglang/srt/model_executor/runner/decode_cuda_graph_runner.py#L288-L346).
- [PR5319 Split finalizer](https://github.com/flashinfer-ai/flashinfer/blob/f9dd3c10541e087b716772245a9d033499745048/flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py#L110-L175), [PDL launch](https://github.com/flashinfer-ai/flashinfer/blob/f9dd3c10541e087b716772245a9d033499745048/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L1398-L1407).

## Attribution plan

Run on a separate devbox using the same fixed SGLang image, in an isolated source/environment/cache with a new run ID. The existing serving sweep continues unchanged. The requested first calibration uses the same ad0 source for both Split and Mega:

1. Hold PR5019 source, random inputs, quantized weight bytes, shape, token rows and numerical settings fixed; vary Split all-to-all versus input gather/output reduce-scatter.
2. Hold that communication contract fixed; change only the H/routing-group preset, then routing inclusion. Router GEMM remains outside this microbenchmark and must be identified as such.
3. On Mega, compare live-sized capacity with 32768 tokens/rank using separate empty tactic caches and the serving-style omitted/default `None` policy. Separately compare explicit `auto` on representative token counts, isolating each token count to prevent reuse of a prior fixed-capacity cache winner. Do not mix cold compile/tuning with steady-state samples.
4. Profile SGLang Split and Mega separately to collect actual batch shapes and stage spans. The source points above guide trace inspection; they are not measured overheads.
5. Isolate the PR5319 Split changes on an explicitly pinned compatible source combination. Do not compare two different heads and label the ratio an isolated Mega kernel effect.

Record warmup, correctness checks, raw rank-MAX samples, timing mode, graph policy, routing inclusion, preset, collectives, capacity, source revision and selected tactics with every ablation. Preserve both wins and regressions. Keep `--refcheck` at its existing tolerance; do not silently relax numerical acceptance.

## Calibrated benchmark controls

The original default remains `--model-shape deepseek-v3 --ep-communication alltoall` with live-sized Mega capacity. New gather modes are EP W4A16 only. They keep E/EP experts and full I on each rank; the existing TP mode is unchanged.

- `--model-shape glm-5.2`: H6144 / I2048 / E256 / K8 / group1 / selected1 / scale2.5. Inputs and logits remain synthetic.
- `--ep-communication allgather`: padded BF16 input all-gather, global-row routing (unless precomputed), local experts, SUM reduce-scatter.
- `--ep-communication allreduce`: zero/copy/SUM-all-reduce input replication with the same local compute and SUM reduce-scatter. This is a **fixed padded** approximation of SUM_LEN, not SGLang's variable-size buffer/collective implementation.
- `--megamoe-max-tokens-per-rank 32768`: changes reserved Mega capacity without changing reported live input rows. An undersized capacity fails argument validation.
- CASE/RESULT JSON records shape, valid/padded token counts, collective, capacity, routing and timing settings. New-mode CSV labels include the mode identity to avoid mixing historical results. Profiler subprocesses receive all new flags; unsupported NCU gather simulations are rejected.

The helper initializes/masks collective padding and returns only the original valid local rows. It does not reproduce scheduler-padded rows routed as part of a SGLang graph batch. All required staging/gather/reduction stays in the timed closure; preprocessing weights, compilation and tactic selection remain outside it.

### GPU correctness gate (running; not yet passed)

From this branch, in the separately prepared SGLang-image devbox with FlashInfer based on ad0 and CuTe4.7.1:

```bash
for ep in 4 8; do
  for comm in allgather allreduce; do
    python -m torch.distributed.run --nproc-per-node="$ep" \
      --master-port=30327 benchmarks/bench_cute_dsl_moe_distributed.py \
      --num-gpus "$ep" --parallel-modes ep --variants w4a16,w4a16_megamoe \
      --model-shape glm-5.2 --ep-communication "$comm" \
      --num-tokens 1,3,4,5,32 --warmup 1 --iters 3 \
      --no-fused-finalize --refcheck --timing cuda_event --cuda-graph
  done
done
```

Then repeat with `--megamoe-max-tokens-per-rank 32768`. The unchanged numerical acceptance is atol=rtol=1e-2; failures must be retained and investigated, not hidden by a wider tolerance.

### Performance matrix

After correctness, compare `alltoall`, `allgather`, and `allreduce` at global token rows16/32/64/128/256/512/1024 and EP4/8, with separate live/32768-capacity results. Use both routing-included and precomputed-routing representative cases, and graph decode versus eager prefill separately. Save raw samples with `--log-timing-samples`. The previous PR5019 auto-tuned results and SGLang's capacity-keyed lookup/default policy require separate tactic-policy measurements; do not silently substitute `--megamoe-knobs auto` for the serving default. Record exact source and compiler pins, selected tactics and cache provenance for every run. No timing result is claimed until those commands actually complete.

## Active calibration environment

A separate8×B300 devbox uses the exact SGLang image above, with both kernels from ad0 and benchmark commit `0a9cd944b11fc297737993cfc3f132d3d51fc882`. CuTe providers are4.7.1, CUPTI Python13.2.0/library13.2.86; Torch2.13.0+cu130/CUDA13.0/loaded NCCL2.29.7 and image NVSHMEM3.4.5 are preserved. The environment retains12 pip-check conflicts:9 inherited,3 intentional FlashInfer/CuTe override conflicts;4 prior CuTe4.6.2/protobuf conflicts disappear. This is not a resolver-clean environment.

The first launch stalled before a benchmark case because torchrun standalone rendezvous selected an unresolvable node hostname. Its logs and termination evidence are preserved. A new run uses explicit single-node `--master-addr=127.0.0.1 --master-port=30327`; it entered the first EP4/allgather numerical gate at16:17 UTC and is compiling. No calibration result is claimed yet. The planned serial run includes60 invocations:8 correctness,24 core,12 auto,8 precomputed-routing and8 eager-prefill. Failed numerical checks retain the original tolerance and stop the pipeline.

## Validation boundary

The serving numbers above are measured and their raw token/duration arithmetic is checked. The new benchmark modes have entered GPU setup/compilation but have not yet passed the numerical gates or produced performance evidence. Static/CPU validation of layouts, flags and capacity guards does not establish NCCL CUDA-graph compatibility, numerical parity or performance. Final claims await GPU reference checks and measurement.

## GLM routing compatibility correction

The first GLM GPU attempt failed before correctness or timing: the historical FlashInfer DeepSeek routing helper rejects `n_group=1, topk_group=1, topk=8`. GLM parameters remain unchanged. The GLM benchmark now uses the exact Triton routing kernel from SGLang `50eeb742961908afa68f4f523a1a19c5de6eb0b3`, copied with source attribution into `sglang_glm_routing.py`; the original DSV3 routing path is unchanged. It writes existing FP32 weights and int32 expert IDs directly, with bias-only selection, unbiased sigmoid renormalization and scale2.5. Metadata records the reference, kernel AST and adapter hashes.

Six additional CPU contract tests and nineteen layout tests pass. Independent review confirms the complete kernel text matches the pinned source. These are source checks; GPU eager/graph routing parity and distributed MoE validation remain required before reporting calibrated timings. Failed rendezvous and routing attempts contain no performance result and remain archived separately.
