# Independent d1 tensor replay findings

The captured N1/N3 executions localize the final-output difference **after FC2**, in the different reduction and BF16-rounding paths. Every routed FC2 term, input and route agrees; the original cross-path tolerance still fails at two N3 elements. No GPU timing or model-quality conclusion follows.

The analysis ran only on CPU in the dedicated calibration node, using `torch.load(map_location="cpu", weights_only=True)` and C99 `libm.fmaf` under round-to-nearest. Its helper SHA256 is `bf4c6c76f087feaa7d37d5387eef6a3b14f91050b8a82737ac50b7a20ca80cae`. All eight `.pt` hashes match their capture sidecars before and after analysis. Eight analysis/helper artifacts were SHA-verified on retrieval, and all eight GPUs remained 0% / 0 MiB afterward. Original capture files, kernels, packages and tolerance were not changed.

## Exhaustive checks on the captured values

| Check | N1 | N3 |
|---|---:|---:|
| Hidden states, route logits/bias, FP32 route-score bits | All equal | All equal |
| Expert IDs / unique owner rank / padding masks | All agree | All agree |
| BF16 route FC2 terms, selected directly from each unique owner | 49,152 / 49,152 bit-equal | 147,456 / 147,456 bit-equal |
| Mega K-order FP32 `fmaf`, then BF16 cast, vs actual Mega output | 6,144 / 6,144 bit-equal | 18,432 / 18,432 bit-equal |
| Owner-local K-order FP32 `fmaf`, then BF16 cast, vs all four actual Split rank partials | All bit-equal | All bit-equal |
| Saved reference vs actual reduce-scatter result | All bit-equal | All bit-equal |
| Original fixed cross-path elementwise check | 0 / 6,144 failures | 2 / 18,432 failures |

The N3 partition is `[1,1,1,0]`, padded to four rows, and each expert owner holds 64 of 256 experts. Original expert-ID storage widths differ between paths; integer values agree. Scores are compared by FP32 bits and FC2 terms by BF16 bits, rather than merely a tolerance or a sum of disjoint buffers.

## Collective arithmetic reconstruction

Enumerating all 15 commutative binary addition trees over four BF16 rank partials, with a BF16 cast after **each** addition, found these unique candidates matching each complete 6,144-element output row:

| Captured token | Equivalent candidate rank sequence, BF16 after each addition |
|---|---|
| N1 token0 | `((r1 + r2) + r3) + r0` |
| N3 token0 | `((r1 + r2) + r3) + r0` |
| N3 token1 | `((r2 + r3) + r0) + r1` |
| N3 token2 | `((r3 + r0) + r1) + r2` |

The actual NCCL schedule was not captured. These are bit-exact arithmetic reproductions, **not proof of a particular NCCL algorithm**. A single fixed tree cannot reproduce every N3 row, but the destination-dependent candidates above reproduce all of them. Summing the already rounded BF16 partials in FP64 and casting only once does not reproduce NCCL: it differs at 1,824 N1 elements and 5,734 N3 elements. Thus a one-final-rounding partial-sum oracle would miss this observed collective contract.

## The two failing elements

Both failures are global token2, source rank2. Its expert IDs are `[152,28,22,165,119,223,11,43]`, with owner ranks `[2,0,0,2,1,3,0,0]`.

| Quantity | Hidden295 | Hidden3363 |
|---|---:|---:|
| Actual Mega output | 0.62890625 | 0.76171875 |
| Actual Split output | 0.609375 | 0.7421875 |
| Absolute difference | 0.01953125 | 0.01953125 |
| Fixed `.01 + .01*abs(Split)` threshold | 0.016093749552965164 | 0.017421875149011612 |
| Error / threshold | 1.213592290878296 | 1.121076226234436 |
| Mega K-order FP32 `fmaf` accumulator | 0.6275045275688171 | 0.7609586119651794 |
| Diagnostic FP64 sum of all weighted route terms | 0.6275045241345651 | 0.7609586933394894 |
| Actual owner BF16 partials, ranks0–3 | `[1.0859375,-0.244140625,-1.421875,1.203125]` | `[1.171875,0.3203125,-1.7265625,0.9921875]` |
| FP64 sum of those rounded partials | 0.623046875 | 0.7578125 |
| Rank-partial rounding shift from full FP64 route sum | −0.004457649134565145 | −0.0031461933394894004 |
| Further actual collective/final shift | −0.013671875 | −0.015625 |
| BF16(`r3 + r0`) | 2.28125 | 2.15625 |
| BF16(previous + `r1`) | 2.03125 | 2.46875 |
| BF16(previous + `r2`) | **0.609375** | **0.7421875** |

Both corresponding full FP64 weighted sums cast once to BF16 equal the Mega output. This is only a diagnostic reference: globally, the N3 FP64-then-BF16 result differs from the actual K-order FP32-FMA Mega result at one other element by 0.00390625. The actual K-order `fmaf` reconstruction matches Mega everywhere. An FP64 oracle must not silently replace the original GPU arithmetic or the original `.01` test.

## Limits and evidence

d1 reproduces r3's N1 PASS/N3 FAIL and reported max-error/relative-L2 aggregates, but r3 did not retain tensors, so it cannot prove every d1 tensor equals its r3 counterpart. d1's CPU snapshots and skipped timing/graphs also perturb scheduling. The findings establish the reduction explanation for the **captured d1 values**, while retaining the original cross-path failure. They do not establish behavior for other N/EP/communication/tactics or authorize a tolerance relaxation.

- [Full machine-readable checks, candidate trees and all eight input hashes](cpu/analyses/glm52-numerics-20260920-d1-cpu-r1/analysis.json)
- [Generated CPU analysis report](cpu/analyses/glm52-numerics-20260920-d1-cpu-r1/analysis.md)
- [SHA-verified retrieval receipt and post-analysis idle GPUs](cpu/verification.json)
- [Exact violating-element collective replay steps](violating-collective-replay-steps.json)
- [Frozen deployed helper and invocation](cpu/setup/helpers-d1-cpu-analysis-r1/invocation.json)
