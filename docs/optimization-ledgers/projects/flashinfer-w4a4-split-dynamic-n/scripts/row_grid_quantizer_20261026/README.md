# Resource-bounded grid for per-token quantization

Independent unstaged source `flashinfer-row-grid-20261026`, built on the frozen count-only `flashinfer-route-count-20261026` change. Runtime performance control is the count-only source, not0def, so this experiment isolates traversal and its effect on initial quantization. The backend arithmetic and core GEMMs are unchanged.

The per-token quantizer caps its grid at SM count times the existing minimum CTA residency budget,1024threads divided by CTA width. It then strides rows by actual grid size through the padded runtime live count. This applies uniformly to initial and intermediate quantization. The existing CTA-width policy remains unchanged. No new dtype/model/dimension/tactic conditions or user-facing tuning knobs are introduced.

PDL wait, ancestor publication and startup signal occur once perCTA before the loop. The device live-row count is read once perCTA after waiting. Every row iteration ends in a CTA barrier before shared reduction scratch is reused: `block_reduce` has a write→read barrier but no read→next-write barrier. The existing per-row arithmetic, K fallback, SF layouts and zero padding remain unchanged. Dynamic count zero still executes startup PDL publication but no row body.

A source-paired task-local gate uses the same scripted inputs on count-only and row-grid sources. It checks124 direct quantizer graph replays per source across BF16/FP16, all SF layouts, changing live lengths, PDL, multi-row CTA reuse and a default two-pass fallback at K65552. It also checks80 public wrapper graph replays per source across one/twoCTA, N16..256, CLC/static, PDL and SwiGLU/SiTU, with changing data/routes including zero local work. It compares saved output byte hashes across sources and adds no upstream tests. Scoped pre-commit passed before GPU execution.

Performance uses the same saved native public tactics, source-private DSL caches with proven-identical native C++ reuse,10warmup/100cold-L2 CUDA-graph CUPTI samples, input quantization included, no fused finalize. Candidate and count-only control remain source-pinned and unstaged throughout the screen.

The paired gate passed408 graph replays in total (124 direct +80 chain per source), with all saved output byte hashes identical. Both the register-resident path and the default wide-row two-pass fallback passed. The measured source remains byte-identical to `source.json`; its full0def patch SHA256 is `b4c3860c44b0cc5e3502fe76e9774708eac535e29921884b8d9d290aa03ece49`.

Fixed native-tactic CAAC completed all three models on c3 B300 GPU0, with initial quantization included. Ratios below are count-only / count-plus-grid, so they isolate this second step rather than comparing against0def:

|Model|T32|T128|T4096|T8192|
|---|---:|---:|---:|---:|
|V3|0.99791|1.00240|1.15047|1.12552|
|V41-Flash|1.01800|1.00554|1.04996|1.06767|
|Kimi K3|1.01134|1.01038|1.11850|1.15520|

Both candidate repeats agree closely. Every run verified the source bytes, immutable native tactic cache, identical routing identities, exact100-sample timer vectors and median agreement. All final receipts are complete. Full four-arm medians, raw vectors, source/cache/probe receipts and exact commands are in `results/row-grid`; `summary.json` is a compact derived view. This is strong bounded retention evidence, but final combined native-AUTO full-grid validation remains the parent task's responsibility. No commits, pushes or canonical-source edits were made by this experiment.

Narrow review points:

- Live count is read after the PDL dependency wait; startup signal remains once perCTA outside the row loop. Count-zero executes no row body but still publishes PDL startup.
- The prefix includes all actual expert-tile padding. SF slots through the final128/8/1-row atom are initialized, while unused capacity beyond that atom is not consumed. Output buffer shapes and public MoE workflow stay unchanged.
- The grid cap and compiler minimum-residency hint share the existing1024-thread budget. The runtime loop uniformly covers every padded live row exactly once for any SM count and CTA width; no model/dtype/tiler thresholds were added.
- End-row synchronization protects reuse of `block_reduce` scratch. Its existing barrier orders writes before readers, so a second barrier is required before the next row can overwrite it.
- Most of the300-line quantizer diff is indentation of the unchanged row body into the loop. No arithmetic, pointer-width, register-resident fallback or4over6 ordering changes accompany traversal. The large default two-pass fallback was included in the source-paired gate.
