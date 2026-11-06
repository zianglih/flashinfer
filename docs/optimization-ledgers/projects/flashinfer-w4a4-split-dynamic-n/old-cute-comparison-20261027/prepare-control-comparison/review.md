# V3 MXFP8 T16384 saved-control comparison

| Campaign | GPU | First / second control (µs) | Geomean (µs) |
|---|---:|---:|---:|
| linear_sf | 0 | 737.300 / 738.663 | 737.981 |
| half_grid | 4 | 786.454 / 783.270 | 784.860 |
| primary | 1 | 785.285 / 779.429 | 782.352 |

No recorded tactic, routing, source-library, recipe or timing-contract mismatch explains the faster GPU0 control. GPU identity and time differ. Without per-leg clocks/power/temperature or a same-GPU crossover, the cause is unresolved; do not normalize or compare candidates across these separate brackets.

The exact native cache snapshot is identical in all six rows. Both FC phases are M256/N256/group2/K4/static, PDL enabled, and dispatch channels/reductions/routed capacity match. The matching mixed-precision activation recipe is unchanged; initial MX activation quantization remains outside timing. Primary uses the base-three-model benchmark rather than the Nemo-extended file; all library hashes and observed V3 execution contracts match.

Half-grid / linear control GM: 1.063523×; primary / linear: 1.060124×. These are cross-GPU diagnostic differences, not optimization speedups.
