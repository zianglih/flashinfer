# Candidate004 T128 diagnostic profile

Source `7a2bf6ca` on hu-pdx-43. The complete repeat remains in `logs/candidate004-raw-b-repeat-ep8-fused.json`; both profilers used its T128 cache `6b255c3e`, confirmed config cache hits and did not autotune. Fused finalize, single GPU simulated EP8.

- NSYS completed in 33.614s; six graph kernels, FC2 is the second exact-symbol grouped GEMM. FC2 grid2×1×74, cluster2, block512, registers128, dynamic shared memory209984B, local memory0.
- NCU kernel/node/full completed in26.630s with40 passes and one selected FC2 kernel. Dynamic shared memory209984B, driver shared1024B, total211008B, allocated211072B, static0; registers128.
- The normally selected T128 tactic uses ((128,16,256),(2,1),True) for both GEMMs.

Limitations:
- Six CTC metrics unavailable: RX/TX user data sum, pct_of_peak_sustained_elapsed, per_second.
- NCU source import empty because normal benchmark compilation did not include lineinfo; separate native captures preserve PTX/SASS lineinfo.
- GPU cache/clock controls remain none as in previous profiles; captured timings are diagnostics, not normal benchmark evidence.
- Single GPU simulated EP8, fused finalize; this candidate004 stage trial is not a retained/published result.

Reports, SQLite, raw CSV, kernel-order JSON and exact execution receipts are preserved. Final source checks passed and no compute processes remained. No nonfused source arm was started.
