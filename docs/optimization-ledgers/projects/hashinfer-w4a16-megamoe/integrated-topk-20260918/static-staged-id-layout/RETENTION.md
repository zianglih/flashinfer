# Static staged-ID layout: not retained

Independent complete-file audit PASS (2c0610abcf97bdccb2aa88ff48a6835abd1cc5bd01c2d958c93d4327ef559356). Fresh same-boot hu59 d01 A1 versus912f B1,13 shapes,100 samples/arm/shape,104 exact outputs. All13 selected tactics match across all8 ranks. Decode4–512 geometric speedup 1.000422134×, 6/8 lower medians: effectively flat; no demonstrated general benefit. No promotion or causal instruction-efficiency claim.

| Tokens | d01 A1 µs | static-ID B1 µs | A1/B1 |
|---:|---:|---:|---:|
| 1 | 65.6805 | 65.3285 | 1.005388× |
| 2 | 84.7690 | 82.7205 | 1.024764× |
| 4 | 94.7040 | 96.9615 | 0.976718× |
| 8 | 120.8970 | 119.5050 | 1.011648× |
| 16 | 134.5290 | 134.1610 | 1.002743× |
| 32 | 159.7930 | 159.2970 | 1.003114× |
| 64 | 182.9625 | 180.1290 | 1.015730× |
| 128 | 184.9770 | 188.5930 | 0.980826× |
| 256 | 191.0255 | 191.0100 | 1.000081× |
| 512 | 195.5375 | 192.9780 | 1.013263× |
| 4096 | 464.0205 | 460.6760 | 1.007260× |
| 8192 | 797.7025 | 792.7100 | 1.006298× |
| 16384 | 1530.8020 | 1499.8520 | 1.020635× |

Prefill dispersion (consecutive25-sample quarter medians, µs):

- T4096: A1 [463.235, 463.044, 464.388, 465.059]; B1 [460.837, 460.965, 459.332, 461.637]; MAD 2.753/3.137.
- T8192: A1 [771.174, 769.638, 818.662, 833.83]; B1 [767.334, 769.799, 812.102, 821.287]; MAD 26.097/25.281.
- T16384: A1 [1372.752, 1481.041, 1551.506, 1565.97]; B1 [1366.507, 1485.453, 1583.117, 1571.213]; MAD 49.969/74.561.

All298 original sealed member files are locally verified, including208 source files and16 output files copied by exactSHA from the audited A1 content cache. The original685MB gzip remains remote and was not locally byte-verified. Compact transport and assembly do not change the numerical validator. Serial arms do not remove timing drift; these are hu59 results, not comparisons with hu15 A1/A2/A3. The fresh d01 A1 is separately available as the control for the subsequent same-node metadata-first trial.
