# PR7290 rebased scope audit and benchmark refresh

Starting PR head: `24da0138fd67dc7172ef3dd9e6d1358e2b059a53`.
Upstream parent: `215f83cb27e39b6b973c0691b93fc378a53a10e4`.
Final source: `65c2c5c4635257d920ddb7524096f2e67bfcc9e3`, one commit, pushed with an explicit lease against measured `eb141478505103f4bc65d10fb655f3deb3cd71dc`. The pre-squash archive branch/tag is unchanged.

## Audit

- Restore upstream diagnostic ordering, shared MX scale validation and weight dtype inference. The latter restores rejection of FP8 weights paired with FP4 activations.
- Reuse upstream MX quantizer defaults; retain only the necessary Blackwell gated layout difference.
- Restore upstream localized Rubin calls and Rubin rejection tests. Rubin kernels and tactics remain unchanged. Restore public two-CTA GEMM defaults so omitted Rubin cluster settings retain upstream behavior. Scope the stronger global-scale validation to Blackwell.
- Drop the unrelated zero-quota autotune sampler fix and its added test, inheriting the upstream sampler and its tracked TRTLLM behavior. New timings therefore supersede historical tables.
- Reuse the existing MXFP8 trace dequantization helper. Benchmark executable source is unchanged from the rebased starting head.

Detailed audits and scoped validation: [host.md](host.md), [kernel.md](kernel.md), [bench-tests.md](bench-tests.md), [precommit.log](precommit.log). Full PR diff is 24 files, +5583/-7935 (net -2352).

## GPU environment and completed measurements

Fresh dedicated c2 B300 devbox `fi-moe-rebase-audit-1026`, namespace `ziangli`, host `hu-pdx-47`; 8 GPUs, no size override. Requested with managed `/usr/local/bin/h`, `--bare` and explicit `nvcr.io/nvidia/pytorch:26.05-py3`.
The live NVIDIA NGC catalog and release26.06 support matrix were checked immediately before requesting it: 26.05 is the newest CUDA13.2 container; 26.06 moves to13.3. Runtime matches historical campaign: PyTorch2.12/CUDA13.2 and CuTeDSL4.7.1. Exact runtime versions are in the fresh campaign receipts.

Persistent Python dependencies are reused, but rebased csrc/include point into the measured checkout. Only exact unchanged CUTLASS/CCCL/spdlog header revisions are reused. All source hashes are verified. Native compilation artifacts from the stopped initial audit run are reused only after exact native source equality; DSL caches remain source-specific and fresh. No AUTO result file is reused. The initial 3c0 campaign was stopped before any token row completed after the final omitted-geometry Rubin default check found a compatibility issue; only final eb141478 results will be published.

Six public benchmark tables completed successfully with existing `scripts/generality_audit/launch_screen.py`: V3 EP8, V4.1-Flash EP4, KimiK3 EP8; NVFP4 on GPUs2/3/4, MXFP on GPUs5/6/7. One process/GPU, independent model/family jobs. Native AUTO, PDL, 10 warmups/100 cold-L2 CUDA-graph CUPTI iterations; deterministic CuTe finalize/native TRT finalize. NV initial quantization included; MX prequantized. Tokens1/2 included in output and excluded from retention decisions. No before/after source baseline rerun; TRTLLM is the performance baseline.

Focused GPU checks passed on GPU0: **71 passed, 0 failures/errors/skips, 302 warnings in 448.90s**. These cover the previous focused selectors minus unrelated sampler coverage, plus the complete upstream MXFP8 test file adapted for replacement M256/M512 channel geometry. [Raw outputs](../evidence/rebased-audit-eb141478-tests/raw/) and the [fetch/source receipt](../evidence/rebased-audit-eb141478-tests/fetch-receipt.json) preserve the executed command and verify the remote checkout is still clean at `eb141478` with all 87 source pins unchanged.

## Final restoration and publication

The final user-directed restoration returns both surviving Rubin tails, including `a_per_token_scale_ptr` creation/forwarding, to upstream setup. Factory signatures/cache and launch forms remain upstream-compatible; no stale Blackwell kernel constructor or fallback returned. All six public wrapper signatures/defaults now match upstream. [Restoration proof](rubin-scope-restoration/proof.json) binds clean final `65c2c5c4` to measured `eb141478`: exact Blackwell reachable statements, unchanged device source/64 active functions, 544 upstream Rubin factory comparisons, and explicit benchmark geometry. [Final scoped hooks](final-static.json) pass over all24 changed files.

All six measured-eb outputs were fetched and hash-verified: 78 token rows, 377 latency cells, 208 public ratio cells. [Raw tables and PR body](pr-body.md), [summary](benchmark-summary.md), [source/format verification](body-receipt.json), and [byte-exact GitHub readback](publication.json). The measured commit is retained in the fork tag `archive/pr7290-benchmark-20261026`; the original pre-squash archive is unchanged. Both local source checkouts are clean and synchronized at the final pushed commit. No timing or GPU-test result is relabeled as measured on final65c2c5c4.
