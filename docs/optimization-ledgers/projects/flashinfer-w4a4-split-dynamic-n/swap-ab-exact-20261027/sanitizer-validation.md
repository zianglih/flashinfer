# Swap-AB sanitizer port validation — 2026-10-27

The manual harness is `scripts/sanitize_cute_dsl_moe_swap_ab.py`. It supports only
SM100/103 `swap_ab=True`, unfused execution. It is outside normal test discovery:
its filename does not match pytest's default `test_*.py` / `*_test.py`, and
`scripts/find_marked_tests.py` scans `tests` by default and accepts only
`test_*.py`. No CI wiring or pytest.ini changes were added.

## Final local source

- Harness SHA256: `36f4897e80a2bc9f351a5fad0cb490aaede7b1f93c15920c25a85cc958918299`.
- Oracle SHA256: `911951361eed612514b3fc6b55efd1233b606483152d25c66af8d2f78be4b6aa`.
- Source remains unstaged in `flashinfer-weight-layout-api-review`.
- `--quant-mode` accepts `w4a4`, `per-token`, `mxfp8`, `w4a8`, and `w4a16`.
  `per-token` explicitly maps to runtime `w4a4` with per-token activation scales;
  the other four modes explicitly disable per-token scales. Unknown modes fail.
- The old `--per-token` flag is removed. Receipts keep both the user-facing mode
  and resolved runtime quantization mode / per-token flag.

## Final script checks without GPU execution

The final harness was copied into the private `sanitizer-final-cli` directory;
the shared remote source snapshot was not modified. With GPUs hidden, explicit
pytest collection found **150 cases**, including **30 per-token cases**. Help,
all five mode mappings, unknown-mode rejection, removed-flag rejection, and
instrumented-kernel owner selection passed. Both source files also compile as
Python syntax locally. See `sanitizer-final-cli-result.json` and the complete
`sanitizer-artifacts/sanitizer-final-cli/` receipts.

## Earlier bounded GPU pilot

The pilot used the preceding harness SHA256
`b677e9d5c69a5405e82fe20f1f8babd156fc5fa4809a3ea78a9fe3b934c1e3a3`, before the
per-token CLI refactor. This is not GPU validation of the final script hash.

- Device: C3 `fi-moe-nvfp4-port-1026`, B300 SXM6 AC, GPU3.
- Python environment: CuTe DSL 4.8, PyTorch `2.12.0a0+5aff3928d8.nv26.05`,
  CUDA 13.2; Compute Sanitizer `2026.3.0.0` build `38855100`.
- Snapshot HEAD: `5ac452450f65c6cec179290a66503ae86143a13f`; frozen patch SHA256:
  `c98621c477b3bc716e4c7993df431fcd06bffd26137c1ca5d9cddc32fb8dbd48`.
- W4A16 synccheck, one local token, EP8, optimized compilation: **23/23 tactics
  passed**, each with random and skewed routing in eager and CUDA-graph modes.
  Compute Sanitizer reported `ERROR SUMMARY: 0 errors`.
- Driver wall time: 598.624 seconds. Worker time: 587.119 seconds, dominated by
  the native-routing JIT build. Full receipts are under
  `sanitizer-artifacts/sanitizer-synccheck-w4a16-t1/`.
- The GPU2 W4A4 memcheck pilot was cancelled **before tactic execution**, while
  waiting for a shared native-cache build. Only its verified process groups were
  stopped; the accuracy/benchmark build was preserved. This produces neither a
  sanitizer pass nor a sanitizer failure. See
  `sanitizer-artifacts/sanitizer-memcheck-w4a4-tensor-t1/cancelled.json`.

No full memcheck/racecheck campaign or final-script GPU rerun was performed.
The user subsequently requested skipping sanitizer runs. The external local
`moe_swap_ab_prepare.py` WIP was preserved and was excluded from this port and
the frozen pilot snapshot. The final harness hash must be included when the
parent refreshes the overall source manifest; the old remote manifest remains
an accurate record of the earlier pilot.
