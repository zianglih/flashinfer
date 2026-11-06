# Fixed-control sample budget diagnostic

The completed fixed CONTROL arm contains all 26 paired rows and 26 arrays of 100 post-rank-MAX CUPTI samples. Original raw/tactic/resource checks pass; all 104 compiled objects have local0. Array medians match the printed six-decimal rows (maximum rounding difference 0.000000500 ms). Auto remains in progress.

The original subprocess took **899.791 s**. Rank-zero timing-utility intervals total **11.815639 s**, or **1.313%**: split 5.889443 s and Mega 5.926196 s. These utility intervals include graph setup, estimates, flushing, processing and reduction. The remaining time is not a compilation estimate; this fresh-node arm included a first-use native build. It is not a warmed iteration-time measurement.

| Samples | Worst absolute prefix error, all26 | Worst point window p95, all26 | Worst absolute prefix error, Mega13 | Worst point window p95, Mega13 |
| --- | ---: | ---: | ---: | ---: |
| 20 | 7.031% | 7.670% | 3.203% | 2.998% |
| 30 | 7.173% | 7.031% | 2.677% | 2.569% |
| 50 | 5.441% | 5.346% | 1.299% | 1.279% |

**Decision: retain 100 samples for ordinary full-grid fixed screens.** Cutting count is a weak speed lever in this measured arm, while 20/30/50 prefixes can materially move the medians. Fifty samples is the least sensitive of these choices but still shifts a split point by 5.44% and a Mega point by 1.30%; this is not evidence of sub-percent screening reliability. No extra shorter-count run or repeated fixed calibration is needed. The full 1–4096 grid remains unchanged.

These are within-run diagnostics against the same 100-sample reference, not confidence intervals or between-run repeatability. Overlapping windows are dependent. Removing 80% of samples does not imply removing 80% of utility wall, and the 11.816-second utility scope is not pure sample execution. No actual shorter-run speedup is measured. Complete raw arrays, all point diagnostics and exact evidence hashes are preserved in the neighboring JSON files.
