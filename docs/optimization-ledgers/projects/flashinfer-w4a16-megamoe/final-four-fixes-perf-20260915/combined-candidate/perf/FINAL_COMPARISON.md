# Original BEFORE and FC2-only versus combined AFTER

H7168/I2048/E256/topk8 W4A16 EP8; 8 B300; AUTO/O3/maxregs96; 3 warmups/100 samples.

All outputs passed exact canonical hashes, finite/bit-repeat checks and full raw-file verification. Complete local archives and fresh process/GPU/source/environment closure passed.

| Tokens | Original BEFORE us | FC2-only C3 us | Combined C4 us | BEFORE/C4 | C3/C4 |
|---:|---:|---:|---:|---:|---:|
| 1 | 88.08 | 87.38 | 85.95 | 1.0248x | 1.0166x |
| 2 | 116.08 | 96.56 | 112.55 | 1.0314x | 0.8580x |
| 4 | 119.36 | 124.74 | 124.35 | 0.9598x | 1.0031x |
| 8 | 139.06 | 141.38 | 144.15 | 0.9648x | 0.9808x |
| 16 | 161.43 | 147.27 | 148.61 | 1.0863x | 0.9910x |
| 32 | 176.20 | 182.56 | 185.87 | 0.9479x | 0.9822x |
| 64 | 201.69 | 202.90 | 206.47 | 0.9769x | 0.9827x |
| 128 | 207.16 | 208.87 | 213.41 | 0.9707x | 0.9787x |
| 256 | 212.29 | 213.33 | 215.15 | 0.9867x | 0.9915x |
| 512 | 212.59 | 216.19 | 215.31 | 0.9873x | 1.0041x |
| 1024 | 231.32 | 238.88 | 229.75 | 1.0069x | 1.0398x |
| 2048 | 320.41 | 317.14 | 314.52 | 1.0187x | 1.0083x |
| 4096 | 470.59 | 473.04 | 464.69 | 1.0127x | 1.0180x |
| 8192 | 748.63 | 752.41 | 749.54 | 0.9988x | 1.0038x |

8–8192 geometric speedups: BEFORE/C4 **0.995550x**; C3/C4 **0.998102x**.
All 14 rows shown; 1/2/4 excluded only from aggregates. Ratios greater than 1 favor C4. BEFORE is 7f1a0931 before all four correctness fixes; C3 is isolated paired-FC2 candidate 71f94; C4 is combined 8da5ab77. Raw milliseconds, both original A1/A2 medians, tactic winners and evidence pins remain in JSON; detailed B3 attribution remains in the frozen checker result.

Same hu-pdx-69 node, environment, external PDL-off benchmark, fixtures, autotune catalog and cold-L2 CUPTI graph timer. Two earlier BEFORE sweeps versus later single C3 and C4 sweeps; temporal drift is not canceled. The 100 graph samples per row are not independent statistical trials, and these comparisons do not establish causal or statistical certainty.
