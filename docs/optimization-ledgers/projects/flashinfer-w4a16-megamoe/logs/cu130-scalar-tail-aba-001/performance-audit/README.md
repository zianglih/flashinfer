Scalar-tail Mega B exceeds both control medians at 3/3 measured shapes (global tokens [1, 256, 4096]). This A/B/A bracket does not support adopting the scalar tail.

Original printed medians in milliseconds; positive changes mean slower. All 18 raw values, 72 original split selections, 72 compiled records, and per-rank tactic changes are preserved in `audit.json`.

| Global tokens | Variant | A1 ms | B ms | A2 ms | B/A1 change | B/A2 change | A2/A1 change | A spread |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | Split | 0.086929 | 0.105201 | 0.106881 | +21.02% | -1.57% | +22.95% | 22.95% |
| 1 | Mega | 0.112449 | 0.130721 | 0.107297 | +16.25% | +21.83% | -4.58% | 4.80% |
| 256 | Split | 0.310961 | 0.493972 | 0.300291 | +58.85% | +64.50% | -3.43% | 3.55% |
| 256 | Mega | 0.274786 | 0.417843 | 0.275859 | +52.06% | +51.47% | +0.39% | 0.39% |
| 4096 | Split | 0.568085 | 0.670246 | 0.572595 | +17.98% | +17.05% | +0.79% | 0.79% |
| 4096 | Mega | 0.539011 | 0.716805 | 0.539686 | +32.99% | +32.82% | +0.13% | 0.13% |

A spread is `100 × (max(A1,A2)/min(A1,A2) − 1)`. It is not an error bar.

| Tactic comparison | T1 changed ranks | T256 changed ranks | T4096 changed ranks |
|---|---:|---:|---:|
| A1 → A2 | 3/8 | 0/8 | 2/8 |
| A1 → B | 7/8 | 8/8 | 2/8 |
| A2 → B | 7/8 | 8/8 | 2/8 |

B modifies the shared decoder for both Split and Mega. Split retunes in each process; its movement cannot be treated as an unchanged timing baseline. A1–A2 spread and the changed selections remain separate from the fixed-Mega comparison.

Recorded setup: nvcr.io/nvidia/pytorch:25.11-py3; node `fi-w4a16-mega-cu130-0908`. Original CONTROL, EP8, T1/256/4096, 100 CUPTI, 3 warmups, CUDA graph, cold L2, two transform groups.

Checks passed: original stdout rows and rank tactic files exactly reproduce saved per-arm/combined results; every arm has six raw rows and 24 split/compiled records; imported decoder/compiler/kernel fields match the arm preflight; source before/after and exact one-file overlay match; all selected Mega configurations/resources and per-rank split input shapes/other metadata agree across arms; baseline restoration is recorded.

- A1 source `4a3716c6e6dc7f38ae84c182ffd7e06b083b4b606849031180f8939f340a8045`; decoder `c36c5fce4e8132dd19f1928fbc72100a1d7ddc8d90cc8db88cfe24b8d3e722c9`.
- B source `a0e08551c2da352b77aab6b4f7d06ce05843891ba993b3104d578304cff92975`; decoder `735beaa0697ac948c26f8ecb8ec16a70ec369a686f4f776e3effbcb36cb4f26e`.
- A2 source `4a3716c6e6dc7f38ae84c182ffd7e06b083b4b606849031180f8939f340a8045`; decoder `c36c5fce4e8132dd19f1928fbc72100a1d7ddc8d90cc8db88cfe24b8d3e722c9`.

This is one process median per arm/shape, without a statistical confidence interval. No new GPU work, numerical check, tensor-byte identity audit, or instruction-level causal claim is made. Source/runtime and loaded-library details remain in the separate `../source-runtime-audit.json`. Reproduce locally with `python3 logs/cu130-scalar-tail-aba-001/performance-audit/audit.py`.
