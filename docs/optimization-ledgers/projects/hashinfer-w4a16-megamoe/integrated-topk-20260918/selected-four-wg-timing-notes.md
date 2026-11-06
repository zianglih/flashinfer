# Selected four-WG refresh interpretation

Both complete baseline comparisons pass full raw/source/sample/output audits.
The original A1 and later A2 tables remain separate in
`selected-four-wg-vs-baselines.md`. The selected source is 14a9e720; A1/A2 are
both 68eb1fe. A README-only publication head was not retimed.

- A1/selected: 1.009891× over 8–8192, 8/11 rows faster. A2/selected: 1.016513×, 9/11
  faster. A1/A2: 0.993485×. These are serial observations, not a drift-cancelled
  estimate. All 100 samples were retained; 1/2/4 are excluded only from retention.
- A2 and selected use identical AUTO tactics at all 14 tokens. A1 differs only
  at 2048: N128 epilogue return versus the selected/A2 N128 dispatch return.
- At 8 tokens, selected remains slower against both controls: 135.7135 µs versus
  A1 129.441 and A2 133.057 µs (0.953781×/0.980426×).
- At 128, unchanged selected 203.874 µs goes from slower than A1 199.1055 to faster
  than A2 208.1935 µs (0.976611×/1.021187×). The control's shift changes the sign;
  this does not prove the original regression was solely measurement noise.
- At 4096, selected 469.7795 versus A2 469.301 µs is 0.998981×, smaller than either
  arm's within-run MAD. At 8192, selected 775.304 versus A2 801.416 µs is 1.033680×,
  but all arms show substantial sample drift; per-arm medians are still the
  unmodified 100-sample values.

Chronology (UTC): A1 10:55:42–11:03:28; selected 12:02:00–12:09:50;
A2 12:18:50–12:26:35 on 2026-09-18. Intervening candidate runs are not a balanced
randomized experiment. No further timing run is implied.

| Tokens | Arm | Median µs | MAD µs | Quarter medians µs | Last/first quarter change |
|---:|:---|---:|---:|:---|---:|
| 8 | A1 | 129.441 | 1.073 | 128.929, 129.377, 128.801, 130.081 | +0.894% |
| 8 | selected | 135.713 | 2.080 | 133.217, 135.426, 135.938, 137.794 | +3.436% |
| 8 | A2 | 133.057 | 1.231 | 130.529, 133.282, 133.217, 134.401 | +2.966% |
| 128 | A1 | 199.105 | 1.296 | 196.322, 199.554, 199.778, 199.362 | +1.548% |
| 128 | selected | 203.874 | 1.456 | 201.026, 205.250, 204.066, 204.290 | +1.624% |
| 128 | A2 | 208.194 | 1.440 | 209.282, 208.162, 207.010, 208.385 | -0.429% |
| 8192 | A1 | 781.334 | 17.248 | 764.326, 766.726, 782.088, 814.214 | +6.527% |
| 8192 | selected | 775.304 | 19.361 | 762.216, 761.415, 800.360, 815.657 | +7.011% |
| 8192 | A2 | 801.416 | 26.081 | 762.503, 760.392, 808.936, 817.704 | +7.239% |

Every comparison verifies 112 finite BF16-bit exact rank/token outputs. This is
benchmark-output coverage; full strict 60 and main 6 sanitizer qualification are
separate. Closure is recorded-only, with no new live GPU/process query.
