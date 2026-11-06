Selected implementation: native `4d183b83` / Hash `dbd3cea`. Only comments differ from measured FC2-only `71f94c12` / `f14a1b1`; the early FC1 wait is retained. No new timing on the comment commit is claimed. The combined C4 trial is rejected and remains archived under `combined-candidate/perf/FINAL_COMPARISON.*`.

# Before all four correctness fixes versus latest completed AFTER

BEFORE `7f1a0931`; AFTER `71f94c12` includes all four fixes and paired FC2 waits. It excludes the FC1 early-wait removal, whose combined C4 sweep is pending.

EP8, eight B300 on hu-pdx-69, CUDA 13.2, full auto tune/O3, H7168/I2048/E256/top-k8, non-fused finalize, identical external benchmark. 3 warmups and 100 cold-L2 CUDA-graph CUPTI samples per row. Each sweep reports the median per-sample rank-MAX latency. BEFORE is sqrt(A1*A2), not the corrected B3 control.

| Tokens | BEFORE us | AFTER us | BEFORE / AFTER | AFTER latency change |
|---:|---:|---:|---:|---:|
| 1 | 88.08 | 87.38 | 1.0080x | -0.80% |
| 2 | 116.08 | 96.56 | 1.2021x | -16.81% |
| 4 | 119.36 | 124.74 | 0.9569x | +4.51% |
| 8 | 139.06 | 141.38 | 0.9836x | +1.66% |
| 16 | 161.43 | 147.27 | 1.0962x | -8.78% |
| 32 | 176.20 | 182.56 | 0.9651x | +3.61% |
| 64 | 201.69 | 202.90 | 0.9940x | +0.60% |
| 128 | 207.16 | 208.87 | 0.9918x | +0.82% |
| 256 | 212.29 | 213.33 | 0.9951x | +0.49% |
| 512 | 212.59 | 216.19 | 0.9833x | +1.70% |
| 1024 | 231.32 | 238.88 | 0.9684x | +3.27% |
| 2048 | 320.41 | 317.14 | 1.0103x | -1.02% |
| 4096 | 470.59 | 473.04 | 0.9948x | +0.52% |
| 8192 | 748.63 | 752.41 | 0.9950x | +0.50% |

8–8192 geometric speedup: **0.997443x**. Tokens 1/2/4 stay visible but are excluded from this aggregate. All selected tactics match between the before sweeps and C3.

Same node, environment, benchmark, workload, fixtures, timer and autotune catalog. Two earlier BEFORE sweeps versus one later AFTER sweep; temporal drift is not canceled and these data do not establish statistical significance.
