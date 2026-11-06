# Cross-model BEFORE and AUTO evidence

Untrimmed median of 100 CUPTI per-iteration rank-MAX spans per point; one fresh EP8 process group per arm.
Separate CUDA-event AUTO scoreboards; not pooled with final CUPTI spans.
Only tokens 1 and 2 are excluded from aggregates; 512 and all prefill points remain included.

## deepseek-v41-flash

Measured expanded24 selector; final16 body evidence can be reused only if all13 rank-agreed winners are members. Does not measure final16 selector cost/tie order.

BEFORE `dsv41-flash-before-v1` versus `dsv41-flash-scheduler-off-auto-v1` (24 candidate tactics). Complete: True.

| Tokens | BEFORE µs | BEFORE tactic | Candidate µs | Candidate tactic | Speedup |
|---:|---:|---|---:|---|---:|
| 1 | 62.209 | M256/N64/G512/epi | 66.897 | M256/N32/G1024/epi | 0.9299× |
| 2 | 66.368 | M256/N64/G1024/epi | 67.201 | M128/N32/G1024/epi | 0.9876× |
| 4 | 71.745 | M256/N64/G512/epi | 60.881 | M128/N32/G512/epi | 1.1785× |
| 8 | 86.481 | M256/N64/G1024/epi | 88.034 | M128/N32/G512/epi | 0.9824× |
| 16 | 102.337 | M256/N64/G1024/epi | 103.201 | M128/N32/G512/epi | 0.9916× |
| 32 | 122.593 | M256/N64/G512/epi | 130.545 | M128/N32/G1024/epi | 0.9391× |
| 64 | 172.002 | M256/N64/G1024/epi | 167.490 | M128/N32/G1024/epi | 1.0269× |
| 128 | 210.706 | M256/N64/G1024/epi | 204.209 | M128/N32/G512/epi | 1.0318× |
| 256 | 214.770 | M256/N64/G512/epi | 208.369 | M128/N32/G1024/epi | 1.0307× |
| 512 | 217.011 | M256/N64/G512/epi | 212.242 | M128/N32/G1024/epi | 1.0225× |
| 4096 | 332.755 | M256/N128/G1024/dispatch | 333.748 | M256/N128/G512/epi | 0.9970× |
| 8192 | 500.949 | M256/N128/G1024/dispatch | 503.111 | M256/N128/G512/dispatch | 0.9957× |
| 16384 | 873.786 | M256/N128/G1024/dispatch | 860.361 | M256/N128/G1024/dispatch | 1.0156× |

All 13 winners belong to retained16: True.

- all11: geometric-mean speedup 1.0178× (+1.746% latency reduction).
- decode4_through512: geometric-mean speedup 1.0235× (+2.293% latency reduction).
- prefill4096_8192_16384: geometric-mean speedup 1.0027× (+0.273% latency reduction).

## glm5

Measured owner-selected final catalog on all13 points; saved same-model BEFORE reused. No cross-model latency comparison.

BEFORE `glm5-before-v1` versus `glm5-final-auto-v1` (16 candidate tactics). Complete: True.

| Tokens | BEFORE µs | BEFORE tactic | Candidate µs | Candidate tactic | Speedup |
|---:|---:|---|---:|---|---:|
| 1 | 64.481 | M256/N64/G512/epi | 66.769 | M128/N32/G1024/epi | 0.9657× |
| 2 | 84.833 | M256/N64/G1024/epi | 84.481 | M256/N32/G512/epi | 1.0042× |
| 4 | 92.497 | M256/N64/G1024/epi | 93.377 | M256/N32/G1024/epi | 0.9906× |
| 8 | 113.408 | M256/N64/G1024/epi | 109.169 | M128/N32/G512/epi | 1.0388× |
| 16 | 124.528 | M256/N64/G1024/epi | 120.946 | M256/N32/G512/epi | 1.0296× |
| 32 | 142.401 | M256/N64/G512/epi | 143.249 | M256/N32/G1024/epi | 0.9941× |
| 64 | 156.881 | M256/N64/G1024/epi | 158.530 | M256/N32/G512/epi | 0.9896× |
| 128 | 165.665 | M256/N64/G512/epi | 162.802 | M256/N32/G1024/epi | 1.0176× |
| 256 | 169.761 | M256/N64/G1024/epi | 155.793 | M256/N32/G1024/epi | 1.0897× |
| 512 | 172.817 | M256/N64/G1024/epi | 165.890 | M256/N32/G512/epi | 1.0418× |
| 4096 | 396.435 | M256/N128/G1024/dispatch | 389.060 | M256/N128/G1024/dispatch | 1.0190× |
| 8192 | 662.869 | M256/N128/G1024/dispatch | 657.639 | M256/N128/G1024/dispatch | 1.0080× |
| 16384 | 1232.413 | M256/N128/G512/dispatch | 1229.966 | M256/N128/G512/dispatch | 1.0020× |

All 13 winners belong to retained16: True.

- all11: geometric-mean speedup 1.0197× (+1.929% latency reduction).
- decode4_through512: geometric-mean speedup 1.0235× (+2.294% latency reduction).
- prefill4096_8192_16384: geometric-mean speedup 1.0096× (+0.952% latency reduction).

Adjacent JSON retains all raw samples, quartiles, selected tactics, eight-rank receipts, model/source/runtime identities, and input hashes.
