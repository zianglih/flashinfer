# K3 fixed width and CLC diagnostic

**CLC does not fix the N256 real-routing loss.** Its additional cost is larger at N128. The actual-routing N256 penalty is concentrated in FC1; the FC2 wall-time tail after FC1 completion is nearly unchanged.

Retained1b0-equivalent source, B300 GPU7 on `fi-gather-opt-1029`, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2/CuTe4.8.0. K3 EP8 W4A4,8192tokens, same M256/two-CTA/K4 for both GEMMs. Positive percentages mean the latter configuration is faster.

| Scope | N128 static us | N256 static us | N128 CLC us | N256 CLC us | N256/static width | CLC/N128 | CLC/N256 |
|---|---:|---:|---:|---:|---:|---:|---:|
| runner_balanced | 506.332 | 492.244 | 621.612 | 520.811 | +2.862% | -18.545% | -5.485% |
| runner_actual | 468.195 | 506.771 | 579.596 | 527.660 | -7.612% | -19.220% | -3.959% |
| full_actual | 491.092 | 516.851 | 593.140 | 540.948 | -4.984% | -17.205% | -4.454% |

| Scope | Configuration | FC1 us | FC2 us | FC2 after FC1 us | Paired spread |
|---|---|---:|---:|---:|---:|
| runner_balanced | n128_static | 301.474 | 152.793 | 143.521 | 0.054% |
| runner_balanced | n256_static | 294.498 | 152.105 | 134.073 | 0.039% |
| runner_balanced | n128_clc | 381.035 | 179.433 | 178.473 | 0.018% |
| runner_balanced | n256_clc | 310.762 | 146.097 | 145.305 | 0.132% |
| runner_actual | n128_static | 276.362 | 142.705 | 133.681 | 0.068% |
| runner_actual | n256_static | 311.770 | 166.609 | 134.481 | 0.076% |
| runner_actual | n128_clc | 351.074 | 169.969 | 169.105 | 0.036% |
| runner_actual | n256_clc | 320.954 | 145.977 | 145.201 | 0.015% |
| full_actual | n128_static | 283.490 | 151.377 | 133.921 | 0.007% |
| full_actual | n256_static | 307.490 | 166.008 | 133.745 | 0.037% |
| full_actual | n128_clc | 349.362 | 170.369 | 169.449 | 0.021% |
| full_actual | n256_clc | 318.986 | 146.209 | 145.545 | 0.089% |

- **Timing:** Three scopes × four fixed configurations × two symmetric passes ×100 CUPTI samples =2,400 samples. A-B-C-D-D-C-B-A ordering,10 warmups, cold-L2 graph replay, no event fallback, no AUTO or winner selection. Actual runner and helper-balanced runner share every non-route input pointer. Full actual uses the original benchmark quantize→route→MoE closure.
- **Components:** Raw activities are copied from the unchanged CUPTI timing function only at its return after measurement/aggregation. Every activity-to-iteration correlation and end-to-end span was reconstructed and checked against all2,400 samples. FC1/FC2 share a symbol and are distinguished by start order under their PDL dependency. Kernel duration includes device waits and overlaps; never sum those columns. “FC2 after FC1” is FC2-end minus FC1-end, a residual wall-time interval rather than isolated FC2 compute.
- **Source/guards:** All513 source files match clean local retained `1b0f1f69acbb7e20055d5aaf76cc29c840779304`; remote immutable tree is c0c0 plus its measured120-register patch. Kernel SHA `bb11f4d16ee3a4314102f99f076c8e0a0c6b8e8e1d2bcd82e0a05519b4346a64`. Eight runtime executable guards passed; all local storage is zero. Both CLC requests are admitted and compiled, not silently replaced by static scheduling.
- **Resource difference:** FC1 N128 has8 operand stages /2 accumulator stages; N256 has5 /1 with overlapping windows and a64-column protected interval. FC2 has6 /2 versus5 /1. Both use K96 and512 TMEM columns; CLC does not change these capacities. Actual compiled shared-memory footprints are230400/195584 bytes for FC1 N128/N256 and205824/228352 for FC2. Full resource records are in `summary.json`.
- **Direction:** Dynamic MMA already uses actual N rounded to16, but Gather4 payload/scales transport remains tactic-sized. Actual routes produce185 N128 tiles versus112 N256 tiles, giving23,680 versus28,672 allocated rows (+21.1% atN256). Balanced routes make both28,672. This is consistent with the FC1 reversal and motivates a lower-overhead live-group transport loop; it is not proof that gather transport alone is the bottleneck. Previously rejected unrolled live-row predicates and cp.async payload substitutions should not be repeated.
- **CLC scope:** The worst-case launch has1135/623 route slots for N128/N256 versus185/112 actual; padded tickets must still be drained. This suggests cancellation/setup overhead merits profiling. No cancellation-order assumption, new tactic axis, source change, or production profiling-policy change is proposed from this single diagnostic.
- **Provenance:** Nine-file archive SHA `c764531f29a0a07e12e82928f03c62605c90c976c886faa513a8357d47904c94`. Initial setup stopped at a guard-policy assertion before any GPU process; archived validated120 guard bytes fixed setup. All native and prior c0 measurements remain immutable. Persistent native and CuTe disk caches retained. GPU7 was verified idle and released.

Raw: `evidence/results.json`; source/launch: `evidence/config.json`, `evidence/launch.json`; verified aggregate: `summary.json`; reconstructed per-component samples: `component-samples.json`; policy/source audit: `DESIGN_AUDIT.md`.
