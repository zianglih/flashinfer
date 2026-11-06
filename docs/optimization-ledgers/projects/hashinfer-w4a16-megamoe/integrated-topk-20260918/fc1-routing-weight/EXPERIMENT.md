# FC1 routing-weight placement

Base: PR8 head `534a623c7fc167837b5946b10e6b9ed1e22c9d3a`, with retained
`3de81245c1f484177b8ca50b47fd0464068d230e` kernel. This is an independent
experiment, without the unpromoted two-slab, conversion, or division trials.

`apply_topk_in_fc1=False` remains the default. True multiplies the completed
FP32 SwiGLU activation by the FP32 route weight before the BF16 intermediate
handoff. Expert FC1 scales, clamps, approximate exp2/reciprocal, and W4A16's
`up * (gate * sigmoid(gate))` association remain unchanged. The route weight
is loaded for the post-transpose lane's token after the existing accumulator
wait and multiplied with packed FP32 instructions after transpose. FC2 keeps
its ordinary BF16-input / FP32-accumulator math and expert scale. Deterministic
combine becomes first-term assignment followed by ordered FP32 additions and
one BF16 conversion. Optional atomic FC2 reduction does not multiply again.

The transport already pulls each route's FP32 score alongside its activation.
This experiment adds no fetch, buffer, barrier, extra alignment requirement,
role change, or tactic. Public session configuration pins the numerical mode
through autotuning; workspace and persistent winner caches distinguish modes.
The final combine's score loads/register array/multiply are compile-time absent
in True mode. Scores remain necessary during staging and FC1; this is not a
claim that the whole routing-weight allocation can be removed.

Moving a real scalar through FC2 is algebraically valid but moves BF16 rounding
boundaries. Cross-mode bit equality is neither expected nor a retention check.
The reference gathers route scores with global expert assignments and applies
RN FP32 multiplication inside the existing Triton SwiGLU helper before BF16.
Every tactic, O2/O3, eager/graph, repeat, and pairwise comparison must match its
own finite BF16-bit reference. The two mode cases use the same seeded inputs.

Performance uses the same 13 global token counts, EP8, H7168/I2048/E256/K8,
AUTO4/O3, 3 warmups and 100 cold-L2 CUPTI graph samples, per-iteration rank-MAX
public-forward span. Compare to the fresh same-hu15 A2 retained control, with
mode-labelled output and unchanged fixture digests. Decode4–512 is primary;
1/2 are reported only; each prefill4096/8192/16384 remains a guard. A short
all-tactic bit-exact case precedes the first full sweep. Full numerical and
sanitizer qualification are separate from benchmark repeat/finite checks.

Possible benefit: shorter score lifetime and fewer repeated combine score loads.
Cost: extra FC1 FP32 multiplies and a live scalar during activation/transpose.
The first same-node full sweep gives 1.0070x geometric decode speedup, with
8K/16K slower by 2.55%/1.51% and substantial prefill dispersion. The default
remains False; this is a mixed result. `decode13-benchmark` retains the full
table, samples, output evidence, source identity and independent audit. Its
64 original member files are verified locally; the original gzip itself is
not. Cross-mode equality is deliberately not a check. The initial EP8/128-token
all-tactic O2/O3 eager/graph reference case passes finite BF16 bit equality.
Full numerical and sanitizer qualification of True remains pending.

Generated PTX confirms RN packed multiplication before the BF16 handoff, and
ordered RN packed additions without score loads in the final combine. This
does not assert no FTZ elsewhere: the retained approximate SwiGLU uses FTZ.
The next isolated experiment, `../fc1-combine-quad`, changes only the width of
score-free workers to test whether more combine concurrency helps. It compares
directly against the same FC1-weighted numerical contract.

## Arithmetic lowering check

The installed CuTe4.7.1 packed add/mul wrappers pass default `rnd=None` and
`ftz=None` into NVVM (captured in `installed-packed-arithmetic.json`). CUDA13.2
PTX9.2 documents default round-to-nearest-even and subnormal support for
[f32/f32x2 mul](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#floating-point-instructions-mul)
and [add](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#floating-point-instructions-add).
The new multiply is followed by BF16 conversion, and the new combine is a
sequence of adds. Keep the repository's existing packed primitive call pattern;
retain actual compiled PTX to verify the compiler emits RN/no-FTZ operations.
Source defaults alone are not a generated-code validation claim.
