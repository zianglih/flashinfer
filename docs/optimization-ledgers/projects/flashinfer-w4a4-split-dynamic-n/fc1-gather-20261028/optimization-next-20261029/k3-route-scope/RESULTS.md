# K3 route and timing-scope diagnostic

Changing only the routing tensor reverses the N128/N256 ranking on the retained kernel. This establishes that the balanced native routing distribution is sufficient to cause the observed K3 EP8 W4A4 selection reversal; graph/event timing and omission of the input quantizer are not necessary for the reversal.

K3 EP8, 8192 tokens, retained `c0c0bc41` kernel SHA `3225acf2…`, B300 GPU7 on `fi-gather-opt-1029`, CUDA13.2, CuTe DSL4.8.0, image `nvcr.io/nvidia/pytorch:26.05-py3`. Positive percentages mean N256 is faster. Each scope/timer uses old/new/new/old, 100 samples per phase, 10 warmups, explicit 2×L2 flushing; medians combine geometrically. Both timing implementations replay the exact same captured graph for a given scope/tactic.

| Scope | Timer | N128 us | N256 us | N256 change | N128/N256 spread |
|---|---|---:|---:|---:|---:|
| runner_balanced | graph_events | 516.685 | 503.562 | +2.606% | 2.068% / 0.951% |
| runner_balanced | graph_cupti | 506.868 | 491.852 | +3.053% | 0.190% / 0.042% |
| runner_actual | graph_events | 480.740 | 518.743 | -7.326% | 0.825% / 1.987% |
| runner_actual | graph_cupti | 471.543 | 506.659 | -6.931% | 1.477% / 0.297% |
| full_actual | graph_events | 488.215 | 526.896 | -7.341% | 0.358% / 1.121% |
| full_actual | graph_cupti | 481.991 | 516.732 | -6.723% | 0.883% / 0.102% |

- **Controlled data:** the original benchmark constructs its seeded inputs and captures the public functional MoE runner inputs. Actual routes match the earlier published route-ID and route-weight hashes. The real unchanged `inputs_pre_hook` generates the balanced route tensor. Every other tensor—including quantized activations, scales, weights, token weights and output—uses the identical pointer, shape and stride in both runner arms. Neither source nor cached selections are changed.
- **Routing:** actual local expert counts 64–252, 16,464 assignments, 185 N128 tiles/112 N256 tiles. The native helper actually produces 147–148 per expert, 16,569 assignments, 224 N128 tiles/112 N256 tiles. These measured route counts confirm the earlier source-based target calculation. The histogram is saved in raw results.
- **Tactics:** both FC1 and FC2 use two-CTA M256, K-step pair (4,4), static scheduling. Only routing/MMA-N tile changes 128→256. These are the exact old/new native winners, forced only in this local diagnostic; no production tuning rule is changed.
- **Scope:** `runner_actual` excludes initial activation quantization and router execution. `full_actual` captures the original benchmark quantize→route→MoE closure. Both include the retained prepare/FC1/FC2/combine chain. The additional full-chain work does not change the ranking. Timer absolute values differ and some event pairs have about 2% spread; the routing reversal has the same sign under both timers and is larger than the paired spread.
- **Guard/provenance:** all 513 source hashes and source patch verified before/after; four runtime register checks pass, all zero local bytes. All 2,400 raw samples verified. Archive 9 files, SHA `5dcf826a8a611a8185986685d14dc088a6e4efe6c35fb0e3952f5e30354e05af`. Future CuTe DSL disk cache is explicitly persistent via `CUTE_DSL_CACHE_DIR`, with strict source keys and the original nine native C++ cache links.
- **Boundary:** this is one controlled K3 EP shape, not a justification to remove the intentional approx-max-load simulation. The native hook provides deterministic balanced load for general tuning; any replacement needs an explicit general contract and broader evidence. K3 TP selection has not received this controlled route probe. Production source, API, tuning defaults, native84 caches and PR performance tables are untouched.

Full raw results: `evidence/results.json`; source/launch binding: `evidence/launch.json`; analysis: `summary.json` and `analyze.py`. GPU7 released after completion.
