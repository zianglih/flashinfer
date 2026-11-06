# Pipeline initialization fence consolidation: hold

The source-only candidate remains unstaged in `flashinfer-pipeline-fence-review` on retained `8b74eb6fa77651bb20dacb56b8e13872f3ad9885`. The two-file patch SHA is `c9d17cc6f9a88761e8f19c3d6ab47922186443abf1db73350f05680f1e1d5f60`.

The bounded gate passed 45 changed-input/changed-routing captured-chain replays with exact output equality. All 27 unique FC1/FC2 specializations had identical hardware registers, shared memory, occupancy and zero local bytes/spills. Initialization fences decreased, while the existing cluster and TMEM synchronization sequences stayed intact. Fifteen PTX pairs differ only by fence removal; twelve one-CTA pairs additionally coalesce initialization guards, so attribution covers the whole consolidation/code-generation change.

Fixed N16 whole-chain C–A–A–C timing on B300, with 10 warmups, 100 repeats, cold L2 and CUDA-graph/CUPTI timing, screened T4/32/128/512. Direct paired geometric means were:

| Model | NVFP4 | MXFP8 | MXFP4 × MXFP8 |
|---|---:|---:|---:|
| V3 EP8 | 0.999199× | 0.999658× | 0.999978× |
| V4.1 Flash EP4 | 0.998532× | 0.999655× | 1.000392× |

The largest repeat-negative point was V4.1 NVFP4 T32, 0.995637× (0.996258× / 0.995016× repeats). Unaffected W4A16 control geometric means were 0.999855× / 0.999727×. The screened change provides no practical latency gain. Hold the candidate and do not broaden native AUTO timing or retain it in the PR.

Exact/code-generation evidence is in `comparison.json` and `codegen-sync-comparison.json`; full timing medians, source/route/tactic/cache receipts and raw observations are preserved in `../pipeline-fence-r1-fixed/{summary.json,summary.md,raw}`. These fixed-tactic points do not establish a full-grid AUTO retention result. Earlier failed helper attempts are preserved separately; they did not alter frozen kernel source.
