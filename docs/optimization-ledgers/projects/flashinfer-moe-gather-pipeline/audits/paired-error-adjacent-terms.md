# Adjacent independent error terms: bounded read-only proposal

A small native/isolated-payload pilot is defensible, but the NCU evidence does not predict a gain. Keep the retained one-candidate `_nvfp4_4over6_fp16_error(original_scaled, candidate_scaled, config) -> Float32` API and both existing calls. Pack only adjacent values within that candidate for subtraction and, for MSE, square; accumulate the two resulting scalar terms sequentially in original order. This removes the rejected packed accumulator dependency without changing a scoring graph, policy, ownership, reduction, or public interface.

## Evidence and distinction

Current retained c1ac source is `flashinfer/quantization/quantization_cute_dsl_utils.py:1693–1715`; its callers at1858/1863 each supply a16-value tuple. The rejected5f232 implementation instead joins candidate4/candidate6 into one helper call and maintains a packed two-lane accumulator. All source remains unchanged by this audit.

The isolated NCU reports are bound to the actual K640 images (`ff00cf52` / `83a6345e`). Complete decoded-PC grouping gives:

| Operation | Scalar control sites | Rejected packed sites | Math samples C/A | Wait samples C/A |
|---|---:|---:|---:|---:|
| Error subtraction |32|16 FADD2|1 /112|23 /79|
| Error square |32|16 FMUL2|3 /110|31 /51|
| Ordered accumulation |32|16 FADD2|10 /160|107 /93|

Both versions retain52 other scalar multiplies. The rejected packed version has lower issue utilization, higher aggregate math-pipe pressure, unchanged input sectors, and no spill/NOP increase. These observations motivate separating packed accumulation from independent term formation. They do **not** prove packed-add latency: the packed accumulation's raw wait count is lower than both scalar chains combined, samples are not time fractions, and nearby unchanged HMUL2 instructions also acquire more math-pipe samples. Packed subtraction/square themselves have elevated pressure, so the alternative may still lose.

## Minimal prospective change

Only the existing helper body/imports change. Its constexpr loop becomes8 iterations; each iteration forms RN packed differences for indices2i and2i+1, forms RN packed squares for MSE (or the existing two scalar fabs for MAE), then performs `err = fadd_rn(err, term[0])` followed by `err = fadd_rn(err, term[1])`. No tuple-return API or caller changes; no new helper, runtime branch, policy axis, recipe rescue, or strict-path change. Expected source growth is roughly6–10 net lines, depending on formatting, and must be judged against the native result.

The original scalar sum remains `RN(...RN(RN(0+t0)+t1)...+t15)`. Computing t1 early introduces no dependency on t0 and does not reassociate the sum. Operand order, RN boundaries, and absence of FTZ/FMA must remain explicit. This is an arithmetic-graph argument, not a NaN-payload/device-output guarantee; reuse existing exact/reference coverage. The tuple length is already fixed16, so there is no new tail branch.

Across the two MSE candidate scores, nominal arithmetic sites become16 packed subtract +16 packed square +32 scalar adds =64, versus96 original scalar /48 rejected packed sites. For MAE, the two scalar fabs per adjacent pair remain. These are source arithmetic counts, not predicted SASS counts. Packing adjacent inputs may introduce aligned-register moves or alter scheduling/liveness; no forced register allocation or inline-PTX workaround is proposed.

## History and bounded gate

The current `experiments/CLOSED_LEADS.md` and `experiments/paired-4over6-error/DESIGN.md` close cross-candidate packed recurrence, scalar inverse hoist, width/warp changes and max-chain changes. A peer's bounded lookup of both earlier CLOSED_LEADS indices and per-token Markdown ledgers found no matching adjacent-term packing plus scalar ordered-add trial. This is a bounded negative search, not an exhaustive historical claim.

If authorized, reuse the existing exact/native K640 pilot and the already captured isolated FC1 payload on unchanged c1ac controls. First require correct explicit RN packed term operations, unchanged ordered scalar accumulation/strict image, same output bytes, no new local storage, and acceptable resource/scheduling cost. Only then use the existing one-kernel isolated CAAC before considering any whole-chain screen. No prototype, source edit, GPU use, new framework, or new timing is authorized/executed by this note.

Evidence: `experiments/paired-4over6-error/isolated-intermediate-ncu/{RESULTS.md,summary.json,pc-opcode-groups.json,closure.json}`. The rejected42-cell screen and isolated CAAC remain primary and unchanged.
