# Opt-in split blockscaled iKET instrumentation

`markers.patch` is an independent production-ready diagnostic patch against frozen `13ca1475d96839f3bf3c46699cc63204b4d3b409`. It is separate from the cache hint and NB2 overlap experiments. Parent owns final integration.

- Internal constructor option `enable_iket=False` controls compile-time marker branches. Normal construction does not import iKET. Explicitly enabled construction tries `cutlass.cute.experimental.iket`, then the older `cutlass.cute.iket`, matching the existing MegaMoE convention without importing MegaMoE code.
- Compile an explicitly enabled kernel using `cute.compile(kernel.wrapper, ..., options="iket")`, then run through `run-iket`. There is no public API, tactic, environment, or timing-method change.
- Production markers cover every CTA. Only `iket13_trial/sampled_core.py` adds a task-local `block < 2` sampling condition to bound trace size. No sampling cutoff is included in `markers.patch`.
- The source remains frozen while any CuTe compilation is active. No production checkout or native JIT epoch was modified.

## Zero default overhead

`check_codegen.py` compares full SASS disassembly, normalizing only the kernel mangled symbol because changing the Python module name changes its fixed-length suffix. Every instruction, instruction offset, local label, directive, and control-flow operand remains in the comparison.

| Phase / tactic | Instructions | Disabled markers identical to original SASS |
|---|---:|---|
| FC1 logical M512/N128, two CTAs, two channel tiles | 2072 | yes |
| FC2 M256/N128, two CTAs | 1384 | yes |

Raw PTX, CUBIN, SASS and comparison diffs are archived in `results/disabled-codegen.tar.gz`. The machine-readable receipt is `results/iket13-disabled-codegen-comparison.json`. Both disabled-marker phase outputs matched all control bytes.

## Current NB2 traces

Native NVFP4 DeepSeek input, seed 42, T16384, hidden 7168, intermediate 2048, top-k 8, 32 local experts. Route tile 128, FC1 logical M512/N128 two CTA, FC2 M256/N128 two CTA. c1 B200 GPU1, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe DSL4.7.1. Same native routed input and captured returned allocations as the fixed-tactic diagnostic harness. These are instrumented diagnostics, not primary benchmark or retention evidence.

Each trace contains six instrumented launches; `analyze.py` summarizes the last one and preserves all sampled CTA/warp summaries. Both iKET tracker and profiling passes passed output/SF byte equality. Trace durations include substantial marker overhead and cannot be summed into an uninstrumented performance model.

Compressed raw traces and complete role summaries:

- `results/iket13-nv-nb2-fc1-r1.trace.json.gz` and `-summary.json`.
- `results/iket13-nv-fc2-r1.trace.json.gz` and `-summary.json`.

Representative leader-CTA observations:

| Range | FC1 NB2 | FC2 |
|---|---:|---:|
| Persistent output tiles | 16 | 54 |
| K stages observed | 448 | 432 |
| Mean MMA accumulator-empty wait / output tile | 4.328 us | 0.069 us |
| Mean epilogue body / output tile | 4.334 us | 2.170 us |
| Mean epilogue accumulator-ready wait / output tile | 17.886 us | 2.201 us |
| Mean warp0 A/SFA TMA issue / K stage | 128.6 ns | 117.3 ns |
| Mean warp0 activation Gather4 issue / K stage | 58.4 ns | not applicable |
| Mean local SF-ready wait / K stage | 78.4 ns | 59.1 ns |
| Mean peer SF-ready wait / K stage | 40.0 ns | 39.9 ns |
| Mean TMA-ready wait / K stage | 36.9 ns | 37.9 ns |

FC1's one accumulator window serializes the next output tile behind almost the whole epilogue. FC2 N128 has two accumulator stages and does not show that wait. This source-and-trace evidence motivates the separate `../nb2_overlap_experiment`; it does not itself establish the achievable speedup. Producer warp1 spends more time in SF-stage-reuse waits than warp0 because warp0 issues A/SFA; the trace does not prove that SF global traffic is the primary bottleneck.

## Reproduction

From the remote frozen candidate checkout:

```bash
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/run-iket \
  --output-dir ../logs/<new-name> --log-level info \
  profile --postprocess json --max-ts-cnt-per-warp 32768 -- \
  env DKG_IKET_INSTRUMENTATION_METHOD=NativeDump \
  ../.venv/bin/python ../scripts/iket13_experiment/probe_iket.py \
  --repo . --expected-head 13ca1475d96839f3bf3c46699cc63204b4d3b409 \
  --tokens 16384 --phases fc1 --variants sampled --profile \
  --tactic '[128,[[512,128],[2,1],false],[[256,128],[2,1],false]]' \
  --output ../logs/<new-name>.json
```

Use `--phases fc2` for FC2. `probe_iket.py` enables the constructor flag and compile option only for the sampled snapshot, and gives each iKET pass its own output file. Disabled codegen was produced with `CUTE_DSL_KEEP=ptx,cubin,sass`, `CUTE_DSL_DUMP_DIR=../logs/iket13-disabled-codegen`, `probe_native.py --variants baseline,marked --phases fc1,fc2 --profile` and the same tactic.
