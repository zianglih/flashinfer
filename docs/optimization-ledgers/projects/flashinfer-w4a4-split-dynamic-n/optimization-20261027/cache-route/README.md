# Reuse-aware weight cache screen

Frozen candidate: runtime NORMAL when another routed tile reuses the same expert; FIRST otherwise. Weight scales remain FIRST. No dtype, model, or dimension threshold; no new tactic axis.

Source kernel SHA256: `64698e033f47185a5b447e5983278a80f85705e6998d42df091fd9565ac13630`. e2728 production baseline; corrected adjacent-expert routing predicate. Initial mn_limit prototype and artifact-dump attempts are superseded diagnostics only.

Matched frozen native winners and routes; C-A-A-C, 10 warmups, 100 cold-L2 CUPTI samples per median, no timing fallback. All eight phases and 32 timed medians verified locally against receipts, hashes, raw samples, and routes. Candidate uses source-private CuTe cache with verified shared native C++ compilation cache.

| Model / dtype | Tokens | C0 us | A1 us | A2 us | C3 us | Paired speedup | Forward / reverse |
|---|---:|---:|---:|---:|---:|---:|---:|
| Nemo NVFP4 | 4 | 38.112 | 38.240 | 38.304 | 38.160 | -0.35% | -0.33% / -0.37% |
| Nemo NVFP4 | 128 | 137.233 | 137.312 | 137.265 | 137.185 | -0.06% | -0.06% / -0.06% |
| Nemo NVFP4 | 4096 | 232.865 | 234.849 | 234.609 | 233.025 | -0.76% | -0.85% / -0.68% |
| Nemo NVFP4 | 16384 | 572.114 | 533.666 | 531.410 | 579.058 | +8.08% | +7.20% / +8.97% |
| V3 MXFP4x8 | 4 | 46.560 | 46.688 | 46.592 | 46.577 | -0.15% | -0.27% / -0.03% |
| V3 MXFP4x8 | 128 | 134.912 | 134.976 | 134.993 | 134.944 | -0.04% | -0.05% / -0.04% |
| V3 MXFP4x8 | 4096 | 225.025 | 225.952 | 226.064 | 225.681 | -0.29% | -0.41% / -0.17% |
| V3 MXFP4x8 | 16384 | 747.106 | 679.154 | 701.058 | 736.034 | +7.47% | +10.01% / +4.99% |

Four existing exact cases passed (K-tail with/without PDL; MXFP4x8 N16 and N128 two-CTA public API). Generated PTX confirms runtime TMA cache-hint registers are assigned. Narrow N16 steady-state producer code computes neighbor metadata in all four producer warps; explicit warp0 ownership can remove this unnecessary work. N128 TMA-SFB generated code already sinks the computation under warp0. Startup is warp0-only in both cases.

Evidence archive SHA256: `ce72b2fed49ab428dbceb5211cc992d35b029ab300621f7f575013f5ea649270` (70 files). Codegen and finalize diagnostic archive: `b0f2ffe2e9d2e220708a16b41be07e3b7c626a6f97e3555ae8ef658f6e633774` (43 files).

Retention boundary: promising targeted screen only; no broad four-model/all-dtype retain decision yet. V3 large-prefill paired repeats vary, but both directions improve.
