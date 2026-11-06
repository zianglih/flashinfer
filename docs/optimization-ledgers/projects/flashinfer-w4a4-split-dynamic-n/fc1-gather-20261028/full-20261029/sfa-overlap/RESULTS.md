# SFA-before-gather-wait screen

Clean `fb66a27e` control versus the same commit with kernel `04c92e1fbea8222c58ae968e627790366c41ca1a8338ecf52c543b12d1864104`. Separate local review clone stays unstaged; no commit or push.

- 7 existing exact tests passed (FP4/per-token, MXFP4x8/MXFP8, two CTA, SiTU, partial K). No sanitizer.
- Five same-GPU C-A-A-C jobs, 44 cells / 17,600 strict CUPTI samples; 36 affected cells, 8 W4A16 diagnostics. Frozen routes and tactics; all source/cache/observer checks passed.
- Runtime cubin guard: 128 compile observations in 10 phase receipts; all passed. No compiler options changed.
- Affected aggregate: +0.170%; decode (8 tokens) +0.040%; middle (256) -0.012%; prefill (4096/16384) +0.327%.

| Shape / family | Gmean |
|---|---:|
| kimi-k3 EP | +0.662% |
| nemo3-ultra EP | -0.008% |
| v41-flash EP | +0.411% |
| v3 TP | -0.028% |
| v41-flash TP | +0.061% |

Most cells are neutral. V41F EP MXFP8 16K measures +2.727%, but candidate-pass spread is 5.740% (920.17 vs 972.98 us), so this is not a stable gain. K3 EP MXFP4x8 16K measures +2.602%; both candidate passes (1054.56/1068.03 us) beat both controls (1092.49/1085.29 us), with 1.278% candidate spread. This small screen does not justify a broad performance claim.

Evidence: `report/cells.csv`, `report/summary.json`, `evidence/validation/smoke`, and all raw CAAC receipts under `evidence/perf`. Archive SHA256: `d281e151d7c0dc26354c9656cb281372a0248eb1f6d5f8be0f48acd9e77def08`.

Ordering rationale and unchanged nongather AST proof are in `ORDERING.md` and `source-proof.json`.
