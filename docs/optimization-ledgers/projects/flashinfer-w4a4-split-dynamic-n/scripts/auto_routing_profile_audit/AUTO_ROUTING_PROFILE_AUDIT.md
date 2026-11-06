# AUTO routing-profile audit — existing 442 / regular-TMA evidence

CPU-only audit, 2026-10-25. The tuner has a substantially different expert-tail distribution from the saved native workload. This is a plausible tactic-selection bias to investigate; it does **not** establish why the two historical runs chose different FC2 tactics. Production remains `442d2aa53f68b4640c3ab5118a76f1599ff60d34`.

## Verified source behavior

- Profiling is explicitly **cold L2** in [tuner.py:633](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-regular-tma/flashinfer/fused_moe/cute_dsl/tuner.py:633); both saved cache values also record `l2_cache_policy=cold` and `cuda_graph_profile_replays=1`. A hot-L2 explanation is unsupported.
- The blockscaled runner installs the helper at [tuner.py:628](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-regular-tma/flashinfer/fused_moe/cute_dsl/tuner.py:628). Its hook always requests `approx_max_load=True` at [_inputs_helper.py:195](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-regular-tma/flashinfer/fused_moe/cute_dsl/_inputs_helper.py:195). It first computes a slightly elevated rank total, then divides that total nearly evenly across local experts ([formula at :93](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-regular-tma/flashinfer/fused_moe/cute_dsl/_inputs_helper.py:93), [balanced division at :105](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-regular-tma/flashinfer/fused_moe/cute_dsl/_inputs_helper.py:105)).
- The MXFP8 benchmark borrows this policy ([runner construction at :125](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/scripts/unfused-blockscaled/bench_cute_dsl_mxfp8.py:125), [tuning_config at :141](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/scripts/unfused-blockscaled/bench_cute_dsl_mxfp8.py:141)), while timed native routing calls DeepSeek top-k ([runtime routing at :327](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/scripts/unfused-blockscaled/bench_cute_dsl_mxfp8.py:327)). Native inputs use seed 42 and random logits/bias ([seed at :172](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-regular-tma/benchmarks/bench_moe_deepseek.py:172), [router inputs at :178](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-regular-tma/benchmarks/bench_moe_deepseek.py:178)).
- The W4A16 runner instead generates seed-515 IID expert IDs across all global experts ([intent at :1074](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-regular-tma/flashinfer/fused_moe/cute_dsl/tuner.py:1074), [randint at :1097](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-regular-tma/flashinfer/fused_moe/cute_dsl/tuner.py:1097)). It retains expert-count variance, but this does not prove it matches native routing or performs better.
- Both cache keys profile exactly 8192 tokens. This is also an exact power-of-two bucket ([uncapped bucket mapper at :309](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-regular-tma/flashinfer/fused_moe/utils.py:309)); this case needs no bucket-rounding explanation.

## Exact local-expert counts and derived padding

For `T=8192, E=256, local_E=32, top_k=8, EP=8`, the helper computes `ceil(8192 + sqrt(8192 * ln(8))) = 8323`; `divmod(8323,32) = (260,3)`. All 32 experts therefore cross the 256-token boundary. Counts are ordered local IDs 0–31:

```text
profile: [261, 261, 261, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260, 260]
native:  [252, 296, 289, 197, 303, 232, 237, 202, 174, 249, 308, 323, 245, 207, 230, 278, 176, 194, 254, 227, 290, 295, 286, 187, 297, 232, 347, 262, 255, 284, 251, 247]
```

| Distribution | Routes | Mean | Population stddev | Min / max | Experts >256 |
|---|---:|---:|---:|---:|---:|
| Profile, CPU-derived | 8323 | 260.09375 | 0.291480595409 | 260 / 261 | 32 |
| Native, saved capture | 8106 | 253.3125 | 43.501751042343 | 174 / 347 | 13 |

The full native histogram is from the existing **NVFP4** diagnostic [all_expert_counts at :313](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/evidence/regular-tma-pipeline/nv-n128-forward-0-control.json:313), using its first 32 experts at `tokens=8192`. The MXFP8 screen logs independently agree on min 174, max 347, median 251.5. This audit did not capture a new MXFP8 histogram. Exact expert-count and tile-row frequency histograms, ordered arrays, and input fingerprints are in the JSON receipt.

| Route N | Profile tiles | Native tiles | Profile padded rows | Native padded rows | Profile utilization | Native utilization |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 544 | 521 | 8704 | 8336 | 95.622702% | 97.240883% |
| 32 | 288 | 270 | 9216 | 8640 | 90.310330% | 93.819444% |
| 64 | 160 | 140 | 10240 | 8960 | 81.279297% | 90.468750% |
| 128 | 96 | 77 | 12288 | 9856 | 67.732747% | 82.244318% |
| 256 | 64 | 45 | 16384 | 11520 | 50.799561% | 70.364583% |

At N128 the profile has **64 full tiles +32 tails of 4/5 rows =96 tiles**; native has **45 full tiles +32 tails =77 tiles**, only one tail at most 16 rows. Ordered native remainders:

```text
[124, 40, 33, 69, 47, 104, 109, 74, 46, 121, 52, 67, 117, 79, 102, 22, 48, 66, 126, 99, 34, 39, 30, 59, 41, 104, 91, 6, 127, 28, 123, 119]
```

The profile has 2.6770% more local routes but 24.6753% more N128 tiles. Allocated route padding is not executed MMA work: rounding valid rows to 16 gives 8704 profile rows versus 8336 native rows, distinct from 12288 versus 9856 allocated rows.

## Historical AUTO evidence and causal limit

| Screen | Route N / FC1 | FC2 | Native full-chain median |
|---|---|---|---:|
| Grid16 | N128 / logical M512, 2 CTA | M256, 2 CTA | 492.481 µs |
| LDG256 | N128 / logical M512, 2 CTA | M128, 1 CTA | 503.057 µs |

Evidence: [grid16 cache](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/evidence/regular-tma-auto-grid16-A1/raw/results/regular-tma-auto-grid16-A1/A1-mxfp8.t8192.autotune.json:691), [grid16 result](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/evidence/regular-tma-auto-grid16-A1/raw/results/regular-tma-auto-grid16-A1/A1-mxfp8.log:60); [LDG256 cache](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/evidence/regular-tma-auto-ldg256-A1/raw/results/regular-tma-auto-ldg256-A1/A1-mxfp8.t8192.autotune.json:691), [LDG256 result](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/evidence/regular-tma-auto-ldg256-A1/raw/results/regular-tma-auto-ldg256-A1/A1-mxfp8.log:60). These are historical nonadjacent AUTO screens. The caches persist winners and profile options, **not per-candidate timings or winning margins**. Both use the same synthetic count profile, and FC2 implementation is unchanged between these experiment arms (the LDG256 change is preparation).

The many tiny synthetic tiles could weight CTA coordination and tail overhead differently for M128/1-CTA versus M256/2-CTA. This is an inference about possible profile bias, not a demonstrated explanation of the between-run winner flip or the 10.576 µs full-chain difference. No cache bug, hot-L2 effect, or routing-induced causal timing delta is established.

## Bounded diagnostic for a future cycle

Freeze one source, N128, and logical-M512/2-CTA FC1. Compare only FC2 M128/1-CTA and M256/2-CTA on (a) a saved native routing/permutation and (b) a fixed helper-generated routing/permutation. Use the same cold-L2 method and retain per-tactic samples and margins, with full-chain timing and FC2 phase timing if needed. This audit proposes the diagnostic only; it changes no tuner policy and launches no GPU work.

## Receipt and CPU reproduction

Run `python3 scripts/auto_routing_profile_audit/build_routing_profile_audit.py` from the project root. It reads existing files, checks the native 77-tile sequence, validates the cache hashes/cold-L2 flags, and rewrites only these audit artifacts.

JSON receipt: [auto-routing-profile-audit.json](auto-routing-profile-audit.json), SHA-256 `9f0ca7828d04178ce693d8f81a98a8864c995a7f382ed48ace4c2ecf70d4f0a2`. It contains SHA-256 hashes for all cited source/evidence files and this builder. No production files or tests were changed.
