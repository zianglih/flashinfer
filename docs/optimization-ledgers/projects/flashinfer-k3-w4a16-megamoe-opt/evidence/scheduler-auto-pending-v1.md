# Scheduler ON/OFF with native AUTO24

Untrimmed median of 100 CUPTI per-iteration rank-MAX spans; one fresh EP8 process group per arm.
ON speedup versus OFF = OFF median / ON median; above1 favors retaining the scheduler change. Positive ON latency reduction also favors ON.
Only tokens1/2 excluded from phase aggregates. Keep all13 rows. No numeric retention threshold or conclusion is invented; user requires a clearly visible benefit.
Both sides independently use AUTO24; selected tactics may change. This is the requested AUTO policy comparison, not a fixed-tactic causal estimate. Existing ON and original BEFORE controls are reused without sample pooling. Hot selection scoreboards are separate.

## deepseek-v41-flash

Complete: False; same full24 catalog and order.

| Tokens | ON µs | ON tactic | OFF µs | OFF tactic | ON speedup vs OFF | Tactic changed |
|---:|---:|---|---:|---|---:|---|
| 1 | 64.561 | M128/N32/G512/epi | pending | pending | pending | None |
| 2 | 68.689 | M128/N32/G1024/epi | pending | pending | pending | None |
| 4 | 72.512 | M128/N32/G1024/epi | pending | pending | pending | None |
| 8 | 87.201 | M128/N32/G1024/epi | pending | pending | pending | None |
| 16 | 102.657 | M128/N32/G1024/epi | pending | pending | pending | None |
| 32 | 135.346 | M128/N32/G1024/epi | pending | pending | pending | None |
| 64 | 168.754 | M128/N32/G1024/epi | pending | pending | pending | None |
| 128 | 202.290 | M128/N32/G512/epi | pending | pending | pending | None |
| 256 | 208.546 | M128/N32/G1024/epi | pending | pending | pending | None |
| 512 | 207.698 | M128/N32/G512/epi | pending | pending | pending | None |
| 4096 | 333.396 | M256/N128/G512/epi | pending | pending | pending | None |
| 8192 | 492.581 | M256/N128/G1024/dispatch | pending | pending | pending | None |
| 16384 | 880.354 | M256/N128/G512/dispatch | pending | pending | pending | None |

Original BEFORE context, reused without reruns:

| Tokens | BEFORE µs | BEFORE tactic | ON / BEFORE speedup | ON tactic | OFF / BEFORE speedup | OFF tactic |
|---:|---:|---|---:|---|---:|---|
| 1 | 62.209 | M256/N64/G512/epi | 0.9636× | M128/N32/G512/epi | pending | pending |
| 2 | 66.368 | M256/N64/G1024/epi | 0.9662× | M128/N32/G1024/epi | pending | pending |
| 4 | 71.745 | M256/N64/G512/epi | 0.9894× | M128/N32/G1024/epi | pending | pending |
| 8 | 86.481 | M256/N64/G1024/epi | 0.9917× | M128/N32/G1024/epi | pending | pending |
| 16 | 102.337 | M256/N64/G1024/epi | 0.9969× | M128/N32/G1024/epi | pending | pending |
| 32 | 122.593 | M256/N64/G512/epi | 0.9058× | M128/N32/G1024/epi | pending | pending |
| 64 | 172.002 | M256/N64/G1024/epi | 1.0192× | M128/N32/G1024/epi | pending | pending |
| 128 | 210.706 | M256/N64/G1024/epi | 1.0416× | M128/N32/G512/epi | pending | pending |
| 256 | 214.770 | M256/N64/G512/epi | 1.0298× | M128/N32/G1024/epi | pending | pending |
| 512 | 217.011 | M256/N64/G512/epi | 1.0448× | M128/N32/G512/epi | pending | pending |
| 4096 | 332.755 | M256/N128/G1024/dispatch | 0.9981× | M256/N128/G512/epi | pending | pending |
| 8192 | 500.949 | M256/N128/G1024/dispatch | 1.0170× | M256/N128/G1024/dispatch | pending | pending |
| 16384 | 873.786 | M256/N128/G1024/dispatch | 0.9925× | M256/N128/G512/dispatch | pending | pending |

All OFF winners retained by final16: None.


## kimi-k3

Complete: False; same full24 catalog and order.

| Tokens | ON µs | ON tactic | OFF µs | OFF tactic | ON speedup vs OFF | Tactic changed |
|---:|---:|---|---:|---|---:|---|
| 1 | 84.561 | M128/N32/G1024/epi | pending | pending | pending | None |
| 2 | 94.369 | M128/N32/G512/epi | pending | pending | pending | None |
| 4 | 105.665 | M128/N32/G1024/epi | pending | pending | pending | None |
| 8 | 137.489 | M128/N32/G1024/epi | pending | pending | pending | None |
| 16 | 144.642 | M256/N32/G1024/epi | pending | pending | pending | None |
| 32 | 225.251 | M256/N32/G1024/epi | pending | pending | pending | None |
| 64 | 312.450 | M256/N32/G1024/epi | pending | pending | pending | None |
| 128 | 367.476 | M256/N32/G512/epi | pending | pending | pending | None |
| 256 | 394.628 | M256/N32/G1024/epi | pending | pending | pending | None |
| 512 | 398.164 | M256/N32/G1024/epi | pending | pending | pending | None |
| 4096 | 586.504 | M256/N128/G1024/epi | pending | pending | pending | None |
| 8192 | 1075.354 | M256/N128/G512/epi | pending | pending | pending | None |
| 16384 | 2059.401 | M256/N128/G1024/dispatch | pending | pending | pending | None |

Original BEFORE context, reused without reruns:

| Tokens | BEFORE µs | BEFORE tactic | ON / BEFORE speedup | ON tactic | OFF / BEFORE speedup | OFF tactic |
|---:|---:|---|---:|---|---:|---|
| 1 | 84.193 | M256/N64/G512/epi | 0.9957× | M128/N32/G1024/epi | pending | pending |
| 2 | 97.745 | M256/N64/G512/epi | 1.0358× | M128/N32/G512/epi | pending | pending |
| 4 | 108.161 | M256/N64/G512/epi | 1.0236× | M128/N32/G1024/epi | pending | pending |
| 8 | 137.825 | M256/N64/G1024/epi | 1.0024× | M128/N32/G1024/epi | pending | pending |
| 16 | 160.081 | M256/N64/G1024/epi | 1.1067× | M256/N32/G1024/epi | pending | pending |
| 32 | 238.067 | M256/N64/G1024/epi | 1.0569× | M256/N32/G1024/epi | pending | pending |
| 64 | 321.811 | M256/N64/G512/epi | 1.0300× | M256/N32/G1024/epi | pending | pending |
| 128 | 377.045 | M256/N64/G512/epi | 1.0260× | M256/N32/G512/epi | pending | pending |
| 256 | 400.756 | M256/N64/G1024/epi | 1.0155× | M256/N32/G1024/epi | pending | pending |
| 512 | 415.941 | M256/N64/G1024/epi | 1.0446× | M256/N32/G1024/epi | pending | pending |
| 4096 | 593.606 | M256/N128/G1024/epi | 1.0121× | M256/N128/G1024/epi | pending | pending |
| 8192 | 1069.037 | M256/N128/G512/epi | 0.9941× | M256/N128/G512/epi | pending | pending |
| 16384 | 2089.781 | M256/N128/G1024/dispatch | 1.0148× | M256/N128/G1024/dispatch | pending | pending |

All OFF winners retained by final16: None.


Adjacent JSON retains every raw sample, quartiles, tactic identities, source/runtime records, and checksummed controls. No samples or models are pooled.
