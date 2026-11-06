**Closed: rejected.** See [RESULTS.md](RESULTS.md) and all raw CAAC rows in [screen-cells.csv](screen-cells.csv).

# MMA operand-readiness gate

Launched after the independently verified 150/150 sanitizer release. The primary GPU5 exact-output gate passed160 source-paired replay comparisons across two intermediate widths; matched EP timing is running on primary/secondary GPU5. Final codegen acceptance also requires the isolated-CWD control recollection described below. The candidate is the sole unstaged kernel change in `flashinfer-mma-ready-peek-review` on d1767be1. K-tail experiments use another checkout and must not be composed into this trial.

`probe_pair.py` and `run_gate.py` adapt the retained producer experiment's public-wrapper closure and compilation instrumentation. Default configurations 0/1/6/7/10 cover NVFP4, per-token NVFP4, MXFP8 and MXFP4x8; one/two CTAs; N16/32/128/256; SiTU/SwiGLU/ReLU2. Each case uses static and CLC scheduling, both PDL states, and balanced/skewed/empty/reactivated captured routes. The existing per-token recipe and initial quantizer are included. Run both intermediate384 and2304 to cover short/long FC2 reductions. H256 is intentionally small; actual stage depths and effective CLC are recorded, not forced. W4A16 has no source change and remains a perf control.

The graph mutates routed IDs/weights with `sqrtsoftplus` routing, whose benchmark closure deliberately retains the supplied routes. It does not overwrite mutations with a DeepSeek router. Final tensor bytes must agree across sources and all scheduler/PDL choices. Compile PTX, cubin, SASS and resource evidence; `analyze_codegen.py` requires identical launch/storage geometry and zero spills/stack. Readiness-site counts and register differences are recorded for inspection, not treated as speedups. This is a source-equivalence experiment, not a new mathematical reference or a replacement for sanitizers.

The gate runner accepts a source config containing `python`, `python_deps` and `sources.{control,candidate}.{repo,head,workspace_base,benchmark_source_sha256}`. Bind all relevant source files to their actual hashes. Give each intermediate a distinct output subtree; candidate `--reference` points at that intermediate's completed control result. Example after explicit GPU assignment:

```sh
python run_gate.py --config gate-config.json --gpu <gpu> --role control \
  --intermediate 384 --output-root <gate-results>
python run_gate.py --config gate-config.json --gpu <gpu> --role candidate \
  --intermediate 384 --output-root <gate-results> \
  --reference <gate-results>/i384/control/result.json
python analyze_codegen.py --control <gate-results>/i384/control/result.json \
  --candidate <gate-results>/i384/candidate/result.json --output <gate-results>/i384/analysis.json
```

Repeat with2304. CPU preparation currently consists only of AST parsing, source tracing and the separate symbolic state proof; no helper has imported CUDA or executed GPU work.

`run_perf.py` reuses the managed observer unchanged. It copies a completed d1767be1 replay cache into two disposable screen caches and replays C-A-A-C on one GPU with identical winners, routes and public APIs. Every phase checks source hashes before/after, zero profiling, unchanged caches, frozen winner identities, 100 positive CUPTI samples, exact medians and route identities. Retain native C++ caches in `workspace_base`; the observer's graph timing stays cold-L2 with10warmups. This is a fixed-winner mechanism screen; retained performance still requires the full fresh-tuning TP/EP campaign.

The perf config has `python`, `python_deps`, `output`, `observer`, `observer_hashes` (relative to the observer's directory), `sources.{control,candidate}.{repo,head,workspace_base,source_sha256}`, and `jobs`. Start with `jobs.json`, adding `winner_results` and `winner_cache` for each job. EP uses completed d1767be1 frozen replay caches; TP must use the new source-bound TP campaign's completed swap-AB replay caches. Do not import EP winners into TP. Run one `--job` per assigned GPU, with four phases serialized internally.

`jobs.json` contains15 bounded EP/TP jobs. EP selections cover all16 existing negative non-W4A16 cells above token2 from the source-bound report, plus representative decode/prefill controls. `ep-gap-selection.json` preserves that audit. TP samples4/64/4096/16384 across supported formats; V41F TP MX and K3 MXFP8 are skipped under the user's baseline-support policy. For an early stop, first run V3 EP MX, N3U EP NV/MX, K3 EP NV/MX, V41F EP MX and V3 TP NV/MX. Expand to the remaining jobs only if codegen and that first bracket warrant it. Do not replace full-matrix cells with screen results.

The first gate exposed shared-CWD compiler dump collisions in two control PTX files; output replay checks remain valid. `gate-recapture/` repeats control artifact collection on secondary GPU7 in a unique `compiler-artifacts/` CWD for each width, retaining the same source and persistent native cache. `probe_pair_isolated.py` also checks PTX/SASS CTA and block-scale instruction identity. The original gate archive is preserved at `gate-evidence/` with676 verified files; inconsistent PTX is not accepted as final codegen evidence. Final paired analysis compares recollected control against the original serialized candidate artifacts.
