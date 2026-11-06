# W4A16 static Gather4 traversal screen

The instruction-sanity candidate passed all33 existing W4 exact cases and the four-cell fixed-winner CAAC screen. It remains unstaged in `flashinfer-w4a16-linear-issue-review`, base22ffe662, kernel8590ed74f7df06e40145e03ea76b572dd32b6094d14a8932de34c7d044a78515. No retention decision yet; broader shape coverage is appropriate before publication.

| Case | Retained us | Candidate us | C/A−1 | Control repeat spread | Candidate repeat spread |
|---|---:|---:|---:|---:|---:|
| K3 EP8 T4096 |547.613|547.540|+0.013%|0.372%|2.515%|
| K3 EP8 T8192 |984.424|980.224|+0.428%|2.996%|4.195%|
| V3 TP8 T8 |57.168|57.105|+0.111%|0.111%|0.057%|
| V3 TP8 T4096 |480.508|478.868|+0.342%|0.063%|0.067%|

K3 changes are unresolved within repeat drift. Its100-sample quartiles show substantial intra-run slowdowns; these are not evidence of a0.4% source gain. The V3TP4K gain is small but stable across both candidate repeats. V3TP8 has byte-identical FC1 code, so its small timing difference is a useful noise boundary. No sampled regression, no claim that K3's old-baseline gap is closed.

Source mechanism is independently supported by SASS: gather-scope N128314→275 and N192405→344 non-NOP instructions, with12/20 fewer uniform branches. Metadata SHFL/R2UR counts, other warp scopes, quotas, copy count/geometry, barriers/bytes, PDL and FC2 remain unchanged. N16 PTX/CUBIN is byte-identical. No runtime division/remainder by N192 geometry was introduced: both task-group operations are compile-time. See `GATE_RESULTS.md` and144-combination geometry proof.

Timing used existing native winner caches and frozen actual routes, fresh22ffe controls on the same physical GPUs5/7 as their candidate, four C-A-A-C processes,100 strictCUPTI cold-L2 CUDA graph samples,10 warmups, no fresh AUTO, and existing read-only2ms NVML wrapper. All source/tactic/route/runtime/sample guards passed. GPU5 K3EP8K reports occasional SM clock decreases and reasonmask4 in control/candidate phases; memory3996MHz. NVML can be stale/coarse. Changed workload utilization can also cause power-capping, so this is not attributed solely to external noise. GPU7 V3 reports2032MHzSM,3996memory,reason0 throughout measured windows. Full sample quartiles and telemetry remain in summary.json/telemetry-summary.json.

All33 captured kernels and22 Gather4 FC1 captures are present; Gather4 has zero local storage and no LDL/STL. No sanitizer or native retuning. Marker tracing stayed off. Raw final archive SHA256 `3edffd6680580e2166318e3f3109cad6c3c3fb24622256b012dc350aea79bd5e` (7,309,198bytes), fetched in hash-checked2MB chunks after managedCLI stdout truncation. No incomplete fetch enters the result. GPU5/7 are idle after both completed jobs.

Aggregation definition: each phase latency is the median of100 CUPTI samples; each arm latency is the median of its two phase medians (for two values this equals their arithmetic mean). Cell speedup is the ratio of those arm latencies minus1. Any reported cross-cell geometric mean is the geometric mean of cell latency ratios, not a geometric average of the raw phase medians. Raw rows are unchanged.
