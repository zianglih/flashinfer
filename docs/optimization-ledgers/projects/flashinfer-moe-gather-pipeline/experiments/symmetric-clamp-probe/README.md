# Signed symmetric-clamp probe

Source base: `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`.
Review: `flashinfer-symmetric-clamp-review`; changes remain unstaged.
No performance timing or complete E2E qualification is authorized in this probe.

The current swap SwiGLU epilogue and parameterized W4A16 SwiGLU use
`-fmin(-fmin(u, limit, nan=True), limit, nan=True)`. The public validator requires
`limit` to remain positive and finite after FP32 rounding. Both callers construct
it from a compile-time Python parameter; gate capping remains unchanged.

The candidate uses `-min.NaN.xorsign.abs.f32(u, -limit)`. Moving the sign to the
compile-time limit avoids a run-time negation of each input. For finite inputs,
the inner operation gives the clipped magnitude with the opposite input sign;
the outer negation restores it. This also preserves both signed zeros and clamps
infinities. For NaNs, both original and candidate feed the canonical NaN produced
by `min.NaN` into their final negation. No FTZ modifier or special-case branch is
introduced. `source_helpers.py` is extracted from the actual proposed utility and
retained fmin implementation, not a NumPy arithmetic replacement.

PTX reference: [CUDA13.2.2 floating-point min](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#floating-point-instructions-min).
The `.xorsign.abs` instruction ignores those modifiers on a NaN result and uses
the original operand signs before absolute value for non-NaN results. Hardware
raw-bit tests supplement this source argument; they do not claim exhaustive
verification of all2^64 input/limit combinations or other architectures.

## History boundary

The old project `scripts/fc1_arithmetic_experiment` compact arm already tested a
direct XORSIGN clamp together with ABS3 on the pre-gather kernel, CuTe4.7.1/B200.
Its +0.30% single-prefill result was rejected. That was not an isolated clamp test
and did not prove the signed NaN contract; neither ABS3 nor the quantization max
chain is changed here.

## Raw-bit and native probe

Recovery C2 B300 GPU1; same pinned CuTe4.8/CUDA13.2 runtime. Each case uses262,912
values:528 explicit input/limit edge pairs,262,144 deterministic random pairs,
and240 zero-valued padding entries. The edges include signed zeros, subnormals,
normal boundaries, limit neighbors, infinities, quiet NaNs and signaling NaNs.
Source-limit random pairs cover arbitrary positive finite FP32 limits. Constant
limits7, FLTMAX and3.1 also use the actual compile-time conversion. Both raw
outputs and the existing packed `+1` continuation are compared as uint32 bits.
All tested outputs match. `probe-summary.json` completely counts native SASS
address lines; raw inputs/outputs, PTX, ELF and disassembly remain in the trial
archives. No compiler options or resource constraints were relaxed.

- R1 put the sign on the input: exact, but materialized input FADD instructions,
  leaving native instruction count unchanged. This spelling is rejected.
- R2 puts the sign on the limit: dynamic-limit code remains neutral; compile-time
  7/FLTMAX replaces two min instructions per value with one XORSIGN min, plus one
  reusable uniform constant setup. The output negation folds into packed FADD2.
  The two-element probe removes one total non-NOP after that setup, with12
  registers and zero local memory in both arms.
- R3 repeats the constant check for non-FP32-exact3.1: identical result and native
  reduction, including the normal FP32 constant-rounding behavior.

The current retained gathered caller really contains both min instructions:
`experiments/epilogue-alpha-reuse/qualification/native-evidence/evidence/`
`w4a4-15-Swiglu-control/codegen/00-Sm100BlockScaledGroupedGemmKernel.ptx`
lines1227–1234 and its corresponding SASS. Source metadata binds that control to
retained swap bytes482b. This is historical native evidence, not a fresh timing.

## Real-caller gate

`callers/` runs only one existing small SwiGLU signature in each of swap W4A4 and
W4A16, both control and candidate, with the same public/reference `swiglu_limit=7`.
It preserves existing zero-tolerance oracles, register guards, compiler options,
source/cache checks and actual PTX/cubin capture. This initial gate passed all four calls. Swap FC1 removes15 non-NOP
instructions (32 ordinary mins become16 XORSIGN mins, plus one uniform constant
setup; other allocation/address opcode churn nets zero), retaining168 registers.
W4 FC1 removes8 instructions exactly (16 ordinary mins become8 XORSIGN mins),
retaining96 registers. All local memory remains zero. Both FC2 and finalizer
images are byte-identical. See `caller-summary.json`; these are small static
one-CTA signatures, not performance results.

The follow-up `qualification/` freezes a signature-only adjustment (no keyword-only
separator; forward loc/ip into inline assembly) with identical operation AST.
Its eight paired signatures cover all four swap modes and W4, one/twoCTA,
static/CLC, PDL on/off, finite limits and the default limit, plus unchanged SiTU
and ReLU2 paths. The sixteen calls remain exact/native qualification only; no
timing is launched.

Two deployment-only failures are preserved: an overlong CLI argument payload,
and a copied runtime-receipt location. Neither launched a GPU kernel; the resumed
run uses the same immutable source files and exact SHA-bound recovered runtime
receipt. Raw probe R0 likewise preserves a launcher quoting error before GPU use.

## Final16-call qualification

`qualification-summary.json` combines the first four successful selected calls from the original leaf with the12-call R1 continuation. All16 exact public/reference calls pass; MX also checks the wrapper. The original MX retained-control wrapper failure is preserved: only the task-local wrapper omitted the selected limit, and R1 forwards the same settings already used by the functional call/reference. No production failure is inferred.

The final shared helper has no keyword-only separator and forwards `loc`/`ip`; `qualification/source-proof.json` binds the identical arithmetic AST to the earlier exceptional-bit probe. Final utils SHA8a4e38fe, swap a7ca6801, W413d35d8b remain unstaged. All24 native pairs preserve resources and LOCAL0. Five affected FC1s each remove15 non-NOP instructions:32 ordinary minima become16 XORSIGN minima and one reusable uniform constant. Address/allocation compiler churn in swap is retained in the complete opcode deltas; it is not described as an otherwise byte-identical body. All19 unaffected images (FC2, finalizers, default W4 V3, SiTU and ReLU2) are raw cubin-identical.

The gate covers all four swap modes plus W4, actual static/CLC, one/twoCTA, PDL on/off, default/finite7/non-FP32-exact3.1 clamp limits. It is bounded exact/native qualification, not exhaustive testing or performance evidence. The completed screen covers13 jobs/208 frozen supported cells across gated V3/V41 EP/TP plus V41 W4. V41TP MX arms are absent from the existing supported reference matrix; V3W4 and K3/N3U are unchanged specializations. All13 token counts stay raw;1/2 are excluded only from retention aggregates.

## Final decision

Rejected after the complete208-cell screen (176 retention cells, GM−0.00816%). The review checkout/branch is retired; retained2b8 remains unchanged and clean. All source proofs, scripts, raw probes, exact/native captures, failures and benchmark records remain. See [RESULTS.md](RESULTS.md), [retirement/decision.json](retirement/decision.json), and the shared [closed-lead index](../CLOSED_LEADS.md).
