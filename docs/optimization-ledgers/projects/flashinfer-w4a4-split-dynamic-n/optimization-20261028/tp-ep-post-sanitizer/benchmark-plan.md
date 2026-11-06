# TP and EP benchmark plan

Status: running after all 150 sanitizer cases passed, the independent evidence audit completed, and both devboxes passed idle postflight. Seven supported TP model/family jobs were launched on disjoint GPUs; V41F TP4 MX has an explicit skipped receipt. Both devboxes and persistent compilation caches are retained. Source under investigation is PR7290 `d1767be1f42fdc371f90db4fb06598299ea32845`; a later retained optimization must receive a new source receipt and fresh candidate measurements.

## Workloads

`benchmarks/bench_moe_deepseek.py` already implements expert tensor parallelism by dividing the intermediate dimension by `--tp`, while `--ep` divides the expert count. This is a single-GPU local compute benchmark: no TP all-reduce or EP communication is measured. Token count remains the requested per-rank input count. `--tp` does not reset the model's default EP, so all TP commands must explicitly pass `--ep 1`.

| Display | Model selector | TP | EP | Hidden | Local intermediate | Local experts | Top-k | Routing | Activation |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| V3 TP8 | v3 | 8 | 1 | 7168 | 256 | 256 | 8 | DeepSeek V3, groups 8/4, scale 2.5 | SwiGLU |
| V41F TP4 | v41-flash | 4 | 1 | 5120 | 576 | 384 | 6 | SqrtSoftplus, scale 1.5 | SwiGLU, limit 10 |
| K3 TP8 | kimi-k3 | 8 | 1 | 3584 | 384 | 896 | 16 | Sigmoid, scale 1 | SiTU, gate 4 / linear 25 |
| N3U TP8 | nemo3-ultra | 8 | 1 | 2048 | 640 | 512 | 22 | Sigmoid, scale 5 | ReLU2 |

N3U uses the existing latent MoE width 2048. Canonical BF16 FC1/FC2 weights occupy approximately 2.625, 6.328, 6.891 and 2.500 GiB respectively, before quantized/prepared buffers. Preserve the existing model definitions and logical widths, including V41F 576.

Run all 13 token counts: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Exclude 1 and 2 from retention and displayed tables. Keep EP workloads unchanged: V3/K3/N3U EP8 TP1 and V41F EP4 TP1.

## Arms and public calls

Use the same functional public API and `prepare_*_weights` flows as the completed EP campaign. Candidate swap-AB is always unfused. NVFP4 includes initial activation quantization; MX inputs are prequantized. W4A16 consumes BF16 directly. Preserve the standalone per-token recipe: MSE 4over6, E4M3 maximum 256, 4over6 fast math, ordinary FP4 quantization fast math disabled for activation quantization, ordinary NVFP4 weights.

| Family | Candidate | Fresh TP external controls |
|---|---|---|
| NVFP4 | CuteDSL W4A4, PER-TOKEN, W4A16 | TRTLLM NVFP4, TRTLLM PER-TOKEN; old non-swap W4A4/PER-TOKEN; pre-PR W4A16 with old layout |
| MXFP | CuteDSL MXFP4x8, MXFP8 | TRTLLM MXFP4x8/MXFP8; old non-swap MXFP4x8/MXFP8 with required fused finalize marked † |

Omit TRTLLM BF16 and CUTLASS. K3 SiTU exclusions remain explicit: TRTLLM PER-TOKEN/MXFP8 and old non-swap MXFP4x8/MXFP8. Skip current K3 MXFP8 as well because neither matching external control supports it; K3 MX measures only CuteDSL MXFP4x8 against TRTLLM MXFP4x8. Do not turn unexpected exceptions into N/A.

Source receipts for existing baselines come from `optimization-20261027/retained-rerun/evidence/config.json`. Old non-swap source is `e2728a2908f38cbcfa997c031bea059e3724ccde`; pre-PR W4A16 source is `002529e17b22567a071091053c6c4dc2a55e050e` with the previously recorded four-model benchmark adapter. Their kernel hashes and adapter hashes must be reverified before use. Existing EP external timings are reused unchanged. No TP timing or TP winner may be inferred from EP measurements.

## Timing and cache contract

Reuse `api-cleanup-20261028/full-validation/benchmark-tools/{run_job,observe_benchmark,arm_contracts,nested_timing}.py`, the established receipt/archive helpers, and the existing report/plot implementation. Extend project-local helpers through explicit workload and arm descriptors rather than creating a separate benchmark implementation.

Each source/workload/model/family arm freshly tunes in an empty managed cache directory, using the source's intended policy. Current code uses public `autotune_v2`: default `auto` for NV/TRT; public `MeasurementPolicy(execution_mode="cuda_graph")` for CuTe MX. Freeze cache contents and winners, then measure two independent replay processes with `--no-autotune`. Native fallback tactic `-1` remains a valid winner. No old EP winner or JSON cache is an input to TP selection.

Historical snapshots predate the managed-cache helper. Preserve their explicit source-specific public tuner and fresh native cache contract using the already archived observer, or use a separately reviewed benchmark-only adapter to the shared managed tuner. Do not silently fall back between cache versions. The exact baseline harness choice must be recorded before launch; production backend code must remain unchanged. A current non-swap control may replace a historical checkout only after source equivalence is established and the manifest names the actual measured source.

Accepted public measurements: CUDA graph, cold L2, 10 warmups, 100 CUPTI samples. GPU-event fallback is fatal. Reject tuning during timed capture, cache misses, changed cache contents, source mismatches, route mismatches, or disagreement between raw sample medians and printed values. Combine the two accepted medians geometrically. Retain tune timing only as diagnostics. Use standard medians for retention; time strata may explain existing prefill bimodality but cannot replace accepted medians.

For fresh TP controls, serialize C1/A1/A2/C2 on the same physical GPU after each arm's fresh tuning. Persist GPU UUID and before/after utilization. Candidate-to-control comparisons must not pair different GPU UUIDs. Existing EP controls are historical explicitly reused evidence, as requested.

## Concrete command shape

These are underlying public benchmark commands; the observer supplies source/cache/timer assertions. Each model uses the TP/EP values in the workload table.

```sh
python benchmarks/bench_moe_deepseek.py --functional-api \
  --model v41-flash --tp 4 --ep 1 --quant-family nvfp4 \
  --backends cutedsl,cute-dsl-per-token,trtllm-nvfp4,trtllm-per-token \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
  --swap-ab --no-fused-finalize --include-activation-quant \
  --warmup 10 --iters 100 --cache <fresh-managed-cache-directory>

python benchmarks/bench_moe_deepseek.py --functional-api \
  --model v41-flash --tp 4 --ep 1 --quant-family mxfp \
  --backends cute-dsl-w4a8,cute-dsl-mxfp8,trtllm-mxfp4,trtllm-mxfp8 \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
  --swap-ab --no-fused-finalize --warmup 10 --iters 100 \
  --cache <fresh-managed-cache-directory>
```

The V41F MX command is shown only to document the requested geometry. Skip that model/family job: both external baseline implementations reject the logical width, and the user explicitly requested skipping configurations unsupported by both controls. Frozen A1/A2 append `--no-autotune`. Legacy arms omit swap-AB; legacy MX enables its required fused finalize. Pre-PR W4A16 selects only that dtype with the existing project observer selection hook, without changing the public measured call.

## Identified admission gap

V41F TP4 has logical intermediate 576. Current CuTe and TRTLLM MX weight preparation reject intermediate widths not divisible by 128. Swap-AB `can_implement` also requires FC2 K divisible by `4 * sf_vec_size`, i.e. 128 for MX scales and 64 for NVFP4. Thus NVFP4 accepts 576 while MX rejects it. Other requested TP widths 256/384/640 satisfy 128. Current skip policy covers activation support but not this dimension restriction.

Skip V41F TP4 MX in this campaign under the user's latest direction; preserve the logical shape and print explicit N/A cells. Do not pad the benchmark or extend baseline APIs just to run it. TRTLLM low-level block-scale APIs expose `valid_intermediate_size`, while old CuTe does not; this is background source evidence, not an adapter to introduce now. The separate kernel experiment instead targets robust compile-time partial-K processing and SM103 NVFP4 K96 MMA for supported workloads. Its design and exact touched paths will be recorded before edits.

## Minimal helper changes and evidence

1. Add a workload descriptor with logical H/I/E, local H/I/E, TP, EP, routing and activation. Include the descriptor and hash in source/job/results receipts.
2. Replace `run_job.py`'s hardcoded EP/TP and old EP route-identity comparison. Establish one fresh TP route anchor for every model/token and compare all TP arms and passes against it. The expert-locality portion legitimately differs from EP. Keep seed42 and original input-generation order.
3. Parameterize source/arm/finalization/cache contracts. Preserve current managed timing policies and explicit historical baseline adapter identity. Freeze all prepared-weight and logical/physical dimension receipts if padding is introduced.
4. Keep EP and TP report inputs separate. Reuse the current assembler/plot with workload labels and baseline-manifest arguments. Do not overwrite EP artifacts or mutate previous baseline values.
5. Bind results to commit, full source manifest, benchmark/observer hashes, exact argv/env, cache manifest, winning tactic identities, route hashes, GPU UUID and CUPTI raw arrays. Archive untouched logs and receipts before report assembly.

Suggested artifact roots: `tp-ep-post-sanitizer/{sources,runtime,benchmark-tools,runs/tp/<model>-<family>,runs/ep/<model>-<family>,evidence,report/tp,report/ep}`. Use the existing `measurements.json` phase schema plus explicit workload/arm IDs. Every phase lists paths and hashes for results/stdout; source manifests are independent of phases.

Complete supported TP evidence is 221 current cells plus 364 external control cells, each with two accepted medians: 1,170 medians and 117,000 CUPTI samples. V41F MX excludes 26 current cells and 52 control slots; K3 activation exclusions account for another 52 control slots and 13 unmatched current MXFP8 cells. The display remains 44×9 with explicit N/A cells, and a skipped V41F MX native-output section records its reason.

## Resources and launch order

Keep C3 `fi-moe-nvfp4-port-1026` and `fi-moe-sanitize-1028`, both 8×B300, CUDA13.2 image `nvcr.io/nvidia/pytorch:26.05-py3`. Reuse the existing Python/CuTe runtime and persistent native C++ cache. Do not delete caches. CuTe process-local compilation time is recorded separately from actual tactic profiling; native compilation links remain persistent.

After the final sanitizer evidence audit, verify both boxes' GPU UUIDs/toolchains and idle status. Start seven supported model/family jobs across seven distinct GPUs, preferably four on one box and three on the other to reduce host compilation contention. Record the eighth (V41F MX) as a source-proven skipped job without GPU execution. Each active job serializes all matching arms and accepted CAAC passes on its GPU. Leave other GPUs for narrow shape gates/profiling only after explicit scheduling. No GPU may serve both a benchmark and a concurrent profiler/test.

First run small-token admission and exact checks for any retained K-tail change. Then execute all TP jobs. For subsequent general optimization candidates, refresh current TP and EP arms across all five dtypes, reusing unchanged EP and newly established TP external controls. Run material-gap fixed-tactic matched diagnostics separately; never replace full-sweep cells opportunistically. Push/publication remains parent-owned after validation.

## Report

Preserve the existing 44-row × 9-column table and red/green full-table plot. TP labels are `V3 TP8`, `V41F TP4`, `K3 TP8`, `N3U TP8`; the EP report retains existing labels. Column order remains TRTLLM W4A4, PER-TOKEN, MXFP4x8, MXFP8; non-swap W4A4, PER-TOKEN, MXFP4x8†, MXFP8†; W4A16 before PR. Each cell is `(baseline_ms / current_ms - 1) * 100`; positive means swap-AB is faster. Include the actual eight native outputs per workload, source-bound raw medians, unsupported reasons and † fused-control marks. Keep incremental diagnostic ledgers local.
