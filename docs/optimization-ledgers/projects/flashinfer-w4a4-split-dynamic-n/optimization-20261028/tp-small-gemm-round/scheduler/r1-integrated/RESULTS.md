# R1 scheduler publication composed with retained rank cleanup

Base `659777aa2e94b4454437f65a447bb085ca75787b`; candidate kernel `9a566ff271ef563e3ccb292b449768dab19666d56108e19c0502ad77dc697f0d`; patch `9f38fecf0c7810ae7f9991ffa2c6c94b64ce3154b3ce7ce45a9ea1f7eaa0bf9f`. Only the kernel file is unstaged in the active review.

Decision: rejected by the parent; do not retain this scheduler metadata-publication change. The complete final-source screen is neutral overall, does not demonstrate a CLC-selected gain, and has a material prefill outlier. The publication/handoff complexity and one-CTA instruction/resource costs are not justified by these results. No further scheduler variant is authorized in this round.

The original R1 writes the already computed route into the reserved fourth metadata word and carries it through the existing acquisition/release. Four short compile-time role selections preserve ordinary coordinate expressions; the weight helper receives a precomputed channel. No new metadata capacity, barrier, arrival, tactic, public API, math or layout contract.

## Qualification

All40 source-paired storage-byte replays passed (20 GEMM pairs,3 combine pairs), allfour scaled formats/static+CLC/one+twoCTA/PDLon/changing routes, plus partialK and channel_tiles2. No new independent-reference suite or sanitizer. Zero local-memory/stack spills; existing uniform spills are reported separately. All61 broadly selected synchronization/fence/PDL call ASTs match the659777 control.

Eight of10 ordinary SASS streams are exactly equal including encodings. MX8FC2 has17 descriptor-register swap sites; NVFC1 has68 different scheduling/register/op-selection sites. All10 ordinary instruction/resource/spill totals match. For one-CTA CLC, FC1 gains5 registers and FC2 gains13 non-NOP sites; both have two more static LDS sites and one fewer STS site. Two-CTA CLC preserves priorR1 instruction benefits and its previously recorded EP tradeoffs. No claim of universal static binary identity.

Original105474 R1/R3 transfer proof separately showed all10 originalR1 CLC streams equal measuredR3 and all10 originalR1 ordinary streams equal105474 including addresses/128-bit encodings. That proof does not erase the new659777 composition changes.

## Fixed-winner screen

15 supported model/topology/family jobs, T4/16384,72cells including56scaled+16unchangedW4A16 sanity. C-A-A-C,10warmups,100strictCUPTI samples permeasurement,coldL2 CUDAgraph timing;288pass medians/28,800samples. Each raw pass median is preserved and two pass medians are combined geometrically perrole. Existing83df publicAPI winners/routes are frozen, NV input quantization included, swapAB unfused. No autotuning, event fallback, external baseline rerun, time-strata substitution, or selective replacement.

| Group | Cells | Speedup GM |
|---|---:|---:|
| all | 72 | -0.0497% |
| scaled | 56 | +0.0084% |
| clc_selected | 23 | -0.1157% |
| static_selected | 33 | +0.0950% |
| w4_sanity | 16 | -0.2529% |

| Topology/model | Decode | Prefill |
|---|---:|---:|
| ep-v3 | -0.130% | +0.803% |
| ep-v41-flash | +0.159% | -1.318% |
| ep-kimi-k3 | +0.122% | -1.198% |
| ep-nemo3-ultra | -0.156% | +2.148% |
| tp-v3 | +0.292% | -0.188% |
| tp-v41-flash | +0.080% | +0.250% |
| tp-kimi-k3 | -0.010% | +0.053% |
| tp-nemo3-ultra | -0.027% | -0.810% |

Frozen `requested_clc` is the shared tactic flag; existing small-grid admission may run static. No attribution to actual CLC execution is inferred from that flag alone.

Largest scaled negative: V41F EP MXFP4x8 T16K−4.660%; C1/C2=0.7921835/0.7929835ms, A1/A2=0.829219/0.8334315ms. Controls are stable and both candidatepasses slower. This row remains in the decision. EP aggregate is offset by large positives (N3U up to+5.278%), not a broad gain. TP prefill GM−0.257%, worst−1.319%. UnchangedW4 variation is a diagnostic boundary, not a correction factor.

## Evidence and execution boundary

`audit_perf.py` independently verifies all1,904 archive hashes, source receipts,60 phases, raw medians/samplecounts/CUPTI mode, cache/winner/route identities, commands and environment. Full rows: `perf-cells.csv`; raw archive `perf-evidence.tar.gz`, SHA `8cbf82f5f1e44894e68bbab88263d0dbe8fae3be4be6812a39f2d8293232eb4b`. Exact/codegen archive SHA `cf1a2d460edbf160bc2c1a9a459d63e13b9f51b4966c3a0bd7f6b858f218d47c`. Secondary GPUs0–3 idle/released after completion.

An initial gate deployment launched on primary1/2 before the parent corrected the reservation. Only those owned process groups were stopped, logs preserved in the remote primary-cancelled directory. Independent W4 timeline proved its final measurements ended374/390seconds earlier, so no overlap or invalidated benchmark phase. The accepted gate and all timing ran onsecondary; measuredCAAC phases were uninterrupted. No source changes after freeze.
