# SF-coordinate-cache FC1 diagnostic

The rejected15d6 composition removes the measured SF request/MIO pressure, but introduces a coordinate shared-load dependency. In TP, that dependency has a strong native/PC signal and the serialized FC1 profile slows down. This is not an observed coordinate bank conflict, and it does not justify a new source variant or change the rejected56-cell decision.

## Scope and closure

- Four reports only, approved plan01df2b86 with subsequent two-lane binding85cb22f0: N3U W4A4 T16384, EP8 control→candidate on GPU2 and TP8 control→candidate on GPU3. Original recorded choices/routes; no retune or timing repeat. [Binding diff](binding.diff).
- Control c1ac/482b and candidate15d6, same adopted moe_utils046552b8 release cohort. All13,245 source files/arm checked before and after; actual normal private-arm JIT loads, generated/Ninja identities, native ELF hashes and no-op checks passed. Both GPUs released idle. No source or production PR change.
- [Fetched evidence](evidence/controller-receipt.json):305 files, archive SHA`7e760dd1b3e193e5adc2c4f26f189249f3ffe61487d3c1974b529e9b76a5fac1`. Four reports each have seven application capture processes; the raw profiler replay counter reports11. These are distinct counters.
- [Native/PC replay](analysis.json) verifies all16,000 exported PCs against the exact returned normal FC1 images, all28 FC1 plus28 FC2 native captures, source/options/resources and frozen route/tactic joins. Same-arm images are identical over replays; both FC2 images are byte-identical across arms. The control FC1 images exactly match the previous retained EP19296983 and TPdb9cf015 captures.
- [Resource joins](native-profile-resources.json): all FC1 images168 initial registers,384 threads,LOCAL0, unchanged geometry and driver capacity1 CTA/SM. Shared allocation rises1,024B in both: EP189,440→190,464; TP222,208→223,232. Measured average active warps is3.00 in each. Driver capacity is not achieved residency. Static non-NOP: EP4,027→4,100; TP3,831→3,815.

## Aggregate counters

| Counter | EP control | EP candidate | TP control | TP candidate |
|---|---:|---:|---:|---:|
| Diagnostic FC1 duration (µs) | 293.024 | 264.448 | 427.968 | 484.544 |
| Issued warp instructions | 97,854,852 | 104,977,350 | 143,135,742 | 147,866,305 |
| Issue active (%) | 32.60 | 40.29 | 31.59 | 28.53 |
| Tensor active (%) | 26.20 | 29.48 | 18.05 | 15.94 |
| Long scoreboard (%) | 54.11 | 34.00 | 55.23 | 48.61 |
| Short scoreboard (%) | 6.48 | 17.32 | 4.50 | 15.19 |
| MIO throttle (%) | 2.02 | 0.31 | 8.39 | 0.32 |
| Wait (%) | 5.35 | 9.10 | 5.34 | 11.01 |
| Barrier (%) | 13.59 | 13.65 | 8.91 | 8.79 |
| DRAM read (bytes) | 409,829,632 | 402,949,888 | 387,411,456 | 386,799,360 |
| DRAM throughput (%) | 25.35 | 27.78 | 16.49 | 14.57 |
| L2 hit (%) | 72.28 | 72.53 | 77.43 | 77.62 |
| Global-load L1 sectors | 28,657,718 | 7,443,158 | 58,518,633 | 15,264,873 |

These NCU durations are diagnostic only. The immutable production CAAC observations remain EP+4.748737% / TP−4.687648%, with exposed FC1 changes−25.232µs /+55.721µs. The diagnostic EP duration falls9.752%, TP rises13.220%; those percentages must not replace the CAAC rows. Aggregate executed instructions rise7.279%/3.305% despite the TP static reduction.

## Native dependency and traffic evidence

The candidate PTX directly loads the four coordinate words with `ld.shared.v4.b32` and passes the same four outputs to `cp.async.bulk.tensor.2d...gather4`. On TP, for example, the actual LDS at0xda10 writes R4–R7 and the following elected R2UR instructions consume those registers. This repeats at16 static coordinate-load sites (EP has8 sites across the generated paths, four packets per warp per stage rather than TP16).

| Observation | EP control→candidate | TP control→candidate |
|---|---:|---:|
| SF theoretical global sectors |28,286,080→7,071,520|57,671,680→14,417,920|
| SF cp.async + completion MIO samples |121→0|1,601→3|
| Gather4 MIO samples |50→2|204→0|
| Gather4 wait samples |0→204|121→1,001|
| New coordinate R2UR short-scoreboard samples |0→1,512|0→3,564|
| Total short-scoreboard samples |1,263→2,656|1,203→4,712|

All candidate coordinate `LDS.128` instructions have N-way1 and zero excessive shared wavefronts. Actual equals ideal: EP954,880 and TP4,267,520. The fourfold SF sector reduction is visible in both topologies, while the TP coordinate-read dependency replaces much of the removed MIO pressure. These are measured request and sampled-stall observations; they do not measure a hardware load latency or prove inter-warp bank contention. The source-only padding hypothesis is not supported by these intra-warp counters.

[TP wait attribution](tp-wait-analysis.json) binds the existing probes, branches and fallback loops to their actual barrier offsets. Long-scoreboard samples change: gather-full1,274→1,859; epilogue accumulator-full1,908→6,166; gather operand-empty494→210; MMA accumulator-empty405→228. This is consistent with a slower gather-readiness path propagating to MMA/epilogue, rather than a new producer-buffer-capacity limit. It does not authorize removing any required wait. Coordinate publication stores account for only3 samples; the source warp synchronization lowers without an added gather WARPSYNC instruction in this TP image.

[Independent EP wait mapping](ep-analysis.md) confirms25 required wait groups per arm. Gather operand-empty long-scoreboard samples fall2,350→715, while MMA gather-full changes190→214 and epilogue accumulator-full419→564; weight-full66→48 and accumulator-empty193→165. EP therefore improves without a measured reduction in its MMA gather-ready wait. The observations support different critical-path balance between the frozen wide-EP and narrow-TP geometries, not an unnecessary-wait deletion or a claim that one counter explains the whole gain.

## Interpretation boundary

The unchanged public graph and PDL flags are retained, but this is node-selected application replay: Nsight Compute serializes kernel launches for collection. Consequently it does not preserve production FC1/FC2 overlap. It can expose target FC1 work/dependency differences; it cannot establish a whole-chain PDL or L2-interference cause. [NVIDIA serialization documentation](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html#serialization).

PC samples are observations, not additive time fractions. SourceCounters' executed-instruction sums and aggregate issue metrics come from separate profiler collection passes and are not equated. The original56 primary, all negatives/clocks, and rejection remain immutable. No additional profile, timing repeat, bank-padding or source prototype was run.
