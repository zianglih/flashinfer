# All-thread FC1 PDL prefill timeline

One warmed graph replay per arm on GPU3, 2026-10-25. This is a diagnostic trace, not a benchmark median or retention result. The independent source copy is `flashinfer-pdl-fc1-trigger-review`, base `aab93f854054de834447bdd8985b8bbd653fb3c8`; core SHA `ac1aef1e9ff52ee57a10841eb69a1ce2cf44790968f5283fa36533f9022358fa`, preparation SHA `a3b0042ea0ae64f66cfc968768c85b96118ed750fa92a668cb1485f91866a67b`. The corrected-aab control is clean `profile-aab93f`. No source was modified.

Actual native DeepSeek routing, NVFP4 T16384, N256/M256/two-CTA FC1 and FC2, unfused finalization. Each arm uses its own actual core/preparation/finalizer modules and caches. Ten ordinary warmups and ten graph replays precede one profiler-range replay. CUDA graphs retain their invocation-local scratch. Native inputs, final output bytes, source hashes and module dispatch passed pre/post checks; the source owner's independent phase exact gate is preserved in `evidence/raw/owner-gate.json`.

| Kernel | Control start/end (us) | Candidate start/end (us) | Control/candidate lifetime (us) |
|---|---:|---:|---:|
| route | 0 / 25.184 | 0 / 25.216 | 25.184 / 25.216 |
| sort init | 24.224 / 25.760 | 24.192 / 25.952 | 1.536 / 1.760 |
| sort | 25.664 / 33.472 | 25.760 / 33.696 | 7.808 / 7.936 |
| preparation | 33.248 / 59.168 | 33.504 / 59.456 | 25.920 / 25.952 |
| FC1 | 58.912 / 260.289 | 55.648 / 264.033 | 201.377 / 208.385 |
| FC2 | 259.681 / 405.409 | 236.353 / 418.017 | 145.728 / 181.664 |
| combine | 404.833 / 485.921 | 265.153 / 506.401 | 81.088 / 241.248 |

Kernel lifetime overlap increases from0.256 to3.808us for preparation→FC1,0.608 to27.680us for FC1→FC2, and0.576 to152.864us for FC2→combine. These lifetimes include dependency waiting; they do not measure simultaneous useful tensor computation.

The candidate's20.480us longer graph span can be partitioned at predecessor completion: FC1 end is3.744us later; the FC2 span after FC1 completion grows from145.120 to153.984us (+8.864); the combine span after FC2 completion grows from80.512 to88.384us (+7.872). This is an exact arithmetic decomposition of this trace, not a causal attribution. In particular, a kernel can do some independent setup or some work before its predecessor's final CTA exits; subtraction does not isolate its exact useful-work duration.

FC1 registers return to80 for both arms; dynamic SMEM195584B, executed SMEM200704B, block288, cluster2 and maximum active clusters74 are unchanged. FC2 remains120→122 registers, dynamic SMEM229888B, executed SMEM233472B, block288, cluster2. Both report zero local memory per thread. Combine remains80 registers/block128; preparation remains32 registers/block128. No spill/occupancy-change claim follows from these numbers. QMD timestamps are NULL. The full resource records and exact kernel identities are in `summary.json`.

The source currently keeps weight/activation transfers after the GEMM dependency wait. Combine preloads only route mapping and scales before its wait (`moe_finalize.py:131–141`); its FC2 output reads follow at156. Therefore this trace does not establish future-payload prefetch, cache pollution, or the cause of the residual regression. A new instruction/traffic profile would be required for causal attribution. The owner's separate all-thread FC2 experiment is not included here.

`probe_graph.py` is the prior trace helper with only the known-invalid graph-edge query removed. CUDA graph DOT and Nsight node identities remain captured. No complete graph edge-type/port claim is made; the older binding issue is documented in `../EDGE_METADATA_LIMITATION.md`. `source-manifest.json`, command/environment receipts, raw Nsight reports and SQLite exports are preserved. Raw archive SHA: `b7614d17f40688b57898f491d79626b787483ba4cb0c7fc1959e8bb1ee1195ac`. GPU3 is released.
