# Full PR audit and cleanup — 2026-10-26

Subsequently committed and pushed as `6c3fdea87500227a66c7b8ed3cdcd2127c43293b`,
archived with the full PR history, then included in rebased squash `24da0138`.
The following records the original audit state; see
[rebase evidence](../rebase-20261026/README.md) for the current source.

Reviewed all 22 paths in PR #7290 against merge base
`a65d5b09e7e4c4c5c160b0161c48becd100b3970`. The canonical checkout and upstream
branch remain at `74388819899d0abfd1a12102f7cc108bda13c812`. Code changes are
unstaged in `../flashinfer-generality-review`.

## Fixes and tightening

- **Trace reference:** undo 6-D MMA scale layout for every supported format,
  reinterpret NV E4M3 scale bytes, normalize the trailing-singleton activation
  scale view, and undo gated rows through the same architecture/layout helper
  used by weight preparation. Previously NVFP4 and W4A16 used the generic
  dequantizer directly on MMA scales and left gated rows interleaved. This is
  the approximate tracing reference, separate from the shared bit-exact W4A16
  test reference.
- **Benchmark state:** copy the default model dataclass so programmatic TP
  runs cannot mutate the V3 preset. Keep initial input quantization opt-in.
- **Reuse:** replace two local weight-interleave copies with the existing
  shared helper; remove a duplicate dominated MXFP8 import.
- **Dead code/docs/tests:** remove two unused Blackwell reduction helpers,
  correct stale PDL/CTA/dtype descriptions, and simplify equivalent legacy
  tactic assertions. No new test files or extra GPU cases.

The kernel audit covers resource planning, layout ownership, TMA, MMA, PDL,
CLC, barriers, epilogues, prepare/combine, and the shared W4A16 and quantizer
changes. Host review covers public function/wrapper dispatch, preparation,
private tactic parsing/cache specialization, and benchmark integration.
Remaining geometry/format branches and performance-policy boundaries are
classified in [kernel.md](kernel.md). No model/hidden/intermediate/expert-size
whitelist was found in the shared GEMM planner or weight-prefetch path.
Existing narrow bulk-output and mixed-output coverage boundaries are retained;
the audit does not relabel them as hardware restrictions.

## Validation

- All 22 PR files parse; module/class callable argument lists are unchanged
  from retained HEAD. See [source-checks.json](source-checks.json).
- All 64 active compiled-method ASTs are unchanged. Whole kernel modules
  differ only by the dead helpers, comments/docs and one rejection message.
  See [kernel-static-checks.json](kernel-static-checks.json).
- 32 CPU Torch preprocessing regressions pass, including actual strided MMA
  scales, Blackwell/Rubin gated layouts, NV byte/FP8 scale views, per-token
  scaling, and preservation of both MX modes. The architecture query is
  stubbed; CUDA is never initialized. See [tests.md](tests.md).
- Twelve existing host tactic checks pass, including all 360 roundtrips;
  the 68 focused GPU test selectors/decorators are unchanged.
- Benchmark checks pass: 64 permutation cases, 24 byte-identical table
  renderings, 27 CLI cases, and a repeated-TP preset-mutation regression.
  See [benchmark.md](benchmark.md).
- Scoped pre-commit and `git diff --check` pass. No GPU benchmarks,
  sanitizer work, emitted-code identity, or new performance gains are claimed.

**Existing limitation identified:** the CuTe trace reference's standalone
source export already fails on unresolved default globals and missing helper
registration; its shared SiTU helper also uses a package-relative import.
This cleanup fixes in-process preprocessing, not the separate standalone
export mechanism. The before/after check is in
[trace-independent-review.json](trace-independent-review.json). Fixing export
without duplicating shared contracts should be a separate focused change.

## PR body update

Published only the requested component line-count table, before the existing
speedup table. The current pushed PR has **+5,816 / −8,068, net −2,252 lines**.
Every changed file is assigned exactly once, totals match GitHub, and all prior
body content (including the six raw benchmark outputs) is byte-preserved.
The unstaged cleanup is deliberately excluded from those published counts.

Reproduce the breakdown with `python3 audit-final-cleanup/update_pr_line_counts.py`.
[line-counts.json](line-counts.json) records file-to-component mapping and
before/after body hashes; [pr-publication.json](pr-publication.json) verifies
the exact remote body and unchanged branch head. No PR comment was posted.
