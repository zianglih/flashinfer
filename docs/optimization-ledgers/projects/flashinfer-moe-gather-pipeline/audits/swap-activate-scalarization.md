# Swap FC1 scalar activation spelling: read-only assessment

**No performance-motivated prototype is justified by the saved FC1 profiles.** A scalar loop could shorten the current tuple-heavy source, but it would increase arithmetic instructions before backend optimization. The actual profiles do not establish the packed-math pressure needed to support that trade. This is a source/profile feasibility conclusion, not a measured rejection of a scalar candidate.

## Source and minimal prospective change

Retained `c1ac8ce7341039db65195b99445fcdeb193cf226` has swap SHA `482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`. `_activate` at `moe_swap_ab_kernel.py:626–694` is a 69-line existing helper. Its AST is identical at 822, 49, 2b8 and c1ac (`5bd96f2bd8e2ba1c894565788e0a6e936401b25fb83b1ec7ed01dae6983c6b5b`). The whole 49 swap module is byte-identical to c1ac. The V3 822 whole-kernel capture remains historical even though its activation helper is unchanged.

The smallest prospective rewrite would keep this helper/signature and all call sites, iterate over 16 scalar values, replace only the existing packed add/multiply boundaries with existing `fp4_common.fadd_rn`/`fmul_rn`, and leave clamp, max, EX2/RCP, SiTU and GeGLU scalar calls in their current order. It needs no new helper, state, policy, runtime branch, shape exception or quantizer change. Tuple construction and duplicate helper calls would become scalar expressions. No rewrite was implemented and no exact source-line saving is claimed.

| Branch, per 16-value invocation | Existing packed arithmetic sites | Prospective scalar sites at those same boundaries | Other arithmetic |
|---|---:|---:|---|
| ReLU² | 16 multiplies | 32 multiplies | 16 max operations unchanged |
| SwiGLU | 40 multiplies + 16 adds | 80 multiplies + 32 adds | Clamp and scalar SFUs unchanged |
| SiTU / GeGLU | 24 entry/final multiplies | 48 multiplies | Existing inner scalar helpers unchanged |

These are source-expanded sites, not a prediction of final SASS: the compiler may repack a scalar spelling or change register allocation/scheduling. Explicit scalar RN helpers would preserve the intended rounding boundaries; substituting generic `silu_f32`, folding the exponent constant, or changing the SiTU `tanh_f32` sequence would not be this proposal. The source audit alone does not establish arbitrary NaN-payload equality or emitted no-contraction behavior. Retained W4 paired SiTU and the user-reverted quantizer maximum chain are outside scope.

## Saved native evidence

The independent [native/profile audit](swap-activate-scalarization-native.md) binds the existing CSVs to loaded native images, resources and source history. Counting **all** packed FADD2/FMUL2, including output scaling/quantization, upper-bounds the activation work:

| FC1 capture | Packed share of executed warp instructions | Packed math-throttle samples / kernel math samples |
|---|---:|---:|
| V3 TP MXFP8 T16K, gated, 822 | 3.903% | 0 / 59 |
| N3U TP MXFP4×8 T32, ReLU², 49-equivalent | 3.511% | 0 / 6 |
| N3U TP W4A4 T16K, ReLU², 2b8 | 6.180% | 3 / 223 |
| N3U EP W4A4 T16K, ReLU², 2b8 | 8.076% | 2 / 101 |

For N3U prefill, operand tracing identifies the actual alpha and square sites: together they are two-thirds of packed executions, with only 3 TP / 2 EP math-throttle samples. The hot N3U packed alpha consumers instead wait on the preceding global alpha load. V3's hot `FMUL2` at `0x5440` waits both alpha and TMEM dependency barriers; its 117 long-scoreboard samples cannot distinguish those producers. Neither observation establishes multiply-pipe cost. Alpha prefetch is separately rejected and is not reopened here.

All four profiles report 168 initial registers and LOCAL0. There is no candidate resource result or demonstrated pair-register constraint. Sample counts and executed-instruction shares are not time fractions, hardware latency measurements or expected speedups. The different, issue-active isolated quantizer's packed-error regressions cannot fill this evidence gap.

## History and decision

Bounded searches of current `experiments/CLOSED_LEADS.md`, both prior swap CLOSED_LEADS ledgers, the original W4 optimization ledger, and the related activation/native-TMEM notes found no matching full scalar-loop `_activate` trial. This is not an exhaustive claim about every historical artifact.

- `audits/paired-activation-math/README.md` established that ordinary ReLU²/SwiGLU math is already packed; its open arithmetic-removal opportunity was the separate scalar SiTU sequence.
- `experiments/swap-paired-situ/RESULTS.md` tested the **opposite** direction for SiTU internals: more packing and one private helper. It was rejected at +0.113% over 66 retention cells with 22 negatives and +40 source lines. It does not test full scalarization.
- Prior native-token/native-TMEM activation trials changed ownership/packing and explicitly preserved the packed arithmetic body. Their regressions are not a direct scalar-versus-packed comparison.
- Cross-candidate and adjacent-term quantizer packing pilots are separate kernels/recurrences. Their rejection does not establish an FC1 benefit from unpacking.

Keep `_activate` unchanged for now. Scalarization remains a possible readability change, but the current evidence offers no concrete performance mechanism to prioritize it over its instruction-count and scheduling risk. Unprofiled K3/SiTU and other tactics are not covered by a universal no-benefit claim. No source edit, GPU/NCU action, test, timing run or new validation framework was performed.
