# Cross-model BEFORE and AUTO evidence

Untrimmed median of 100 CUPTI per-iteration rank-MAX spans per point; one fresh EP8 process group per arm.
Separate CUDA-event AUTO scoreboards; not pooled with final CUPTI spans.
Only tokens 1 and 2 are excluded from aggregates; 512 and all prefill points remain included.

## deepseek-v41-flash

Measured expanded24 selector; final16 body evidence can be reused only if all13 rank-agreed winners are members. Does not measure final16 selector cost/tie order.

BEFORE `dsv41-flash-before-v1` versus `dsv41-flash-expanded-auto-v1` (24 candidate tactics). Complete: False.

| Tokens | BEFORE µs | BEFORE tactic | Candidate µs | Candidate tactic | Speedup |
|---:|---:|---|---:|---|---:|
| 1 | 62.209 | M256/N64/G512/epi | pending | pending | pending |
| 2 | 66.368 | M256/N64/G1024/epi | pending | pending | pending |
| 4 | 71.745 | M256/N64/G512/epi | pending | pending | pending |
| 8 | 86.481 | M256/N64/G1024/epi | pending | pending | pending |
| 16 | 102.337 | M256/N64/G1024/epi | pending | pending | pending |
| 32 | 122.593 | M256/N64/G512/epi | pending | pending | pending |
| 64 | 172.002 | M256/N64/G1024/epi | pending | pending | pending |
| 128 | 210.706 | M256/N64/G1024/epi | pending | pending | pending |
| 256 | 214.770 | M256/N64/G512/epi | pending | pending | pending |
| 512 | 217.011 | M256/N64/G512/epi | pending | pending | pending |
| 4096 | 332.755 | M256/N128/G1024/dispatch | pending | pending | pending |
| 8192 | 500.949 | M256/N128/G1024/dispatch | pending | pending | pending |
| 16384 | 873.786 | M256/N128/G1024/dispatch | pending | pending | pending |

All 13 winners belong to retained16: None.


## glm5

Measured owner-selected final catalog on all13 points; saved same-model BEFORE reused. No cross-model latency comparison.

BEFORE `glm5-before-v1` versus `glm5-final-auto-v1` (16 candidate tactics). Complete: False.

| Tokens | BEFORE µs | BEFORE tactic | Candidate µs | Candidate tactic | Speedup |
|---:|---:|---|---:|---|---:|
| 1 | pending | pending | pending | pending | pending |
| 2 | pending | pending | pending | pending | pending |
| 4 | pending | pending | pending | pending | pending |
| 8 | pending | pending | pending | pending | pending |
| 16 | pending | pending | pending | pending | pending |
| 32 | pending | pending | pending | pending | pending |
| 64 | pending | pending | pending | pending | pending |
| 128 | pending | pending | pending | pending | pending |
| 256 | pending | pending | pending | pending | pending |
| 512 | pending | pending | pending | pending | pending |
| 4096 | pending | pending | pending | pending | pending |
| 8192 | pending | pending | pending | pending | pending |
| 16384 | pending | pending | pending | pending | pending |

All 13 winners belong to retained16: None.


Adjacent JSON retains all raw samples, quartiles, selected tactics, eight-rank receipts, model/source/runtime identities, and input hashes.
