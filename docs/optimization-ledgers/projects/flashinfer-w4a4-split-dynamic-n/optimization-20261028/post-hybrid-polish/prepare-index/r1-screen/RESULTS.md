# R1 bounded end-to-end screen

**Promising but not yet retained.** The simpler unsigned-index variant with the compiler's default loop policy gives+1.10% for V3 and is effectively neutral for K3 in this bounded comparison. This justifies broader integrated33b7 validation/performance, not a direct PR promotion. R2's forced `unroll=1` is not selected.

| Model | C1 ms | A1 ms | A2 ms | C2 ms | R1 speedup | C2/C1 drift |
|---|---:|---:|---:|---:|---:|---:|
| V3 TP8 | 1.5064110 | 1.4923165 | 1.4906520 | 1.5094515 | +1.10% | +0.20% |
| K3 TP8 | 1.9165430 | 1.9175835 | 1.9135025 | 1.9177590 | +0.08% | +0.06% |

Speedup is100×(mean of control phase medians / mean of candidate phase medians−1). Each phase uses100 raw CUPTI samples,10 warmups and cold-L2 CUDA graph timing through the public functional API on GPU7, B300/CUDA13.2/CuTeDSL4.8, image `nvcr.io/nvidia/pytorch:26.05-py3`. Both cases are MXFP4x8, TP8/EP1,16384 tokens, unfused finalize. V3's frozen route tile is256; K3's is128. Source348-file manifests, native routing identities, frozen tactic identities/cache hits and CUPTI/no-event-fallback assertions all passed for every phase. Persistent native C++ caches were reused; no new tactics, external baseline rerun or sanitizer.

R1 prepare SHA603dcdf240e23e958a35bee5f3666f83c51a078a1ab317ad48bdb15671d211e5. Controls are byte-identical to retained61c2 although remote Git metadata is older. This source and all bounded receipts remain frozen; the later33b7 integration is separate under `../integrated-full`.

R1 quick/persistent gates passed120 exact byte/canary graph replays per source and20 compiled pairs. These include scaled and shared BF16 prepare, PDL off/on, empty/reactivated routes and non-power-of-two route96/top_k6/22. The gate's V3 width/top_k used route128; integrated qualification adds the actual frozen route256 geometry.

The compiler's static row-body replication in K3 is not proof of redundant executed instructions or worse performance: unrolling can expose ILP and reduce loop overhead. Retention follows end-to-end measurements and complete validation rather than static instruction totals alone.

Raw170-file archive SHA256 ba1ab596fe60ca35ad17029c4c5eede18a6d5cfa1ca62e24849be5fcb905e214; per-file manifest verification is in `evidence/verified.json`.
