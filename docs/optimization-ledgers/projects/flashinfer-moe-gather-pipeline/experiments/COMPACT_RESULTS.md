# Independent compact comparisons against82254e20

These are three separate source-bound experiments. They do not measure the composed source. Tokens1/2 remain in raw evidence but are excluded below. Every negative row remains in the full reports. Same-GPU C-A-A-C uses100strict-CUPTI samples per phase with frozen routes and recorded choices. The primary estimate is the geometric mean of the two phase medians.

| Experiment | Cells | GM | Negative cells |
|---|---:|---:|---:|
| FC2 writer-owned commit (R1 swap only) | 84 | +0.076% | 27 |
| W4A16 byte selector (R2) | 24 | +0.082% | 9 |
| Static SF byte selectors | 30 | -0.055% | 13 |

The original W4R1 packing experiment is superseded, not folded into the W4R2 result. The K3 EP MXFP4x8 16K losses remain unresolved (R1−4.463%,SF−3.557%); see [the complete attribution](k3-ep-mx4-prefill/INITIAL_RESULTS.md). A balanced fresh CAAC/ACCA diagnostic is prepared, and the composed full matrix is held until review.

The results support considering concise instruction cleanup, not a broad throughput claim. Source complexity and persistent regressions still govern retention. “Tight” below means both observed two-phase median spreads≤0.5%; it is descriptive and does not establish statistical confidence.

## FC2 writer-owned commit (R1 swap only)

![FC2 writer-owned commit (R1 swap only)](../plots/compact-round1/r1-swap.png)

[All raw phases and cell values](../evidence/r1-compact/1793358417877966000/report/table.md) · [all group summaries](../evidence/r1-compact/1793358417877966000/report/groups.md) · [clock quartiles](../evidence/r1-compact/1793358417877966000/report/clock-quartiles.json)

| Model | EP/TP | Mode | T4 | T512 | T16384 | GM |
|---|---|---|---:|---:|---:|---:|
| kimi-k3 | ep | CuteDSL MXFP4x8 | +0.113% | +0.136% | -4.463% | -1.429% |
| kimi-k3 | ep | CuteDSL PER-TOKEN | +0.230% | +0.110% | -0.605% | -0.089% |
| kimi-k3 | ep | CuteDSL W4A4 | -0.455% | -0.069% | +0.202% | -0.108% |
| kimi-k3 | tp | CuteDSL MXFP4x8 | +0.056% | +0.041% | +0.091% | +0.063% |
| kimi-k3 | tp | CuteDSL PER-TOKEN | -0.198% | +0.181% | +0.115% | +0.032% |
| kimi-k3 | tp | CuteDSL W4A4 | +0.279% | +0.045% | +0.525% | +0.283% |
| nemo3-ultra | ep | CuteDSL MXFP4x8 | +0.067% | +0.017% | +1.155% | +0.412% |
| nemo3-ultra | ep | CuteDSL MXFP8 | +0.137% | -0.060% | +4.041% | +1.355% |
| nemo3-ultra | ep | CuteDSL PER-TOKEN | +0.080% | +0.086% | +0.017% | +0.061% |
| nemo3-ultra | ep | CuteDSL W4A4 | +1.069% | +0.103% | -0.069% | +0.367% |
| nemo3-ultra | tp | CuteDSL MXFP4x8 | -0.100% | +0.006% | +1.923% | +0.605% |
| nemo3-ultra | tp | CuteDSL MXFP8 | +0.091% | +0.059% | +0.931% | +0.360% |
| nemo3-ultra | tp | CuteDSL PER-TOKEN | +0.107% | +0.023% | +0.002% | +0.044% |
| nemo3-ultra | tp | CuteDSL W4A4 | -0.019% | +0.031% | +0.081% | +0.031% |
| v3 | ep | CuteDSL MXFP4x8 | -0.107% | +0.005% | +2.191% | +0.691% |
| v3 | ep | CuteDSL MXFP8 | +0.046% | +0.170% | +0.018% | +0.078% |
| v3 | ep | CuteDSL PER-TOKEN | +0.372% | +0.092% | +0.053% | +0.172% |
| v3 | ep | CuteDSL W4A4 | +0.088% | -0.011% | +0.146% | +0.074% |
| v3 | tp | CuteDSL MXFP4x8 | -0.307% | +0.137% | -0.686% | -0.286% |
| v3 | tp | CuteDSL MXFP8 | -0.035% | +0.226% | -0.133% | +0.019% |
| v3 | tp | CuteDSL PER-TOKEN | +0.199% | -0.114% | +0.150% | +0.078% |
| v3 | tp | CuteDSL W4A4 | +0.114% | -0.075% | +0.035% | +0.025% |
| v41-flash | ep | CuteDSL MXFP4x8 | +0.071% | -0.066% | +0.344% | +0.116% |
| v41-flash | ep | CuteDSL MXFP8 | -0.083% | -0.028% | -1.459% | -0.526% |
| v41-flash | ep | CuteDSL PER-TOKEN | +0.147% | +0.068% | -0.289% | -0.025% |
| v41-flash | ep | CuteDSL W4A4 | +0.100% | +0.013% | -0.858% | -0.249% |
| v41-flash | tp | CuteDSL PER-TOKEN | -0.019% | -0.031% | -0.042% | -0.031% |
| v41-flash | tp | CuteDSL W4A4 | +0.093% | -0.067% | +0.090% | +0.039% |

| Tight negative cell | Change | C spread | A spread |
|---|---:|---:|---:|
| kimi-k3 EP8 CuteDSL W4A4 T4 | -0.455% | 0.126% | 0.345% |
| v3 TP8 CuteDSL MXFP4x8 T4 | -0.307% | 0.000% | 0.173% |
| v41-flash EP4 CuteDSL PER-TOKEN T16384 | -0.289% | 0.303% | 0.123% |
| kimi-k3 TP8 CuteDSL PER-TOKEN T4 | -0.198% | 0.067% | 0.067% |
| v3 TP8 CuteDSL PER-TOKEN T512 | -0.114% | 0.039% | 0.219% |
| v3 EP8 CuteDSL MXFP4x8 T4 | -0.107% | 0.035% | 0.108% |
| nemo3-ultra TP8 CuteDSL MXFP4x8 T4 | -0.100% | 0.360% | 0.080% |
| v41-flash EP4 CuteDSL MXFP8 T4 | -0.083% | 0.068% | 0.033% |
| v3 TP8 CuteDSL W4A4 T512 | -0.075% | 0.176% | 0.218% |
| kimi-k3 EP8 CuteDSL W4A4 T512 | -0.069% | 0.072% | 0.010% |
| nemo3-ultra EP8 CuteDSL W4A4 T16384 | -0.069% | 0.086% | 0.164% |
| v41-flash TP4 CuteDSL W4A4 T512 | -0.067% | 0.089% | 0.074% |
| v41-flash EP4 CuteDSL MXFP4x8 T512 | -0.066% | 0.038% | 0.005% |
| nemo3-ultra EP8 CuteDSL MXFP8 T512 | -0.060% | 0.227% | 0.067% |
| v41-flash TP4 CuteDSL PER-TOKEN T16384 | -0.042% | 0.033% | 0.027% |
| v3 TP8 CuteDSL MXFP8 T4 | -0.035% | 0.037% | 0.104% |
| v41-flash TP4 CuteDSL PER-TOKEN T512 | -0.031% | 0.024% | 0.086% |
| v41-flash EP4 CuteDSL MXFP8 T512 | -0.028% | 0.018% | 0.039% |
| nemo3-ultra TP8 CuteDSL W4A4 T4 | -0.019% | 0.039% | 0.000% |
| v41-flash TP4 CuteDSL PER-TOKEN T4 | -0.019% | 0.078% | 0.039% |

Campaign audit: 72,000 samples, 1232 loaded zero-LOCAL kernels, 126/2880 observed clock/reason exceptions and 0 missing quartiles. The R1 counts include its superseded W4R1 raw rows; the table above excludes them.

## W4A16 byte selector (R2)

![W4A16 byte selector (R2)](../plots/compact-round1/r2-w4.png)

[All raw phases and cell values](../evidence/r2-w4-compact/1793358674260664000/report/table.md) · [all group summaries](../evidence/r2-w4-compact/1793358674260664000/report/groups.md) · [clock quartiles](../evidence/r2-w4-compact/1793358674260664000/report/clock-quartiles.json)

| Model | EP/TP | Mode | T4 | T512 | T16384 | GM |
|---|---|---|---:|---:|---:|---:|
| kimi-k3 | ep | CuteDSL W4A16 | +0.083% | +0.123% | -0.166% | +0.013% |
| kimi-k3 | tp | CuteDSL W4A16 | -0.064% | +0.092% | +0.042% | +0.023% |
| nemo3-ultra | ep | CuteDSL W4A16 | -0.178% | +0.639% | -1.333% | -0.294% |
| nemo3-ultra | tp | CuteDSL W4A16 | +0.345% | -0.244% | +0.566% | +0.222% |
| v3 | ep | CuteDSL W4A16 | -0.153% | +0.175% | -1.130% | -0.371% |
| v3 | tp | CuteDSL W4A16 | +0.348% | +0.299% | +1.276% | +0.640% |
| v41-flash | ep | CuteDSL W4A16 | +0.555% | -0.005% | -0.610% | -0.021% |
| v41-flash | tp | CuteDSL W4A16 | +0.306% | +0.350% | +0.694% | +0.450% |

| Tight negative cell | Change | C spread | A spread |
|---|---:|---:|---:|
| nemo3-ultra TP8 CuteDSL W4A16 T512 | -0.244% | 0.127% | 0.055% |
| kimi-k3 TP8 CuteDSL W4A16 T4 | -0.064% | 0.128% | 0.385% |
| v41-flash EP4 CuteDSL W4A16 T512 | -0.005% | 0.061% | 0.051% |

Campaign audit: 16,000 samples, 276 loaded zero-LOCAL kernels, 77/640 observed clock/reason exceptions and 0 missing quartiles. These audit counts cover only the W4 R2 campaign.

## Static SF byte selectors

![Static SF byte selectors](../plots/compact-round1/static-sf.png)

[All raw phases and cell values](../evidence/static-sf-compact/1793358674260782000/report/table.md) · [all group summaries](../evidence/static-sf-compact/1793358674260782000/report/groups.md) · [clock quartiles](../evidence/static-sf-compact/1793358674260782000/report/clock-quartiles.json)

| Model | EP/TP | Mode | T4 | T512 | T16384 | GM |
|---|---|---|---:|---:|---:|---:|
| kimi-k3 | ep | CuteDSL MXFP4x8 | +0.414% | -0.070% | -3.557% | -1.087% |
| kimi-k3 | tp | CuteDSL PER-TOKEN | +0.151% | +0.145% | -0.070% | +0.075% |
| nemo3-ultra | ep | CuteDSL W4A4 | +0.118% | -0.097% | +0.334% | +0.118% |
| nemo3-ultra | tp | CuteDSL MXFP4x8 | +0.564% | -0.320% | +0.028% | +0.090% |
| nemo3-ultra | tp | CuteDSL MXFP8 | -0.076% | -0.259% | +0.806% | +0.156% |
| v3 | ep | CuteDSL W4A4 | +0.142% | -0.027% | -0.251% | -0.045% |
| v3 | tp | CuteDSL MXFP4x8 | +0.067% | +0.286% | -0.562% | -0.070% |
| v3 | tp | CuteDSL MXFP8 | +0.161% | +0.420% | +0.134% | +0.238% |
| v41-flash | ep | CuteDSL PER-TOKEN | +0.147% | -0.007% | -0.239% | -0.033% |
| v41-flash | tp | CuteDSL W4A4 | -0.024% | +0.027% | +0.031% | +0.011% |

| Tight negative cell | Change | C spread | A spread |
|---|---:|---:|---:|
| nemo3-ultra TP8 CuteDSL MXFP4x8 T512 | -0.320% | 0.032% | 0.032% |
| nemo3-ultra TP8 CuteDSL MXFP8 T512 | -0.259% | 0.014% | 0.006% |
| v3 EP8 CuteDSL W4A4 T16384 | -0.251% | 0.083% | 0.049% |
| v41-flash EP4 CuteDSL PER-TOKEN T16384 | -0.239% | 0.023% | 0.481% |
| nemo3-ultra EP8 CuteDSL W4A4 T512 | -0.097% | 0.264% | 0.228% |
| nemo3-ultra TP8 CuteDSL MXFP8 T4 | -0.076% | 0.335% | 0.242% |
| kimi-k3 TP8 CuteDSL PER-TOKEN T16384 | -0.070% | 0.070% | 0.053% |
| kimi-k3 EP8 CuteDSL MXFP4x8 T512 | -0.070% | 0.029% | 0.063% |
| v3 EP8 CuteDSL W4A4 T512 | -0.027% | 0.054% | 0.172% |
| v41-flash TP4 CuteDSL W4A4 T4 | -0.024% | 0.000% | 0.048% |
| v41-flash EP4 CuteDSL PER-TOKEN T512 | -0.007% | 0.025% | 0.020% |

Campaign audit: 12,000 samples, 236 loaded zero-LOCAL kernels, 21/480 observed clock/reason exceptions and 0 missing quartiles. These audit counts cover only the static-SF campaign.

Compact plot color range is clipped at±2%, but printed values are not. Asterisk marks either arm’s repeat spread>1%; these cells are retained, not filtered. Historical TRTLLM/non-swap results are reused only for the eventual final table and are not controls in these experiments.
