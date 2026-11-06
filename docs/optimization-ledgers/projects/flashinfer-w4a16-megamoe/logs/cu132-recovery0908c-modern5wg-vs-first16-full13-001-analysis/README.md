# Complete first16 comparison

Complete same-node ec94-to-first16 source trials with identical native stack, five warpgroups/two decode groups/REG96 and unchanged graph scorer/primary CUPTI metric. First16 changes shared transform/decoder utils and the Mega kernel together; split uses the same changed shared source and retunes independently. This is a paired whole-source comparison, not an isolated pipeline-stage ablation or unchanged split control. No row minima, drift subtraction, uncertainty estimate or automatic retention decision.

control: all 13 rows, ms.

| T | Modern5WG split | Modern5WG Mega | First16 split | First16 Mega | First16 split/Mega | Mega change | Split change |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.080656 | 0.094928 | 0.067456 | 0.093536 | 0.7212x | -1.47% | -16.37% |
| 2 | 0.116624 | 0.112033 | 0.098817 | 0.119937 | 0.8239x | +7.06% | -15.27% |
| 4 | 0.127505 | 0.135777 | 0.144337 | 0.138449 | 1.0425x | +1.97% | +13.20% |
| 8 | 0.162385 | 0.158593 | 0.162321 | 0.156881 | 1.0347x | -1.08% | -0.04% |
| 16 | 0.180945 | 0.173153 | 0.168049 | 0.176033 | 0.9546x | +1.66% | -7.13% |
| 32 | 0.204002 | 0.213362 | 0.204354 | 0.216049 | 0.9459x | +1.26% | +0.17% |
| 64 | 0.240978 | 0.232706 | 0.223073 | 0.225313 | 0.9901x | -3.18% | -7.43% |
| 128 | 0.231969 | 0.245058 | 0.228897 | 0.245489 | 0.9324x | +0.18% | -1.32% |
| 256 | 0.233153 | 0.251074 | 0.244737 | 0.247858 | 0.9874x | -1.28% | +4.97% |
| 512 | 0.238689 | 0.255154 | 0.243073 | 0.253298 | 0.9596x | -0.73% | +1.84% |
| 1024 | 0.250433 | 0.265618 | 0.260674 | 0.263025 | 0.9911x | -0.98% | +4.09% |
| 2048 | 0.351634 | 0.344834 | 0.336674 | 0.344162 | 0.9782x | -0.19% | -4.25% |
| 4096 | 0.554212 | 0.509651 | 0.553940 | 0.514547 | 1.0766x | +0.96% | -0.05% |

auto: all 13 rows, ms.

| T | Modern5WG split | Modern5WG Mega | First16 split | First16 Mega | First16 split/Mega | Mega change | Split change |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.086481 | 0.087441 | 0.083600 | 0.088673 | 0.9428x | +1.41% | -3.33% |
| 2 | 0.102448 | 0.108656 | 0.098657 | 0.105440 | 0.9357x | -2.96% | -3.70% |
| 4 | 0.143441 | 0.121488 | 0.128321 | 0.128577 | 0.9980x | +5.84% | -10.54% |
| 8 | 0.156209 | 0.150577 | 0.162913 | 0.150145 | 1.0850x | -0.29% | +4.29% |
| 16 | 0.175761 | 0.162480 | 0.179377 | 0.163554 | 1.0967x | +0.66% | +2.06% |
| 32 | 0.203105 | 0.192385 | 0.200369 | 0.197809 | 1.0129x | +2.82% | -1.35% |
| 64 | 0.222610 | 0.220529 | 0.209921 | 0.221089 | 0.9495x | +0.25% | -5.70% |
| 128 | 0.234050 | 0.226257 | 0.234161 | 0.217345 | 1.0774x | -3.94% | +0.05% |
| 256 | 0.243185 | 0.226338 | 0.238337 | 0.230946 | 1.0320x | +2.04% | -1.99% |
| 512 | 0.238049 | 0.236770 | 0.236978 | 0.238594 | 0.9932x | +0.77% | -0.45% |
| 1024 | 0.260722 | 0.258385 | 0.269010 | 0.250353 | 1.0745x | -3.11% | +3.18% |
| 2048 | 0.336658 | 0.336866 | 0.345907 | 0.334706 | 1.0335x | -0.64% | +2.75% |
| 4096 | 0.557189 | 0.496995 | 0.548244 | 0.498308 | 1.1002x | +0.26% | -1.61% |

Full choices, resource observations and tactic changes are in comparison.json; all 104 literal raw values are in raw-latencies.csv.
