# Cleanup validation results

All **106 existing tests passed** on `d1767be1f42fdc371f90db4fb06598299ea32845`:
95 pytest cases and 11 Linux CI compile-cache unit tests. No failures, errors, or
skipped pytest cases. No repository test was added for this validation.

| Suite | GPU | Passed | Runtime |
|---|---:|---:|---:|
| Relevant MoE accuracy | 6 | 33 | 122.48 s |
| Legacy/swap-AB wrapper, unified API, scoped autotuner and policy | 7 | 62 | 71.48 s |
| Linux CI compilation-cache lifecycle | CPU | 11 | 5.169 s |

Environment: 2 × NVIDIA B300 SXM6 AC, CUDA 13.2, image
`nvcr.io/nvidia/pytorch:26.05-py3`, PyTorch `2.12.0a0+5aff3928d8.nv26.05`,
CuTe DSL `4.8.0`, Python `3.12.3`, pytest `9.1.1`, TVM FFI `0.1.15.post1`.
The GPU tests ran concurrently on GPUs 6–7; benchmark work used the other GPUs.
This is correctness validation, not performance timing evidence.

The selected 72 MoE cases cover W4A4/per-token/MXFP8/MXFP4x8 swap-AB,
W4A16 old/new layouts, strict/fast quantization recipes, K tails, one/two CTA
MX tactics, all supported activation types, eight legacy/swap-AB wrapper modes
in eager and CUDA graph execution, unified typed activation, and legacy W4A8
fused APIs. Swap-AB cases use their existing exact reference checks; legacy
controls retain their existing tolerance. The 23 autotuner tests include both
real GPU strict/non-strict replay and graph-capture modes, CPU context isolation,
fresh-process cache hydration, and measurement-policy identity/override cases.

Sanitizer was explicitly skipped. This focused selection does not qualify all
tactics or Rubin. Existing historical 176-replay kernel gates are separate;
they were not relabeled as tests of this commit.

## Source and result evidence

- Shared benchmark/test snapshot receipt: [`../source.json`](../source.json),
  SHA256 `4315d60d71f89f8cd67d02a23188488718244251f0f7bf37be832fe2046bc835`.
- Source checked clean and exact HEAD before/after each suite. 3070 relevant
  tracked source/test/CI files were hashed, rechecked after execution, and matched
  the canonical local source on fetch. Native compilation caches were retained.
- [`selection.json`](selection.json) lists every pytest selector; runtime
  collection matched the expected counts exactly. [`run_existing_tests.py`](run_existing_tests.py)
  records full commands, package paths, telemetry, and source hashes.
- [`evidence/gpu6-exact/receipt.json`](evidence/gpu6-exact/receipt.json) and
  [`evidence/gpu7-api/receipt.json`](evidence/gpu7-api/receipt.json) bind both results
  to the commit, runner/selection hashes, environment, and JUnit output.
- [`evidence/fetch-hashes.json`](evidence/fetch-hashes.json) records SHA256 for all
  19 fetched evidence files. JUnit contains 33 and 62 passing cases with zero
  failures/errors/skips. Linux unittest exited 0 with all 11 cases passing.

## Raw output

```text
.................................                                        [100%]
33 passed, 1287 warnings in 122.48s (0:02:02)
..............................................................           [100%]
62 passed, 2424 warnings in 71.48s (0:01:11)
```

Linux command: `python3 -m unittest discover -s ci/tests -p test_compile_cache.py -v`.

```text
test_disk_pressure_and_stale_image_eviction (test_compile_cache.CompileCacheTest.test_disk_pressure_and_stale_image_eviction) ... ok
test_docker_failure_preserves_exit_status_and_prunes (test_compile_cache.CompileCacheTest.test_docker_failure_preserves_exit_status_and_prunes) ... ok
test_failed_pull_does_not_run_or_mutate_cache (test_compile_cache.CompileCacheTest.test_failed_pull_does_not_run_or_mutate_cache) ... ok
test_invalid_configuration_disables_caching (test_compile_cache.CompileCacheTest.test_invalid_configuration_disables_caching) ... ok
test_opt_out_and_cpu_mode (test_compile_cache.CompileCacheTest.test_opt_out_and_cpu_mode) ... ok
test_private_entrypoint_preserves_timestamps_and_command_status (test_compile_cache.CompileCacheTest.test_private_entrypoint_preserves_timestamps_and_command_status) ... ok
test_pruning_retains_content_keyed_objects (test_compile_cache.CompileCacheTest.test_pruning_retains_content_keyed_objects) ... ok
test_pulled_image_identity_isolates_rebuilt_tags (test_compile_cache.CompileCacheTest.test_pulled_image_identity_isolates_rebuilt_tags) ... ok
test_read_only_jobs_preserve_seed_and_cleanup_on_success_or_failure (test_compile_cache.CompileCacheTest.test_read_only_jobs_preserve_seed_and_cleanup_on_success_or_failure) ... ok
test_runner_eviction_cannot_remove_another_runners_cache (test_compile_cache.CompileCacheTest.test_runner_eviction_cannot_remove_another_runners_cache) ... ok
test_same_runner_is_locked_across_eviction_and_execution (test_compile_cache.CompileCacheTest.test_same_runner_is_locked_across_eviction_and_execution) ... ok

----------------------------------------------------------------------
Ran 11 tests in 5.169s

OK
```
