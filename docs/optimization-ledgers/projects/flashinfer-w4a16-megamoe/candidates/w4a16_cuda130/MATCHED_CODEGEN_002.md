# Matched native-compiler codegen

Both source6315 captures completed on the same CUDA13.0 B300 node, with all eight ranks observed per arm. `logs/cu130-matched-codegen-002/` records identical1572-file source inventories before and after each arm, helper hashes, commands, actual compiled geometry and loaded-library maps. The per-rank native-extension hashes match the respective preflights. All16 workers load the same NVSHMEM3.4.5, NCCL2.28.8 and CUDA runtime13.0.96 binaries; the selected compiler is13.3/direct or12.9/fallback. Torch and Python DSL4.7.1 sources are unchanged.

Both arms use M256/N128/K256, cluster2x1,640 threads/two transform groups, raw5/decoded2/acc2, flag4/epi(2,4)/group512/atomic/epilogue return, H7168/I2048/E256/top-k8/EP8/T4096. Every rank has a new DSL cache/dump. Existing native C++ build caches are reused only within their respective verified stack owner. These are instrumented codegen launches; all durations are excluded from timing claims.

| Static generated-code observation, identical across ranks | Direct compiler13.3 | Fallback compiler12.9 |
| --- | ---: | ---: |
| Total SASS instructions | 5672 | 6288 |
| Cubin REG / STACK / resource LOCAL | 96 /112 /0 | 96 /112 /0 |
| Explicit SASS local operations | 21 | 21 |
| Instructions in marked transform interval | 809 | 1280 |
| FP4 pair conversions in interval | 128 BF16 | 128 FP16 |
| E4M3 scale conversions in interval | 16 BF16 | 16 FP16 |
| Additional FP16-to-FP32 widening, HADD2.F32 | 0 | 256 |
| Additional FP32-to-BF16 pair packing | 0 | 128 |
| Transform STTM.x8 stores | 16 | 16 |

The marked intervals are half-open `[0x5d10,0x8fa0)` for direct and `[0x62b0,0xb2b0)` for fallback, from the transform group's register release to the epilogue allocation. They include branch bookkeeping as well as decode, and are not dynamic instruction counts. The384 extra widening/packing instructions account for384 of the471 extra instructions in this interval. Another145 net instructions appear outside it. Compiler differences outside decode remain part of this comparison.

The conversion adds a real dependency before TMEM publication. In the direct capture, the first `STTM.x8` at0x6a90 consumes R4–R11 produced by packed BF16 multiplication. In fallback, R4 needs `HADD2.F32` at0x71c0/0x71d0 and `F2FP.BF16.F32.PACK_AB` at0x7200; the last packed output in R4–R11 completes at0x7360 before the first store at0x73e0. Independent excerpts and exact SASS hashes are saved in `profiles/codegen-comparison/cu130-matched-002-decode-independent.json`.

No new transform spill is observed. The21 local operations in each arm are eight STL.64, eight STL, one LDL.128 and four predicated LDL.64. Nineteen source anchors identify inherited FC2-router arrays; two nearby generic anchors remain unresolved. The transform interval contains no LDL/STL. The balanced role targets remain176/80/64/80/80, totaling61440 registers per CTA. Source-attributed named GPR maxima and static instruction counts are not liveness, occupancy or cycle measurements.

The extra conversion chain is a plausible contributor to the repeated4096 fallback gap, not a complete causal attribution. Before a broad kernel change, the focused question is whether these extra producer instructions delay TMEM availability to MMA, or whether both arms mainly wait elsewhere.

## Proposed bounded next capture, not launched

Use the existing coordinated EP8 application-replay NCU path at T4096 and exactly the same fixed tactic, source6315 and two compiler environments. Capture the actual production `Sm100W4A16MegaMoEKernel` symbol, one profile iteration, with a small tensor/short-scoreboard/math-pipe set and existing PC sampling groups:

```text
sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed
smsp__warp_issue_stalled_short_scoreboard_per_warp_active.pct
smsp__warp_issue_stalled_math_pipe_throttle_per_warp_active.pct
smsp__pcsamp_sample_count
group:smsp__pcsamp_warp_stall_reasons
group:smsp__pcsamp_warp_stall_reasons_not_issued
```

Verify live tool support before dispatch, retain source/native before/after evidence and all eight rank reports, and check sampling overflow/dropped bytes and actual replay counts. Correlate samples to the exact generated instructions, particularly raw LDS, FP4 conversion, widening/packing, first STTM and the MMA wait for decoded weights. Compare those with waits for activation, accumulator and raw/TMEM stage availability. Sampling percentages use their stated per-rank sample denominator; profiler durations are excluded from CUPTI tables. If conversion pressure is confirmed, prioritize a source-traced pre13.2 decoder alternative or existing smaller-fragment partition; do not treat the lack of spills as a reason to increase register limits.

Reproduce the CPU-only audit:

```bash
python3 compare_public_codegen.py profiles/codegen-comparison/cu130-matched-002.config.json \
  --output profiles/codegen-comparison/cu130-matched-002.json
python3 candidates/w4a16_cuda130/audit_matched_codegen.py
```

Capture001 is preserved separately as an entrypoint import failure caused by a missing tactic-output environment variable. It launched no benchmark kernels. Capture002 corrects only that effort-helper setup.
