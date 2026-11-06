# Cumulative W4 prefill comparison

No completed same-runtime822→c1ac paired24 campaign is established. The previous24-cell CAAC directly measured822→02de; the cutoff campaign measured2b8→c1ac for nine TP prefill cells. Historical heatmaps and per-commit comparisons do not substitute for the cumulative pair.

This plan reuses the original eight W4 jobs and every frozen route/tactic: four models × EP/TP × tokens4096,8192,16384. Both arms receive fresh C–A–A–C phases,100 strict CUPTI samples/phase and10 warmups, cold-L2 CUDA Graphs. The original held helpers are preserved. Deployment adds only the supported canonical `FLASHINFER_CUBIN_DIR` phase environment setting to `run_perf.py`; its timing logic and the other eleven helper files are byte-identical. Fourteen explicit choices and ten recorded defaults retain their original resolution checks. All9,600 samples,96 phase medians, negative rows, repeat spreads, clocks, resources, FC1/FC2/combine durations and exposed extensions remain reportable.

Control is the existing immutable822 source at `control/`; candidate is the existing immutable c1ac-equivalent source at `candidate-w4-tail-cutoff-r0/`. Their full13,245-file inventories differ in exactly the four files from Git822→c1ac, with exact Git bytes at each endpoint. No source edits or new checkout are needed. [Bindings](plan.json), [held config](screen/perf-config.json).

The old24 used routing94cd8afa/moe_utils91ef42f6. Current bindings require routing88e6a970/moe_utils046552b8 and the unchanged FP4/MXFP8 modules. No old phase is reused and no old ELF is restored. Integration owns remote preparation/normal-load/no-op/idle checks and launch; this local preparation performed no remote or GPU operation.

```bash
/usr/bin/python3 -u /data/ziangli/flashinfer-moe-gather-pipeline/experiments/w4-cumulative-prefill/harness/campaign.py \
  --config /data/ziangli/flashinfer-moe-gather-pipeline/runs/w4-cumulative-prefill/perf-config.json \
  --gpus 0 1 2 3 4 5 6 7
```

Actual launch: PID63860, one whole job per GPU0–7, with source/native/cache and two-sample idle receipts in `screen/launch-preflight.json`. Both arms use separate cached_ops/CuTe directories, sharing only the four current release modules and canonical generated/cubin inputs. This measures the cumulative current branch effect under a matched runtime. It cannot assign that effect to individual commits, replace the earlier per-commit CAAC/ACCA records, or explain historical-baseline drift by itself. No TRT/legacy rerun, retuning, correctness expansion or profiling is included.
