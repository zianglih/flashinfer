# Split CuTe DSL W4A16 optimization

Independent follow-up to FlashInfer PR #4048 and the MegaMoE work in PR #5019.

- Source checkout: `flashinfer/`, independently cloned from upstream.
- Initial upstream baseline: `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`.
- Branch: `perf/w4a16-split-megamoe-learnings`.
- Scope: transfer applicable, established MegaMoE optimization patterns to SM100/SM103 split W4A16 while preserving numerical/API contracts and the two decode warpgroup design.
- Existing source/results are read-only references under `../flashinfer-w4a16/` and `../flashinfer-w4a16-megamoe/`.
- Retention: compare absolute split BEFORE/AFTER on the same node/source environment, full 1–8192 token sweep; retain 1/2/4 in reporting and exclude them from optimization aggregates. Profile selected candidates with Nsight and verify unchanged reference tolerances.
- Initial audit: compile-time feature bounds/top-k, actual shared-memory pipeline sizing, and source-to-register release timing. Earlier rejected split experiments must be checked before admitting a trial.

Current draft: [FlashInfer #5186](https://github.com/flashinfer-ai/flashinfer/pull/5186), published commit `88ff7db6a558e8acbc0cd964275410cf94e5c22c`.

- Retained: compile-time top-k, full physical-cluster feature bounds, and plain TMA stores for complete route-tail subtiles. The separate fused-finalize table gives 1.0141× speedup / 1.39% lower geometric-mean latency over 8–8192 versus the original upstream controls. Top-k provides the demonstrated latency gain; bounds specialization has verified instruction reductions with neutral timing. All 14 rows and four raw sweep medians are in `FINAL_PERFORMANCE.md` and the PR.
- Validation: 66 selected GPU tests passed. Six mixed-store cases also match the retained control bit-for-bit across repeats and PDL settings (36 launches per source). Actual native code removes aligned feature checks and keeps the fallback SASS exact. See `NATIVE_COMPARISON.md` and `native/CANDIDATE002_FULL_M_REVIEW.md` for checked cases and limits.
- Raw-release trial: passed 42 tests and four long-K reference calls; native code confirms the intended issue-to-completion overlap. Two complete sweeps did not improve latency, so it was not published. Source, results and proof remain under `candidates/raw_release_after_tmem_issue/`.
- Unequal raw/SF and activation rings: candidate004 passed 42 tests and six long-K reference calls. Two fused sweeps were neutral, while native/profile evidence showed extra instructions and 18,432 bytes more dynamic shared memory for an eligible tactic. Rejected; source and complete diagnostics remain under `candidates/unequal_raw_b/` and `profiles/`.
- Current priority: non-fused finalize with deterministic FP32 combine. The latest full 1–8192 upstream/current comparison shows 1.005561× speedup over 8–8192 (0.55% lower latency, small and subject to noise); see `FINAL_NONFUSED_PERFORMANCE.md`. Fused and non-fused evidence remain separate. Fused sweeps were measured atb90 and reused based on unchanged SwiGLU fused source/native control.
- Retained scratch-store change: one condition, native plain stores and no resource growth, repeatable gains at1024–4096 versus its immediate control. One8192repeat was noisy; no stable gain claimed for that row. Detailed outcomes/bitwise proof under `candidates/nonfused_tma_prefix/`.
- Unroll trial006: numerical and bitwise checks passed, but its full sweep was neutral while native code grew; not retained. Artifacts remain under `candidates/nonfused_epilogue_unroll/`.
- Useful-subtile trial007: numerical, private zero-route and bitwise checks passed; two complete non-fused sweeps showed tiny/mixed gains, so the added dynamic bound was not retained. The checkout is clean on88ff. Source, native proof and both tables remain under `candidates/nonfused_skip_invalid_subtiles/`.
- Current retained005 non-fused NSYS and full NCU profiles are downloaded under `profiles/retained005-nonfused-t2048-*`.
- Environment: c2 B300, CUDA 13.2 image/runtime; DSL 4.7.1 contains compiler 13.3.27. Exact versions and provenance are recorded in the PR and `remote-prep/`. The dedicated box is `fi-w4a16-split-0913a` on `hu-pdx-43`.
- Development records: `optimization_experiments.md`, `PROFILE_COMPARISON.md`, `HISTORICAL_TRANSFER_AUDIT.md`, `HOST_EPILOGUE_TRANSFER_AUDIT.md`, and `RAW_B_RESOURCE_PLAN.md`. Nsight reports and native exports remain under `profiles/` and `native/`.
