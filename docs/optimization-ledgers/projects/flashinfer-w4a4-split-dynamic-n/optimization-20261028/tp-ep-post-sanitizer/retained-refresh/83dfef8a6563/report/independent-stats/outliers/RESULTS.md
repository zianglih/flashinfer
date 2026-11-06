# Four N3U EP historical outliers

Current `83dfef8a656384f5cd10db847602593bb6f9b2c6` versus published `d1767be1f42fdc371f90db4fb06598299ea32845`. Routing identities match across all four passes in every case. Replays used frozen native winners with zero profiling calls. Source/result hashes and source-extracted stage calculations are in `source-audit.json`.

| Case | Prior A1/A2 (µs) | Current A1/A2 (µs) | Historical speedup | Winner changed? | Prior/current pass spread |
|---|---:|---:|---:|---|---:|
| W4A4 T4096 | 217.793 / 218.657 | 239.138 / 237.074 | -8.349% | Yes | 0.396% / 0.870% |
| MXFP8 T16384 | 824.501 / 785.267 | 840.339 / 862.755 | -5.500% | No | 4.996% / 2.667% |
| MXFP4x8 T8 | 45.856 / 45.824 | 50.017 / 50.016 | -8.350% | Yes | 0.070% / 0.001% |
| PER-TOKEN T8192 | 518.531 / 518.434 | 534.868 / 533.859 | -2.972% | Yes | 0.019% / 0.189% |

The three changed winners are stable across A1/A2. This is evidence of a different selected implementation, not proof that selection alone causes the whole difference.

- **W4A4 T4096:** old route N128, FC1/FC2 M256 and two CTAs, K steps8/4, static schedule; new N256, FC1 M128/one CTA and FC2 M256/two CTAs, K4/4, static. FC1/FC2 operand rings change4/6 →4/5; both accumulator rings change2→1. The independently controlled FC2 screen using the old N128 winner measured only -1.023% at this cell (21f control216.578/216.610µs; measured-R3 candidate218.913/218.754µs). That experiment does not qualify the new N256 winner's source effect.
- **MXFP8 T16384:** exact same N256, M256/two-CTA FC1 and FC2, K4/4, static. Both sources have six FC1 and five FC2 operand stages, one accumulator stage, K128 stages, and64-row/two-stage BF16 bulk scratch. K96 is disabled. The compact path changes prepare prefix work, FC2 dense-index publication and slab/tail stores, and combine addressing. The previous fixed-winner FC2 screen measured -1.578% here; the new controlled repetition below measures -0.155%.
- **MXFP4x8 T8:** old FC1/FC2 M256/two CTAs, K8/4, static; new FC1 M128/one CTA and FC2 M256/two CTAs, K4/8, CLC. N16 is unchanged. Operand rings change5/11→10/5. Both compact output and K96 are disabled; compact-prefix/index/store additions compile out. The original FC2 codegen qualification proved non-bulk FC2 instruction identity versus21f. The historical winner change still requires a same-source winner A/B to quantify causality; none is claimed here.
- **PER-TOKEN T8192:** old N128, FC1 M512/two CTAs with two channel tiles, FC2 M256/two CTAs; new N256, both M256/two CTAs. K4/4 and static scheduling unchanged. FC1/FC2 operand rings4/6→5/5; FC2 accumulator stages2→1. Both current NVFP4 cases enable the retained SM103 K96 policy and1024-byte operand alignment; the old d1767 source used K64 and128-byte alignment.

N3U has H2048 and I5120 (`bench_moe_deepseek.py:163`), divisible by every selected K128/256/512 stage here. No partial final K stage is exercised. The source-static planner is extracted independently from each head's `_accumulator_storage`, `_stage_storage_bytes`, `_pipeline_metadata_bytes`, `_operand_stage_capacity`, and `_epilogue_storage`. `_configure_pipeline_storage` verifies the actual CuTe operand-layout bytes match this calculation. These are static source-derived counts, not new profiler measurements.

## Focused MXFP8 T16384 source A/B

Primary B300 GPU0, same routing and exact old/current-identical frozen winner, `21fbe72c` control versus pushed `83dfef8a`, C–A–A–C,100 CUPTI samples per pass, no autotuning or external-control rerun:

| C1 µs | A1 µs | A2 µs | C2 µs | Geomean speedup |
|---:|---:|---:|---:|---:|
| 764.116 | 812.165 | 766.7405 | 812.4365 | -0.155% |

Both source arms exhibit approximately764–767µs and812µs pass medians. The historical -5.500% difference is not reproduced by this paired source comparison. This does not identify the reason for the historical spread and does not establish a d1767-versus83df code-only result. The full published matrix remains unchanged.

The12 fetched evidence files are SHA-verified; the independent audit checks all400 raw samples and medians, unchanged winner identities, route identity, source/benchmark hashes, GPU UUID and zero profiling. Archive SHA256: `6972fdefee13147a9ea62565c3967d009a8e6283b9ce152f86a00e0ece37fe30`. See `paired-mx8-analysis.json`, `fetch-verification.json`, `evidence/`, and the unchanged original `run_perf.py` framework bound by the launch receipt. GPU0 is released. No canonical source or public result changed.
