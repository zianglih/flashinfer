# PR7290 retained-source performance refresh

Preparation only, 2026-10-30. No source change, GPU launch, asset upload, or GitHub write by this audit. The saved upstream body is `pr7290-before.json`; it records ready/open PR7290 at82254e20, targetingmain from `codex/w4a4-split-dynamic-n`. Root has merged retainedfork9 as **a620ce7790b32f7f0ae524a811417d2c6cee1152**, with parents82254e20/8bc69ee4 and a tree exactly equal to8bc69ee4 (`781f85c35fc7c8dd8a6089a209106320b461e800`). Bind fresh measurements to this actual merge head.

Read-only whole-PR counts against current localorigin/main merge base`002529e17b22567a071091053c6c4dc2a55e050e` are **29 files,9,589 additions/1,803 removals**; `publication-source-diff.json` preserves all paths and the origin/main revision observed. No rebase is involved.

| Component | Added | Removed |
|---|---:|---:|
| Swap-AB kernel, launcher and tactics |4,361|0|
| W4A16 implementation |908|853|
| Shared pipeline, combine, quantizer and utilities |485|200|
| Public API, dispatch and weight preparation |382|114|
| Benchmark scripts |1,109|487|
| Tests and references |1,565|112|
| Standalone sanitizer script |706|0|
| Documentation and trace template |73|37|
| **Total** |**9,589**|**1,803**|

## Fresh input and scope

Integration owner will produce `integration/pr7290-refresh-20261030/` and `evidence/pr7290-retained-refresh/<stamp>/{data,report}`, remote run `runs/pr7290-retained-refresh`. It is a complete candidate-only A/A refresh:31 jobs,36 supported arms,13 tokens,468 cells and93,600 strict CUPTI samples. Every candidate row must be fresh; do not inherit39/429 or any older candidate overlay. Bind the actual merge head and exact source/native cohort from this run, not c1ac labels from copied tools.

Preserve all13 raw token rows, negative results, repeat spreads and clock exceptions/missing windows. Heatmaps and aggregates omit1/2:396 distinct candidate cells. Candidate latency is the geometric mean of its two100-sample pass medians. Public functional API, quantization inclusion, frozen routes/tactics/default resolutions and unfused candidate finalize stay as recorded; no baseline rerun or tuning is needed.

## Immutable denominators to reuse

Use the published denominator selection, not newer rejected-experiment controls. The current project's `harness/historical/external/{ep,tp}/summary-cells.csv` is byte-identical to the old project's `cleanup-20261030/performance/external/{ep,tp}/summary-cells.csv`. Each has468 comparison slots (4 models ×13 tokens ×9 columns). Preserve `model,tokens,column,baseline,status,baseline_ms,reason,baseline_evidence` exactly, replacing only candidate fields and recomputing ratios.

| Denominator | Original structured sources under `../flashinfer-w4a4-split-dynamic-n/` |
|---|---|
| EP TRTLLM | `optimization-20261027/retained-rerun/evidence/runs/<model>/<family>/{a1,a2}/results.json` |
| EP legacy CuTe | Same root, `{c0,c3}-legacy[-w4a4|-per-token]/results.json` (MX uses plain `legacy`) |
| EP pre-PR W4A16 | Same root, `{c0,c3}-prepr-w4a16/results.json` undernvfp4 |
| TP TRTLLM | `optimization-20261028/tp-ep-post-sanitizer/evidence/runs/tp/<model>/<family>/{c1,c2}-trtllm/results.json` |
| TP legacy CuTe | Same root, `{c1,c2}-legacy[-w4a4|-per-token]/results.json` |
| TP pre-PR W4A16 | Same root, `{c1,c2}-prepr-w4a16/results.json` undernvfp4 |

Frozen external CSV hashes: EP`01bed08308cb6da4c66648535eb9699a39523c1ed8f67333b4945e002d5270fe`; TP`f5be713170238a13a3f0f4c89dc16ac099ed3d75a08bd45aac6a0443e7d5d6ad`. These are historical cross-instance baselines, not fresh same-node controls. Legacy MX retains its required fused-finalize footnote. Pre-PR W4A16 means the original old-layout implementation, not822 or326.

The prior upstream publication is immutable asset commit`9390a1a47d03def09be35f3b2be5be4b39f06d55`, prefix`pr7290/2026-10-30/326c4a79-cleanup`. Its measured326 candidate is a separate historical PR-head comparison, **not** one of the TRT/legacy/pre-PR denominators. An optional retained-head comparison can use that original candidate A/A data, but should not displace the requested end-to-end external heatmaps.

Native TRT table selection is `publication-w4-tail-cutoff/completed-tables/baseline-index.json`, SHA`51ce4db4f9beac023ba3eb6c0755c585a294cddded3948875dcd8745d6db6284`. It selects the last original pass (EPa2, TPc2), not geometric denominator values. Saved BF16 table-only rows come from `scripts/perf_round_20261027/public-refresh/final-public-f7182d5c/evidence/tables/` for V3/V41F EP only; their older timer-guard limitation remains explicit. Missing/unsupported staysN/A; no BF16 column in same-dtype heatmaps. K3 TRT per-token/MXFP8 and V41F TP MX support exclusions stay unchanged.

## Minimal rendering adaptation

Create a new local publication folder under this effort, leaving all previous publications untouched.

1. Start with `publication/assemble.py`, the original full A/A468 assembler—not the latest partial-overlay assembler. Replace experiment-specific source assertions with the actual merged-source receipt; accept the fresh full31-job leaf (or the owner's disjoint leaves). Keep the existing structured `(model,topology,backend,tokens)` joins, geometric medians, frozen baseline-field equality, raw stdout copying, resource/default joins and clock summaries. No table-text parsing.
2. Reuse `publication-w4-tail-cutoff/plot_external.py` for the two requested EP/TP red-white-green end-to-end heatmaps. Its44×9 layout, ratio1 neutral, all negatives and gray unsupported cells are already correct. Supply new CSVs and actual merge label; emit PNG/SVG plus input/output hash manifests. No old causal-overlay plot belongs in the fresh468 headline.
3. Adapt `publication-w4-tail-cutoff/completed-tables/render_comments.py` by replacing its historical candidate overlay lists with only the fresh source records and final phase `1-candidate`. Load the actual measured benchmark printer using the existing AST extraction, verify its printer AST/hash against the original, and replay all31 final-pass stdout suffixes byte-for-byte before combining families. Keep all62 original `--output-format both` logs untouched. Merge saved original TRT JSON records through the unchanged printer:468 fresh CuTe +390 historical TRT records,15 native tables across16 model/topology/family groups. V41F TP MX remains explicitly skipped. No rendered table is parsed into data.
4. Preserve four existing upstream comment targets from the saved body:6519314397 (V3/V41F EP),6519315021 (K3/N3U EP),6519315606 (V3/V41F TP),6519316131 (K3/N3U TP). Generate the four local comment bodies first; eventual publisher edits these existing comments, not forkPR9 comments and not new duplicates. Tables use final-pass medians; plots use two-pass aggregates.
5. Recompute external summary statistics, absolute latency CSVs, numerical tables, all negative counts, clock coverage and repeat spread from fresh records. Current values such as old5.90% spread or96/3,744 exceptions must not be copied into the refresh.

## Body and source wording

Use the saved PR7290 body/template, keeping `@humansand` as the first content beneath Description, related issues, checkboxes, experimental fence and other repository template sections. Write the final combined design; remove stale statements that PR head differs from326 only in a sanitizer script. Root supplies whole-PR diff counts against the actual current merge base, actual merged head and source-qualified validation wording. Preserve the original opt-in swap/default behavior and no-new-axis contract.

Replace the main end-to-end statistics, two EP/TP images, fresh raw/native links, measurement head and current046-cohort/cache/environment evidence. Say explicitly: **all468 candidate cells freshly measured; original historical denominators reused**. Do not call the refresh a same-GPU causal comparison or attribute old red cells to an isolated retained commit. Keep command examples self-contained with functional API, frozen winners/no-autotune, initial quant inclusion and strict wrapper boundary.

The original upstream **+1.54% GLM5 single-PRMT duplication** section remains relevant and historical, bound to4376662a and asset commit`2402bcd61a7cc39f650f6b92dd1aa2293ee50518` under`pr7290/2026-10-29/glm5-helper-4376662a`. Preserve its raw phases, limitations and native proof. **Do not replace it with forkPR9's +0.032% byte-index helper experiment:** that extra interface was reverted in8bc69ee4, restoring the upstream822 helper. The retained consumed-K call handoff passes the padded extent for Mega; representative raw-native equality is separate evidence, not a fresh distributed timing claim.

## Incremental archive and publisher boundary

The latest sealed archive is already97,169,580bytes: [c1ac archive](https://raw.githubusercontent.com/zianglih/flashinfer/7961a1f13b620e45741fd7057a72f1f248789448/c1ac8ce7/moe-gather-pipeline-results.tar.xz), SHA`8e78c5e0f122f06630a61f4e7b97b18358141e0f650699f683dfc9ee7e2ead31`. Do not copy its3,586 members or nested previous publications into the refresh.

The new explicit allowlist should contain only fresh468 raw evidence/logs, current config/source/native/cache/runtime receipts, structured denominator indexes/fields, new derived data/tables/plots, render scripts and final checks. Add a small dependency manifest with immutable URLs, commit/path, byte size and SHA for the historical publication/baseline/GLM5 inputs. Earlier full evidence remains accessible through that dependency; no deletion or relabeling. Exclude old raw payload duplication, draft bodies, publisher logs and nested archives. Use deterministic tar.xz, verify every member hash, and enforce **each published file <100,000,000bytes**. If the fresh-only archive exceeds that cap, split only by complete job/evidence leaves into separately hashed XZ files; never omit samples or append the old97.2MB payload.

The current publisher precedent is `tools/publish_w4_cutoff_assets.py`, not the older gzip/orphan-branch `publication/publish_assets.py`. Adapt only the new publication prefix/head, current asset-branch parent and dependency-based archive inputs; do not execute it yet. It should publish new small browsable outputs and fresh archive(s) on the existing asset branch, keep raw evidence archive-only, and preserve all old prefixes. Root owns final publication authorization. Before eventual public GitHub operations, select/verify account`zianglih`; never alter Git transport credentials.

Final QA: all468 identities/93,600 samples and31 complete A/A jobs; frozen denominator equality;31 native suffixes/62 stdout logs/15 tables; visible exclusions and negatives; image numeric/visual checks; dependency and archive-size/hash checks; actual merged-source binding. After authorized publishing, exact body plus four comment readbacks and HTTP/hash verification of both PNGs/archives complete the refresh. Until then, no assets or PR contents are changed.
