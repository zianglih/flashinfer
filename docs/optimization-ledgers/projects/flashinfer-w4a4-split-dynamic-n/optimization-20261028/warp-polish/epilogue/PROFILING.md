# Clean 99f4 prefill profile

Diagnostics only, not retention timings. Source `99f4d0c277746fb706d10a4bb303c98c5f31e0a9`; all 342 benchmark source hashes and native winner cache hashes verified before/after. Existing C3 B300 GPU1, `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA 13.2), source-keyed persistent C++ cache reused. Both workloads use the unchanged public benchmark, unfused swap-AB, frozen native winners, 20 Nsight Systems CUDA-graph replays. NVFP4 includes input quantization. No external baseline rerun, AUTO sweep, source mutation or sanitizer run.

Raw reports, SQLite, commands/environment, selection receipts and hashes are in `profile-current/`; `summarize_profile_remote.py` derives the stage breakdown. Critical extension is the increase in graph completion time as each kernel interval is added, preserving PDL overlap. Do not sum kernel durations as end-to-end latency.

| Stage | V3 MXFP4x8 T16384 duration / critical extension (us) | N3U W4A4 T4096 duration / critical extension (us) |
|---|---:|---:|
| Input quantization | — | 6.208 / 6.208 |
| Routing / top-k | 30.161 + 3.296 + 7.360 / 38.097 | 19.120 / 18.129 |
| Prepare | 39.713 / 39.505 | 7.905 / 7.601 |
| FC1 | 318.866 / 310.354 | 90.945 / 89.937 |
| FC2 | 221.282 / 186.369 | 90.593 / 82.049 |
| Combine | 84.273 / 80.737 | 17.281 / 14.192 |
| Median full graph | **654.916** | **218.642** |

The displayed stage medians need not add exactly to the median graph. V3 winner: route N128, FC1 M512/group2, FC2 M256/group2, K4/K4, static. N3U: route N128, M256/group2 in both, K4/K4, static. Current N3U differs from the older one-CTA/N256 winner; its historical profile is not a causal source comparison.

## Focused memory counters

One V3 graph replay with application-replay NCU, filtering only prepare/combine; three counter passes, unchanged source/winner, 65.5 s wall time. Counter instrumentation changes scheduling, so NCU duration is not a new benchmark measurement. `analyze_memory_ncu.py` verifies the artifact hashes and exports `memory-summary.json`.

| Metric | Prepare | Combine |
|---|---:|---:|
| NCU duration (us) | 44.256 | 82.016 |
| DRAM read / write (MB, decimal) | 81.401 / 120.860 | 230.642 / 223.072 |
| DRAM throughput / peak | 59.63% | 72.14% |
| Read + write (GB/s) | 4570.3 | 5532.0 |
| L2 read sectors | 5,371,233 | 11,038,470 |
| L2 hit | 18.46% | 0.75% |
| Warp instructions | 7,013,344 | 14,967,296 |
| Registers / thread | 32 | 80 |
| SM active cycles avg / max | 0.862 | 0.960 |

Prepare + combine contribute about 120.24 us (18.4%) of V3 critical extension. Neither has shared-memory barriers. Combine already obtains substantial DRAM throughput and has limited SM active-cycle imbalance, so another speculative barrier/vector rewrite is not supported. Aggregate prepare counters do not establish scalar SF stores' individual share; a per-PC/store-sector profile would be needed to attribute their cost.

## Follow-up and closed directions

A new general hypothesis is routed FC2 scratch instead of sparse expanded scratch in the high-level unfused swap-AB chain. Existing combine already supports permuted input. This could remove FC2 output-address metadata work and reduce backing footprint/TLB pressure; it does not eliminate compulsory live output bytes. Preserve the low-level expanded-output API, per-token scaling, exact ordered FMA, and PDL. Implementation is an isolated follow-up, not a result.

Do not repeat the already rejected LDG256 combine, broad CTA geometry, selective/warp-coalesced metadata, vector-outer accumulator lifetime, output-LAST/input-FIRST handoff, destination-linear SF loop, SF shared transpose, or separate payload/SF warpgroup variants without a new mechanism. See `optimization-20261027/{finalize-vector,prepare}/README.md`, `scripts/{finalize_geometry_experiment,pdl_handoff_cache_experiment,prep_linear_sf_experiment,prep_sf_vector_experiment}/README.md`. The prepare SF preload is already retained in 99f4. Root's producer owner is auditing row-parallel SF ownership against those prior failures.

GPU1 was empty and released after completion; no further GPU work started.
