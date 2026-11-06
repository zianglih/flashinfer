# Multi-stage FC2 startup weight prefetch experiment

Frozen source: `flashinfer-pdl-weight-prefetch-multistage-review`, clean base `853aaf69d706b291afee477f738956b997033f53`, two-file unstaged patch `9cea43321866c8b08fa5b2371c436f78cbc1e46e6117838cbd960741e134dc07`. Full source receipt and patch: `evidence/pdl-weight-prefetch-multistage-r1/`. The original single-stage candidate remains frozen at patch `b4ac8987f5d221c579ea42f1a46b017a6591d59b23d854f4bdb35084e4126a44`.

The only kernel delta from single-stage is priming `min(actual operand stages, ceil_div(K,tile_k))` A/SFA stages with an independent producer state before the all-thread dependency wait. Each distinct stage acquires its existing full transaction expectation once. The ordinary producer starts at its original state and skips only those A/SFA acquisitions for its first work tile; B/SFB complete the expectations after the wait. Subsequent K-ring wrap and persistent work tiles use normal acquisition. No stage count, model, token, or geometry-specific threshold was added. Default-false private knobs, public API, FC1 GPU-release publication, same-memory-domain admission and no-work wait remain the single-stage contract documented in `../pdl_weight_prefetch_experiment/README.md`.

Scoped pre-commit passed (mypy/ruff included). On c2 B300 GPU2 with the same CUDA13.2 runtime, the bounded gate passed324 exact full-chain changing-data replays: K384/K2304, N16/N128, NVFP4/MXFP8/mixed, prefetch off/on and PDL off/on, shrinking routes and zero local work. A further27 NVN16K2304 replays with FC2 SM budget2 exercised subsequent persistent work tiles, with separately named PTX/SASS bound to exact compile results. All83 source pins remained unchanged. This is a focused diagnostic; no broad sanitizer run was requested.

The fixed screen runs V41 EP4 at tokens32/128/512 with original N16/M128 tactics, native10warmup/100cold-L2CUDAgraph/CUPTI timing on GPU2. Six same-GPU arms are C1/S1/M1/M2/S2/C2: clean853, frozen single-stage prefetch with publication, and frozen multi-stage prefetch with publication. NV then the two MX modes execute sequentially on the same GPU. Exact fresh-B300 routing identities and fixed tactic caches are verified per point, with source hashes before/after every arm. Results and helper receipts are under `evidence/pdl-weight-prefetch-multistage-r1-fixed/`.

Fixed diagnostics alone do not establish retention; any proposed retention needs both-model native AUTO comparisons. No production source, commits or PR body were changed by this experiment.

## Fixed result

All9 affected points improved in both clean-to-multi repeats. The unaffected W4A16 observations remain noise/control data.

| Backend | T | clean/multi | clean/single | single/multi | repeats clean/multi |
|---|---:|---:|---:|---:|---|
| CuteDSL W4A4 | 32 | 1.017542 | 1.006193 | 1.011280 | 1.016989/1.018096 |
| CuteDSL W4A16 | 32 | 0.997122 | 1.000745 | 0.996379 | 0.997037/0.997207 |
| CuteDSL W4A4 | 128 | 1.009001 | 1.002933 | 1.006051 | 1.007317/1.010688 |
| CuteDSL W4A16 | 128 | 1.002489 | 1.000380 | 1.002109 | 1.002109/1.002870 |
| CuteDSL W4A4 | 512 | 1.005491 | 1.002814 | 1.002670 | 1.004728/1.006254 |
| CuteDSL W4A16 | 512 | 0.999335 | 1.000283 | 0.999052 | 0.996850/1.001825 |
| CuteDSL MXFP8 | 32 | 1.010904 | 1.003611 | 1.007267 | 1.011093/1.010716 |
| CuteDSL W4A8 | 32 | 1.007583 | 1.003059 | 1.004510 | 1.006511/1.008656 |
| CuteDSL MXFP8 | 128 | 1.005916 | 1.002520 | 1.003388 | 1.005998/1.005834 |
| CuteDSL W4A8 | 128 | 1.005977 | 1.004118 | 1.001851 | 1.006337/1.005617 |
| CuteDSL MXFP8 | 512 | 1.005536 | 1.001583 | 1.003946 | 1.005928/1.005143 |
| CuteDSL W4A8 | 512 | 1.006180 | 1.000489 | 1.005688 | 1.005584/1.006776 |

The candidate remains unretained until the parent selects public wiring and completes both-model nativeAUTO retention.
