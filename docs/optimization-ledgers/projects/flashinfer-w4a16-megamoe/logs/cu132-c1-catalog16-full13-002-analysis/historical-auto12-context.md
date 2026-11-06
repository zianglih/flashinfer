Historical auto12 versus current auto16 on the same recorded CUDA 13.2 software stack. **Different source and catalog; this is not a C1 or catalog-size ablation.**

Historical: `cu132-cross-stack-full13-001`, source `4a3716c6e6dc7f38ae84c182ffd7e06b083b4b606849031180f8939f340a8045`. Current: `cu132-c1-catalog16-full13-002`, source `250553779d5278c66794abef19696df40297d0767336e2782836298fc0a9074b`. Both use EP8 and 100 CUPTI iterations at all 13 global token counts; every selected tactic retains two transform warpgroups.

Manifest SHA-256: historical `7e26ec15893db53f71932726909cceb376a7eb358d532887efdb11aecd81fbc9`; current `a3bfcd503b84e684945cbd2d2addfbb66ef7718cf8beb4dd0ef64cd5d84393ed`. The JSON retains manifest paths, all six source-file hash changes, verified native-stack fields, and original evidence hashes.

All 26 original auto latency rows per run are preserved in JSON. Negative change below means current auto16 is faster; no rows or winners are substituted.

| Global tokens | Old split ms | Old Mega ms | New split ms | New Mega ms | Mega change | Split change | Old choice | New choice |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 0.086368 | 0.093920 | 0.076320 | 0.078849 | -16.05% | -11.63% | M256/N128, C2, F8, epi | M256/N64, C2, F8, epi |
| 2 | 0.154849 | 0.120336 | 0.116817 | 0.111169 | -7.62% | -24.56% | M256/N128, C2, F8, epi | M256/N64, C2, F4, epi |
| 4 | 0.144561 | 0.119441 | 0.127905 | 0.117873 | -1.31% | -11.52% | M256/N64, C2, F4, epi | M128/N64, C1, F4, reuse |
| 8 | 0.155057 | 0.149425 | 0.162465 | 0.156593 | +4.80% | +4.78% | M256/N64, C2, F4, epi | M128/N64, C1, F8, reuse |
| 16 | 0.180561 | 0.162817 | 0.178929 | 0.168001 | +3.18% | -0.90% | M128/N64, C2, F8, epi | M256/N64, C2, F8, reuse |
| 32 | 0.204321 | 0.192802 | 0.204545 | 0.208241 | +8.01% | +0.11% | M256/N64, C2, F8, epi | M128/N64, C1, F4, epi |
| 64 | 0.209361 | 0.240321 | 0.218737 | 0.226865 | -5.60% | +4.48% | M128/N64, C2, F8, reuse | M128/N64, C1, F8, epi |
| 128 | 0.234129 | 0.238546 | 0.233841 | 0.223873 | -6.15% | -0.12% | M256/N64, C2, F8, reuse | M256/N64, C2, F4, epi |
| 256 | 0.241922 | 0.238226 | 0.242785 | 0.230241 | -3.35% | +0.36% | M128/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 512 | 0.238370 | 0.243601 | 0.239474 | 0.234833 | -3.60% | +0.46% | M128/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 1024 | 0.259954 | 0.250818 | 0.260801 | 0.248578 | -0.89% | +0.33% | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 2048 | 0.349027 | 0.335539 | 0.350498 | 0.334978 | -0.17% | +0.42% | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse |
| 4096 | 0.551636 | 0.500723 | 0.562021 | 0.501842 | +0.22% | +1.88% | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse |

Token 32 is the clearest historical repeat hotspot: Mega +8.01% while split changes +0.11%. Tokens 8 and 16 are +4.80% and +3.18%; token 4096 is +0.22%. These are historical observations. In the separate same-source fixed-versus-auto16 comparison, token 8 is the only slower Mega row (+1.37%); split changes +5.11% between those processes.

C1 won four shapes. The following are online host scores, distinct from final CUPTI spans. Gap is best C2 minus selected C1; a zero printed gap cannot resolve the unrounded ordering.

| Global tokens | Selected C1 | C1 host us | Best C2 host us | Gap us | Best C2 choice at printed score |
| ---: | --- | ---: | ---: | ---: | --- |
| 4 | M128/N64, C1, F4, reuse | 296.5 | 300.1 | 3.6 | M256/N64, C2, F4, reuse |
| 8 | M128/N64, C1, F8, reuse | 301.3 | 303.5 | 2.2 | M256/N128, C2, F8, epi |
| 32 | M128/N64, C1, F4, epi | 310.6 | 311.5 | 0.9 | M256/N128, C2, F4, reuse |
| 64 | M128/N64, C1, F8, epi | 310.0 | 310.0 | 0.0 | M256/N64, C2, F8, epi |

All 16 catalog choices are listed below. Counts are per global shape; each shape has eight agreeing actual rank selections. All 13 returned winners match the minimum printed host score among the exact 16 candidates.

| Candidate | Winning global tokens | Shape wins | Rank selections |
| --- | --- | ---: | ---: |
| M256/N128, C2, F4, epi | — | 0 | 0 |
| M256/N128, C2, F4, reuse | 2048, 4096 | 2 | 16 |
| M256/N128, C2, F8, epi | — | 0 | 0 |
| M256/N128, C2, F8, reuse | — | 0 | 0 |
| M256/N64, C2, F4, epi | 2, 128, 1024 | 3 | 24 |
| M256/N64, C2, F4, reuse | — | 0 | 0 |
| M256/N64, C2, F8, epi | 1, 256, 512 | 3 | 24 |
| M256/N64, C2, F8, reuse | 16 | 1 | 8 |
| M128/N64, C2, F4, epi | — | 0 | 0 |
| M128/N64, C2, F4, reuse | — | 0 | 0 |
| M128/N64, C2, F8, epi | — | 0 | 0 |
| M128/N64, C2, F8, reuse | — | 0 | 0 |
| M128/N64, C1, F4, epi | 32 | 1 | 8 |
| M128/N64, C1, F4, reuse | 4 | 1 | 8 |
| M128/N64, C1, F8, epi | 64 | 1 | 8 |
| M128/N64, C1, F8, reuse | 8 | 1 | 8 |

The runs are separated in time, and split tactics retune per process. Split changes are not confidence intervals. Small online margins do not establish stable C1 superiority or nonregression. The ten-entry final capacity cache is not the 13-shape selection history; actual per-shape winners are retained. This artifact required no GPU work.
