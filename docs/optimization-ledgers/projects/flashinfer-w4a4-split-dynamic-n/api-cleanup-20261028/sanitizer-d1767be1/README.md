# Swap-AB sanitizer run

Requested after the cleanup benchmark/test publication. This supersedes the
previous instruction to skip sanitizers. **Complete: 150 passed, zero failures,
errors or skips; independent full audit passed.** See [RESULTS.md](RESULTS.md).

- Source: PR #7290, `d1767be1f42fdc371f90db4fb06598299ea32845`.
- Harness: tracked `scripts/sanitize_cute_dsl_moe_swap_ab.py`, unchanged.
- Hosts: C3 `fi-moe-nvfp4-port-1026` and `fi-moe-sanitize-1028`, sixteen B300 SXM6
  GPUs total. Both are retained for the subsequent TP benchmarks.
- Image: `nvcr.io/nvidia/pytorch:26.05-py3`; CUDA 13.2; Compute Sanitizer 2026.3.
- Matrix: five modes × three local token counts × ten tool/shard combinations
  = 150 pytest cases. Modes are W4A4, per-token NVFP4, MXFP8, MXFP4x8, W4A16;
  local token counts are 1, 8, 1024. Memcheck and synccheck each cover the full
  tactic catalog; racecheck divides that same catalog into eight shards.
- Each tactic runs with random and skewed routing, eager execution and CUDA
  graph replay. One active case per GPU; new cases consume a shared queue.
- Geometry is GLM-5, local emulation of EP8 (32 of 256 experts), hidden 6144,
  intermediate 2048, top-k 8. Only unfused swap-AB is covered.
- Existing harness exclusions: numerical checks, real distributed communication,
  legacy/fused finalize, strict and 4over6 quantization, and the captured initial
  quantizer-to-FC1 chain. Numerical tests are recorded in the preceding
  `full-validation/tests/RESULTS.md`.

The harness retains strict zero-warning/error acceptance, native routing filter
proof, O3/PTX compilation receipts, and requested memcheck TMEM access guards.
Instrumentation options are not reduced. The emitted SASS is not independently
checked for guard instructions. See `SCRIPT-AUDIT.md` for exact boundaries.

The remote campaign path is
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/api-cleanup-20261028/sanitizer-d1767be1`.
Source snapshot and persistent native compilation caches are shared with the
completed full validation; instrumented CuTe compilation bypasses that cache.
Each case retains command, pytest/JUnit output, worker/sanitizer logs, PTX and
coverage receipts. The queue and driver scripts are local to this effort and
are not repository or CI changes.

Read live status from the project root:

```sh
python3 swap-ab-exact-20261027/remote.py \
  api-cleanup-20261028/sanitizer-d1767be1/status.py
```
