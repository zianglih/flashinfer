# Cleaned regular-TMA validation

Validated the actual unstaged `regular-tma-review` source copy at base442,
identified by experiment manifest
`9f174d224c41b18fd59f51deb360464f70654724ed1acf91d38aa1a55fe1e1f2`.
All three changed-source hashes matched before and after every run.

| Check | Result | GPU | Wall duration |
|---|---:|---:|---:|
| Existing numerical selection | 71 passed | 4 | 23.04 s |
| Existing unfused W4A16 boundaries | 24 passed; 24 fused cases deselected | 5 | 12.18 s |
| Same 126-case probe under memcheck | 126 passed; zero errors | 6 | 79.01 s |
| Same probe under racecheck | 126 passed; zero hazards/errors/warnings | 7 | 96.28 s |
| Existing reference tests under memcheck | 3 passed; zero errors | 6 | 44.21 s |

All processes exited zero. The 95 existing tests had no failures, errors or
skips; their warnings are CuTe DSL deprecations. Compute Sanitizer2026.1.1
reported no warning, unsupported-operation, or other error diagnostics.
Memcheck used `--check-bulk-copy yes`; racecheck used
`--racecheck-memcpy-async yes --racecheck-report all`.

The frozen 126-case probe is copied byte-for-byte from the validcopy experiment;
only its adjacent source manifest and launch paths change. It includes 90
preparation graph replay checks and 36 FC1/downstream comparisons across six
operand/SF formats. This covers zero/growing/shrinking route counts, invalid
mapping poison, N16 physical padding, complete SF initialization and canaries,
N16/N128/N256 partial tiles, fused FC1 quantization, and original-token scales.
The same126 checks also passed separately before the performance campaign;
that result is archived in `evidence/regular-tma-review-exact-126`.

FC1 compares all output/SF bytes against frozen442. Downstream quantization,
FC2 and combine use the same unchanged implementation for both arms. This is
paired exact-to-control evidence, not an independent all-six-format reference
claim or a complete repository-suite run. Public per-token support remains
NVFP4-only. No new repository tests were added.

Initcheck was not requested or run. Invalid private payload is intentionally
left uninitialized by the default allocation; the poisoned checks establish
numerical isolation, not initialization safety. No error or warning is waived.

Complete logs, JUnit output, case JSON, source snapshots, environment/command
receipts and the source-pinned runner are in `raw/` and `raw.tar.gz`.
Archive SHA256:
`3efcd8791ce8f24d4a98591d92393046f0da9b375904f93f42d0ac8930a3090d`.

Raw pytest summaries:

```text
71 passed, 366 warnings in 17.49s
24 passed, 24 deselected, 400 warnings in 7.09s
3 passed, 111 warnings in 39.38s
```
