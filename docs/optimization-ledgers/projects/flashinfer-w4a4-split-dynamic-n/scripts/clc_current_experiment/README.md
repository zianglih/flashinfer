# One-item CLC on the composed blockscaled pipeline

Status: rejected for integration; isolated archive, production unchanged. Frozen control is
`442d2aa53f68b4640c3ab5118a76f1599ff60d34`. The parent owns retention and any
production integration. These fixed-tactic diagnostics do not replace AUTO
primary data or the original B1 baseline.

## Hypothesis and scope

The previous NB2 CLC screen measured FC1 283.951 / 276.735 / 290.3355 us
(static / CLC / static) on 7829-derived code. It was deferred before primary
retention, not conclusively rejected. The current pipeline releases protected
accumulator windows earlier; this can change the benefit of balancing variable
expert/route tile duration across persistent clusters.

This prototype ports the established W4A16 one-item CLC scheduler: one scheduler
warp per CTA, one metadata slot, full-warp response consumption, acquire the
metadata slot before requesting another item, and one terminal sentinel. The
current source changes only scheduling and its metadata storage. Existing
accumulator, operand and relay PipelineStates advance once per published work
item; accumulator phase is sequence parity, never the global work-tile index.
The old channel offset fix, actual SF footprint, protected-window release,
optional iKET markers, cache hints, constexpr wrapper dimensions and FC2 TMA SFB
remain present. FC2 and every non-NB2 geometry dispatch the exact frozen class.

Only FC1 logical M512/N128 uses CLC in this first experiment, across all six
input formats and both per-tensor/per-token output contracts. The extra warp
changes 288 to320 threads for homogeneous formats and160 to192 for mixed W4A8.
The metadata fields total64 bytes before alignment;128 bytes is reserved in
the existing epilogue-buffer fit calculation. Operand stage counts are unchanged.
The optional `scheduler_item` iKET range is disabled by default.

The route capacity is the existing `expert_idx` tensor extent. CLC cancels from
the corresponding upper-bound grid and filters entries after `num_tiles[0]`.
There is no token or model-size threshold. W4A16's one-wave capacity dispatch
would need an explicit blockscaled cache/host contract change because route
extent is currently runtime. It is deliberately deferred until the simple
CLC mechanism demonstrates a benefit; small native cases will expose overhead.

## Source evidence and avoided repeats

- `scripts/scheduler_experiment/NB2.md`: prior bounded NB2 CLC timing and exact
  check; no final retention claim.
- `scripts/scheduler_experiment/build_variants.py`: established one-slot recipe.
- `flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`,
  scheduler loop around1220: full-warp response, metadata acquire before query,
  padding exclusion and terminal publication.
- `flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py`, around220:
  geometry/residency-derived one-wave fallback.
- Sibling `flashinfer-w4a16/w4a16_optimization_experiments.md`, sections around
  2500–2760 and4060–4133: bundle2/4, one-lane response, FC2 CLC and reordered
  raster variants were rejected. One-item/full-warp/FC1-only/one-slot survives.
  We do not repeat the rejected changes.

## Validation and measurement contract

`check_static.py` verifies AST equality of all three role bodies after removing
only work acquisition/metadata loads, and equality of dynamic-MMA/Gather4/SFB
helpers and the constexpr wrapper. Its108 arbitrary-order work models are host
checks only, not proof of GPU synchronization. All task-local Python parses.

GPU work is confined to C1 GPU6, image `nvcr.io/nvidia/pytorch:26.05-py3`,
CUDA13.2/CuTeDSL4.7.1. `run_paired.py` restores output and scale allocations to
the same sentinel before each arm and compares every byte. The frozen numerical
control is442d. No production test file is added.

Native diagnostics use the unchanged DeepSeek benchmark preparation and routing,
H7168/I2048, top-k8,256 global/32 local experts. The fixed tactic is the latest
AUTO prefill selection: FC1 logicalM512/N128, FC2 M256/N128, both two CTA. The
T4096 run remains a diagnostic fixed-tactic comparison; its AUTO selection may
be N256. Each arm uses10 warmups and100 cold-L2 CUDA-graph/CUPTI samples, retaining
all samples and the median without filtering. Adjacent baseline/CLC/baseline and
reverse order are used. Final native outputs are compared exactly. Isolated
phase timings do not sum to the full-chain latency because residency differs.

From the remote candidate directory:

```bash
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=. ../.venv/bin/python ../scripts/clc_current_experiment/run_paired.py --script probe_fc1_formats.py
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=. ../.venv/bin/python ../scripts/clc_current_experiment/run_paired.py --script probe_boundaries.py
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=. ../.venv/bin/python ../scripts/clc_current_experiment/run_paired.py --script probe_edges.py
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=. ../.venv/bin/python ../scripts/clc_current_experiment/run_paired.py --script probe_relu2.py
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=. ../.venv/bin/python ../scripts/clc_current_experiment/probe_modes.py --repo . --expected-head 442d2aa53f68b4640c3ab5118a76f1599ff60d34 --mode nvfp4 --tokens 4096,8192,16384 --variants baseline,clc,baseline --output ../logs/clc442-nvfp4-r1-gpu6.json
```

Use mode `mxfp8` for homogeneous E4M3 and `mxfp4` for mixed W4A8 in the existing
native adapter. Repeat with `--variants clc,baseline,clc` into a distinct file.
## Results and decision

The parent agreed to keep this variant local. Across both orders, FC1 gains
about1.0% for NVFP4/MXFP8 and1.6% for mixed W4A8 over the three tested sizes.
The corresponding diagnostic whole-chain ratios are0.9998x,1.0080x and1.0062x.
These small averages are not stable retention evidence: NVFP4 T8192 is slower
in both orders; MXFP8 FC1 T8192 is slower in both orders; and the T16384 chain
result changes direction with run order for MXFP8 and mixed W4A8. The unchanged
FC2 control also drifts substantially at large MXFP8, so its apparent speedups
cannot be attributed to CLC. The extra scheduler warp, metadata pipeline and
launch policy are not justified. No production change, AUTO rerun, baseline
rerun or sanitizer run follows this rejected diagnostic.

82 sentinel-restored paired cases passed:24 six-format short/tail-K,44 protected
boundaries/long-K/SiTU/GELU,8 empty/single-route (including4 exact baseline N256
fallbacks),4 ReLU2 and6 explicit multiwave cases. The multiwave cases cover
NVFP4/MXFP8/W4A8, generated output scales and per-token BF16,130 live NB2 work
items plus34 padding items, preserving alternating accumulator phases under
CLC cancellation. All54 native timing arms completed with exact final-output
agreement within each three-arm group. This is equality to the frozen442d
implementation, not a new independent mathematical reference.

`results/` contains all17 raw logs/JSON files. The six JSON files retain every
100-sample FC1/FC2/chain distribution. `summarize.py` verifies complete runs,
sample counts, unchanged medians and identical routing histograms/valid-row
lists within each group. It writes `summary.json` and `results-table.md`.
`run-receipt.json` records normalized commands and source hashes;
`artifact-manifest.json` hashes the final archive. Critical overlay hashes in
all six run receipts match the local frozen source. All GPU6 processes are
finished and GPU6 was released to the parent.

The full measured medians are below. Mode `mxfp4` means mixed W4A8.

| Mode | Tokens | Run order | FC1 (us) | FC2 (us) | Whole chain (us) |
|---|---:|---|---|---|---|
| nvfp4 | 4096 | baseline/clc/baseline | 114.992 / 113.377 / 114.432 | 63.328 / 63.184 / 63.424 | 202.080 / 202.465 / 203.120 |
| nvfp4 | 8192 | baseline/clc/baseline | 151.488 / 151.265 / 151.952 | 90.688 / 90.656 / 90.688 | 301.313 / 301.921 / 301.345 |
| nvfp4 | 16384 | baseline/clc/baseline | 256.769 / 253.344 / 257.472 | 150.577 / 153.057 / 152.272 | 525.297 / 522.305 / 523.281 |
| nvfp4 | 4096 | clc/baseline/clc | 113.488 / 114.720 / 113.456 | 63.248 / 63.185 / 63.280 | 203.600 / 203.584 / 203.072 |
| nvfp4 | 8192 | clc/baseline/clc | 151.649 / 151.936 / 150.768 | 90.593 / 90.656 / 90.560 | 303.905 / 301.841 / 303.425 |
| nvfp4 | 16384 | clc/baseline/clc | 253.089 / 256.625 / 253.664 | 151.184 / 152.705 / 151.601 | 529.537 / 526.784 / 522.945 |
| mxfp8 | 4096 | baseline/clc/baseline | 199.408 / 192.177 / 198.976 | 104.608 / 104.704 / 104.656 | 330.257 / 327.169 / 329.649 |
| mxfp8 | 8192 | baseline/clc/baseline | 240.096 / 243.825 / 240.416 | 152.928 / 151.424 / 152.400 | 455.121 / 457.009 / 468.065 |
| mxfp8 | 16384 | baseline/clc/baseline | 417.648 / 413.825 / 418.049 | 302.352 / 268.448 / 296.129 | 797.874 / 790.673 / 795.665 |
| mxfp8 | 4096 | clc/baseline/clc | 191.728 / 199.168 / 192.288 | 104.672 / 104.593 / 104.640 | 328.785 / 330.145 / 327.153 |
| mxfp8 | 8192 | clc/baseline/clc | 243.745 / 240.129 / 243.841 | 151.201 / 152.176 / 152.176 | 460.322 / 470.801 / 456.481 |
| mxfp8 | 16384 | clc/baseline/clc | 414.369 / 418.817 / 416.577 | 252.336 / 286.433 / 267.633 | 795.265 / 790.529 / 803.874 |
| mxfp4 | 4096 | baseline/clc/baseline | 147.552 / 144.080 / 147.297 | 80.704 / 80.784 / 80.864 | 252.624 / 249.360 / 253.409 |
| mxfp4 | 8192 | baseline/clc/baseline | 230.849 / 228.849 / 230.944 | 129.553 / 131.089 / 129.792 | 418.513 / 416.560 / 419.809 |
| mxfp4 | 16384 | baseline/clc/baseline | 405.921 / 399.328 / 405.728 | 224.960 / 225.073 / 236.129 | 757.010 / 762.274 / 746.626 |
| mxfp4 | 4096 | clc/baseline/clc | 144.064 / 147.201 / 144.016 | 80.896 / 80.832 / 80.688 | 249.792 / 252.209 / 249.536 |
| mxfp4 | 8192 | clc/baseline/clc | 228.736 / 231.072 / 228.849 | 130.912 / 129.377 / 131.968 | 414.529 / 416.929 / 414.240 |
| mxfp4 | 16384 | clc/baseline/clc | 397.264 / 405.729 / 400.240 | 235.361 / 224.641 / 228.320 | 739.378 / 750.594 / 741.297 |
