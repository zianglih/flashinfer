# Fresh W4 prefill isolation: 822 → 02de

24 cells: four models × EP/TP × tokens 4096, 8192, 16384. Eight jobs run in two waves on GPUs 1–4; GPU0 remains reserved for native retune. Each cell uses C–A–A–C, 100 strict CUPTI samples, 10 warmups, cold-L2 CUDA Graphs, and frozen recorded routes/choices (14 explicit and 10 defaults). All samples, negative rows, repeated-phase spread, clocks and FC1/FC2/combine spans are retained. No new tuning or profiling.

The actual control is immutable `control/` at 82254e20. Candidate `candidate-composed/` records original base822 plus the exact two-file patch committed as02de7785. Full13,245-file inventories match; only the scale-selector utility change is used by W4. Current recovery release C++ libraries are used by both arms; no historical ELF is restored. Both arms generate identical current Ninja descriptions and all four modules are no-op with unchanged ELF hashes.

Local preparation/config: `screen/preparation.json`, `screen/perf-config.json`; current source/native closure: `screen/source-cache-preflight.json`. Same hash-bound helpers as the completed raw-peek matrix. No production files are changed.

Authorized launch command (controller only; workers are serialized per GPU):

```bash
/usr/bin/python3 -u /data/ziangli/flashinfer-moe-gather-pipeline/experiments/w4-initial-selector-prefill/harness/campaign.py \
  --config /data/ziangli/flashinfer-moe-gather-pipeline/runs/w4-initial-selector-prefill/perf-config.json \
  --gpus 1 2 3 4
```

`launch.py` repeats cache/no-op and UUID/idle checks before invoking that command; campaign replays full source inventories before/after. `postflight.py` confirms unchanged current release library identities and idle GPUs1–4. Existing `harness/report_evidence.py` replays raw CUPTI and component attribution after fetching complete jobs. This fresh causal result stays separate from historical326/822-equivalent public comparison rows.
