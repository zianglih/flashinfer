# R2 end-to-end screen

**Not retained.** V3 is effectively neutral. K3 averages a small negative result, but its control drift exceeds that result and crosses the candidate measurements; this is not clean evidence of a causal regression. There is no measured benefit that justifies retaining a forced loop policy. The simpler R1 without `unroll=1` is evaluated separately.

| Model | C1 ms | A1 ms | A2 ms | C2 ms | R2 speedup | C2/C1 drift |
|---|---:|---:|---:|---:|---:|---:|
| V3 TP8 | 1.5056435 | 1.5079470 | 1.5087475 | 1.5080115 | -0.10% | +0.16% |
| K3 TP8 | 1.8809265 | 1.9157265 | 1.9215825 | 1.9283350 | -0.73% | +2.52% |

Speedup is100×(mean of two control phase medians / mean of two candidate phase medians−1); positive means faster. All4 phases are shown rather than collapsing time drift. Each phase has100 raw CUPTI samples,10 warmups, cold-L2 CUDA graph timing through the public functional API, TP8/EP1,16384 tokens, MXFP4x8, deterministic unfused finalize. GPU7 only, B300, CUDA13.2, CuTeDSL4.8, image `nvcr.io/nvidia/pytorch:26.05-py3`.

Both jobs verified identical native-route identities and frozen winning tactics from the retained61c2 benchmark data. All cache lookups hit; no tactic was admitted/profiled, no event-timer fallback, and the native C++ compilation cache was preserved. Sources and helpers were rechecked before/after every phase. The existing control source has old Git metadata but all348 source files are byte-identical to61c2. R2 source is the isolated one-file candidate, SHA f67f46015a8ad5f6740a54cbb9434b2d6bdfc60e8a03ec00deea7f60a3d5c55d.

Exact/compiler qualification is in `QUALIFICATION.md`. Static instruction count and executed instruction count must be kept distinct: automatic unrolling creates extra static copies that can increase ILP without increasing equivalent per-row work. Fewer static sites alone are not retention evidence.

Raw measurements, commands, full environment, source/route/winner identities, caches and logs are in `screen/evidence/raw`. Its170-file verified archive SHA256 is da0ed0696afd0c51e16227756f285f8540828c83e06e758bf2fdeb49b1372664. No full matrix, sanitizer, fresh autotuning or external baseline rerun.
