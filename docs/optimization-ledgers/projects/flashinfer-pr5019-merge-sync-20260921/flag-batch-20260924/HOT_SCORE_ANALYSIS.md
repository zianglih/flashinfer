# Native hot scores and repeat stability

This supplements the final cold-L2 CUPTI table. Native AUTO ranks candidates using hot CUDA-graph GPU-event scores, while the final benchmark measures cold-L2 rank-MAX CUPTI spans. Their ratios are distinct measurements. All eight non-flag candidates are unchanged; F4 and F8 may select different group sizes, tiles or return modes.

Hot ratios below use the median of the two native per-sweep scores. Each native score is the maximum across ranks of that rank's median of ten GPU-event samples. Final cold ratios use the pooled median of 200 samples. Matched-candidate hot ratios hold all non-flag knobs equal before taking the geometric mean across the eight pairs. No combined 16-candidate AUTO run was measured.

## EP4

Decode 4–512: cold F4/F8 **0.9926×**; native hot best F4/F8 **0.9998×**; all matched hot candidates **1.0001×**. Ratios above one favor F8. Tokens 1/2 are excluded from these summaries.

| Global tokens | Cold F4/F8 | Native hot best F4/F8 | Matched hot candidates F4/F8 | F8 cold s1 µs | F8 cold s2 µs | F8 s2 latency change | Non-flag winner same in s1/s2 |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 1.0119× | 1.0013× | 0.9974× | 72.1290 | 73.0090 | +1.22% | no/yes |
| 2 | 1.0168× | 0.9996× | 1.0016× | 92.2245 | 92.1615 | -0.07% | yes/no |
| 4 | 0.9804× | 1.0001× | 0.9996× | 112.3690 | 117.2165 | +4.31% | yes/no |
| 8 | 0.9750× | 0.9977× | 1.0004× | 154.2095 | 156.4180 | +1.43% | no/no |
| 16 | 0.9877× | 1.0051× | 0.9991× | 204.3860 | 203.3620 | -0.50% | yes/yes |
| 32 | 1.0063× | 0.9974× | 0.9987× | 258.6420 | 261.5230 | +1.11% | yes/yes |
| 64 | 0.9977× | 1.0028× | 1.0016× | 296.5790 | 286.3390 | -3.45% | yes/yes |
| 128 | 0.9894× | 0.9999× | 1.0007× | 322.3390 | 318.7535 | -1.11% | yes/yes |
| 256 | 1.0111× | 0.9968× | 1.0000× | 330.1145 | 321.5395 | -2.60% | yes/no |
| 512 | 0.9940× | 0.9983× | 1.0004× | 347.1230 | 337.9710 | -2.64% | yes/yes |
| 4096 | 0.9631× | 0.9459× | 0.9518× | 848.4235 | 866.0100 | +2.07% | yes/yes |
| 8192 | 0.9717× | 0.9680× | 0.9736× | 1591.4525 | 1578.2370 | -0.83% | yes/yes |
| 16384 | 0.9901× | 0.9851× | 0.9799× | 2957.4125 | 2955.5725 | -0.06% | no/yes |

Per-candidate scores and complete selected dictionaries remain in the accompanying JSON. A same-configuration cold change across repeated runs must not be presented as an isolated causal effect of flag_batch.

## EP8

Decode 4–512: cold F4/F8 **0.9877×**; native hot best F4/F8 **1.0002×**; all matched hot candidates **1.0012×**. Ratios above one favor F8. Tokens 1/2 are excluded from these summaries.

| Global tokens | Cold F4/F8 | Native hot best F4/F8 | Matched hot candidates F4/F8 | F8 cold s1 µs | F8 cold s2 µs | F8 s2 latency change | Non-flag winner same in s1/s2 |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 0.9774× | 1.0166× | 1.0097× | 75.1845 | 77.1050 | +2.55% | yes/no |
| 2 | 0.9576× | 1.0112× | 1.0088× | 98.0965 | 94.0805 | -4.09% | yes/no |
| 4 | 0.9391× | 1.0057× | 1.0059× | 98.1930 | 111.0405 | +13.08% | yes/no |
| 8 | 0.9857× | 1.0049× | 1.0034× | 122.1605 | 133.1365 | +8.98% | yes/yes |
| 16 | 0.9890× | 0.9999× | 1.0010× | 147.9845 | 145.6490 | -1.58% | yes/no |
| 32 | 1.0097× | 1.0071× | 1.0052× | 165.8895 | 163.8730 | -1.22% | no/yes |
| 64 | 0.9857× | 1.0008× | 0.9992× | 189.4255 | 195.6815 | +3.30% | yes/no |
| 128 | 0.9998× | 0.9895× | 0.9984× | 202.3845 | 198.2570 | -2.04% | yes/no |
| 256 | 1.0134× | 0.9958× | 0.9989× | 189.8730 | 199.8720 | +5.27% | no/yes |
| 512 | 0.9812× | 0.9978× | 0.9976× | 205.7300 | 204.3860 | -0.65% | yes/no |
| 4096 | 0.9374× | 0.9364× | 0.9439× | 498.2430 | 498.6430 | +0.08% | yes/yes |
| 8192 | 0.9351× | 0.9391× | 0.9453× | 828.8035 | 855.2015 | +3.19% | yes/yes |
| 16384 | 0.9796× | 0.9660× | 0.9722× | 1548.0410 | 1577.7540 | +1.92% | yes/yes |

Per-candidate scores and complete selected dictionaries remain in the accompanying JSON. A same-configuration cold change across repeated runs must not be presented as an isolated causal effect of flag_batch.

## Interpretation boundary

EP8 F8 at N8 changes from 122.1605 µs in sweep 1 to 133.1365 µs in sweep 2 with the same G1024/N64/epilogue-return tactic. N4 changes from 98.1930 µs to 111.0405 µs while group_hint also changes G512 to G1024. These repeat differences show why the initial cold gains alone do not establish a reliable F8 advantage.

The source audit gives a separate, bounded observation: N4/N8 have only 32/64 routed tokens globally at top-k8. With the measured 148-CTA grid and four dispatch warps per CTA, each pulling warp can process at most one token; neither F4 nor F8 reaches its publication threshold before tail flush. This rules out larger publication batches as the explanation for those two cold gains. It does not rule out compiler/code-layout, cache or system effects, and is not a profile identifying their cause. No exact receive-count claim is made for larger random workloads.
