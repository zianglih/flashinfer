# PR #7290 benchmark publication refresh

Validated refresh for candidate `2b4732791a3ce48bc3ae6c030a283fab73854e0e` against retained control `a620ce7790b32f7f0ae524a811417d2c6cee1152`. These are local publication tools; they do not run benchmarks or write GitHub. The root agent owns publication. The complete main campaign and independent numerical replay passed: 468 cases / 187,200 samples. All 31 final-pass stdout tables reproduce exactly; the 15 published tables contain 468 fresh CuTe DSL records plus 390 original TRTLLM records. Matched main geomean is −0.0878% across tokens ≥4; every negative is retained. The separate 12-case / 4,800-sample isolated ACCA diagnostic also completed (+0.4179% geomean; six negative, worst −2.6359%); its values never replace the main matrix.

## Inputs

Pass one or more **complete, nonoverlapping** campaign data directories to `assemble.py --data`. They must be inside the owning project and collectively contain all 31 jobs / 468 cells.

```
<campaign>/fetch-receipt.json
<campaign>/data/perf-config.json
<campaign>/data/<source tracked manifest basename>
<campaign>/data/results/<job>/receipt.json
<campaign>/data/results/<job>/<index>-<role>/results.json
<campaign>/data/results/<job>/<index>-<role>.log
<campaign>/report/summary.json
<campaign>/report/cells.csv
<campaign>/report/clock-quartiles.json
<campaign>/report/runtime-resources.json
<campaign>/report/phase-components.csv
<campaign>/report/component-deltas.csv
<campaign>/report/table.md
```

The runtime owner validates and writes these reports. Preserve existing CAAC `cells.csv` fields: `job,model,topology,ep,tp,backend,tokens,c1_us,a1_us,a2_us,c2_us,control_us,candidate_us,speedup_percent,control_spread_percent,candidate_spread_percent`. Summary keys are `passed,complete_campaign,measured_cells,raw_samples,default_stage_resource_joins`. Resource/clock records carry the exact phase label. Source manifests include pinned submodules; there is no stale fixed inventory-count check.

Phases are `control,candidate,candidate,control`; scripts derive labels from the configuration, so candidate labels are `1-candidate,2-candidate`. Both roles have two fresh process medians: 187,200 total strict-CUPTI samples, including 93,600 candidate samples. Role-specific cache-key translation and frozen-choice identity remain the runtime audit's responsibility and passed the final runtime audit.

## Reproduction

From `/Users/ziangli/playground/projects/flashinfer-moe-gather-pipeline`, use `.venv-publication/bin/python` (already includes matplotlib/numpy):

```bash
.venv-publication/bin/python integration/pr7290-refresh-20261102/publication/preflight.py
.venv-publication/bin/python integration/pr7290-refresh-20261102/publication/assemble.py --data integration/pr7290-refresh-20261102/fetched/1793691596500669000/data
.venv-publication/bin/python integration/pr7290-refresh-20261102/publication/completed-tables/render_comments.py
.venv-publication/bin/python integration/pr7290-refresh-20261102/publication/plot_external.py --csv integration/pr7290-refresh-20261102/publication/external/ep/summary-cells.csv --output-dir integration/pr7290-refresh-20261102/publication/plots --commit-label 2b473279 --topology ep
.venv-publication/bin/python integration/pr7290-refresh-20261102/publication/plot_external.py --csv integration/pr7290-refresh-20261102/publication/external/tp/summary-cells.csv --output-dir integration/pr7290-refresh-20261102/publication/plots --commit-label 2b473279 --topology tp
.venv-publication/bin/python integration/pr7290-refresh-20261102/publication/plot_retained.py
.venv-publication/bin/python integration/pr7290-refresh-20261102/publication/verify_numeric.py
.venv-publication/bin/python integration/pr7290-refresh-20261102/publication/build_bundle.py --prepare
```

Visually inspect both external PNGs and the local retained-head plots. Record `visual-review.json` with `passed:true` and `plots` mapping the exact external paths/hashes from `numeric-validation.json`. The retained-head diagnostics require review but do not appear as additional PR-body heatmaps. Then run `build_bundle.py` without `--prepare`.

The bundle writes separate `publication-{candidate,control}-{ep,tp}.tar.xz` archives plus `publication-metadata.tar.xz`, using at most three compression workers with deterministic member/manifest ordering; each must be below 100,000,000 bytes. It verifies every archive member against the explicit allowlist and forbids nested historical archives. New immutable asset prefixes must be used; do not overwrite old `a620ce77` assets. Add runtime harness/config proofs to the fetched manifest before sealing rather than inventing undocumented bundle inputs.

## Validation and interpretation

- All 468 supported cells must be fresh; no old candidate values or missing cells can be filled. The exact keyset equals the previous complete campaign. K3 MXFP8 and V41F TP MX remain unrun because they lack supported external comparisons.
- Raw tables keep tokens 1/2; both EP/TP heatmaps and derived stats exclude them. External heatmaps have 44 rows × 9 columns each and preserve all negative values and unsupported cells.
- Candidate latency is `sqrt(A1 × A2)` from phase medians. External speedup is `100 × (historical baseline / candidate − 1)`. Historical denominator fields and evidence pointers are unchanged. These are historical cross-instance comparisons.
- Local retained-head speedup is `100 × (sqrt(C1 × C2 / (A1 × A2)) − 1)`. This matched CAAC check covers the whole rebase/current source delta; it does not isolate a particular optimization. Repeat/clock anomalies remain visible. No automatic significance or retention claim is made.
- `verify_numeric.py` independently reconstructs all 187,200 CUPTI spans from timestamp-correlated activities, checks every raw median and geometric aggregate, confirms historical external joins, and verifies table records/plot manifests.
- `render_comments.py` calls the unchanged benchmark table functions directly on structured `BenchResult` records. It reproduces all 31 final candidate stdout tables byte-for-byte before joining original TRTLLM records. It never parses table cells. It emits 15 complete tables, 468 fresh candidate records and 390 reused TRTLLM records; final-pass tables intentionally differ from two-pass heatmap aggregates.
- Original TRTLLM structured sources and baseline index are hash-pinned. BF16 is table-only and retains its older timing-guard caveat. Unsupported records stay N/A.
- Current benchmark source is byte-identical to retained `a620ce77`; preflight reproduced all 15 previous completed tables using the current printer and verified all historical inputs. Fresh main verification also passed: all 187,200 CUPTI spans, 1,872 phase medians, exact histogram/routing/cache choices, source/native postflight, table joins and final plot hashes. Visual review passed for the final explicitly end-to-end EP/TP titles and full panels.

## Public updates (root only)

Keep only the full external EP/TP heatmaps in the PR body. Replace the section beginning `**End-to-end performance.**` through immediately before `**Historical shared-helper evidence.**`. Preserve the latest body snapshot's CodeRabbit text, review template, source diff breakdown, current C3 tests and GLM5 section. Change the old test-boundary sentence to indicate that benchmarks were refreshed while no sanitizer ran. `patch_body.py` performs exactly these two scoped changes and verifies the GLM5 bytes.

The root should refresh the live PR body immediately before applying that patch. After assets publish, write `assets-published.json` with immutable `raw_base` and rerun `render_comments.py`; structured table manifest must remain unchanged while URL-bearing comment hashes update. Update the same comments, never create new ones:

| File | Existing comment ID | Workloads |
|---|---:|---|
| completed-tables/part-1.md | 6519314397 | V3 EP8 / V41F EP4 |
| completed-tables/part-2.md | 6519315021 | K3 EP8 / N3U EP8 |
| completed-tables/part-3.md | 6519315606 | V3 TP8 / V41F TP4 |
| completed-tables/part-4.md | 6519316131 | K3 TP8 / N3U TP8 |

Each comment and the PR body must remain below 65,536 bytes; no unresolved `{{RAW_BASE}}` may be published. Before public writes, recheck source HEAD, immutable asset hashes, byte-exact rendered comments and current GitHub identity (`zianglih`). Root's existing publisher/update/readback tools need the new multi-archive manifest, new prefix/head and scoped body update, rather than the previous hardcoded single-archive assumptions.

## Compact performance-section renderer

`render_performance.py --draft` writes only `performance-section.draft.md/.json`, with explicit unresolved placeholders. The draft is 455 words, including the copy-paste command, MX/TP variants and separate diagnostic paragraph, versus the previous 501-word section. It consumes the copied, hash-pinned `RUNTIME.md` facts in `runtime-context.json` / `runtime-notes.md`; re-copy and update that context if runtime evidence changes. Those files and the renderer enter the metadata archive.

After fresh reports, numeric verification, visual review and asset publication finish, run:

```bash
.venv-publication/bin/python integration/pr7290-refresh-20261102/publication/render_performance.py
.venv-publication/bin/python integration/pr7290-refresh-20261102/publication/patch_body.py --snapshot /absolute/path/to/fresh-live-pr.json --performance-section integration/pr7290-refresh-20261102/publication/performance-section.md
```

Final rendering requires matching head, sample counts, report/table hashes, all-negative retention, matched control identity and an immutable published asset URL. It inserts measured overall / swap-AB / W4A16 / prefill speedups, worst/negative cells, repeat spreads and candidate clock diagnostics; it does not label the campaign a non-regression pass. The PR body gets exactly two external heatmaps and four existing table-comment links. Retained-head plots remain local diagnostics.

## Separate isolated ACCA diagnostic

The predeclared isolated diagnostic is complete and preserved in `diagnostic-inputs.json`; sealing requires its explicit verified allowlist and the credential scan below. The independent isolated audit passed. Its values never replace the main 468 cells, either candidate phase, external comparisons or native tables. The main sample count remains 187,200. Its manifest uses this schema:

```json
{
  "passed": true,
  "head": "2b4732791a3ce48bc3ae6c030a283fab73854e0e",
  "control": "a620ce7790b32f7f0ae524a811417d2c6cee1152",
  "main_cells_sha256": "SHA256 of publication/report/cells.csv",
  "summary": "project-relative/path/to/diagnostic/summary.json",
  "files": {"project-relative/path/to/diagnostic/summary.json": "SHA256"}
}
```

The explicit `files` allowlist must include the selection declared before the isolated run, exact commands/config, raw phase observations, source/cache/routing proofs and completed summary. Every file hash is verified. Summary keys consumed by the compact body paragraph are `passed,head,control,phases,cells,raw_samples,speedup_percent,negative_cells,min_speedup_percent`; phases are `candidate,control,control,candidate`. Add other provenance/clock/repeat fields freely. All diagnostic raw files enter the metadata evidence archive; the compact summary is also published directly as `diagnostic-summary.json`. If the runtime reporter emits another schema, adapt the reader explicitly rather than modifying or replacing raw evidence.

## Credential screen before sealing

After `build_bundle.py --prepare`, run `scan_publication.py`. It streams only the explicit allowlist, verifies every file hash, rejects archives/compiled-cache artifacts, and reports file/category counts only. It never prints matching values or paths. A finding blocks sealing for private review. This heuristic check does not claim to detect every possible form of private information. Final sealing requires a clean receipt tied to the exact allowlist and scanner hash. Any allowlist/script change requires rescanning.
