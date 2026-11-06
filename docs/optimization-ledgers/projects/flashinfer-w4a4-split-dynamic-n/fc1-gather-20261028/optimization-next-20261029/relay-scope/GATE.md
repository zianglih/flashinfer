# CTA-scoped gather relay gate

Candidate: f63e9485 plus the unstaged helper-only patch in `flashinfer-fc1-gather-relay-scope-review`. Kernel SHA `8d64a6c418f213adecce236f88e58e5ab1019667bc8eabaa432a8f707ba99087`; patch SHA `80c35c3c37fd5141c45547c1881c71dd9a624aa8d5ceec67df0acb645342821a`.

The existing helper contract receives compile-time CTA group. Group1 uses ordinary local release/acquire; group2 keeps its exact cluster assembly. Counts, relay warp, local completion wait, caller async proxy fence, PDL and stage reuse are unchanged.

Validation: 23 exact tests passed (7 existing selectors plus 16 existing local geometry cases), covering all four formats, one/two CTA, N16/N128/N256, M512 nonzero channel tiles, CLC/static, SiTU, GeGLU, per-token and partial K. All 44 executable captures have zero stack/local storage. The 14 two-CTA FC1 and 21 FC2 SASS files are byte-identical to the source-equivalent retained controls. All applicable pre-commit hooks passed; no sanitizer.

```text
23 passed, 622 warnings in 106.32s (0:01:46)
```

| Case | N / stage K | Non-NOP instructions | Branches | CTA MEMBAR sites | Async fence sites | PRMT sites |
|---|---:|---:|---:|---:|---:|---:|
| 000-fc1 | 128 / 512 | 1421 → 1417 | 103 → 103 | 4 → 3 | 8 → 7 | 9 → 8 |
| 002-fc1 | 128 / 512 | 1538 → 1534 | 104 → 104 | 4 → 3 | 8 → 7 | 3 → 2 |
| 008-fc1 | 16 / 256 | 1341 → 1337 | 57 → 57 | 3 → 2 | 5 → 4 | 15 → 14 |
| 010-fc1 | 16 / 256 | 928 → 924 | 78 → 78 | 2 → 1 | 5 → 4 | 5 → 4 |
| 011-fc1 | 128 / 512 | 1089 → 1085 | 55 → 55 | 2 → 1 | 5 → 4 | 1 → 0 |
| 028-fc1 | 256 / 256 | 5816 → 5809 | 94 → 94 | 5 → 3 | 7 → 5 | 98 → 96 |
| 030-fc1 | 256 / 256 | 5954 → 5947 | 94 → 94 | 5 → 3 | 7 → 5 | 2 → 0 |
| 032-fc1 | 256 / 128 | 5853 → 5837 | 129 → 129 | 9 → 5 | 11 → 7 | 100 → 96 |
| 034-fc1 | 256 / 128 | 5853 → 5837 | 129 → 129 | 9 → 5 | 11 → 7 | 100 → 96 |

Register allocation is unchanged in every captured kernel. No additional runtime branch is introduced. Static instruction counts are not end-to-end performance claims.

Full gate archive SHA: `4387f1eef902194d42ed85978603042c5d440f2d1b04b3847b933deaefb830fa`. Source/command/runtime receipts, exact output, generated PTX/SASS/CUBIN/ELF, and register guards are under `gate-evidence/`; the paired codegen table is reproducible with `compare_codegen.py`. The former control receipt HEAD label is older than publication, but its kernel bytes match f63 exactly; the comparison does not infer equivalence from that label.
