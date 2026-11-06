# PR #5319 implementation quality and performance audit

Audited `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095..ca2692a62679336301758d1b83b193b3c5b1170c`, with the current archived B300 evidence. This audit reuses existing measurements; it does not add benchmark sweeps.

## Implementation quality

The five-file change has a coherent scope: two FC2 scheduling changes, one private finalizer specialized for two existing row layouts, and two caller integrations. It introduces no C++ dependency or public API, preserves native reduction order, and uses the surrounding pointer-based CuTe compilation pattern. The layout flag is compile-time and part of the cache key; token count stays runtime with only three launch-geometry cache classes. The device key and current-device guard avoid reusing the finalizer across devices accidentally. The shape/alignment checks support the 128-bit vector contract and should remain.

No extra compatibility fallback is needed. W4A8 requires fused finalize; Rubin rejects unfused finalize before this helper; the existing W4A4 FC2 checks BF16 output. The old public `output_dtype` flexibility is not a new regression in this PR. Do not broaden this optimization to unsupported paths during cleanup.

Cleanup is limited to precise FTZ and metadata-readiness comments/docstrings, plus restoring the original W4A4 keyword ordering to reduce diff noise. Runtime AST equivalence is checked after removing docstrings and normalizing only the safe `moe_unpermute` keyword permutation. No extra tests are added upstream. The measured kernel logic and launch geometry remain intact.

## Performance evidence and remaining opportunities

1. **Resolve W4A16 8K full-pipeline behavior before adding a dispatch exception.** The one-sweep CUPTI result regresses from 0.675767 to 0.683990 ms (1.22%), with identical autotuned tactics. Separate fixed-tactic Nsight captures improve the FC2/finalize span from 259.986 to 248.962 us. Re-reading the complete archived timelines also gives top-k-to-finalizer spans of 676.022 to 664.309 us; FC1 medians are essentially unchanged (365.2035 to 365.0595 us). These are different captures/methods; the profile cannot erase the benchmark regression or prove a noise explanation. Neither slower finalization nor changed tactics is established as its cause. A future targeted matched full-pipeline capture is more useful than a hard-coded N=8192 fallback.
2. **Tune permuted-layout launch geometry independently if pursuing another iteration.** The current 32-thread / 128-thread and one-vector / four-vector cutoffs were selected using the W4A4 expanded layout. The archived standalone sweep supports the choices: at N1024/H7168, t128-v1 is 10.6245 us versus t128-v4 11.040; at N2048, v4 is 16.128 versus v1 18.048; at N16384, v4 is 85.4885 versus v1 120.896. W4A16 gathers sorted rows and may have a different cache/locality tradeoff. Test 1/2/4 vectors with fixed FC2 tactics and measure full MoE; do not select solely from isolated finalizer time. There are no measured alternative W4A16 geometry results in this PR.
3. **Small-token occupancy is a bounded experiment.** At N1/H7168, the 32-thread/eight-BF16 geometry launches 28 CTAs on the measured 148-SM B300. A smaller column tile could expose more parallelism, at the cost of narrower memory transactions and duplicated metadata. Existing v2 already fixes the original v1 small-batch regression. A further change needs a measured decode benefit and must retain ordered FP32 reduction; this audit does not claim one.
4. **Earlier W4A16 launch signaling is optional, not a missing correctness fix.** The native permute already establishes routing metadata. A weight-side hint could allow more setup to overlap FC1/FC2, but could also occupy resources longer while waiting. The present after-FC1-wait placement is easy to prove correct and already shows overlap. Keep it unless a controlled profile identifies remaining setup on the critical path.
5. **Host/JIT costs are outside the GPU benchmark.** The private helper does metadata checks, constructs four pointer objects, and uses an in-memory compile cache on each eager invocation. Cold compilation and Python dispatch are not included in graph/CUPTI results. If eager serving or startup becomes the target, measure those costs separately before removing checks or adding persistent-cache infrastructure. Avoid copying an unmeasured cache/locking layer into this focused PR.

Do not parallelize the top-k reduction or revert to BF16 atomics to chase these opportunities: those alter the accuracy contract. Do not add generic GEMM staging/lookahead: it is outside this finalization bottleneck and already structurally present in the retained W4A16 kernel. Keep the redundant W4A4 tail PDL signal; removing an idempotent hint has no established performance value.

## Boundaries and CI

W4A4 performance remains measured at `fff0070c`; W4A16 at `ca2692a`. Current native tests recheck both W4A4 modes, but the full W4A4 performance/standalone edge matrix was not rerun after sharing the helper. All measurements are one forward sweep per configuration on B300 with simulated EP8. There is no statistical uncertainty estimate, real EP communication measurement, sanitizer evidence, full native suite, or other-architecture validation.

GitHub at the audit start reports docs and pre-commit successful; the GPU test summary is red because CI awaits authorization and its GPU matrix did not run. This is not a failing GPU test. No CI-trigger comments were posted.

Derived profile components are in `profile-component-summary.json`. Original raw logs, complete native output, external checks, profiles, and source snapshots remain preserved in the project archives.
