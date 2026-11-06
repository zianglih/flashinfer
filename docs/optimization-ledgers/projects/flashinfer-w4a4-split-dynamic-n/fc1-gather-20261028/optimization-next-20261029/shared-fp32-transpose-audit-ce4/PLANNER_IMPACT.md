# Gathered FC1 shared-transpose storage impact

CPU extraction of the retained ce4 planner was evaluated against all 364 saved swap-AB native winners, with every FC1/FC2 geometry cross-checked against the actual loaded-kernel receipts. The frozen prototype `e9801fb840c2c8184ff6ef7deb798f2ed25108fb52887bee8596c3f5488f13a8` was then evaluated directly: all 1,456 native and automatic FC1/FC2 results agree with this model (`actual-planner-verification.json`). No source or GPU was changed by this audit.

The new FC1 scratch is 8,704 bytes total, versus 512 bytes retained. Its 8,192-byte increase causes 87/364 cells to lose exactly one operand stage, spanning 14/78 unique FC1 geometry/CLC configurations. Excluding tokens1/2, this is74/308. The losses include21 prefill cells. All current winners explicitly select K4/K8, so their K setting is unchanged. All364 FC2 evaluations remain identical.

| Backend | Cells | Lose one stage | Automatic K changes, separately evaluated |
|---|---:|---:|---:|
| W4A4 |104|39|39|
| Per-token |104|40|40|
| MXFP4x8 |91|7|7|
| MXFP8 |65|1|4|

| Geometry family | Stage change | Cells |
|---|---:|---:|
| NV, M256 N16/32 K4 |10→9|17|
| NV, M256 N16/32 K8 |5→4|47|
| NV, M128 N64 or M256 N128 K8 |4→3|10|
| NV, M256 N128 K4 |8→7|5|
| MX, M256 N128 K4 |9→8|8|

The 4→3 changes reduce staged K capacity by25%; important affected prefills include K3/V41F EP and K3/V3/V41F TP. The prototype must recover this through cheaper ownership exchange; storage fit alone is not evidence of a performance improvement. Full per-cell details, including all unaffected cases, are in `planner-impact.csv`.

Automatic selection on these same geometries changes for90 cells:79 NV cases K8→K4 and11 MX cases K4→K8. This is a default-policy calculation, not a retuning or a changed native winner. The minimum modeled stage count stays2; maximum total modeled allocation is231,424 bytes out of232,448. Actual CuTe cosizes, struct alignment, emitted LDS/STS instructions, resource use, exactness and performance remain separate compiler/GPU gates.
