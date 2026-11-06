# Fence gate comparison

45 changing-route graph replays match exactly across clean8b74 and the frozen fence candidate. Twenty-seven unique FC1/FC2 specializations cover three formats, five geometries, CLC/static, one/twoCTA, cp.async/TMA SFB and zero-local work. All source pins/patches remain unchanged.

| Kernel | CLC | TMA SFB | Fences C→A | Registers C→A | Active blocks/SM C→A | SMEM |
|---|---:|---:|---:|---:|---:|---:|
| w4a4-m128-n16-fc1 | True | False | [3, 1] | [76, 76] | [1, 1] | 197504 |
| w4a4-m128-n16-fc2 | False | False | [2, 1] | [102, 102] | [1, 1] | 197504 |
| w4a4-m128-n128-fc1 | True | True | [3, 1] | [80, 80] | [1, 1] | 74624 |
| w4a4-m128-n128-fc2 | False | True | [2, 1] | [100, 100] | [1, 1] | 219520 |
| w4a4-m256-n128-fc1 | False | True | [3, 2] | [78, 78] | [1, 1] | 230272 |
| w4a4-m256-n128-fc2 | False | True | [3, 2] | [95, 95] | [1, 1] | 207232 |
| w4a4-m256-n256-fc1 | False | True | [3, 2] | [94, 94] | [1, 1] | 195456 |
| w4a4-m256-n256-fc2 | False | True | [3, 2] | [116, 116] | [1, 1] | 229760 |
| w4a4-m512-n128-fc1 | False | True | [3, 2] | [90, 90] | [1, 1] | 189312 |
| mxfp8-m128-n16-fc1 | True | False | [3, 1] | [72, 72] | [1, 1] | 216064 |
| mxfp8-m128-n16-fc2 | False | False | [2, 1] | [100, 100] | [1, 1] | 215936 |
| mxfp8-m128-n128-fc1 | True | True | [3, 1] | [81, 81] | [1, 1] | 136064 |
| mxfp8-m128-n128-fc2 | False | True | [2, 1] | [94, 94] | [1, 1] | 204160 |
| mxfp8-m256-n128-fc1 | False | True | [3, 2] | [83, 83] | [1, 1] | 205696 |
| mxfp8-m256-n128-fc2 | False | True | [3, 2] | [95, 95] | [1, 1] | 214528 |
| mxfp8-m256-n256-fc1 | False | True | [3, 2] | [88, 88] | [1, 1] | 206720 |
| mxfp8-m256-n256-fc2 | False | True | [3, 2] | [112, 112] | [1, 1] | 206720 |
| mxfp8-m512-n128-fc1 | False | True | [3, 2] | [86, 86] | [1, 1] | 213376 |
| w4a8-m128-n16-fc1 | True | False | [3, 1] | [72, 72] | [1, 1] | 216064 |
| w4a8-m128-n16-fc2 | False | False | [2, 1] | [100, 100] | [1, 1] | 215936 |
| w4a8-m128-n128-fc1 | True | True | [3, 1] | [81, 81] | [1, 1] | 136064 |
| w4a8-m128-n128-fc2 | False | True | [2, 1] | [94, 94] | [1, 1] | 204160 |
| w4a8-m256-n128-fc1 | False | True | [3, 2] | [83, 83] | [1, 1] | 205696 |
| w4a8-m256-n128-fc2 | False | True | [3, 2] | [95, 95] | [1, 1] | 214528 |
| w4a8-m256-n256-fc1 | False | True | [3, 2] | [88, 88] | [1, 1] | 206720 |
| w4a8-m256-n256-fc2 | False | True | [3, 2] | [112, 112] | [1, 1] | 206720 |
| w4a8-m512-n128-fc1 | False | True | [3, 2] | [86, 86] | [1, 1] | 213376 |

All variants have zero local bytes/spills. Full hashes and scope are in comparison.json. This validates the bounded source/codegen contract; timing is separate.
