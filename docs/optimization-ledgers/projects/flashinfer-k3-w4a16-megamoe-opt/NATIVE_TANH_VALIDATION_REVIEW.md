# Native tanh validation review

Reviewed `evidence/candidates/native-tanh-v2.patch`, `native-tanh-oracle.patch`, `tests/moe_ep/test_bf16_nvfp4_activation.py`, and the new multirank SiTU/half-boundary cases. This is a source review only: no GPU, compilation, pytest, or repository edits were performed. The user explicitly permits updating the instruction-exact reference for the changed activation implementation.

## Kernel and exact oracle agree at the source level

The native patch preserves this FP32 sequence:

1. `scaled_gate = gate * fp32(1 / Python_beta)`.
2. `bounded_gate = fp32(beta) * tanh.approx.f32(scaled_gate)`.
3. `sigmoid = rcp.approx(1 + exp2.approx(gate * fp32(-log2(e))))`.
4. `gate_activated = bounded_gate * sigmoid`.
5. With a bounded up branch, `up = fp32(linear_beta) * tanh.approx.f32(up * fp32(1 / Python_linear_beta))`.
6. `output = up * gate_activated`.

The proposed Triton inline-PTX oracle reproduces these steps and their association. In particular, it does not rewrite the final multiplication to `(up * bounded_gate) * sigmoid`. The `0fBFB8AA3B` sigmoid constant and Python-double reciprocal followed by FP32 rounding match the kernel. Packed multiplication is independent per lane; archived DSL 4.7.1 PTX emits `mul.rn.f32x2`, consistent with the oracle's scalar `mul.rn.f32`. No clamp, routing, norm, alpha, final cast, or combine logic changes in the oracle patch.

Preserving the original reciprocal contract in v2 also keeps the new non-FP32-exact beta cases meaningful. The earlier `f32_reciprocal` proposal would have changed this separate contract, but v2 does not.

The exact oracle change is scoped to W4A16 MegaMoE consumers. W4A4 and split W4A16 references remain separate. The existing exact end-to-end equality assertions should remain unchanged. Final emitted PTX should still be checked for native tanh and the expected rounding operations; source equivalence is not a substitute for that artifact check.

## Independent FP64 coverage is useful, with two gaps

The new mathematical test calls the **actual epilogue helper**, returns its FP32 output before BF16 rounding, and compares it against independent PyTorch FP64 tanh/sigmoid expressions. This is materially stronger than only changing the inline-PTX oracle to copy the new implementation. Cross-product gate/up inputs cover positive and negative branches, saturation, and both packed lane positions.

Two small additions would make the coverage more convincing:

- Add `(1.75, None)` and `(0.8, 1.5)` parameter cases. These are established SiTU accuracy cases from the earlier split work; currently every SiTU math case uses beta approximately 4, so the test mostly covers K3's activation scales.
- Add a logarithmic set of small nonzero gate values (for example both signs of `1e-2` through `1e-7`) and record or separately assert relative error there with nonzero up values. The existing `±1e-7` rows are effectively unchecked by `atol=2e-5`: an implementation returning zero at those rows would pass. Avoid claiming that the current assertion establishes near-zero relative accuracy or preservation of signed zero.

The FP64 reference correctly rounds beta itself to FP32 before evaluating ideal division. The implementation intentionally uses the reciprocal of the original Python value; the resulting approximately one-ULP reciprocal difference for the non-exact-beta cases is real and tiny compared with the native-tanh error budget. The math test should not be rewritten to reuse the implementation's reciprocal just to eliminate that independent discrepancy.

## Tolerance risk: preserve the current gate first

The proposed `atol=2e-5, rtol=1e-5` comes from the existing **exp/sigmoid-based** gate helper test. It is not a guaranteed bound for native tanh. [NVIDIA's PTX specification](https://docs.nvidia.com/cuda/parallel-thread-execution/#floating-point-instructions-tanh) allows maximum relative error `2^-11` for one FP32 tanh. Two independent tanh factors permit a combined relative error of approximately `9.768e-4` before the sigmoid and FP32 rounding. This does **not** predict the actual B300 error; measured hardware can be considerably better than that bound.

Run the current strict assertion unchanged after the performance gate. If it fails, capture the worst `(gate, up, beta, linear_beta)` values, absolute/relative pre-cast errors, and BF16 output differences before making a retention decision. A failure could be a valid accuracy rejection of the faster candidate; permission to change the bit-exact oracle does not by itself authorize silently relaxing independent accuracy tolerances.

The current scaling by `max(abs(ideal_up), 1)` sensibly normalizes up-branch magnitude, but it does not remove up-tanh approximation error: for a nonzero up branch, the final relative error still includes both tanh approximations. Moderate nonsaturated gate/up values are therefore a more plausible place for strict-tolerance failures than fully saturated tails. Tiny values are dominated by the absolute tolerance; negative sigmoid tails are also weakly constrained in relative terms. Native tanh should avoid the old sigmoid-derived tanh's cancellation near zero, but that benefit requires a stronger near-zero check to substantiate.

## Integration coverage

The new multirank non-exact-beta cases exercise both gate-only and bounded-up paths, config/runtime alpha sources, normalization, FC1 top-k multiplication, and different return-warp modes. The 31/32/33 and 63/64/65 (plus 95/96/97) routed-token cases appropriately target the separate half-tile skipping candidate, while retaining exact outputs and CUDA graph replay. These tests complement rather than replace the independent activation check.

No blocker was found in the native-tanh/oracle operation association. Retention remains conditional on a measured performance win, the independent mathematical accuracy gate, emitted-artifact inspection, and the existing exact integration checks against the deliberately updated oracle.

## Updated validation direction (user request, 2026-10-08)

Use the existing `tests/moe_ep/w4a16_reference.py` and zero-tolerance W4A16
bit-exact tests. Extend their cases concisely; update the instruction-matching
reference for retained algebraically equivalent activation arithmetic. Do not
add a separate non-exact behavioral test. The proposed FP64 tolerance test was
removed from the repository and archived as an unrun, rejected prototype.
Correctness execution still follows confirmed performance improvement.
