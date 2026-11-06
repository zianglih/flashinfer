# FlashInfer #5187: B300 CUB Top-K before/after evidence

No material performance regression was observed in this scoped validation. The 304 comparable CUB workloads changed by +0.006% geometrically; none met the predeclared regression screen (at least 5% and 0.25 microseconds slower). The 24-workload longer-batch follow-up did not reproduce the increase in the selected small-row cases; it does not rerun every broad case with an increase. All 125 final-head correctness tests passed.

- PR: https://github.com/flashinfer-ai/flashinfer/pull/5187
- Before: `93e9eef092c11bc93a6f432a16404054e85d19c5`.
- After: `30b1b2e6d12792951309b607b9e009d791aed7b8`.
- CCCL unchanged: `16bd510c9b712e82b0ab6cbb630d8e29ba1f7116`; actual source checkouts and include links verified.
- Container: `nvcr.io/nvidia/pytorch:26.05-py3`.
- Hardware: GPU 0 of an 8-GPU NVIDIA B300 SXM6 AC node, SM10.3, GPU UUID `GPU-35bac470-aab6-9e0d-e54b-5d3842d60401`; only GPU 0 used.
- Driver `590.48.01`; CUDA toolkit `13.2.78`; Python `3.12.3`; PyTorch runtime `2.12.0a0+5aff3928d8.nv26.05`; FlashInfer `0.7.0` at the exact commits above; apache-tvm-ffi `0.1.11`; numpy `2.1.0`; ninja `1.13.0`; pytest `8.4.2`.
- Separate clean source trees, virtual environments, and source JIT caches; no AOT/prebuilt FlashInfer cubin/JIT-cache packages. Before/after compiled binaries are preserved locally; their SHA256 values are `e383d91d8cb017e0571f6f95ebd1a52a4ce38c9ffbe148941ab61a7b24f1e340` and `e18dea3a20325df8c47797dab6667ee0d4e1e9d0c1dec254422df9298b03243a` respectively.
- `CUDA_VISIBLE_DEVICES=0`, `FLASHINFER_CUDA_ARCH_LIST=10.3a`, `FLASHINFER_NVCC_THREADS=4`, `NVCC_THREADS=4`, `MAX_JOBS=4`, `OMP_NUM_THREADS=4`; backend forced to `cub` or `default` within each process. GPU clocks were not locked or changed. GPU state and compute-process lists were recorded at each arm boundary; no other listed compute process was present when an arm started.

## Workload and measurement

The main random distribution and representative batch/width/K/API/dtype coverage follow PR #4442 (https://github.com/flashinfer-ai/flashinfer/pull/4442); this is a fresh before/after comparison, not a comparison against its historical B200 times.

The exact 394 workload IDs are in `broad-matrix.json`, each evaluated with CUB and native `default`: 788 records/arm, three alternating pairs, 4,728 records. Per-arm record counts are 668 FP32, 60 FP16, 60 BF16. SMALL and LARGE ties, plain/page/page+raw/ragged, physical-short, logical-short/windowed/empty/mixed, normal widths, equality, K=256/2048/4096/8193, and a separate deliberate pivot-tie diagnostic are included. Batch sizes are 1/4/32/128/256; widths span 64 through 131072. The grid is deliberately sparse, not a Cartesian product. Exact input scores are seeded and hashed identically across arms.

All successful calls are checked against exact CPU selected-set references before timing, including tie semantics, mapping, value/index alignment, and padding. Each before arm has 658 successful timings, 90 expected CUB physical-short assertion failures, and 40 native K-limit exclusions. Each after arm has 748 successful timings and 40 native exclusions. Unsupported calls are never assigned timings or speedups. Native graph-safe/tie-break calls reject K>2048 in the unchanged dispatcher.

CUDA events measure the complete captured public API GPU work divided by the number of calls, including every selection, mapping, padding, and native plain-index-conversion launch. `dsa_graph_safe=True`, `sorted=False`, `deterministic=False`; `cold_l2_cache=False` (input buffers reused), `enable_cupti=False`. Main: 100 calls/graph, 10 warmup replays, 30 measured samples. The helper also performs its standard eager warmups and graph duration estimation before the requested warmup/sample loops. Order: before/after, after/before, before/after; case-order seeds 20260913/14/15. JIT, allocation, capture, CPU reference checking, host dispatch, and host/device transfers are outside the timed metric. This differs from #4442's cold-L2 CUPTI metric.

Targeted follow-up: 24 of the main workload IDs at batch 1 FP32, all API/tie variants for d/K=2048/2048,4096/2048,16384/256; 48 records/arm, three alternating pairs, 500 calls/graph and 100 measured samples, seeds 20260923/24/25. All 288 targeted records timed successfully. The broad dataset remains unchanged.

Limitations: one B300 GPU, graph replay with reused inputs, selected shapes and dtypes; no eager host-overhead benchmark, cold-L2/CUPTI rerun, full #4442 grid, end-to-end SGLang throughput, or other-architecture performance claim. Small differences below the screen remain reported; this is not a claim of identical latency for every input.

## Files and reproduction

- `RESULTS.md`: complete result tables and explanation of the targeted rerun.
- `broad-{before,after}-r{0,1,2}.json` and `targeted-...json`: every raw sample plus source, binary, input, environment, command, and timing provenance. CSV/log companions retain every emitted record.
- `broad-paired.csv` / `targeted-paired.csv`: every comparable case, each round's medians, paired ratios, and screen results. `broad-excluded.csv` preserves unsupported comparisons. Targeted exclusions and both final screen-hit lists are empty, as recorded in each `analysis.json`.
- `*-telemetry.json`, `*-commands.json`, and `*-build.ninja`: actual GPU snapshots, executed commands/environment, and native compiler commands.
- `correctness-*`: final 125-test raw log/XML, metadata, environment, and verified summary.
- `SHA256SUMS`: checksums of every other published file.

Download this gist's files together. The consolidated reproduction script recreates the separately executed setup/runner steps; it was syntax-checked, not rerun end-to-end as a second full experiment. The original executed driver scripts and exact per-arm command records are also included.

```bash
docker run --rm --gpus 'device=0' --ipc=host \
  -v "$PWD:/work" -w /work nvcr.io/nvidia/pytorch:26.05-py3 \
  bash reproduce_cub_performance.sh /work/fresh-reproduction
```

To reanalyze the already recorded files without a GPU:

```bash
mkdir -p broad targeted
for prefix in broad targeted; do
  for arm in before after; do
    for round in 0 1 2; do
      cp "$prefix-$arm-r$round.json" "$prefix/$arm-r$round.json"
    done
  done
  python3 analyze_cub_before_after.py "$prefix"
done
python3 summarize_cub_performance.py broad
```
