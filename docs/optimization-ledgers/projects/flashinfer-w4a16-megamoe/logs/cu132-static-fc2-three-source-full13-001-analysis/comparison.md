# CUDA 13.2 static-FC2: complete comparison with fresh C1 and base512

All three original analyzers pass independently. This report preserves 156 raw values, 624 split selections, 624 compiled records, 312 returned auto winners and 39 complete catalog16 rankings. The static run alone contributes 52/208/208/104/13. No cross-source row minimum is substituted for a final table.

## Observations

- Fixed static512 improves 9/13 rows versus base512, with gains of 0.30–4.60% and regressions of 1.00–2.75%; none exceeds 5%. It improves 10/13 versus fresh C1, while T1 is 12.60% slower. These sequential runs are not a bracket and small changes require context/control scrutiny.
- Complete static auto improves 7/13 versus base512 auto and 4/13 versus C1 auto. Its only >5% regression against base auto is T1 (+7.07%, same selected tactic; paired split +10.21%); against C1 auto it is T4096 (+6.28%, different return mode). Neither comparison isolates the epilogue effect alone.
- Static auto improves 11/13 versus its fixed arm; T8 and T64 are 4.71% and 3.10% slower. At T4096 the actual config, compiled resources and compiler gate match fixed on all 8 ranks, so the 0.94% lower auto latency cannot be credited to a changed tactic.
- Static auto at 4,096 tokens is 0.526965 ms versus paired split at 0.554979 ms (1.0532x). Its C1 predecessor auto is 0.495827 ms with reused-dispatch return, while static chose epi return. Preserve both actual complete tables; no cross-source fastest-row synthesis or new-best claim follows from this audit.

## Fixed CONTROL

Actual public config dictionaries match on all 104 rank/shape pairs across all three sources. Static versus base512 changes only epilogue.py. All 208 static selected-object resource observations report REG128, 512 threads, two groups and local_bytes=0.

| T | C1 Mega ms | Base512 Mega ms | Static512 Mega ms | Static vs base | Static vs C1 | Paired static split ms | Split / static |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.081633 | 0.092592 | 0.091920 | -0.73% | +12.60% | 0.084256 | 0.9166x |
| 2 | 0.118193 | 0.114081 | 0.117217 | +2.75% | -0.83% | 0.116752 | 0.9960x |
| 4 | 0.137361 | 0.136817 | 0.130529 | -4.60% | -4.97% | 0.127202 | 0.9745x |
| 8 | 0.161793 | 0.153680 | 0.151761 | -1.25% | -6.20% | 0.147921 | 0.9747x |
| 16 | 0.181265 | 0.177713 | 0.174418 | -1.85% | -3.78% | 0.179538 | 1.0294x |
| 32 | 0.210705 | 0.206721 | 0.199553 | -3.47% | -5.29% | 0.203538 | 1.0200x |
| 64 | 0.235954 | 0.238049 | 0.230210 | -3.29% | -2.43% | 0.222674 | 0.9673x |
| 128 | 0.242594 | 0.241522 | 0.240289 | -0.51% | -0.95% | 0.233505 | 0.9718x |
| 256 | 0.250626 | 0.232289 | 0.238305 | +2.59% | -4.92% | 0.243922 | 1.0236x |
| 512 | 0.251922 | 0.258113 | 0.246434 | -4.52% | -2.18% | 0.239042 | 0.9700x |
| 1024 | 0.268962 | 0.268786 | 0.267985 | -0.30% | -0.36% | 0.261122 | 0.9744x |
| 2048 | 0.336435 | 0.338337 | 0.342035 | +1.09% | +1.66% | 0.351475 | 1.0276x |
| 4096 | 0.522484 | 0.526691 | 0.531972 | +1.00% | +1.82% | 0.552262 | 1.0381x |

## Complete auto arms

Each source uses its actual returned 16-candidate winner. These rows include selection changes and are not a fixed-tactic source ablation.

| T | C1 Mega ms | Base512 Mega ms | Static512 Mega ms | Static vs base | Static vs C1 | Static auto vs fixed | Paired static split ms | Split / static |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.088336 | 0.077664 | 0.083152 | +7.07% | -5.87% | -9.54% | 0.086161 | 1.0362x |
| 2 | 0.118321 | 0.118432 | 0.102705 | -13.28% | -13.20% | -12.38% | 0.106721 | 1.0391x |
| 4 | 0.129025 | 0.134784 | 0.129793 | -3.70% | +0.60% | -0.56% | 0.143281 | 1.1039x |
| 8 | 0.157473 | 0.159585 | 0.158913 | -0.42% | +0.91% | +4.71% | 0.160482 | 1.0099x |
| 16 | 0.165105 | 0.159649 | 0.166818 | +4.49% | +1.04% | -4.36% | 0.168226 | 1.0084x |
| 32 | 0.188978 | 0.201889 | 0.196817 | -2.51% | +4.15% | -1.37% | 0.203986 | 1.0364x |
| 64 | 0.240770 | 0.231425 | 0.237345 | +2.56% | -1.42% | +3.10% | 0.224610 | 0.9463x |
| 128 | 0.220081 | 0.235713 | 0.225489 | -4.34% | +2.46% | -6.16% | 0.235425 | 1.0441x |
| 256 | 0.227921 | 0.224977 | 0.225329 | +0.16% | -1.14% | -5.45% | 0.241569 | 1.0721x |
| 512 | 0.228514 | 0.233921 | 0.236433 | +1.07% | +3.47% | -4.06% | 0.229297 | 0.9698x |
| 1024 | 0.251970 | 0.252225 | 0.253761 | +0.61% | +0.71% | -5.31% | 0.253714 | 0.9998x |
| 2048 | 0.335859 | 0.341714 | 0.337986 | -1.09% | +0.63% | -1.18% | 0.349506 | 1.0341x |
| 4096 | 0.495827 | 0.530227 | 0.526965 | -0.62% | +6.28% | -0.94% | 0.554979 | 1.0532x |

## Actual choices and split retuning

| T | C1 auto | Base512 auto | Static512 auto | Static fixed/auto config+compiled+gate same on 8 ranks | Split changed ranks versus base, fixed / auto |
| ---: | --- | --- | --- | --- | --- |
| 1 | M128/N64, C1, F8, reuse | M128/N64, C2, F8, epi | M128/N64, C2, F8, epi | False | [] / [0, 3, 4, 6] |
| 2 | M256/N64, C2, F8, reuse | M256/N128, C2, F8, reuse | M128/N64, C2, F8, epi | False | [] / [0, 3, 4, 6] |
| 4 | M128/N64, C1, F8, reuse | M256/N128, C2, F4, reuse | M128/N64, C2, F4, reuse | False | [] / [0, 3, 4, 6] |
| 8 | M128/N64, C2, F4, epi | M256/N128, C2, F8, epi | M128/N64, C2, F8, reuse | False | [] / [0, 3, 4, 6] |
| 16 | M128/N64, C2, F8, epi | M128/N64, C2, F8, epi | M128/N64, C2, F8, reuse | False | [4] / [] |
| 32 | M256/N64, C2, F8, epi | M128/N64, C2, F4, reuse | M128/N64, C2, F8, epi | False | [0, 6] / [0, 2, 4, 5, 6, 7] |
| 64 | M256/N64, C2, F4, epi | M128/N64, C2, F8, epi | M128/N64, C2, F8, epi | False | [0, 6] / [6, 7] |
| 128 | M256/N64, C2, F4, epi | M256/N64, C2, F4, reuse | M128/N64, C2, F8, epi | False | [2, 6] / [1, 5, 6] |
| 256 | M128/N64, C2, F4, epi | M128/N64, C2, F4, epi | M256/N64, C2, F8, epi | False | [5] / [1, 5] |
| 512 | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi | M128/N64, C2, F4, epi | False | [3, 4, 5, 6] / [1, 2, 3, 4, 5, 6] |
| 1024 | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi | False | [0, 6] / [4, 5] |
| 2048 | M256/N128, C2, F8, reuse | M256/N128, C2, F4, epi | M256/N128, C2, F8, epi | False | [0, 2, 5] / [2, 3, 5, 6] |
| 4096 | M256/N128, C2, F4, reuse | M256/N128, C2, F4, epi | M256/N128, C2, F4, epi | True | [] / [] |

## Every paired split raw value

| T | C1 fixed | C1 auto | Base512 fixed | Base512 auto | Static512 fixed | Static512 auto |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.075681 | 0.084720 | 0.071072 | 0.078176 | 0.084256 | 0.086161 |
| 2 | 0.101712 | 0.101584 | 0.100160 | 0.116369 | 0.116752 | 0.106721 |
| 4 | 0.137649 | 0.145120 | 0.136753 | 0.144065 | 0.127202 | 0.143281 |
| 8 | 0.160449 | 0.151409 | 0.162481 | 0.151361 | 0.147921 | 0.160482 |
| 16 | 0.179874 | 0.182240 | 0.179600 | 0.177281 | 0.179538 | 0.168226 |
| 32 | 0.204978 | 0.204113 | 0.193681 | 0.193873 | 0.203538 | 0.203986 |
| 64 | 0.222801 | 0.209105 | 0.224113 | 0.220497 | 0.222674 | 0.224610 |
| 128 | 0.234961 | 0.235698 | 0.233298 | 0.235025 | 0.233505 | 0.235425 |
| 256 | 0.241905 | 0.232258 | 0.243202 | 0.242386 | 0.243922 | 0.241569 |
| 512 | 0.241041 | 0.236818 | 0.240208 | 0.238370 | 0.239042 | 0.229297 |
| 1024 | 0.262401 | 0.260738 | 0.262769 | 0.261297 | 0.261122 | 0.253714 |
| 2048 | 0.355106 | 0.351186 | 0.350914 | 0.349379 | 0.351475 | 0.349506 |
| 4096 | 0.555268 | 0.550483 | 0.552515 | 0.551171 | 0.552262 | 0.554979 |

## Derived counts

```json
{
  "improved_rows": {
    "control_static_vs_c1": [
      2,
      4,
      8,
      16,
      32,
      64,
      128,
      256,
      512,
      1024
    ],
    "control_static_vs_base512": [
      1,
      4,
      8,
      16,
      32,
      64,
      128,
      512,
      1024
    ],
    "auto_static_vs_c1": [
      1,
      2,
      64,
      256
    ],
    "auto_static_vs_base512": [
      2,
      4,
      8,
      32,
      128,
      2048,
      4096
    ],
    "static512_auto_vs_fixed": [
      1,
      2,
      4,
      16,
      32,
      128,
      256,
      512,
      1024,
      2048,
      4096
    ]
  },
  "regressions_over_5pct": {
    "control_static_vs_c1": [
      1
    ],
    "control_static_vs_base512": [],
    "auto_static_vs_c1": [
      4096
    ],
    "auto_static_vs_base512": [
      1
    ],
    "static512_auto_vs_fixed": []
  },
  "same_fixed_auto_config_compiled_gate_rows": {
    "c1": [],
    "base512": [
      2048,
      4096
    ],
    "static512": [
      4096
    ]
  },
  "static_auto_choice_changes": {
    "c1": [
      1,
      2,
      4,
      8,
      16,
      32,
      64,
      128,
      256,
      512,
      1024,
      2048,
      4096
    ],
    "base512": [
      2,
      4,
      8,
      16,
      32,
      128,
      256,
      512,
      2048
    ]
  },
  "split_changed_rank_shape_counts": {
    "control_static_vs_c1": 33,
    "control_static_vs_base512": 17,
    "auto_static_vs_c1": 33,
    "auto_static_vs_base512": 41
  },
  "local_bytes_selected_object_observations": {
    "c1": {
      "control": {
        "not_observed": 104
      },
      "auto": {
        "not_observed": 104
      }
    },
    "base512": {
      "control": {
        "112": 104
      },
      "auto": {
        "0": 80,
        "112": 24
      }
    },
    "static512": {
      "control": {
        "0": 104
      },
      "auto": {
        "0": 104
      }
    }
  }
}
```

## Interpretation limits

- Six sequential fixed/auto processes, not an adjacent performance bracket. Positive latency deltas mean slower.
- C1 source 250553 uses 640 threads; base512 e2d88 and static512 28a use 512 threads, all with two decode groups. Only epilogue.py differs between the 512-thread sources.
- Preflight identities and every compiled gate match; live native-library maps are available for C1 auto only, not newly observed for each later run.
- Same input factory/source and recorded seed conventions do not newly attest identical tensor bytes across these three runs.
- Split independently retunes in each process. Host online ranking and final CUPTI GPU activity span measure different intervals.
- The final cache has ten capacity buckets; all thirteen shape choices are preserved in 104 returned rank records per source.
- Source/native cache admission and before inventories do not prove cache contents immutable afterward.
- Selected-object CUDA local_bytes attributes are not a source-level spill or latency attribution. C1 did not emit the later per-object register/local queries.

Reproduce: `python3 -B candidates/cuda132_recovery_0908b/integration_analysis/compare_static_fc2.py`. Original analyzer outputs and their hashes are in comparison.json. No benchmark, source, cache, GPU or PR modification is performed.
