# Retained 83df TP prefill stage diagnostic

Final retained source `83dfef8a656384f5cd10db847602593bb6f9b2c6`, TP8/EP1, 16,384 tokens, MXFP4x8, unfused finalize. Both captures used the **current full-refresh A2 managed winners** and matched its routing IDs/weights exactly. No autotuning, source changes, native-cache deletion, external-baseline rerun, or NCU collection occurred.

FC2 remains the largest timeline contributor for both models. K3 FC1 is now almost as large, so the remaining gap is no longer predominantly an FC2-output problem. V3 combine is also significant. The existing FC1/prepare overlap is much larger than FC2/FC1 overlap; these intervals include PDL waits and do not establish how much productive work overlaps.

| Model | Graph span µs | Prepare duration / extension µs | FC1 duration / extension µs | FC2 duration / extension µs | Combine duration / extension µs |
|---|---:|---:|---:|---:|---:|
| V3 TP8 | 1547.306 | 314.050 / 313.778 | 436.675 / 340.962 | 512.035 / 486.291 | 372.402 / 367.075 |
| K3 TP8 | 1867.004 | 335.250 / 334.418 | 653.444 / 553.747 | 659.924 / 648.708 | 326.994 / 321.779 |

Each cell is the median of 20 captures. “Extension” is the increase in the rightmost GPU-kernel end timestamp as kernels are visited in start order; it is additive within each individual graph and avoids double-counting overlapping duration. It also includes any intervening gap. It is **not** a dependency-DAG critical-path proof. Stage medians need not sum exactly to the median graph span.

| Model | Prepare extension / span | FC1 extension / span | FC2 extension / span | Combine extension / span | FC1 overlap with preceding work µs | FC2 overlap µs | Combine overlap µs |
|---|---:|---:|---:|---:|---:|---:|---:|
| V3 TP8 | 20.28% | 22.04% | 31.43% | 23.72% | 95.521 | 25.664 | 5.280 |
| K3 TP8 | 17.91% | 29.66% | 34.75% | 17.24% | 99.409 | 11.728 | 5.072 |

Routing contributes the remainder. V3 includes the top-k kernel (30.176 µs) plus expert routing; K3 shares precomputed model sigmoid routes, so that model routing remains outside capture, as in the public benchmark. Graph spans range from 1542.986–1555.786 µs for V3 and 1848.780–1894.604 µs for K3.

## Comparison with the saved d1767 diagnostic

K3 has the **same selected tactic** as the old profile: route128, FC1/FC2 M256N128 with two CTAs, K steps4/4, shared CLC off. Routing hashes match the associated saved d1767 A2 benchmark. The old profiler did not independently hash its captured routes, so that part is bound through its saved public-run receipt. Both profiles use the same public 20-replay/cold-L2 method, but different B300 GPUs and times; this is a stage diagnostic, not a paired latency-retention experiment.

| K3 TP8 stage | d1767 duration µs | 83df duration µs | d1767 extension µs | 83df extension µs |
|---|---:|---:|---:|---:|
| Prepare | 304.434 | 335.250 | 303.474 | 334.418 |
| FC1 | 651.556 | 653.444 | 581.780 | 553.747 |
| FC2 | 824.709 | 659.924 | 808.645 | 648.708 |
| Combine | 365.587 | 326.994 | 358.738 | 321.779 |
| Graph | 2062.092 | 1867.004 | — | — |

The current K3 timeline is consistent with a smaller FC2/output cost, while FC1 duration is similar and prepare remains substantial. The extra prepare duration is an observation, not a causal attribution to compact-offset construction.

V3's winner changed: old `[K4,K8]`, shared CLC on; current `[K4,K4]`, shared CLC off. Both use route256 and FC1/FC2 M256N256 with two CTAs. Its old 1736.870 µs and current 1547.306 µs graph spans therefore compare two retained configurations, **not the isolated effect of the source changes**. Full old/current stage and winner data remain in `analysis.json`.

The next source/profiler review should prioritize the remaining FC1+FC2 work and their narrow overlap window, then the visible prepare/combine traffic. This trace does not justify removing a particular barrier or changing warp ownership. Previous prepare ownership experiments remain rejected; the separate fixed-SF-index arithmetic experiment preserves that ownership and is not included in these traces.

## Capture and evidence

- Image: `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA13.2), NVIDIA B300 SXM6 AC, driver595.91.07, NSYS2026.2.1.210-262137639646v0.
- One GPU, serial cases: `fi-moe-sanitize-1028` GPU0, UUID `GPU-55ba4050-98dc-a313-f475-531a0b6f7934`. GPU0 was checked idle before launch and after both captures; no clocks were forced. Sampled post-capture SM clock2032MHz, memory3996MHz, temperature39°C. These are endpoint readings, not a continuous clock trace.
- All348 pinned source files and nine persistent native-cache links verified before/after. Managed winner files were unchanged, and any attempted tactic search was forbidden. Both v2 contexts were disabled for tuning and used `measure_execution_mode=cuda_graph`.
- Unmodified public `--profile-cuda` path: **three** warmup graph replays, then20 recorded graphs; a twice-L2-size flush precedes each graph. The benchmark CLI's `--warmup10 --iters100` values do not override this separate profiling branch. CUPTI benchmark medians in the public tables are unchanged.
- Existing untimed histogram routing outputs were observed without another routing invocation. IDs, weights, histogram, dtypes, shape, local expert count and offset matched the fresh A2 result. Initial MXFP8 activation quantization remains outside capture, matching the MX family benchmark contract.
- `evidence/` contains both original `.nsys-rep` files, SQLite exports, kernel CSVs, full commands/environment, source/runtime receipts, current-winner/route observations, and raw20-sample stage intervals in `analysis.json`. `evidence-verification.json` verifies32 raw files against the archive/manifest; `analysis.json` binds the resulting analysis to those hashes.
- `attempt1-helper-policy-field/` preserves a helper-only assertion failure before profiling began. The observer initially used `execution_mode` instead of the actual manifest key `measure_execution_mode`; only that diagnostic assertion was corrected. No reports or kernel failures resulted from the first attempt.

Full invocations/environment are in `evidence/receipt.json`. The NSYS command was:

```bash
nsys profile --trace=cuda,nvtx --cuda-graph-trace=node \
  --capture-range=cudaProfilerApi --capture-range-end=stop \
  --sample=none --cpuctxsw=none --output "$PROFILE_OUTPUT" \
  "$PYTHON" -u profile_entry.py --repo "$REPO" \
  --expected "$MODEL_EXPECTED" --output "$SELECTION_RECEIPT" -- \
  --functional-api --model "$MODEL" --ep 1 --tp 8 --quant-family mxfp \
  --backends cute-dsl-w4a8 --num-tokens 16384 --cache "$CURRENT_MANAGED_CACHE" \
  --no-autotune --profile-cuda --profile-backend cute-dsl-w4a8 --profile-iters 20 \
  --swap-ab --no-fused-finalize --warmup 10 --iters 100
```

`MODEL` is `v3` then `kimi-k3`; all variables resolve to the exact absolute paths recorded in the receipt. `profile_entry.py` adds read-only winner/route/policy assertions around the tracked benchmark, without replacing its public API or profiler capture.
