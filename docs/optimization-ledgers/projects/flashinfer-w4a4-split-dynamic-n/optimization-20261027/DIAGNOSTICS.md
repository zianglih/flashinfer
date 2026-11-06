# Current swap-AB prefill diagnostics

Source: clean PR head `e2728a290`, production identical to `5ac45245`. B300/CUDA13.2/CuTe DSL4.8. Frozen winners and exact input/model settings come from `swap-ab-full-rerun-20261027`; no implementation or native benchmark policy changes. Existing native `--profile-cuda` captures 20 cold-L2 graph replays under Nsight Systems. The entrypoint verifies every CuTe/TRT native cache hit against its saved runner and tactic, and verifies that the cache bytes do not change.

These profiler spans are diagnostics, not replacement CUPTI benchmark medians. Kernel durations include PDL waits and must not be added as independent stage costs. `timeline-summary.json` records relative starts/ends and each kernel's extension of the already-enqueued chain. Medians of individual components do not necessarily sum to the median graph span.

| T16384 model/mode | Graph span (us) | Prepare duration (us) | FC1 duration (us) | FC2 duration (us) | Combine critical tail (us) |
|---|---:|---:|---:|---:|---:|
| Nemo NV swap-AB | 572.660 | 22.273 | 257.762 | 235.745 | 54.752 |
| Nemo NV legacy unfused | 501.251 | — | 230.402 | 191.633 | 53.600 |
| Nemo NV TRT | 650.148 | — | 323.746 | 199.601 | 97.697 |
| V3 MXFP4x8 swap-AB | 684.052 | 41.136 | 324.274 | 214.881 | 86.144 |
| V3 MXFP4x8 legacy fused | 599.076 | — | 333.874 | 204.817 | fused |
| V3 MXFP4x8 TRT | 679.812 | — | 344.482 | 182.561 | 132.369 |

- Nemo isolates a shared GEMM/prepare gap: both CuTe paths have unfused finalize and essentially the same finalizer tail. The new prepare adds22us; combined GEMM critical extension is467.8us versus419.7us. The selected swap tactic is M256/N128, 2CTA, K4, static scheduling; legacy uses M256/N256, 2CTA.
- V3's GEMMs are close to the legacy implementation. Its extra deterministic-combine tail explains almost all of the 85us graph-span gap; the41us prepare cost is offset elsewhere by better GEMM overlap/critical path. It is incorrect to label the whole old fused-finalize comparison as GEMM regression.
- The legacy Nemo finalizer lasts242us in the trace but starts before FC2 finishes. Only54us extends the chain. Optimizing a misleading summed duration would target the wrong bottleneck.
- Both prepare captures use2368 CTAs×128threads (29/32 registers for Nemo/V3). Nearly all prepare time extends the critical path.

Native source manifests, profile commands, selected tactics, raw `.nsys-rep` and `.sqlite` captures remain under the matching remote `optimization-20261027` directory. Current NCU application-replay counter profiles use the same native workload and frozen selections, with no cache/clock override; these counters also remain diagnostic because profiling can alter PDL scheduling.

## NCU memory/compute evidence

The same frozen native graph calls were collected with application replay (3 passes), profiling only FC1 and FC2, with application-controlled cold-L2 preparation. All four captures completed. No counters are attributed to prepare/combine. Profiler scheduling and concurrency effects remain a limitation; compare final decisions using the native CUPTI C-A-A-C screen.

| Case | Phase | Swap / legacy DRAM read MB | Swap / legacy L2 read MB | Swap / legacy L2 hit % | Swap / legacy tensor-active elapsed % | Swap / legacy instructions M |
|---|---|---|---|---|---|---|
| Nemo NV | FC1 | 1089.6 / 412.2 | 3999.1 / 2432.4 | 55.42 / 67.14 | 39.57 / 53.52 | 91.16 / 103.16 |
| Nemo NV | FC2 | 746.9 / 531.2 | 3229.5 / 2697.9 | 52.89 / 57.63 | 49.28 / 65.18 | 27.33 / 16.76 |
| V3 MXFP4x8 | FC1 | 1196.6 / 611.7 | 5182.3 / 4473.5 | 61.68 / 73.32 | 80.29 / 76.55 | 44.43 / 81.38 |
| V3 MXFP4x8 | FC2 | 563.7 / 473.5 | 2669.4 / 2027.6 | 54.72 / 63.70 | 57.18 / 59.50 | 30.91 / 19.03 |

Nemo FC1 reads2.64× as much HBM data despite fewer executed instructions. This supports testing general weight-reuse/cache policy before instruction micro-optimizations. It does not prove eviction priority alone caused the difference: the N128-versus-N256 geometry also changes how often weights are requested. Nemo FC1 SM max/mean active cycles1.081 versus1.008 also leaves some scheduling/imbalance opportunity; FC2 is1.017 versus1.022. V3 FC1 shows that extra read traffic can coexist with high tensor activity, so cache-policy retention must be measured across both workloads.

`ncu-summary.json` records counter values and units. The61 raw profile artifacts are locally preserved in `evidence/`; archive SHA256 `9e15809465a4adaf7e06220b8e56ade6d15ae2b2a544062d8b21c02da782b3e5`.
