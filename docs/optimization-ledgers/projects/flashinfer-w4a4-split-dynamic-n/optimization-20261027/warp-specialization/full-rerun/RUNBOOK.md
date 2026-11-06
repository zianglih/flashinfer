# Full PR-table refresh with reused baselines

The retained implementation is `99f4d0c277746fb706d10a4bb303c98c5f31e0a9`.
All eight model/family groups completed their current-source AUTO, A1 and A2
phases. The user then directed baseline reuse: the supervisor stopped seven
workers only after they entered baseline-only C3 phases; K3 MX had already
completed naturally. No current phase was interrupted and no further GPU work
is required. Original receipts and unfinished baseline artifacts remain intact.

Frozen config: `0e497a5d623027316c423b02b19a62e061da6ba4bcca751f1e7d11d5a05c770b`.
The clean retained checkout has341 benchmark/source files byte-identical to the
gatedR2 implementation and one approved frontend annotation/formatting delta.
The freeze independently verified recursive bytecode equivalence, native source
hashes/cache links, and all208 reused native CuTe public selection keys. The
pilot winners remain unchanged, including negative cases. Missing W4A16/TRT
selections were filled through ordinary native AUTO; no new tactic axis exists.

## Comparison inputs

- Four models: V3 EP8, V41F EP4, K3 EP8, N3U EP8.
- All13 tokens: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`.
  Tokens1/2 remain in raw results but are excluded from the44-row views.
- Fresh candidate: this campaign's original A1/A2 pass medians, clean99f4.
  There are520 CuTe medians/52,000 samples including unchangedW4A16.
- Every baseline comes consistently from `optimization-20261027/retained-rerun`:
  TRTLLM uses its A1/A2; non-swap CuTe and pre-PR W4A16 use its C0/C3.
  The extra44×4 view compares current blockscaled formats with that campaign's
  retained1e69 current A1/A2 measurements.
- Never select between historical and newly collected controls. Fresh TRT and
  baseline-only control measurements are preserved as diagnostics, excluded
  from every comparison denominator. This is **not a fresh C-A-A-C comparison**.
- Each used timing retains10 warmups and100 cold-L2 CUDA-graph CUPTI samples,
  with fallback forbidden. Native tuning remains eagerNV/graphMX. NV includes
  the input quantizer; MX inputs are prequantized. Routes and source/backend
  contracts are verified across the selected historical and fresh inputs.
- Swap-AB is unfused; legacyMX uses fused finalize where required (`†`).
  Unsupported K3 baselines remain N/A. W4A16 is included without attributing
  performance changes to this blockscaled-kernel refactor.

`candidate-completion.json` separately proves all24 required current phases
(8AUTO +16 frozen), frozen cache identity, source/route hashes, samples and idle
GPUs. It does not rewrite original stopped-chain completion flags. The final
archive preserves both completed and stopped records. Eight native A2 CSV
blocks are kept verbatim; their newly measured TRT rows are diagnostic only.

`assemble_hybrid_results.py` validates the selected evidence and produces the
44×9 PR view and44×4 retained-head view. The existing full-table plot script
renders both with the requested red-white-green palette. No PR changes occur
until the parent reviews the verified tables, figures and provenance.

The original launch plan and commands are preserved in `INITIAL_RUN_PLAN.md`.
The unchanged original observer/assembler remain available; the original full
assembler intentionally rejects the stopped chains and is not used to publish
hybrid comparisons.

## Publication

Published the full 44×9 end-to-end table and heatmap to PR7290 at `99f4d0c27`, with exact body readback verified. Only this full end-to-end plot is included in the PR. Saved baselines are reused consistently; no further GPU runs are active. See `publication-receipt.json`, `assembled-hybrid/provenance.json`, and `plots/plot-validation.json`.
