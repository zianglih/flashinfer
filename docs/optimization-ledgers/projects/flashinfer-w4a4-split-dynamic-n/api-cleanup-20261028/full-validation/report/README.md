# Cleanup rerun report

Helpers only. No canonical source changes or GitHub writes. The current source
campaign must rerun all five CuTe formats, including W4A16. Only external
comparison baselines are reused.

## Existing evidence and exact comparison contract

- Latest published PR body and image are in
  `optimization-20261028/warp-polish/final-polish/`, source
  `17bff619c11dcbf65bd6394546fa70b21999b9ef`. `combined/` is the preceding
  `cb35c42f6` campaign; it is not the latest published table.
- Latest candidate raw runs:
  `optimization-20261028/warp-polish/final-polish/sole-measurements/full-evidence/`.
  Its four blockscaled formats were fresh; its W4A16 candidate reused the older
  `99f4d0c27` campaign. The new report explicitly requires fresh W4A16 too.
- The comparison template is `final-polish/assembled/summary-cells.csv`, verified
  against its `provenance.json`. All saved baseline values are independently
  recomputed from each cell's original `baseline_evidence` JSON files.
- Baseline raw campaign:
  `optimization-20261027/retained-rerun/evidence/runs/`.
  TRTLLM is attributed to retained `1e69d0a39`; non-swap CuTe uses `e2728a290`;
  W4A16 uses pre-PR `002529e1` with up64/gate64 weights. Source attribution lives
  in `optimization-20261027/warp-specialization/full-rerun/baseline-attribution.json`
  and the retained-rerun source-equivalence/provenance receipts.
- Preserve 44 rows × 9 columns. Models: **V3 EP8**, **V41F EP4**, **K3 EP8**,
  **N3U EP8**. Display tokens: 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192,
  16384. Tokens 1/2 are measured and preserved in raw output but excluded from
  the table and retention.
- Columns: TRTLLM W4A4, PER-TOKEN, MXFP4x8, MXFP8; non-swap W4A4, PER-TOKEN,
  MXFP4x8, MXFP8; W4A16 before PR. Every comparison matches dtype. K3 has four
  unsupported baseline columns, so 352 displayed measured cells and 44 N/A.
- Swap-AB always uses unfused finalize; saved non-swap MX uses required fused
  finalize. Both pass medians are combined geometrically. Signed percent is
  `100 * (baseline_ms / current_ms - 1)`. Initial NVFP4 activation quantization
  is included; MX inputs are prequantized. Fresh managed-cache winners are
  frozen for A1/A2; old winner identities are not a requirement.

## New evidence manifest

`assemble_report.py --manifest <manifest.json>` accepts project-relative paths
(absolute paths inside this project also work):

```json
{
  "measured_head": "<full pushed commit SHA>",
  "source_sha256": {"benchmarks/bench_moe_deepseek.py": "<hash>", "<other measured source>": "<hash>"},
  "observer_hashes": {"observer_sha256": "<hash>", "arm_contracts_sha256": "<hash>"},
  "tune_receipts": [{"path": "<per-job receipt.json>", "sha256": "<hash>"}],
  "phases": [
    {"model": "v3", "family": "nvfp4", "pass": "a1", "results": "<observed results.json>", "stdout": "<matching log>", "results_sha256": "<hash>", "stdout_sha256": "<hash>"}
  ]
}
```

Each phase can contain one format or a complete family. The aggregate must
contain exactly four models × 13 tokens × five formats × two passes = 520
medians / 52,000 CUPTI samples. It verifies source hashes against the commit,
saved routes, 100 finite CUPTI samples per median, complete A1/A2 coverage,
frozen cache-hit identity, benchmark flags, stdout CSV, and baseline equality.
It refuses partial data and never substitutes old candidate measurements.

Each completed tune receipt contains a `winners` list with
`{model,tokens,backend,cache_hits:[{key,runner,tactic},...]}`. Every A1/A2 hit must
match that fresh tune receipt. All five formats are required even for K3 modes
that have no supported external comparison baseline.

The assembler also produces local `retained-comparison.csv`, `.md` and `.json`
against all 260 prior candidate cells (17bff blockscaled and saved99f4 W4A16).
Its 44×5 displayed table, per-model/per-format decode and prefill summaries,
largest slowdowns, and >3% latency-increase flags exclude tokens1/2. This is a
historical comparison across separate campaigns and fresh current tuning; it
does not replace the external-baseline PR table or assert matched causality.
Material flags must be reviewed before publication.

## Generate table, heatmap and draft

From the project root, after evidence is complete:

```bash
audit-final-cleanup/.venv-cpu/bin/python api-cleanup-20261028/full-validation/report/assemble_report.py \
  --manifest api-cleanup-20261028/full-validation/measurements.json

swap-ab-full-rerun-20261027/.venv-plot/bin/python swap-ab-full-rerun-20261027/plot_speedup_table.py \
  --csv api-cleanup-20261028/full-validation/report/assembled/summary-cells.csv \
  --output-dir api-cleanup-20261028/full-validation/report/plots \
  --commit-label '<short SHA> · saved baselines'

audit-final-cleanup/.venv-cpu/bin/python api-cleanup-20261028/full-validation/report/build_body.py \
  --benchmark-section api-cleanup-20261028/full-validation/report/benchmark-section.md \
  --validation-section api-cleanup-20261028/full-validation/report/validation-section.md
```

`full-validation/build_manifest.py` produces `measurements.json` after the
benchmark agent fetches complete evidence. `build_validation.py` has already
rendered the passed 95 pytest/11 Linux-test results from the fetched current
receipts; it verifies JUnit counts, raw output and pre-commit evidence. Its
`validation-section-receipt.json` binds the generated section and inputs.

The existing heatmap renderer is reused unchanged. It uses red/white/green,
neutral ratio 1.0, limits covering at least 0.5–2.0, gray N/A cells, compact
model labels, and the same nine-column order. Outputs are PNG, SVG and a
hash-bound `plot-manifest.json`. It verifies the assembled CSV provenance.

The PR builder requires new benchmark and validation sections; it cannot
silently relabel old test results or obsolete cache instructions. It preserves
the repository PR template, updates the LOC component table from the new
commit, and removes the obsolete prepared-weight mismatch assertion claim.
An optional `--implementation-section` supplies revised scope bullets. Without
an image receipt the draft uses the local PNG and is marked unpublished.

## Existing image publication workflow (root owns execution)

Existing helper:
`optimization-20261028/warp-polish/final-polish/publish_plot.py`.
It accepts a campaign JSON containing `measured_head`, `--plots`, and `--output`.
It switches and verifies GitHub identity `zianglih`, uploads exactly one PNG to
the existing fork branch `codex/pr7290-benchmark-assets`, verifies the commit
has only that image, downloads the immutable raw URL, and checks exact bytes.
The path is `pr7290/2026-10-28/<short SHA>/swap-ab-speedup-table.png`.
It does not edit PR7290. The latest published receipt is
`final-polish/plot-publication.json`, asset commit `5d2351a1635f95c43a01c476764d0ae343b7967e`.

After root approves and publishes the new image, rerun `build_body.py` with
`--image-receipt <new plot-publication.json>`. Root then updates the live PR
body and verifies readback. No new publication has been performed here.
