# Staged FC1 direct-gather experiment

The separate review checkout remains unstaged at the tested R6 local-TMA version. Retained PR head `d35fcfda` is clean and unchanged. The measured direct-gather variants do not justify retention under the frozen tactics.

## Implementation

- FC1 removes standalone routed activation/SF preparation and gathers original input with a dedicated four-warp group. FC2 retains regular TMA; W4A16 is unchanged.
- Operand stages are calculated from shared-memory capacity, operand layouts and epilogue storage. The 224 checked FC1/FC2 plans preserve their retained depths; FC1 ranges from 2 to 11 stages, usually 4–6. This is planner evidence, crosschecked against eight compiled records, not a claim that every stage stays busy.
- Gather producers issue ahead without a per-stage completion wait. An asynchronous local barrier and control-warp relay publish readiness; the original operand-empty ring remains the sole reuse gate.
- The current local-TMA variant uses CTA-group1 Gather4 for payload and cp.async for scales, sharing local completion. The cp.async payload alternative also uses all 128 producer threads. No public API or autotune axis was added.

## Matched timing screen

Four models; 8, 256, 4096 and 16384 tokens. Same-GPU C-A-A-C, 100 strict CUPTI cold-L2 graph samples per phase, 10 warmups, public functional API, frozen routes and winners, unfused finalize. NVFP4 includes input quantization. Positive speedup is faster: `100 × (retained latency / candidate latency − 1)`. Each candidate quick screen contains 28 affected cells plus four unchanged W4A16 controls. The geometric means below use only affected cells.

| Model / modes | Staged Gather4 | cp.async payload | Local-TMA payload | Local-TMA, ordinary FC1 incoming launch |
|---|---:|---:|---:|---:|
| V3 EP8 · W4A4 + per-token | -30.98% | -30.50% | -30.69% | -31.18% |
| V41F EP4 · MXFP8 + MXFP4x8 | -47.40% | -46.97% | -47.54% | -47.38% |
| K3 EP8 · MXFP4x8 | -64.77% | -64.59% | -64.85% | -65.00% |
| N3U TP8 · MXFP8 + MXFP4x8 | -18.57% | -19.27% | -18.44% | -18.91% |

All raw phase samples and receipts are under each revision’s `evidence/perf/`; audited per-cell latencies are in `r4/report/cells.csv`, `r5b/report/cells.csv`, `r6/report/cells.csv` and `r7/report/cells.csv`. [comparison.csv](comparison.csv) contains all 32 matched rows. The original staged Gather4 R4 screen additionally covers all 15 supported EP/TP jobs, 144 cells including unchanged W4A16 controls; its plots are in `r4/plots/`. These are fixed-winner diagnostic screens, not freshly retuned full-token retention results.

## Attribution and validation

- Each of R4, R5b, R6 and R7 passes the same 44 selected existing cases: 32 primary tests and 12 supplemental cases, including six confirmed active-CLC cases and PDL on/off. Existing exact/tolerance assertions and the oracle are unchanged. No sanitizer was run.
- The payload transport changes and ordinary incoming FC1 launch do not recover the main gap. R7 is preserved as a diagnostic patch; the review copy restores R6’s incoming PDL behavior.
- [CUPTI activity breakdown](r6/cupti-timeline/RESULT.md) for K3 EP8 MXFP4x8 at 4096 tokens locates the regression in FC1: median FC1 duration 223.633 → 1037.849 µs. Prepare removal saves about 12 µs; FC2 completion after FC1 and combine remain essentially unchanged. This single diagnostic capture is separate from the CAAC decision evidence and does not identify the internal FC1 stall cause.
- NCU timed out during profiler startup without counters. No NCU performance conclusion is claimed.
- Runtime: eight B300 GPUs, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.8.0. After the original box disappeared, `fi-fc1-gather-1028` recovered the same eight GPU UUIDs and persistent runtime/native compilation cache. Sources and cache links were reverified.
- Current source binding: `review-state.json`; local review is `../flashinfer-fc1-gather-review`. No commit, push or PR-body update was made.
