# R12 shared-only relay publication code generation

Source `da060e963548bba403d4afac14e32143c0854b739c217e7028f8af3764890a9a`.
GPU4 K3 EP8 T4096 and N3U TP8 T16384 diagnostics completed with source/patch,
frozen-cache, route and tactic checks. Zero autotuning; CUPTI required.
All six compiled FC1/FC2 cubins are retained in `evidence/`.

| FC1 case | R6 → R12 GPU membars | R6 → R12 CTA membars | R6 → R12 instructions | REG | STACK | LDL/STL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| K3 EP8 MXFP4x8 T4096, two CTA | 29 → 1 | 57 → 57 | 2984 → 2936 | 81 | 0 | 0/0 |
| N3U TP8 MXFP8 T16384, one CTA | 1 → 1 | 18 → 34 | 7472 → 7512 | 168 | 208 | 26/46 |
| N3U TP8 MXFP4x8 T16384, one CTA | 1 → 1 | 18 → 34 | 7472 → 7512 | 168 | 208 | 26/46 |

K3 loses all 28 broad GPU fences from the relay. The remaining GPU fence is
outside the relay publication. The one-CTA path gains 16 CTA membars because
it previously used a CTA-scoped arrival; this is a scope-cost consideration
for matched performance data, not an automatic reason to introduce branching.
R12 does not change register allocation or spills in these cases.

FC2 resources and instruction counts match R6. K3 and N3U MXFP8 instruction
text matches exactly after removing addresses/encoding comments. MXFP4x8 has
a small uniform-register assignment difference; `4-n3u2-fc2.sass.diff` records
it, so binary identity is not claimed. Detailed counts are in `summary.json`.

The executable cubin/SASS is authoritative. Artifact PTX may be stale on CuTe
cache hits; no safety decision is based on that field. The R12 guarded test
campaign is owned by the parent; these captures are codegen diagnostics, not
additional correctness or retention results. Timing samples are excluded from
retention claims.

Archive SHA256:
`97f32812ff83c66b2721865725c8654d4d204dddbf4001146ca17f821d82b2e4`.
46 manifest entries verified after download. GPU4 was released.
