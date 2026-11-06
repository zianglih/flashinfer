# C3 validation after review-test cleanup

**22 passed**, zero failures, errors, or skips. No further tests or benchmarks were run.

- Existing C3 devbox `fi-pr7290-small-w4-1103`; B300 (SM103); `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.8.0.
- Base `14a338579eb8acddcc5cfd1cc58871fc0788de22` plus the existing six-file unstaged reviewer fixes. Only the two trimmed test files changed from the prior 28-case validation; production/docs hashes match that snapshot.
- Four autotune cases: W4A4/W4A16 × legacy/swap-AB. Ten CPU guard/helper cases. Eight typed NVFP4 activation cases across both layouts.
- Normal previously qualified native caches were reused. The source overlay contains the two new test files and links to the prior validated source. No production code, compiler options, benchmarks, or earlier receipts were changed.
- Final source checks passed for both test files and the four unchanged review files. Current local test hashes still match the tested snapshot. Final GPU process list was empty.

| Job | Passed | Wall time (s) |
|---|---:|---:|
| autotune-false-w4a16 | 1 | 45.99 |
| autotune-false-w4a4 | 1 | 26.14 |
| autotune-true-w4a16 | 1 | 56.77 |
| autotune-true-w4a4 | 1 | 149.69 |
| layout-and-typed | 18 | 33.68 |

Trim archive SHA256: `b0d21b2c080c001701b74ad98f15d6210037f0e98751f75382d9b2d07d89b832`.
Fetched evidence archive SHA256: `2b7e95bff1b65c6336bb7683a54591fcff98067e737379ac49f499ee87763283`.

Raw pytest output, JUnit XML, commands, environment, source proof and launch receipts are in `evidence/`; `audit.json` verifies all 22 JUnit cases and all fetched hashes. `trimmed-tests-manifest.json` records the exact local test bytes.

Source remains local and unstaged. No commits, pushes, public writes, sanitizer, or additional performance work.
