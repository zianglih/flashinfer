The padded FC2 candidate `ff6993cb`, based on `61249e0b`, passes **208 paired final-output replay comparisons per source** and **8 existing repository smoke tests**. Captures include 104 GEMM codegen pairs.

- Main fixtures exercise actual 64-row/two-stage scratch. A capacity-forced supplement exercises 32-row/one-stage scratch. N16/N64 fixtures exercise the nonbulk SIMT path.
- Coverage includes static/CLC, PDL off/on, one/two CTA, four scaled formats, full and partial slabs, nonlocal/empty/reactivated routing, original reciprocal maps, and NaN-poisoned FC2 output. Invalid padded rows are intentionally not checked.
- The repository smokes cover existing W4A4 per-tensor/per-token fused/unfused APIs and legacy/swap-AB W4A16 APIs and graphs. Their existing exact/nonexact assertion contracts are preserved.

All 52 FC1 PTX/SASS pairs are identical. FC2 static non-NOP differences range from −38 to +2561 and register differences from −18 to +17. Uniform spill/fill counts are unchanged, with no candidate local-memory/stack spills. These are codegen observations, not performance claims.

Two earlier forced-depth controls stopped at the diagnostic bulk32 geometry assertion because depths 2/3 still yielded 64×2. The successful supplement explicitly uses depth 4, derived from 55,296 bytes per operand stage and the actual 232,448-byte SM100 capacity. It realizes 32×1 and passes. Production source remained unchanged. Sanitizer was skipped as requested.

Raw artifacts and all 1,090 hashes are verified under `gate-evidence/`. `GATE.json` binds source and analysis hashes. The first performance attempt failed in observer import before any benchmark row. Those logs/config/helper are preserved separately. The corrected observer passed Ruff F821/F823/F811 and a full import/`--help` startup before relaunch.
