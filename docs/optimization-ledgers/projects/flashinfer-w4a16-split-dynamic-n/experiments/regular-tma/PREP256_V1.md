# W4A16 regular-TMA permutation candidate

Baseline `36740c36a32a6c6d1c7d8162823fe823912de741`. The independent `flashinfer-regular-tma` checkout contains the unstaged implementation. `candidate-prep256-v1.patch` and `prep256-v1/manifest.json` pin the two-file snapshot.

The launcher replaces its native `moe_permute` call with a W4A16-only CuTe permutation. Every other launcher expression is AST-identical, and the GEMM kernel, original 23 tactics, FC2, combine, workspace ownership and tests are unchanged. The original Gather4 checkout is untouched.

The preparation kernel preserves native permutation semantics: each persistent CTA owns one routed row at a time, checks that row against its route tile's boundary, and copies only valid rows from `mapping[row] // top_k`. Invalid rows and unused capacity remain untouched. No numerical conversion or arithmetic is applied to activation payloads; copies use unsigned 32-bit storage words.

- Top-k, row width, route tile, vector width, grid and PDL are compile-time constructor constants. The compiled entrypoint takes five pointers and a stream; no runtime divisor argument is present.
- The fast path uses 256-bit copies when source, destination and row bytes are 32-byte aligned. An explicit 128-bit branch retains the native 16-byte alignment contract for offset views. Unsupported alignment below 16 bytes raises explicitly; the native implementation also unconditionally requires that alignment for its 128-bit vectors.
- One CTA has 128 threads. The persistent grid is bounded by routed capacity and `SM_count * floor(max_threads_per_SM / 128)`. This follows #7290's thread-capacity approach without introducing a workload cutoff. Actual registers and occupancy remain to be checked from compiled evidence.
- PDL waits before reading route metadata and signals dependents after copying. Host code reads the current CUDA stream per call, including graph capture.

Read-only sources used: the latest #7290 `flashinfer/fused_moe/cute_dsl/blackwell/moe_prepare.py` in the neighboring `flashinfer-w4a4-split-dynamic-n/flashinfer` checkout, its `scripts/fc1_regular_tma_experiment/GRID_PREPARATION.md`, and the baseline native `csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu`. The retained #7290 preparation uses 256-bit valid-row copies; its activation-scale-factor zeroing does not apply to BF16 W4A16.

Passed local checks: Ruff format/check, Python compilation, whitespace check, reverse patch application, and launcher AST scope check. GPU correctness, generated vector instructions, occupancy and benchmark outcomes are pending root-owned validation using existing bit-exact coverage. No dedicated test was added.
