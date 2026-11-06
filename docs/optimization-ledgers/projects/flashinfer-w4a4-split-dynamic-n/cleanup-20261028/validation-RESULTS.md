# Cleanup validation

PASS: 95 existing tests executed, with zero failures, errors, or skips.

Tested source: retained head `33b7e5260132eb4ba2fdfdd97bd71a892f04a481` plus the frozen cleanup patch `47a0ca625c8959ed7292b598bc9ea8f9b998ad9072ce5b378ed6d95503a7a8a9`. The patch remains unstaged. Both runners and the final archive check verified all 513 frozen source hashes and the exact full-index Git diff before/after. Each test group additionally recorded and rechecked 3,070 tracked Python/shell files.

Environment: existing C3 B300 devbox, requested image `nvcr.io/nvidia/pytorch:26.05-py3`; Python 3.12.3, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CUDA 13.2, CuTe DSL 4.8.0, pytest 9.1.1, TVM FFI 0.1.15.post1. Exact and API groups ran concurrently on separate physical GPUs0/1. Nine persistent native compilation-cache links were preserved.

| Group | Passed | Failed/errors/skipped | Pytest time |
|---|---:|---:|---:|
| Existing exact MoE tests | 33 | 0/0/0 | 122.35s |
| Existing API/wrapper/graph/cache tests | 62 | 0/0/0 | 94.57s |

Raw summary output:

```text
.................................                                        [100%]
33 passed, 1275 warnings in 122.35s (0:02:02)
..............................................................           [100%]
62 passed, 2406 warnings in 94.57s (0:01:34)
```

The complete test selectors are in `selection.json`; the exact executed pytest commands, environment logs, collected node IDs and JUnit files are retained under `validation-evidence/raw/validation/{exact,api}`. The frozen runner invokes those existing selectors unchanged.

Executed group-driver commands:

```bash
/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/cleanup-20261028/run_existing_tests.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/cleanup-20261028/flashinfer-candidate --commit 33b7e5260132eb4ba2fdfdd97bd71a892f04a481 --python /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python --python-deps /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps --workspace /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/cleanup-20261028/compile --gpu 0 --group exact --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/cleanup-20261028/validation/exact --image nvcr.io/nvidia/pytorch:26.05-py3
```

```bash
/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/cleanup-20261028/run_existing_tests.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/cleanup-20261028/flashinfer-candidate --commit 33b7e5260132eb4ba2fdfdd97bd71a892f04a481 --python /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python --python-deps /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps --workspace /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/cleanup-20261028/compile --gpu 1 --group api --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/cleanup-20261028/validation/api --image nvcr.io/nvidia/pytorch:26.05-py3
```

Scope: no new repository tests, sanitizer, full benchmark rerun, source commit/push, or publication. These tests qualify the frozen cleanup; existing retained benchmark evidence is not relabeled as newly timed.

Archive: `validation-evidence/evidence.tar.gz`, SHA256 `d6b98ac46c6293601e9728d2d96ded5d8f5f16c0d12b0386d5903f7ee8b85577`; 30 files verified against the archive manifest. `validation-audit.json` independently binds source, patch, test counts, cache links, GPU identities and raw logs. `validation-postflight.json` inside the archive records the final source check and idle assigned GPUs.

## Subsequent retention

The tested cleanup was subsequently retained and pushed as `d35fcfda03875077b3af8455575cc1d20e866a8c`. Its parent is the tested base33b7, and all513 frozen source files are byte-identical. The remote validation checkout now has a clean tracked tree at that commit; the nine cache links, data symlink, and all14 original validation files remain unchanged. `validation-workspace-bump.json` records the verification. This is a workspace update, not a new test run; the original test source/patch receipts above remain unchanged.
