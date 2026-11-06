# W4 tail dequantization qualification

Passed: 12 split exact calls and four inherited MegaMoE exact calls. No performance claim is made. The candidate remains separate from retained PR head `02de7785`.

| Split H / I | Weight rows | CTA group | Scheduler | PDL | Boundary |
|---|---:|---:|---|---|---|
| 384 / 640 | 16 | 2 | Static | On | Half-stage tail in both GEMMs |
| 256 / 256 | 16 | 2 | Static | On | Aligned control |
| 384 / 640 | 64 | 1 | CLC | On | Half-stage tail in both GEMMs |
| 256 / 256 | 64 | 1 | CLC | Off | Aligned control |
| 128 / 320 | 64 | 1 | CLC | On | Short FC1; FC2 partial live group plus skipped group |
| 128 / 448 | 16 | 2 | Static | On | Short FC1; both FC2 groups live |

- All split FC1/FC2 native resources remain 96/128 registers with zero local memory. Compiler flags and source snapshots are unchanged.
- Both aligned split cases have raw PTX, cubin and SASS byte identity for FC1, FC2 and combine. The K448 FC2 specialization also remains byte-identical: its tail reaches both transform groups, so the new condition disappears.
- The two single-rank MegaMoE cases (H256/I256 and H384/I640) remain exact and raw-code identical, at 96 registers and zero local/stack memory. They use an explicit padded consumed K extent.
- Affected split code adds 8–32 static instructions. Native branch evidence confirms that the final inactive transform group skips both scale reads, four 128-bit payload reads, conversion/scaling, and eight TMEM store sites. Common waits, raw release and decoded publication remain active.
- The strict existing public split oracle is reused with a correctness-only two-active-cluster cap and explicit W4 CLC selection. The layout proof covers actual constructible partitions; it does not claim complete kernel support for all private geometries.
- No sanitizer, distributed test or performance run was added by this qualification. GPU1 was checked idle and released for the separately authorized screen.

Evidence: `qualification-summary.json`, `qualification/pilot-codegen-proof.json`, `qualification/full-evidence`, `qualification-edges/edges-evidence`, `layout-proof-summary.json`, `mega-qualification/summary.json`, and `gpu1-release.json`.
