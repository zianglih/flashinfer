# Split MoE implementation simplicity

Baseline: `ed67c4857ce4e8d8cc047cf3808e2efa65e874b2`. Frozen patch: `d7cb185e35f55c39c67eb3ae0a0edaf5f9aa1838a777cdd26d6afd39bf4c1087`. Review source: `flashinfer-simplicity-review-20261027/`; seven files, +124/−217, net −93 lines.

## First cleanup scope (historical)

- Share the bulk/direct epilogue's route and rounded-scale metadata calculation. Preserve both transfer paths, output arithmetic, masks, accumulator ownership and ordering.
- Share host activation SF geometry between preparation allocation and launch.
- Centralize existing bulk-output eligibility, reuse the already computed scale-column count, keep transient accumulator layout local, remove two forwarding/dead helpers and one already-implied physical-M check. Merge adjacent identical IKET guards while preserving markers.
- Put invariant settings in the shared host launcher and remove them from its argument list and compiled cache key. Remove preparation-only state from that key. The constructed kernel receives identical explicit behavior knobs.
- Share tactic geometry dictionary construction. Keep separate `gemm1_use_clc_scheduler` and `gemm2_use_clc_scheduler` plumbing; AUTO continues to select one shared CLC flag.

The full PR was reviewed by component. Benchmark/test code, public signatures, standalone quantizer, combine, W4A16 adjustment, trace/reference, MegaMoE and Rubin remain unchanged by this cleanup. Original useful comments are preserved; only a stale cp.async role description is corrected, and helper comments disappear with the removed helper code. Broad comment trimming and scheduler-parameter merging were not retained.

## Validation

Local source-bound receipts in `scripts/simplicity_20261027/`:

- `kernel-static-equivalence.json`: 67,500 constructors, including 4,500 identical rejections and 63,000 identical storage plans. Normalized device/pipeline AST equivalence.
- `host-checks.json`: 2,176 identical tuple/JSON tactic extractions and 2,160 identical launcher configurations. Public signatures, Rubin paths, independent phase controls and tactic lists unchanged.
- `utilities-static.json`: preparation kernel AST unchanged; 51 valid SF geometries and four rejection cases.
- `benchmark-static-checks.json`: all PR-modified benchmark/test files byte-identical to baseline.
- `independent-review.md` / `.json`: no semantic, API, cache, layout or unnecessary-abstraction findings; pinned to the frozen patch and seven hashes.
- Scoped pre-commit passed, including mypy and Ruff.

GPU validation completed against a clean ed67 control on the existing c3 B300 devbox using `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2 and CuTe DSL 4.7.1. Native compilation cache reused only after all 4,389 source/artifact hashes matched; changed DSL uses private cache namespaces. The original 13 tactic and 29 capability tests pass (42 total). Output-byte, emitted-instruction and resource comparisons all passed, as recorded below.

No performance claim is made by this cleanup. The six public benchmark tables retain their original source attribution; no new timing sweep or broad sanitizer campaign is required when executable instructions and resource usage are unchanged.

## Retained first commit

Committed and pushed `1fab0dc8d9da5ac0f4ca81a9fecad7cda9e95729`. All 120 source-paired replays pass. All 60 GEMM and 22 preparation kernel pairs have identical encoded instructions, scheduling controls and resources; no spills. Both bounded IKET processes pass 16 replays each (32 total). Existing tactic/capability tests: 42 passed. No timing sweep rerun. The review copy was advanced clean to this commit and retained for the newly requested structural follow-up.

## Structural follow-up

The separate follow-up uses Rubin and Hopper kernel/utility boundaries. The grouped GEMM module now owns the unchanged epilogue class and its private helpers. Utilities retain their original primitive/reexport surface. No new file or compatibility alias is introduced.

The user prioritized a smaller review diff over cosmetic code reduction. Restore the original pipeline helpers (including `pipeline_init_wait`) and comments, tuner dictionaries, reduction helpers and benchmark-local interleave helper. Keep separate FC1/FC2 scheduler plumbing and the retained shared AUTO flag. The first cleanup's optional helper deletions and dictionary deduplication are superseded by these restorations. Existing file license headers stay unchanged, without a duplicate block.

The five-file freeze and exact move/binding/restoration proof are in `scripts/simplicity_20261027/structure/`. Scoped pre-commit passes. The bounded gate is complete: 48 exact replays, 42 existing tests and dependency import smoke pass. All 24 GEMM and eight preparation pairs have identical resources and scheduling-control words; 31 are instruction-encoding identical and one has a reviewed uniform-register descriptor-pair permutation. This exception is explicit in the receipt. No timing claim or fresh full benchmark sweep is implied.

Retained and pushed `54f5c682bbaa52a23a46b6bb76e3cfdce347ec97`. The PR diff-size table was updated and read back, preserving all existing raw benchmark tables and attribution. The completed review copy was bumped clean to that commit and removed. See `structure/retention.json`, `structure/publication.json`, and `structure/source-copy-cleanup.json`.

Next user request: inspect whether the FC1/FC2 file split itself is reasonable against Rubin/Hopper. That audit is tracked separately under `phase-boundary/`.

## Original prose and header restoration

The FC1/FC2 ownership audit found no boundary bug or cycle. Keep one shared Blackwell regular-TMA pipeline and the existing capability adapters; Rubin/Hopper have materially different gather and contiguous phase pipelines. No source change was needed for that audit.

The subsequent full-PR prose pass is retained and pushed at `2995bfda8338ca6ae623fbc2657d44e35e665627`. Twelve Python files restore accurate original wording or remove unnecessary new explanations. Existing license/copyright headers all match upstream, including the reverted year-only change in `blackwell/utils.py`. Necessary new layout, PDL, shared-CLC and quantizer contracts remain documented. The overall PR diff falls from 14,011 to 13,954 changed lines (57 fewer).

Executable AST equivalence, including type comments and type-ignore tags with source line numbers normalized, passes. Scoped pre-commit passes. No GPU or timing rerun for prose-only changes. The PR diff-size table was refreshed and read back; raw benchmark data and attribution remain unchanged. The completed review copy was bumped clean and removed; proof, patch and receipts are in `scripts/simplicity_20261027/comment-diff/`.
