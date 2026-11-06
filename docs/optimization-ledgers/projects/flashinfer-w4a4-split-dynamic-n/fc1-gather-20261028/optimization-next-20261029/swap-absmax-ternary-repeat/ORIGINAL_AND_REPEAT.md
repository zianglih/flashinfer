# Ternary absmax: primary screen and one bounded repeat

No retention decision. Both source arms remain the immutable b139 control and abd55f60 tree candidate. The isolated repeat uses only the MX4x8 backend selector, followed by per-token; shared inputs are constructed by the unchanged seed 42 helper. All original rows are retained.

| Campaign | Backend | C1 us | A1 us | A2 us | C2 us | Speedup | C/A repeat spread |
|---|---|---:|---:|---:|---:|---:|---:|
| Primary 44 | CuteDSL MXFP4x8 | 744.774 | 764.662 | 779.318 | 744.038 | -3.569% | 0.099% / 1.917% |
| Primary 44 | CuteDSL PER-TOKEN | 913.945 | 912.632 | 912.808 | 913.320 | +0.100% | 0.068% / 0.019% |
| Bounded repeat | CuteDSL MXFP4x8 | 761.879 | 782.534 | 775.958 | 782.119 | -0.938% | 2.657% / 0.848% |
| Bounded repeat | CuteDSL PER-TOKEN | 913.496 | 912.600 | 913.624 | 913.976 | +0.068% | 0.053% / 0.112% |

| Campaign / phase | FC1 us | FC2 us | Combine us | E2E first → last quartile us |
|---|---:|---:|---:|---:|
| Primary 44 / 0-control | 387.683 | 313.235 | 57.953 | 742.694 → 824.102 |
| Primary 44 / 1-candidate | 395.875 | 324.818 | 58.448 | 743.686 → 828.487 |
| Primary 44 / 2-candidate | 401.491 | 332.611 | 59.056 | 745.031 → 835.463 |
| Primary 44 / 3-control | 386.659 | 311.907 | 57.681 | 742.982 → 805.895 |
| Repeat / 0-control | 393.731 | 323.427 | 57.920 | 741.350 → 837.926 |
| Repeat / 1-candidate | 403.779 | 333.187 | 58.864 | 746.407 → 819.655 |
| Repeat / 2-candidate | 404.979 | 328.067 | 58.864 | 746.406 → 841.639 |
| Repeat / 3-control | 405.124 | 331.971 | 59.377 | 742.919 → 835.464 |

The loss has the same direction in the repeat, but its magnitude changes from −3.57% to −0.94%; control phase variation grows to 2.66%. Within-phase slowdown remains substantial. Component timing changes include both FC1 and FC2; an unchanged FC2 binary does not prove its slowdown external because pipeline overlap and machine state can affect its duration. The unchanged per-token control is near neutral in both campaigns. No further repeat, clock adjustment or post-result winner selection was performed.

Primary 44 affected cells: +0.107% geomean overall, −0.022% decode, +0.235% prefill. This is broad near-neutral evidence with an unresolved negative N3U MX row, not a no-regression proof. Tree-only codegen has eight max operations at dependency depth 3 rather than 8; all numerical/resource gates passed. The current local review is rebased to 77391e28, hash 67c2af2f, and has no GPU qualification; its performance cannot be labeled with these b139 results.
