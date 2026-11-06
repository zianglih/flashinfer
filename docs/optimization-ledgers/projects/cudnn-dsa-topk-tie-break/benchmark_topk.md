# DSA top-k benchmark

`benchmark_topk.py` compares the unchanged `bc981788b0901a74accbdd93468eff12a0c764e1`
top-k implementation with candidate policies 0 (arbitrary cutoff ties), 1
(smaller source index), and 2 (larger source index). It is a standalone API
microbenchmark, not a model benchmark. No output sorting or deterministic slot
order is required or inferred.

The script has not been GPU-validated locally. Its CPU oracle self-test and
Python compilation pass; actual GPU results belong to the generated artifacts.

## Source admission and commands

The baseline may be the existing `git archive` extraction containing only the
operation directory. On the local machine, after the candidate source is final:

```bash
cd /Users/ziangli/playground/projects/cudnn-dsa-topk-tie-break
python3 benchmark_topk.py --baseline baseline --candidate cudnn-frontend \
  --write-source-manifest benchmark-source-manifest.json
```

This verifies baseline bytes against the exact Git tree and records the
candidate head, dirty status, source hashes, diff hash, shared helper hashes,
and harness hash. It never imports a GPU package. The output must not already
exist. Regenerate under a fresh name after source or harness changes.

Stage the whole selected project using the orchestrator's normal sync process.
No `.git` directory is required remotely. The harness verifies actual source
and imported helper bytes before timing and rechecks source bytes at completion.
It requires the main `cudnn` package to resolve to the candidate checkout.

On the allocated worker, with the provisioned Python environment:

```bash
cd /root/cudnn-dsa-topk-tie-break
export PYTHONPATH="$PWD/cudnn-frontend/python${PYTHONPATH:+:$PYTHONPATH}"
python benchmark_topk.py --baseline baseline --candidate cudnn-frontend \
  --source-manifest benchmark-source-manifest.json \
  --quick --output results/smoke-forward > results-smoke-forward.log 2>&1
python benchmark_topk.py --baseline baseline --candidate cudnn-frontend \
  --source-manifest benchmark-source-manifest.json \
  --output results/full-forward > results-full-forward.log 2>&1
python benchmark_topk.py --baseline baseline --candidate cudnn-frontend \
  --source-manifest benchmark-source-manifest.json \
  --construction-order reverse --output results/full-reverse \
  > results-full-reverse.log 2>&1
```

Each result directory is exclusive: failed/partial attempts remain intact.
`complete.json` is written only after all cells pass. No timeout silently
reduces the matrix. `--quick` runs one shape; report it as a smoke test.

## Matrix and correctness

| Rows | Width | k | dtype |
|---:|---:|---:|---|
| 1 | 4096 | 512 | FP32 |
| 32 | 32768 | 2048 | FP32 |
| 256 | 65536 | 2048 | FP32 |
| 1 | 131072 | 2048 | FP32 |
| 32 | 65536 | 512 | FP32 |
| 256 | 4096 | 512 | FP32 |
| 32 | 32768 | 2048 | BF16 |
| 1 | 131072 | 512 | BF16 |

Each shape runs random, duplicate-rich, all-equal, and two sparse-cutoff
distributions with `return_val=False` and `True`: **80 cells × 4 variants**.
Sparse-cutoff cases have k−1 strict winners and two ties near the left or right
end. Selecting one tie from the opposite direction requires nearly a full-row
scan. Cases share compiled specializations across distributions, limiting JIT
cost; expected wall time depends on the installed compiler/cache.

Inputs and the independent oracle are generated on CPU. BF16 quantization is
performed there, and the oracle uses those actual stored values. IEEE bit order
distinguishes +0 from −0. Mode 0 must return the exact top-k key multiset;
modes 1/2 must return the exact selected index set. All rows also require valid,
unique indices and bit-exact returned values. Invalid columns are poisoned with
+infinity. Separate untimed FP32/BF16 probes put valid infinities and signed
zeros at the cutoff. NaNs and `next_n>1` are outside this matrix.

All four variants receive the same input/length addresses. A shifted and
modified input is copied into the same allocation, then each captured graph is
replayed and rechecked against a fresh oracle; even the all-equal case changes.
The original input is restored before timing. CPU generation, copies, hashing,
oracle evaluation, JIT, and correctness synchronization are outside timings.

## Timing and interpretation

- **Warm CPU enqueue:** five raw samples of 20 public wrapper calls, with an
  untimed queue drain before/after each sample. Includes normal Python dispatch,
  allocation and FFI launch costs. Excludes the final completion wait; queue
  backpressure can still affect submission wall time.
- **Graph GPU timeline:** each graph contains 16 calls; CUDA events enclose
  eight replays. Five raw samples are normalized per API call. This includes
  every GPU operation emitted by the wrapper and amortized graph submission
  gaps, not just one isolated kernel. Host allocation during capture is excluded.
- Compilation/warmup precedes measurement. Three warmed calls are enclosed by
  `torch.cuda.set_sync_debug_mode("error")`, restored before explicit harness
  synchronization. This detects supported PyTorch sync operations, not every
  possible direct driver call.
- Baseline and each candidate policy use separate imported operation modules
  and Python compilation caches. The mode-0 candidate is the unchanged-policy
  control. This does not prove separate binary code placement.
- Sample order alternates forward/reverse, with CPU and GPU phases opposite.
  A separate `--construction-order reverse` run reverses initial compile/capture
  order. Inputs share addresses within each cell; wrapper-owned outputs and
  scratch are not address-matched. This API exposes no preallocated-output path.
- No cache flush, locked clocks, or representative production concurrency is
  imposed. Compare raw per-cell distributions before interpreting small deltas.
  This evidence cannot establish full-model training or serving speedups.

`metadata.json` records environment/provenance/method; `cells.jsonl` preserves
every timing sample, input hashes, addresses and verification receipts;
`summary.csv` gives medians and ratios. `gpu_speedup_vs_base` is baseline latency
divided by variant latency; `gpu_ratio_vs_candidate0` is variant latency divided
by candidate-mode-0 latency. Preserve both construction-order runs independently.
