# CUDA 13.0: fresh C1 versus exact e2d88 512-thread candidate

Same node/image/native12.9 compiler and loaded libraries; C1→512 changes exactly three Mega source files. Four sequential measured arms, not an adjacent bracket. Auto choices and split retuning are recorded. Positive percentages mean slower. Online host ranking is not a final CUPTI latency measurement.

The fixed 512 candidate improves 8/13 rows versus C1 and regresses 5/13; the largest improvement is T64 (−6.40%) and largest regression T4096 (+4.85%). Whole-auto 512 improves 6/13 rows versus C1 auto; T2 is the only regression above 5% (+9.70%), with a different selected tactic. These separate runs do not establish a uniformly faster fallback implementation.

Within 512, the auto arm is lower in 9/13 rows and higher in 4/13 (maximum +2.16%). At T1, T2048 and T4096, every rank's actual auto config is exactly the fixed config, despite measured differences of −5.26%, −3.00% and −0.37%. Those differences reflect run/context variation rather than tactic improvement. Eleven of thirteen C1-versus-512 winners differ; the whole-auto comparison therefore includes selection changes. No host ranking score is substituted for a primary CUPTI measurement.

Both runs use H7168/I2048/E256/top8, EP8,13 powers of two,100 CUPTI iterations,3 warmups,CUDA graphs,cold L2,median iteration maximum-rank GPU activity span. Fixed is M256/N128/K256,C2,F4,epi,(2,4),group512,atomic. All104 fixed public config pairs are identical; recorded threads change640→512, and both retain two decode groups. Functional/resource/native/source audits are saved separately alongside the original results.

## Mega raw latencies and comparisons

| Tokens | C1 fixed ms | C1 auto ms | 512 fixed ms | 512 auto ms | 512 auto vs fixed | 512 auto vs C1 auto |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.105441 | 0.112289 | 0.110449 | 0.104641 | -5.26% | -6.81% |
| 2 | 0.132449 | 0.122753 | 0.131809 | 0.134657 | +2.16% | +9.70% |
| 4 | 0.154209 | 0.153057 | 0.153969 | 0.150336 | -2.36% | -1.78% |
| 8 | 0.171874 | 0.173489 | 0.176418 | 0.179617 | +1.81% | +3.53% |
| 16 | 0.199138 | 0.188258 | 0.191968 | 0.187106 | -2.53% | -0.61% |
| 32 | 0.233186 | 0.237585 | 0.228386 | 0.232753 | +1.91% | -2.03% |
| 64 | 0.282466 | 0.261347 | 0.264386 | 0.255874 | -3.22% | -2.09% |
| 128 | 0.261906 | 0.250226 | 0.270563 | 0.262673 | -2.92% | +4.97% |
| 256 | 0.279362 | 0.267250 | 0.275923 | 0.275362 | -0.20% | +3.04% |
| 512 | 0.283138 | 0.271986 | 0.279826 | 0.273890 | -2.12% | +0.70% |
| 1024 | 0.296849 | 0.290002 | 0.289250 | 0.292291 | +1.05% | +0.79% |
| 2048 | 0.359139 | 0.356835 | 0.365987 | 0.354995 | -3.00% | -0.52% |
| 4096 | 0.541907 | 0.546835 | 0.568164 | 0.566083 | -0.37% | +3.52% |

## Actual automatic choices

| Tokens | C1 winner | 512 winner | Split changed ranks, fixed / auto C1→512 |
| ---: | --- | --- | --- |
| 1 | M256/N64, C2, F4, reuse | M256/N128, C2, F4, epi | [1, 3, 4, 5] / [1, 3, 4] |
| 2 | M256/N64, C2, F4, epi | M128/N64, C2, F4, reuse | [1, 3, 4, 5] / [1, 3, 4] |
| 4 | M128/N64, C2, F8, epi | M256/N128, C2, F8, epi | [1, 3, 4, 5] / [1, 3, 4] |
| 8 | M256/N64, C2, F8, epi | M128/N64, C2, F4, reuse | [1, 3, 4, 5] / [1, 3, 4] |
| 16 | M128/N64, C2, F4, epi | M256/N64, C2, F8, epi | [2, 4, 5] / [2, 6] |
| 32 | M128/N64, C2, F8, reuse | M256/N128, C2, F8, reuse | [] / [] |
| 64 | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi | [1] / [0] |
| 128 | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi | [] / [] |
| 256 | M256/N64, C2, F4, epi | M128/N64, C2, F8, reuse | [] / [] |
| 512 | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi | [1, 5, 6] / [] |
| 1024 | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi | [] / [] |
| 2048 | M256/N128, C2, F8, epi | M256/N128, C2, F4, epi | [] / [] |
| 4096 | M256/N128, C2, F4, reuse | M256/N128, C2, F4, epi | [5] / [5] |

## Paired split raw latencies

Split is independently retuned in every arm. All416 original rank/shape selections remain in comparison.json; raster flags are preserved verbatim without reinterpretation.

| Tokens | C1 fixed split ms | C1 auto split ms | 512 fixed split ms | 512 auto split ms |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0.095729 | 0.082289 | 0.093553 | 0.095201 |
| 2 | 0.123569 | 0.122689 | 0.121281 | 0.121681 |
| 4 | 0.163537 | 0.173569 | 0.172561 | 0.174304 |
| 8 | 0.199953 | 0.196993 | 0.198337 | 0.192017 |
| 16 | 0.219250 | 0.220851 | 0.220897 | 0.223057 |
| 32 | 0.252034 | 0.256355 | 0.253874 | 0.260947 |
| 64 | 0.280546 | 0.279601 | 0.283058 | 0.274691 |
| 128 | 0.294977 | 0.304003 | 0.294114 | 0.296131 |
| 256 | 0.313891 | 0.314354 | 0.313122 | 0.311809 |
| 512 | 0.303826 | 0.304435 | 0.303281 | 0.302242 |
| 1024 | 0.315987 | 0.305234 | 0.318562 | 0.321250 |
| 2048 | 0.377218 | 0.371795 | 0.375939 | 0.388499 |
| 4096 | 0.571620 | 0.561238 | 0.569173 | 0.570550 |

## Summary counts

```json
{
  "fixed_512_faster_rows": [
    2,
    4,
    16,
    32,
    64,
    256,
    512,
    1024
  ],
  "auto_512_faster_than_c1_rows": [
    1,
    4,
    16,
    32,
    64,
    2048
  ],
  "512_auto_faster_than_fixed_rows": [
    1,
    4,
    16,
    64,
    128,
    256,
    512,
    2048,
    4096
  ],
  "512_auto_slower_than_fixed_over_5pct": [],
  "512_auto_slower_than_c1_over_5pct": [
    2
  ],
  "auto_choice_changed_rows": [
    1,
    2,
    4,
    8,
    16,
    32,
    128,
    256,
    512,
    2048,
    4096
  ],
  "auto_config_equals_fixed_rows": {
    "c1": [],
    "512": [
      1,
      2048,
      4096
    ]
  },
  "fixed_config_pairs_equal": 104,
  "split_tactic_changed_rank_shape_counts": {
    "fixed_c1_to_512": 24,
    "auto_c1_to_512": 16,
    "within_c1": 23,
    "within_512": 22
  }
}
```

All104 raw values are also in raw-latencies.csv. Reproduce with `python3 candidates/cuda130_recovery_0908b/analyze512_vs_c1.py`. No table cell substitutes a different source, tactic or timer method.

Source/native/resource validation: `logs/cu130-recovery0908b-c1-owner-admission-002.json`, `logs/cu130-recovery0908b-zero-dest512-completion-001.json`, both original run manifests, and `logs/cu130-recovery0908b-zero-dest512-library-comparison-001.json`. Public and lifecycle independent audits are linked from the recovery README. Native cache provenance establishes allowed reuse origin, not unchanged cache bytes after execution.
