# Final swap-AB polish sweep

This directory owns orchestration, frozen evidence and local publication drafts. It reuses `warp-polish/run_full.py` unchanged (SHA256 `f3e481b11863679836bc23288ecf84f35b7941de368495d947d4f521de319973`) and the original `full-rerun/tools/observe_benchmark.py`. It does not introduce another timing implementation or touch active experiment sources.

The campaign contains eight independent model/family jobs: V3 EP8, V41F EP4, K3 EP8 and N3U EP8 × NVFP4/MX. Each runs A1/A2, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. Event fallback is prohibited. Tokens are exactly `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; tokens 1/2 are run but excluded from retention and the display. Expected output: 208 current cells, 416 fresh medians, 41,600 raw samples and 24 public benchmark processes. NVFP4 times input quantization; MX starts prequantized. Swap-AB finalize remains unfused.

Every external baseline and all unchanged W4A16 measurements are reused. The final summary stays 44 × 9 with the existing compact model names, same-dtype comparison columns, fused legacy-MX marks, N/A cells and red/white/green plot. The assembler preserves all 468 saved baseline rows/values, updates only current W4A4/per-token/MXFP4x8/MXFP8 latencies, and leaves W4A16 rows entirely unchanged. Native A2 CSV is checked against actual stdout; both raw medians are kept separately.

## Completed sole-announcer measurement source

Root authorized speculative overlap while scatter4 is evaluated. `start_sole_sweep_remote.py` launched frozen sole-announcer kernel `5d3b3b003b37052671aa362bb2d41166e64dca7e12ae14ab11f6da838a3c9bd4`, source receipt SHA `da4af01726e46889a42753ab4e20f0bb6d199a78be54dae6ef75b1d9c26dd9ad`:

| GPU | Model | Queue PID | Order |
|---|---|---:|---|
| 1 | V3 | 818913 | NVFP4, then MX |
| 5 | V41F | 818914 | NVFP4, then MX |
| 6 | K3 | 818915 | NVFP4, then MX |
| 7 | N3U | 818916 | NVFP4, then MX |

Remote receipt: `ROOT/sole-announcer/final-sweep/launch.json`, with `ROOT=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/warp-polish`. Jobs are `final-{model}-{nvfp4,mxfp}`. All eight jobs completed successfully. GPUs 1/5/6/7 were released after an idle check. They can become final measurements only if the final composed source is byte-identical. Otherwise retain them as exploratory evidence and measure the selected composition afresh.

The source-bound archive is in `sole-measurements/full-evidence` (733 manifest entries verified), with its original speculative campaign (`measured_head: null`). `sole-measurements/verified/evidence-verification.json` independently validates 208 cells, 416 medians, 41,600 CUPTI samples, frozen tactics/routes and actual stdout. It is not publication attribution.

From the project root, refresh the queue receipts without launching work:

```bash
python3 optimization-20261028/warp-polish/final-polish/refresh_sole_status.py
```

## Adopt sole-only measurements after retention

After the actual publication commit is known, set `final_head` to its full SHA. The source receipt remains the frozen measured receipt, even though its checkout has the earlier base commit; `verify_composition.py` binds all 342 source files to the publication commit.

```bash
python3 optimization-20261028/warp-polish/final-polish/prepare_campaign.py \
  --source-json optimization-20261028/warp-polish/producers/next-audit/evidence/source.json \
  --measured-head "$final_head" \
  --adopt-launch optimization-20261028/warp-polish/final-polish/sole-launch.json \
  --output optimization-20261028/warp-polish/final-polish/bound-sole
python3 optimization-20261028/warp-polish/final-polish/verify_composition.py \
  --campaign optimization-20261028/warp-polish/final-polish/bound-sole/campaign.json \
  --output optimization-20261028/warp-polish/final-polish/bound-sole/composition-verification.json
python3 optimization-20261028/warp-polish/final-polish/assemble_results.py \
  --campaign optimization-20261028/warp-polish/final-polish/bound-sole/campaign.json \
  --evidence optimization-20261028/warp-polish/final-polish/sole-measurements/full-evidence \
  --output optimization-20261028/warp-polish/final-polish/assembled
```

Adoption emits no launch helper and does not rerun anything. It records four actual GPU workers for the eight serialized model/family jobs. The archive retains the original unbound campaign; the separate bound campaign and composition receipt identify the final commit without rewriting measured provenance. For subsequent body generation, pass `--campaign .../bound-sole/campaign.json`.

## Fresh composed-source launch, only if needed

If a scatter variant is retained, freeze the complete composed source under a new remote root such as `ROOT/final-polish/{source.json,flashinfer,cache}`. Preserve persistent native compilation-cache links. Supply its local exact `source.json` copy and actual publication commit; do not reuse sole-only results for changed code.

```bash
python3 optimization-20261028/warp-polish/final-polish/prepare_campaign.py \
  --source-json /absolute/path/to/final-source.json --measured-head "$final_head"
python3 optimization-20261028/warp-polish/final-polish/verify_composition.py
python3 swap-ab-exact-20261027/remote.py \
  optimization-20261028/warp-polish/final-polish/launch_prepared_remote.py
```

Preparation itself launches nothing. The final command launches eight jobs, one per GPU 0–7, only after all eight are idle and every source/helper hash matches. Do not execute it while the speculative or scatter workers are active. No source or cache is deleted or edited. The general eight-worker launch plan has not been executed.

## Verify, assemble and render

After all jobs complete:

```bash
python3 swap-ab-exact-20261027/remote.py \
  optimization-20261028/warp-polish/final-polish/status_prepared_remote.py
python3 optimization-20261028/warp-polish/final-polish/fetch_evidence.py
python3 optimization-20261028/warp-polish/final-polish/assemble_results.py
swap-ab-full-rerun-20261027/.venv-plot/bin/python \
  swap-ab-full-rerun-20261027/plot_speedup_table.py \
  --csv optimization-20261028/warp-polish/final-polish/assembled/summary-cells.csv \
  --output-dir optimization-20261028/warp-polish/final-polish/plots \
  --commit-label "${final_head:0:9} · saved baselines"
```

The archive contains exact sources, observers, launch receipts, raw result JSON, all stdout and frozen native-winner caches. Transfer is chunked and hash-verified. Assembly independently checks source binding, source-only kernel changes, route hashes, frozen cache hits/tactics, raw sample counts and medians, CUPTI-only timing, CLI/environment contracts, exact token/mode/model coverage, source-identical baselines and actual A2 stdout. No time-stratum substitution is allowed. Inspect the generated plot visually before publishing.

## Local body and eventual publication

Keep the final body concise. Do not include the synchronization audit or experiment ledger. `build_body.py` requires a current validation paragraph and a verified receipt containing `complete`, final `head`, `kernel_sha256`, `section_sha256`, and an `inputs` mapping of evidence paths to hashes. Distinguish current gates from the saved 28-test prior-head accuracy output. State **zero local-memory/stack spills** unless uniform-register spill behavior was also checked. Sanitizer remains skipped.

The sole-only draft is assembled and visually reviewed for `17bff619c`. `publication-audit-local.json` checks all 468 unchanged baseline rows, 396 plotted cells, raw outputs and validation attribution. Its image link is deliberately local; `plot_published: false` prevents treating the draft as a published image. Rebuild locally without a GitHub write:

```bash
python3 optimization-20261028/warp-polish/final-polish/build_body.py \
  --campaign optimization-20261028/warp-polish/final-polish/bound-sole/campaign.json \
  --plot-local optimization-20261028/warp-polish/final-polish/plots \
  --validation optimization-20261028/warp-polish/final-polish/validation-current.md \
  --validation-receipt optimization-20261028/warp-polish/final-polish/validation-current.json
```

Only after retention, source/evidence review and plot inspection:

```bash
python3 optimization-20261028/warp-polish/final-polish/publish_plot.py
python3 optimization-20261028/warp-polish/final-polish/build_body.py \
  --plot-publication optimization-20261028/warp-polish/final-polish/plot-publication.json \
  --validation optimization-20261028/warp-polish/final-polish/validation-current.md \
  --validation-receipt optimization-20261028/warp-polish/final-polish/validation-current.json
```

An optional `--implementation-note` supplies one short retained scatter4 sentence. The plot publisher changes one image on the existing asset-only fork branch and verifies the immutable URL. The body builder writes only a local draft. Root owns the final PR-body update and readback; no GitHub action has been taken by this preparation task.

Current helper validation: Python syntax compilation passed. The sole-only source binding, full-result assembly and local body generation passed for `17bff619c`; publication remains pending the final retention decision. The completed sole full sweep is the only GPU launch performed here.
