# Bounded native T1 confirmation after the devbox loss

No GPU launch is authorized by this document or performed by this auditor. The old devbox disappeared while the fresh original-source EP4 sweep was incomplete. Its unclosed partial values are observations, not a completed qualification result. All completed final native logs, caches, successful native-driver receipt and codegen artifacts have already been copied locally.

## Why T1 needs separate treatment

The native EP4 workload is H7168/I2048/E256/K8, globalT1: rank0 has one token, ranks1–3 have zero, and each rank's workspace capacity is one. The final target CUBIN identity audit covers H6144, capacity256/rank, so it does not prove identity for this native specialization.

Every completed native T1 run below chose the same AUTO tactic: N64/G512/epi, M256/K256, cluster2x1x1, atomic counter, deterministic combine, flag4, epilogue flags[2,4], two scheduler stages.

| Source | Median µs | Quarter medians µs |
|---|---:|---|
| Original002 | 65.6325 | 65.888 / 65.888 / 65.217 / 65.505 |
| Retained R1 Store16 | 67.8410 | 68.513 / 69.824 / 66.497 / 67.648 |
| Frozen R2 raw-probe removal | 67.8890 | 67.489 / 67.777 / 68.001 / 68.096 |
| Final owned R2 | 75.0730 | 73.408 / 74.560 / 75.329 / 76.224 |

The final increase is material and not an AUTO tactic difference. Final samples also rise across quarters. Neither observation establishes the cause; it is insufficient to attribute the difference to ownership relocation or to dismiss it as drift. The original negative rows remain in the report regardless of a later confirmation.

## Replacement-node scope

1. Record the new physical node/boot/GPU identities and exact software image. Preserve the frozen original002 (`control`), prototype R2 (`store16_no_raw_peek`) and final-owned (`retained_owned_r2`) source hashes. Do not combine absolute times across old and replacement nodes.
2. Export **ordinary, uninstrumented native H7168 globalT1 / EP4 / capacity1** code for frozen R2 and final-owned using fixed N64/G512/epi. Use the checked wrapper, successful exit receipts and separate fresh processes; include finite/repeated output and matched fixture/output hashes. Run the existing source/hash/resource/per-K analyzer with `per_rank_tokens=1` and `tile_n=64`, then compare actual CUBINs, instruction text, resources and waits across all four compiled staging ABIs. This is compilation evidence, not a timing comparison.
3. If native-capacity1 CUBINs are identical, focus timing on **original002 versus final-owned ABBA** on the replacement node: A1 original, B1 final, B2 final, A2 original. Keep the fixed tactic, 3 warmups and 100 untrimmed cold-L2 CUDA-graph CUPTI rank-MAX samples/run. Report each run, quarters and pooled200 samples/arm. Fixed provenance must preserve the exact driver and all knob fields. This small fixed check does not replace either source's full AUTO matrix.
4. If the two R2 CUBINs differ, inspect the generated difference before attributing the timing change. A direct prototype-R2 versus final-owned fixed ABBA may then be justified to isolate the ownership move; do not automatically expand to a new full native sweep.

Native timing wrappers normally run the independent reference at globalT128, not T1. A T1-only timing check must describe its finite/repeated/paired-hash coverage accurately. The planned strict numerical suite independently covers a skewed EP4 T1 case across all tactics/O2/O3; that separate case does not become a per-run T1 timing oracle. Reuse the appropriate existing reference if a T1 oracle is added, without changing the measured closure.

No new optimization or source mutation is proposed. The retained stack remains R2. A completed same-node comparison is required before claiming the native T1 regression has disappeared or assigning a causal explanation.
