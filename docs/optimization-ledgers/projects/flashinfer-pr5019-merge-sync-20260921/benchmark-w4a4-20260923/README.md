# Native distributed W4A16 / W4A4 MegaMoE comparison

This folder owns local review artifacts for the upstream FlashInfer #5019
benchmark extension. The campaign runs the native repository benchmark;
`worker.py` adds evidence outside its timed regions. It does not patch the
native forward, timer, graph capture, or rank aggregation.

## Fixed measurement contract

- EP4 and EP8 on B300, H7168/I2048/E256/top-k8. The runner requires the exact
  container image and a bootstrap log/receipt, and records actual GPU UUIDs,
  driver/topology, compiler, Python/Torch and package versions.
- Global tokens: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384.
  Decode summaries use 4–512; 1/2 remain visible and prefill is inspected per row.
- BF16 source inputs, shared canonical NVFP4 weight bytes, identical precomputed
  routes, FP32 routing scores, FC2 routing placement. Split uses
  `--no-fused-finalize`; both Mega variants disable in-kernel FC2 reduction.
  Mega W4A4 uses native per-tensor activation quantization within public forward.
- Two native sweeps per EP, each with a new process and empty Mega knob cache.
  Preserve the fixed per-token order: Split W4A16, Mega W4A16, Mega W4A4.
  All three variants use their full native autotuners, with no tactic override.
- Three warmups and 100 cold-L2 CUDA-graph CUPTI samples per row per sweep.
  Each rank reports the first-to-last GPU-activity span, including gaps/overlap;
  aggregate each sample by rank MAX. Pool both sweeps' 200 samples, take the
  median, and do not trim. Quantization of weights, routing, preparation,
  compilation, tuning, warmup, capture and L2 flushing are outside timing.
- `cupti_lifecycle.py` is byte-identical to the previous alpha-batching helper.
  It retains callback ownership and defers detach until the entire native
  benchmark exits and synchronizes. Native per-row activity enable/flush/disable
  and measured callables are unchanged.
- The observer hashes canonical weights before arms and inputs/routes before
  each arm's warmup. Two extra eager forwards after the whole timed row check
  finite logical BF16 outputs and record raw-bit equality. W4A16 repeats must
  match; W4A4 repeat equality is reported but not required. No cross-precision
  equality, independent reference check, or per-timed-replay output claim.

## Launch

Upload these helpers outside the source checkout and record the candidate
benchmark patch identity with the revision. Do not run sweeps concurrently on the same GPUs. EP4 and EP8 may run on separate matched nodes.
The runner refuses an existing output directory or an active GPU process.
It cleans inherited tuning overrides and sets isolated writable cache paths.

```bash
python run_sweep.py \
  --source /workspace/flashinfer \
  --revision '<base commit plus benchmark patch SHA256>' \
  --image 'nvcr.io/nvidia/pytorch:<explicit tag>' \
  --bootstrap-receipt /workspace/bootstrap.log \
  --ep 4 --sweep 1 --output results/ep4-sweep1 \
  --compile-cache /workspace/benchmark-compile-cache
```

Repeat with EP4/sweep2, EP8/sweep1 and EP8/sweep2. Both sweeps for one EP must
use the same node, boot and physical GPU set. The default timeout is six hours
per sweep; `--timeout` and `--master-port` are the only operational overrides.
No workload or timing parameter override is exposed.

Core source trees, native benchmarks and helper hashes are recorded before
launch and verified unchanged afterward. Bootstrap and device/package receipts,
the exact command, controlled environment, exit code and full stdout/stderr
are retained. Each rank has a separate JSONL for fixtures, tactic selections,
raw samples, output checks and CUPTI lifecycle. Native rank-MAX sample JSON is
captured directly before printing, avoiding interleaved multi-rank stdout.

## Render and validate

```bash
python render_results.py \
  results/ep4-sweep1 results/ep4-sweep2 \
  results/ep8-sweep1 results/ep8-sweep2 \
  --output final-performance
```

The renderer requires all 13 rows, all three arms and all ranks in both sweeps.
It verifies exact execution order; same fixture hashes across arms/sweeps;
same source, native timer and helper hashes; successful exits; finite outputs;
all-rank tactic consensus; and exact reconstruction of every rank-MAX sample.
Only complete, valid campaigns produce final tables. Partial runs remain raw
evidence and are not promoted into pooled medians.

The main columns remain in the requested order: tokens, Split W4A16 µs, Mega
W4A16 µs, Split/Mega W4A16, Mega W4A4 µs, Mega W4A4/Mega W4A16. Both ratios
are speedups of Mega W4A16; greater than one means it is faster. A secondary
table records both sweeps' effective tactics for both Mega variants. The JSON
also retains complete configs, pooled MADs, per-sweep and 25-sample medians,
plus evidence-file hashes. The renderer does not edit the PR body or publish
anything.

## Controller split receipt

The initial controller scheduled all four sweeps on the first node. During
EP4/sweep1, only the outer controller (PID 4433) was terminated; the existing
`run_sweep.py` (PID 4434), torchrun (PID 4497), and GPU workers remained alive.
A separate `run_ep_pair.py` controller waits for the successful finalized first
EP4 receipt before starting EP4/sweep2 with the unchanged runtime helpers.
EP8 uses its own identical node and two serial sweeps. `controller-split.json`
and pair-launch receipts retain the exact processes and commands. This changes
orchestration only; timed code, helper hashes, arm order, tuning catalog,
sample count and per-EP comparison host remain fixed.
