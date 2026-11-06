# W4A16-only retained-head refresh

Prepared only. Do not launch until the final retained source, including the requested `num_k_atoms` handoff cleanup, is qualified and root authorizes the refresh.

`anchors.json` contains the original 83df winner-cache manifests, result hashes, routing identities and ordered unique tactic identities for all 13 tokens in eight model/topology jobs. The original results were independently hashed before extracting the 104 W4A16 cells. No tuning or baseline rerun is required.

`run_refresh.py` preserves the existing observer and public benchmark path, selecting only CuteDSL W4A16. It executes A1/A2 using the same frozen cache, 10 warmups, 100 strict CUPTI samples, cold-L2 CUDA graphs and the existing NV input-quantization opt-in contract (W4A16 BF16 input is not quantized). Every source, winner, route, raw median, GPU UUID, command and cache manifest is checked before accepting a phase. Each process has a private compiler working directory; native C++ cache links remain persistent.

Deployment must copy these helpers and `observer/` to a new final-refresh root and supply an immutable clean source receipt plus the matching runtime receipt:

```sh
python prepare_refresh.py --source /absolute/retained/source.json --runtime /absolute/retained/runtime.json
```

The preparation creates `source.json`, `runtime.json`, `config.json` and source-specific native cache links. It launches no GPU work. Root must then create an explicit source-bound `release.json` containing `approved: true`, `source_head`, `candidate_source_sha256` (the full per-file mapping from `config.sources.candidate`), `gate_receipt`, `gate_receipt_sha256`, and the authorized `box`. Only after that:

```sh
TP_BENCH_BOX=<authorized-box> python launch_refresh.py
```

The launcher requires all eight target GPUs idle and records their assignments. Eight jobs produce `runs/{ep-v3,...,tp-nemo3-ultra}/receipt.json`, `0-candidate/results.json`, `1-candidate/results.json` and sibling `.log` files. Each receipt phase includes `phase: a1/a2`, index, role, explicit result/log paths, source/runtime settings, GPU identity, raw-data/log hashes and accepted medians. Results retain the unchanged native observer schema.

Expected counts: 104 W4A16 cells, 208 pass medians, 20,800 raw CUPTI samples; 52 cells and 104 medians per topology. Tokens 1/2 remain in raw output but are excluded from the initial 44-row heatmap. Other dtypes and external controls remain bound to their existing 83df evidence. The report adapter lives in `report/` and must verify every unchanged table row and baseline field. Root owns publication.
