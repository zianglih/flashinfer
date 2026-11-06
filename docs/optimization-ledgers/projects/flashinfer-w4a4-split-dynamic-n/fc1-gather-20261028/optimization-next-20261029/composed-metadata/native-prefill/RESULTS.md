# Final-source native prefill retune

Completed 23/23 jobs and 84/84 supported prefill cells at 4096, 8192, 16384 tokens before the original devbox was reclaimed. Fetched all 567 files from persistent storage after replacement, archive SHA `5c8ba5247486b3849f0d6213708a772bf86b8baa18e177a76bffd6cd7a5aa78c`; every manifest and measurement check passes. No job was rerun on the replacement node. The original physical GPU UUIDs match the reused controls for every cell.

Frozen kernel `3225acf2dfeba54df42481b3186267b1bde642da9887b98cb966d5383d8635af`, retained commit `c0c0bc41c70100c694ac55585990971aba8b7fb9`. Native search explores only the existing tactics; it does not change kernel code or production defaults. Final-source old-winner AA is reused; native winners get two fresh frozen replays with 100 strict CUPTI cold-L2 graph samples each. NV includes its initial quantizer. Fused finalize disabled. No W4A16 search. All 84 outcomes are preserved, including regressions.

| Scope | Cells | Geometric mean improvement |
|---|---:|---:|
| all ALL | 84 | +1.877% |
| v3 ALL | 24 | +2.206% |
| v41-flash ALL | 18 | +1.238% |
| kimi-k3 ALL | 18 | -0.045% |
| nemo3-ultra ALL | 24 | +3.497% |
| all EP | 45 | +2.918% |
| v3 EP | 12 | +4.182% |
| v41-flash EP | 12 | +1.116% |
| kimi-k3 EP | 9 | -0.571% |
| nemo3-ultra EP | 12 | +6.194% |
| all TP | 39 | +0.688% |
| v3 TP | 12 | +0.268% |
| v41-flash TP | 6 | +1.483% |
| kimi-k3 TP | 9 | +0.484% |
| nemo3-ultra TP | 12 | +0.868% |

All 69 runtime process guards passed; 3466 compilation observations, 1740 FC1 observations. 18 FC1 observations have 8 B local storage: {('ep-nemo3-ultra-mxfp', 8): 8, ('tp-nemo3-ultra-mxfp', 8): 10}. These are newly admitted native selections, outside the earlier fixed-winner zero-local claim. Parent independently confirmed real LDL/STL spilling in the wide N3U MX case and is evaluating a separate control-register 120 candidate. This immutable retune remains 112.

Search host spans total 5265.933 s summed over parallel processes: `cute.compile` API 4076.586 s (77.4% of summed process wall); profile-exclusive 668.794 s (12.7%). Compile includes SDK cache handling and is not isolated compiler CPU time; profile-exclusive includes warmups, capture, waits and measurement machinery but excludes nested `cute.compile`. Public replay has 16,800 fresh samples plus 16,800 reused same-source samples. 8,400 search-pass public samples are excluded from comparison.

The native policies differ by format: W4A4/per-token inherit eager host-excluded CUDA-event profiling; MX explicitly requests CUDA-graph CUDA-event profiling. All final public medians use CUPTI graph timing. This can affect selection but is not established as the cause of K3 regressions. See `K3_SELECTION_AUDIT.md` and the independent benchmark-only graph-policy experiment.

Machine-readable full outcomes: `report/cells.csv`, exact old/native keys and tactics `report/winners.json`, timings `report/timing.json`, summary `report/summary.json`; raw results and 100 samples per median in `evidence/runs/`. No cache rewriting, post-hoc winning-cell selection, source edits, or sanitizer.
