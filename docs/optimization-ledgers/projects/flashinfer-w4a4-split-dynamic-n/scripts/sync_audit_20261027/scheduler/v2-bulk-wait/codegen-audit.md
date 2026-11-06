# Bulk reuse wait: emitted-code boundary

Frozen independent V2 patch `cd3c11d8`, based on `9334cb34`. This note reports source-paired correctness and code generation, not an end-to-end speedup. The final combined candidate has a separate gate and performance screen.

- The main gate passed 88 exact replays per source across 44 core pairs. Instruction counts, registers, storage, stages and MMA geometry are unchanged; neither source spills.
- The bounded wide-tile probe passed another 16 exact replays per source across eight core pairs. Uniform-scale and per-token W4A4 both compile FC2 with 64-token slabs, two bulk stages, N256, overlapping accumulators and four emitted reuse-wait sites, with PDL on and off. The skewed routing replay executes stage reuse in nine live tiles for every format/PDL combination. Per-token scales are nonuniform on live rows.
- Across all 52 core pairs, instruction counts including NOPs are unchanged. All 26 FC1 SASS files are byte-identical. The changed FC2 code is an ordering change.

The PTX places the reuse wait immediately before shared-memory writes, after TMEM loads and conversion. The final SASS only preserves part of that freedom: in the inspected `config1-fc2-pdl1` example, ptxas retains the per-issuer `DEPBAR` at the same early address, but delays the 128-thread barrier until after both TMEM loads and some scaling/conversion instructions.

| Representative instruction | Control address / file line | V2 address / file line |
| --- | --- | --- |
| `DEPBAR.LE SB0, 0x1` | `0x3d30` / 1965 | `0x3d30` / 1965 |
| First TMEM load | `0x3df0` / 1989 | `0x3da0` / 1979 |
| Second TMEM load | `0x3e40` / 1999 | `0x3e70` / 2005 |
| `BAR.SYNC.DEFER_BLOCKING 0x6, 0x80` | `0x3d40` / 1967 | `0x3e90` / 2009 |

The corresponding first PTX reuse wait moves from line 1377 to 1526; the shared overwrite remains after the wait and barrier. The emitted improvement is reduced coupling to the slowest peer warp before independent TMEM/register work. These artifacts do **not** prove overlap of that work with each issuing thread's own bulk-read wait, a reduction in instruction count, or a latency improvement.

Evidence is under `scripts/sync_audit_20261027/validation/scheduler-v2/evidence/bulk-extra/{control,candidate}/config1-fc2-pdl1.{ptx,sass}`. [codegen-audit.json](codegen-audit.json) pins file hashes, all 52 paired comparisons, actual bulk geometry, route reuse and representative instruction positions. Reproduce it with `python3 scripts/sync_audit_20261027/scheduler/v2-bulk-wait/audit_codegen.py` from the project root.
