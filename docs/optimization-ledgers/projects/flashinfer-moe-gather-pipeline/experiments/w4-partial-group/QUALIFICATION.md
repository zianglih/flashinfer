# Partial-group qualification

Source: `b25dacfac38c3193a4368e87be2ec058f0da71fbc76db6b56490679b42676851` on retained `49c91adf47d30fc2049c76cbaf34d0ccf3291434`.

- 14 selected exact calls passed: five paired split shapes plus two paired single-rank Mega shapes.
- 17 native pairs have unchanged actual resources and zero local memory/stack.
- 13 unaffected pairs are byte-identical PTX/cubin/SASS; aligned split paths, unrelated FCs/finalizer and both Mega shapes are included.
- The four affected split kernels add static full/tail dispatch code. Performance must justify that growth; the executed tail performs fewer payload loads/conversions/TMEM stores.

| Case | Stage | Control non-NOP | Candidate non-NOP | Delta |
|---|---|---:|---:|---:|
| 256 / 576 | fc2 | 1699 | 1830 | +131 |
| 256 / 448 | fc2 | 1491 | 1611 | +120 |
| 352 / 256 | fc1 | 1765 | 1945 | +180 |
| 256 / 352 | fc2 | 1505 | 1685 | +180 |

The preserved legacy-layout intermediate352 failure occurs in existing test weight preparation before compilation. A separate supported-layout pair passes the FC2-tail96 case. The direct private M-major K16 retained control is admitted by `can_implement` but fails the original transform-partition whole-scale-block assertion; it is an existing capability mismatch, not claimed supported here.

No sanitizer or performance result is included in this qualification. The V41F TP13-cell native CAAC screen is a separate source-bound campaign.
