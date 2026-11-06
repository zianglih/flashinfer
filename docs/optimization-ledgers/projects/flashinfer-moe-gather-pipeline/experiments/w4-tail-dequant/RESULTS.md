# W4 tail-dequant: complete affected screen

Control: retained `02de7785c10847b3528340840bed40bd405d85b4`. Candidate: the two-file frozen source in `source.json`, still unstaged. Native compiler settings, register policies, frozen tactics/routes and original cache entries are unchanged. No sanitizer or retuning.

The two disjoint C-A-A-C campaigns preserve15,600 native CUPTI samples:39 cells ×4 phases ×100 samples. Each phase uses10 warmups, cold L2 and CUDA Graph replay. Per-cell speedup is `sqrt(C1_median*C2_median/(A1_median*A2_median))-1`; group results are geometric means of those ratios. Tokens1/2 remain in all raw tables and are excluded from retention. No sample trimming or clock-based exclusion.

| Group | Retention cells | Geomean speedup | Negative cells |
|---|---:|---:|---:|
| all | 33 | +1.471% | 6 |
| decode | 15 | +1.701% | 0 |
| middle | 9 | +2.110% | 0 |
| prefill | 9 | +0.456% | 6 |
| tp-v41-flash-w4a16 | 11 | +0.967% | 1 |
| tp-kimi-k3-w4a16 | 11 | +2.251% | 2 |
| tp-nemo3-ultra-w4a16 | 11 | +1.199% | 3 |

All24 cells at tokens4–512 improve, with phase-repeat spreads below0.5%. Prefill remains mixed: six of nine cells regress, from−0.24% to−0.75%; the positive aggregate is influenced by noisy8192-token results. N3U prefill averages−0.478%. Across all156 phase/cell records,49 of624 clock quartiles differ from2032MHz or report a clock reason, and one quartile is unavailable. The largest phase-repeat spread is4.978%. These anomalies and all negatives remain in the table. No claim of uniform regression-free performance.

The complete native resource join covers78 measured stage configurations and196 loaded function records. Registers, local memory and configuration are identical across arms, with LOCAL0 throughout. There are40 native stage joins for five recorded-default cells. Both campaigns passed full immutable source pre/postflight and strict cache/timing guards. GPUs0/1/2 are idle and released.

## Full affected table

| Tokens | V41F TP4 | K3 TP8 | N3U TP8 |
|---:|---:|---:|---:|
| 1 | +0.334% | +1.045% | +0.874% |
| 2 | +1.426% | +1.481% | +0.928% |
| 4 | +1.352% | +2.136% | +2.197% |
| 8 | +0.674% | +2.258% | +2.894% |
| 16 | +0.443% | +3.074% | +1.107% |
| 32 | +0.501% | +2.236% | +1.376% |
| 64 | +1.110% | +3.135% | +1.073% |
| 128 | +1.165% | +3.036% | +1.973% |
| 256 | +1.311% | +2.637% | +1.812% |
| 512 | +1.081% | +3.747% | +2.260% |
| 4096 | -0.284% | -0.241% | -0.563% |
| 8192 | +2.895% | +3.591% | -0.293% |
| 16384 | +0.423% | -0.746% | -0.578% |

## Evidence

- `combined39/table.md`: all39 rows with C1/A1/A2/C2 medians and repeat spreads.
- `combined39/cells.csv` and `summary.json`: exact disjoint union and hash-bound inputs. The first12 rows are unchanged.
- Initial raw bundle: `evidence/w4-tail-dequant-screen/1793368574438182000/data`.
- Remaining raw bundle: `evidence/w4-tail-dequant-remaining/1793369332076642000/data`.
- Each sibling `report/` independently recomputes CUPTI sample spans, routes, winners, cache receipts, native resources, timelines and clocks from raw data.
- `performance-remaining/AFFECTED_SCOPE.md`:39 affected and429 reusable full-table cells, with representative native equivalence boundaries.
- `qualification-summary.json`:12 split exact calls and4 Mega exact calls, source/layout/state proofs, full-K and Mega raw-binary equality.

No source commit, push or PR publication was performed by this experiment. Retention awaits the parent decision after independent combined-data review.
