# Scheduler ON/OFF with native AUTO24

Untrimmed median of 100 CUPTI per-iteration rank-MAX spans; one fresh EP8 process group per arm.
ON speedup versus OFF = OFF median / ON median; above1 favors retaining the scheduler change. Positive ON latency reduction also favors ON.
Only tokens1/2 excluded from phase aggregates. Keep all13 rows. No numeric retention threshold or conclusion is invented; user requires a clearly visible benefit.
Both sides independently use AUTO24; selected tactics may change. This is the requested AUTO policy comparison, not a fixed-tactic causal estimate. Existing ON and original BEFORE controls are reused without sample pooling. Hot selection scoreboards are separate.

## deepseek-v41-flash

Complete: True; same full24 catalog and order.

| Tokens | ON µs | ON p25–p75 µs | ON tactic | OFF µs | OFF p25–p75 µs | OFF tactic | ON speedup vs OFF | Tactic changed |
|---:|---:|---|---|---:|---|---|---:|---|
| 1 | 64.561 | 63.417–65.281 | M128/N32/G512/epi | 66.897 | 66.017–67.577 | M256/N32/G1024/epi | 1.0362× | True |
| 2 | 68.689 | 67.937–69.449 | M128/N32/G1024/epi | 67.201 | 66.368–68.073 | M128/N32/G1024/epi | 0.9783× | False |
| 4 | 72.512 | 71.713–73.192 | M128/N32/G1024/epi | 60.881 | 60.088–62.216 | M128/N32/G512/epi | 0.8396× | True |
| 8 | 87.201 | 86.113–87.840 | M128/N32/G1024/epi | 88.034 | 87.129–89.385 | M128/N32/G512/epi | 1.0095× | True |
| 16 | 102.657 | 101.497–103.825 | M128/N32/G1024/epi | 103.201 | 102.457–104.705 | M128/N32/G512/epi | 1.0053× | True |
| 32 | 135.346 | 133.865–145.137 | M128/N32/G1024/epi | 130.545 | 129.602–131.281 | M128/N32/G1024/epi | 0.9645× | False |
| 64 | 168.754 | 168.058–169.514 | M128/N32/G1024/epi | 167.490 | 166.738–168.362 | M128/N32/G1024/epi | 0.9925× | False |
| 128 | 202.290 | 200.914–239.891 | M128/N32/G512/epi | 204.209 | 203.154–205.570 | M128/N32/G512/epi | 1.0095× | False |
| 256 | 208.546 | 207.586–209.490 | M128/N32/G1024/epi | 208.369 | 207.362–209.273 | M128/N32/G1024/epi | 0.9992× | False |
| 512 | 207.698 | 206.778–208.562 | M128/N32/G512/epi | 212.242 | 211.385–213.153 | M128/N32/G1024/epi | 1.0219× | True |
| 4096 | 333.396 | 331.868–334.603 | M256/N128/G512/epi | 333.748 | 332.636–335.157 | M256/N128/G512/epi | 1.0011× | False |
| 8192 | 492.581 | 489.638–495.877 | M256/N128/G1024/dispatch | 503.111 | 500.094–506.095 | M256/N128/G512/dispatch | 1.0214× | True |
| 16384 | 880.354 | 832.290–900.154 | M256/N128/G512/dispatch | 860.361 | 829.201–874.066 | M256/N128/G1024/dispatch | 0.9773× | True |

Original BEFORE context, reused without reruns:

| Tokens | BEFORE µs | BEFORE tactic | ON / BEFORE speedup | ON tactic | OFF / BEFORE speedup | OFF tactic |
|---:|---:|---|---:|---|---:|---|
| 1 | 62.209 | M256/N64/G512/epi | 0.9636× | M128/N32/G512/epi | 0.9299× | M256/N32/G1024/epi |
| 2 | 66.368 | M256/N64/G1024/epi | 0.9662× | M128/N32/G1024/epi | 0.9876× | M128/N32/G1024/epi |
| 4 | 71.745 | M256/N64/G512/epi | 0.9894× | M128/N32/G1024/epi | 1.1785× | M128/N32/G512/epi |
| 8 | 86.481 | M256/N64/G1024/epi | 0.9917× | M128/N32/G1024/epi | 0.9824× | M128/N32/G512/epi |
| 16 | 102.337 | M256/N64/G1024/epi | 0.9969× | M128/N32/G1024/epi | 0.9916× | M128/N32/G512/epi |
| 32 | 122.593 | M256/N64/G512/epi | 0.9058× | M128/N32/G1024/epi | 0.9391× | M128/N32/G1024/epi |
| 64 | 172.002 | M256/N64/G1024/epi | 1.0192× | M128/N32/G1024/epi | 1.0269× | M128/N32/G1024/epi |
| 128 | 210.706 | M256/N64/G1024/epi | 1.0416× | M128/N32/G512/epi | 1.0318× | M128/N32/G512/epi |
| 256 | 214.770 | M256/N64/G512/epi | 1.0298× | M128/N32/G1024/epi | 1.0307× | M128/N32/G1024/epi |
| 512 | 217.011 | M256/N64/G512/epi | 1.0448× | M128/N32/G512/epi | 1.0225× | M128/N32/G1024/epi |
| 4096 | 332.755 | M256/N128/G1024/dispatch | 0.9981× | M256/N128/G512/epi | 0.9970× | M256/N128/G512/epi |
| 8192 | 500.949 | M256/N128/G1024/dispatch | 1.0170× | M256/N128/G1024/dispatch | 0.9957× | M256/N128/G512/dispatch |
| 16384 | 873.786 | M256/N128/G1024/dispatch | 0.9925× | M256/N128/G512/dispatch | 1.0156× | M256/N128/G1024/dispatch |

All OFF winners retained by final16: True.

- all11: ON/OFF 0.9843×; ON/BEFORE 1.0018×; OFF/BEFORE 1.0178×.
- decode4_through512: ON/OFF 0.9786×; ON/BEFORE 1.0015×; OFF/BEFORE 1.0235×.
- prefill: ON/OFF 0.9997×; ON/BEFORE 1.0025×; OFF/BEFORE 1.0027×.

## kimi-k3

Complete: True; same full24 catalog and order.

| Tokens | ON µs | ON p25–p75 µs | ON tactic | OFF µs | OFF p25–p75 µs | OFF tactic | ON speedup vs OFF | Tactic changed |
|---:|---:|---|---|---:|---|---|---:|---|
| 1 | 84.561 | 83.841–85.481 | M128/N32/G1024/epi | 82.417 | 81.489–83.369 | M128/N32/G1024/epi | 0.9747× | False |
| 2 | 94.369 | 93.577–95.584 | M128/N32/G512/epi | 92.417 | 91.729–93.473 | M128/N32/G512/epi | 0.9793× | False |
| 4 | 105.665 | 104.441–106.761 | M128/N32/G1024/epi | 111.777 | 110.585–112.697 | M128/N32/G512/epi | 1.0578× | True |
| 8 | 137.489 | 136.665–138.721 | M128/N32/G1024/epi | 145.441 | 144.177–146.817 | M128/N32/G1024/epi | 1.0578× | False |
| 16 | 144.642 | 143.394–145.449 | M256/N32/G1024/epi | 153.201 | 152.034–155.042 | M256/N32/G1024/epi | 1.0592× | False |
| 32 | 225.251 | 224.418–227.194 | M256/N32/G1024/epi | 229.745 | 228.889–230.890 | M128/N32/G512/epi | 1.0200× | True |
| 64 | 312.450 | 311.699–313.283 | M256/N32/G1024/epi | 313.971 | 313.028–315.331 | M256/N32/G1024/epi | 1.0049× | False |
| 128 | 367.476 | 366.492–368.620 | M256/N32/G512/epi | 357.300 | 356.123–358.724 | M256/N32/G512/epi | 0.9723× | False |
| 256 | 394.628 | 393.363–395.540 | M256/N32/G1024/epi | 386.003 | 384.892–387.011 | M256/N32/G1024/epi | 0.9781× | False |
| 512 | 398.164 | 397.237–399.757 | M256/N32/G1024/epi | 399.029 | 397.948–400.845 | M256/N32/G1024/epi | 1.0022× | False |
| 4096 | 586.504 | 582.631–591.335 | M256/N128/G1024/epi | 594.312 | 585.287–598.376 | M256/N128/G1024/epi | 1.0133× | False |
| 8192 | 1075.354 | 1018.697–1122.819 | M256/N128/G512/epi | 1057.437 | 1018.924–1123.509 | M256/N128/G512/epi | 0.9833× | False |
| 16384 | 2059.401 | 1954.464–2071.457 | M256/N128/G1024/dispatch | 2054.436 | 1881.972–2063.155 | M256/N128/G1024/dispatch | 0.9976× | False |

Original BEFORE context, reused without reruns:

| Tokens | BEFORE µs | BEFORE tactic | ON / BEFORE speedup | ON tactic | OFF / BEFORE speedup | OFF tactic |
|---:|---:|---|---:|---|---:|---|
| 1 | 84.193 | M256/N64/G512/epi | 0.9957× | M128/N32/G1024/epi | 1.0215× | M128/N32/G1024/epi |
| 2 | 97.745 | M256/N64/G512/epi | 1.0358× | M128/N32/G512/epi | 1.0576× | M128/N32/G512/epi |
| 4 | 108.161 | M256/N64/G512/epi | 1.0236× | M128/N32/G1024/epi | 0.9676× | M128/N32/G512/epi |
| 8 | 137.825 | M256/N64/G1024/epi | 1.0024× | M128/N32/G1024/epi | 0.9476× | M128/N32/G1024/epi |
| 16 | 160.081 | M256/N64/G1024/epi | 1.1067× | M256/N32/G1024/epi | 1.0449× | M256/N32/G1024/epi |
| 32 | 238.067 | M256/N64/G1024/epi | 1.0569× | M256/N32/G1024/epi | 1.0362× | M128/N32/G512/epi |
| 64 | 321.811 | M256/N64/G512/epi | 1.0300× | M256/N32/G1024/epi | 1.0250× | M256/N32/G1024/epi |
| 128 | 377.045 | M256/N64/G512/epi | 1.0260× | M256/N32/G512/epi | 1.0553× | M256/N32/G512/epi |
| 256 | 400.756 | M256/N64/G1024/epi | 1.0155× | M256/N32/G1024/epi | 1.0382× | M256/N32/G1024/epi |
| 512 | 415.941 | M256/N64/G1024/epi | 1.0446× | M256/N32/G1024/epi | 1.0424× | M256/N32/G1024/epi |
| 4096 | 593.606 | M256/N128/G1024/epi | 1.0121× | M256/N128/G1024/epi | 0.9988× | M256/N128/G1024/epi |
| 8192 | 1069.037 | M256/N128/G512/epi | 0.9941× | M256/N128/G512/epi | 1.0110× | M256/N128/G512/epi |
| 16384 | 2089.781 | M256/N128/G1024/dispatch | 1.0148× | M256/N128/G1024/dispatch | 1.0172× | M256/N128/G1024/dispatch |

All OFF winners retained by final16: True.

- all11: ON/OFF 1.0129×; ON/BEFORE 1.0293×; OFF/BEFORE 1.0162×.
- decode4_through512: ON/OFF 1.0185×; ON/BEFORE 1.0378×; OFF/BEFORE 1.0190×.
- prefill: ON/OFF 0.9980×; ON/BEFORE 1.0070×; OFF/BEFORE 1.0090×.

Adjacent JSON retains every raw sample, quartiles, tactic identities, source/runtime records, and checksummed controls. No samples or models are pooled.
