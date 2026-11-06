# W4A16 MegaMoE compile-time dispatch audit

**Final outcome:** retain the narrow epilogue/divider changes as compile-time dispatch cleanup. The complete 1–8192 sweep does not demonstrate a performance gain: latency geometric mean over 8–8192 is −0.471073%, with 7 of 11 rows lower in one sweep. Published in commit `083a9fd39e7ddda43a8b912ef50f7a13390287f9`; [PR #5019](https://github.com/flashinfer-ai/flashinfer/pull/5019) remains open and draft. The [publication receipt](publication.json) verifies the pushed head, exact tested source, clean checkout, passing commit hooks and PR-body readback. The historical Final performance table is unchanged.

The retained source is `e470f255b06bd492960ec21dd1b2556e36f49827fb99f1698133ce3f62102b0b`, manifest `e9e7e9e43664ddbf07bbd62f97b618285d27bd3bee134a71e18d0143a96a7ab3`, frozen under [frozen-padding-revert/](frozen-padding-revert/source-manifest.json). Its base is commit `586994d8a054470a17c3dab05be8209c75a33128`, source `2e3b651a`. The two owned files add 28 net lines: epilogue `68674590` and scheduler `30c35c2b`. All applicable scoped hooks and independent source/native reviews passed. This note records the completed root-owned source and publication actions.

## Retained implementation

- **Static hidden dimension:** FC2 output routing uses the validated static H. Complete feature clusters omit hidden-tail clipping; partial-H clusters retain the original clipping and store bounds.
- **Aligned FC1 features:** complete feature clusters omit the feature-bound predicate using the existing compile-time divisibility proof. Partial-I shapes retain the original feature predicate, and token bounds remain dynamic.
- **Static power-of-two divisors:** scheduler feature-index decoding selects a signed shift for positive power-of-two static divisors, following the existing MLA scheduler pattern. Other divisors keep the original floor division. The FC1/FC2 phase decision remains runtime.

The original two cumulative-padding expressions are retained. No new public knob, helper, scheduler state, work ordering, transport behavior or pipeline synchronization is introduced. Runtime token counts, work phases, warp roles and readiness checks remain necessary.

Most other configuration choices already resolve in Python construction or CuTe tracing: MMA geometry, CTA count, scheduler/return mode, stage counts, dtypes, optional operands, fragment layouts and fixed epilogue loops. These host/tracing choices are distinct from GPU runtime branches. The fixed-width staging loop remains unchanged; its prior unrolled experiment raised register usage and worsened its recorded sweep.

## Native evidence

Final captures and [independent native review](PADDING_ABLATION_REVIEW.md) cover the exact retained source on `hu-pdx-59`, B300/SM103, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2 system toolkit, CuTe 4.7.1 and native compiler 13.3.27. Each fixture records one compilation and zero launches.

Full-shape predicates/clipping and the C1 general quotient/remainder path are removed; signed shifts and nonpower floor-division fallbacks are present. Partial-H/I bounds remain. The N64/direct whole-kernel SASS count falls from 5,480 in the saved retained-source control to 5,424. This is a code-size observation, not a latency inference.

| Final native fixture | SASS instructions | Dynamic SMEM bytes | Raw / B / decoded / scheduler stages |
|---|---:|---:|---|
| M128/C1, H256/I2048, direct | 5,056 | 194,048 | 5 / 3 / 3 / 3 |
| N64/C2, H7168/I2048, direct | 5,424 | 200,064 | 5 / 3 / 3 / 2 |
| N128/C2, H7168/I2048, reuse | 6,120 | 230,784 | 4 / 3 / 2 / 2 |
| N64/C2, H7200/I2112, reuse | 5,720 | 200,320 | 5 / 3 / 3 / 2 |

All fixtures retain 96 registers/thread at entry, 640 threads, zero stack/local bytes, 1,024 static shared bytes, two decode warpgroups, and their original stage and dynamic shared-memory allocations. [Native completion](execution/native-completion003.json), SHA `c6321821`, and review SHA `90a88d64` preserve the actual evidence. The saved N64 control is source `2e3b651a`; its prior constructor identity check is in [the control comparison](../w4a16_epilogue_constructor_cleanup/execution/native-n64-f4-comparison001.json).

## Focused numerical validation

The same existing tests and reference tolerances passed on source `e470f255`:

| Existing coverage | Result | Subprocess wall time |
|---|---|---:|
| EP1 regular/tail H/I reference, both return modes | 4 passed | 25.33 s |
| EP2 geometry/pipeline tails, partial H/I and N64/N128 wraps, both returns | 6 passed per rank, 2 ranks | 47.12 s |
| Existing C1 routing helper: static H256/I2048 changing/empty/refill; atomic group1 H7200/I2112 | 2 completed oracle calls per rank, 2 ranks; rounds 7 / 1 | 26.09 s |

All three subprocesses exited 0. Source/native/idle closures passed; final native inventory remains `09b4c8ea`. [Test completion](execution/test-completion003.json), SHA `b4489709`, pins the raw logs under `logs/cu132-recovery0911c-compile-time-dispatch-tests-002/`. This focused coverage does not imply that the PR's entire historical validation matrix was rerun.

## Complete performance evidence

One public-four AUTO14 sweep on eight B300 GPUs completed in 423.495027 seconds. The unchanged workload reports every power-of-two token count from 1 through 8192, with 100 cold-L2 graph-CUPTI full-forward samples per row; each reported latency is the median of the 100 per-iteration rank maxima. The existing saved reader and comparator each passed once: 14 rows, 112 compiled/winner records, 56 candidate rankings, and 1,400 primary timing samples. The sole comparison control is the whole saved retained run `208ce173` on the same node; no baseline or split replay was performed.

- **8–8192 retention range:** candidate/retained latency GM `0.995289265` (−0.471073%); 7 of 11 cold rows lower.
- **All 14 rows:** GM `1.000534640` (+0.053464%); 8 of 14 rows lower. Tokens 1/2/4 are reported but excluded from retention.
- **Matched hot scores over 8–8192:** 24 lower, 2 equal, 18 higher. These GPU-event scores are separate from cold-L2 forward timing. All selected tactics remain unchanged.

The small single-sweep difference is not a demonstrated performance gain or statistical-significance claim. Retention is for compile-time dispatch clarity and native instruction reduction with unchanged resources.

[Complete 14-row cold table and all 56 matched hot scores](../../logs/cu132-recovery0911c-compile-dispatch-padding-revert-vs-retained-comparison-001/README.md) are preserved with proof `c846f428`, result `06892703`, comparison `f64b6c0e`, and [performance completion](execution/performance-completion002.json). Sealed artifacts remain unchanged; this README records the final retention decision after those receipts were written.

## Detailed audit

- [Kernel, mainloop and shared adapters](KERNEL_DISPATCH.md)
- [Epilogues and extension](EPILOGUE_DISPATCH.md)
- [Host dispatch, staging and autotuning](HOST_DISPATCH.md)
- [Scheduler](SCHEDULER_DISPATCH.md)

Detailed trial history remains in the project experiment ledger and sealed candidate artifacts. Vendored sources were read only to verify contracts; no shared/vendor or unrelated backend edits are part of the retained change.
