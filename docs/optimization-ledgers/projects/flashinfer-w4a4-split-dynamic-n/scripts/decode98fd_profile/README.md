# Current NVFP4 decode phase and occupancy audit

Frozen source: `98fd3566b5f945c100f48cddacf25deb2432cbc2`, independent `flashinfer-profile-98fd` / remote `profile-98fd`. No production, MegaMoE, benchmark, or test edits. Source hashes are in every phase receipt. The only untracked package path is the documented `flashinfer/data` symlink to the existing native-cache data tree; the helper verifies its target.

Environment: C1 `fi-w4a4-pipeline-1025`, one B200, GPU4 UUID `GPU-5f3e1a0a-95b5-fca1-e723-ea2e1623c813`, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTeDSL4.7.1, driver580.178.04. Full package/tool records are archived. Every remote shell sourced `scripts/recovery442/env_candidate.sh`; native JIT epoch stayed candidate442, with private CuTe diagnostic caches.

## Direct phase timing

Actual benchmark seed42, hidden7168/intermediate2048, topk8 of256 experts,32 local experts, per-tensor NVFP4, unfused finalize. Saved AUTO choices: T32 A1 N16 and A2 N32; T128 A1/A2 N16. These are fixed-tactic diagnostics, not fresh autotuning or a primary/TRT benchmark.

|Tokens / route tile|Route|Sort|Prepare|FC1 GEMM|FC2 GEMM|Combine|
|---|---:|---:|---:|---:|---:|---:|
|32 /16|2.944|3.520|4.064|62.608|35.664|3.296|
|32 /32|2.944|3.520|4.0635|62.704|35.5205|3.312|
|128 /16|3.104|4.416|4.128|86.593|48.448|4.256|

Microseconds, median of100 cold-L2 CUDA-graph/CUPTI samples after10 warmups. **Independent phase times are not additive**: they do not reproduce whole-chain PDL overlap. Allocation, native input quantization, and weight preparation are outside timing. FC1 GEMM is the raw compiled kernel, with its routed payload/SF owners retained; its preparation is timed separately. No source overlays or altered kernels.

All18 phase cases passed checks before and after timing: route expert/weight pairs, sort coverage/inverse maps/tile bounds, full preparation payload/SF bytes and poison/canonical-padding oracle, FC1/FC2 full output/SF bytes against production wrappers with initialized padding, and combine BF16 bytes against native final output. Input and protected-source hashes stayed unchanged. T32 has31 local routes across21 active experts; T128 has108 across30. Exact per-expert histograms and all100 samples are in receipts.

## NCU, saved N16 tactic

|Tokens / phase|NCU us|DRAM read MB|DRAM throughput %|L2 hit %|Tensor active %|Registers|
|---|---:|---:|---:|---:|---:|---:|
|32 FC1|56.928|348.195|80.52|7.72|3.92|64|
|32 FC2|33.088|173.824|69.98|6.27|3.48|90|
|128 FC1|77.408|497.379|84.41|8.30|4.14|64|
|128 FC2|43.456|248.300|75.74|7.18|3.62|90|

NCU replay durations are diagnostic, not comparable to graph/CUPTI medians above. Kernel filtering excludes FC1 preparation; NVTX explicitly identifies each GEMM. All4 profiled GEMMs repeated exact output/SF bytes. Unsupported CTC metric warnings did not prevent completed reports. Every GEMM uses288 threads, grid148,197504B dynamic SMEM; NCU reports shared-memory occupancy limit1CTA, register limits3CTAs for FC1 and2 for FC2, and zero local-memory load/store sectors.

Weight traffic explains most decode cost. FC1 payload+SF is16,515,072B per expert; FC2 is8,257,536B. Each active expert fits one route tile. A single pass over active-expert weights predicts346.817/173.408MB at T32 and495.452/247.726MB at T128, within0.4% of measured DRAM reads. Thus there is little redundant cold weight traffic to remove. Extra occupancy may improve bandwidth utilization; it cannot be assumed to produce a large gain or explain a TRT difference without a controlled comparison.

## Bounded next mechanism

A two-stage, occupancy-admitted launch is distinct from prior rejected axes:

- `flashinfer-profile-98fd/flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:201,257` passes the physical SM count as `max_active_clusters`. Core `blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:839` launches that many one-CTA groups. Merely reducing stages leaves148 CTAs and cannot expose two resident CTAs/SM.
- Core lines314–379: N16/N32 both allocate physicalN32/K512,288 threads, two32-column accumulator banks plus32 SFA and32 SFB columns:128 TMEM columns. Operand shared memory is49152B/stage; four→two stages halves196608→98304B before metadata/scratch. No `setmaxregister` role directives exist. NCU confirms register headroom for2CTAs, but the candidate must query its own compiled occupancy and local-memory usage.
- Native W4A16 permutation `csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu:54–61,118–121` derives grid from actual kernel occupancy. Existing `scripts/fc1_regular_tma_experiment/grid_screen.py:18–35` can query a compiled CUBIN, but its preparation-only zero dynamic-SMEM argument must become the GEMM's actual storage bytes with opt-in. Hardware-only `get_max_active_clusters(cluster_size)` does not establish candidate occupancy.
- Prior `scripts/small_n_widek_experiment` has a `widek2_core.py` but no saved N16/N32 stage2 run. Saved decode runs used stages3/4, with5 capacity-skipped, on7829 Gather4 at T4/128/512. The parent assigned a separate agent the stage2+admitted2CTA screen; this profiling task made no implementation change.

The later [TMEM permit audit](TMEM_PERMIT_AUDIT.md) records an additional initial virtual-resource admission limit reported by the experiment owner. SMEM/register headroom alone is not proof of actual concurrent residency; early supported permit release requires runtime validation.

## Reproduction and receipts

After reserving GPU4, from the remote project root:

```bash
source scripts/recovery442/env_candidate.sh
.venv/bin/python scripts/decode98fd_profile/run.py
.venv/bin/python scripts/decode98fd_profile/run_ncu.py
```

The scripts refuse to overwrite result files; use new diagnostic labels/paths for an intentional rerun. `run.py` includes exact commands and environment in `logs/decode98fd-profile/commands.json`; `run_ncu.py` preserves NCU command receipts. Source imports assert frozen HEAD and unchanged protected files. `summarize.py` is CPU-only and derives `summary.json` from preserved receipts.

Local raw archive: `evidence/decode98fd-profile/raw.tar.gz`, SHA256 `64e3a9541c33618ac753fe57ef97b28456290ece2ebb01bd36b2196f1b938c21` (1,766,261B). It preserves raw JSON samples, NCU reports/CSV, generated PTX/CUBIN/SASS, source, helpers, commands and environment. CuTe uses a common generated kernel filename, so generated dump files retain the final compile for each dump directory; per-phase resource claims above come from the distinct NCU records. No failed GPU attempt occurred.
