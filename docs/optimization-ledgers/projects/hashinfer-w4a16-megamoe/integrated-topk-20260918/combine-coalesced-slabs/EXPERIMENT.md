# Coalesced two-slab combine experiment

Base: retained `3de81245c1f484177b8ca50b47fd0464068d230e`, independent of the
packed-conversion and unsigned-worker trials. This is an unpromoted prototype.

The first width-eight strip keeps its original worker assignment and routing
score preparation before the tail handoff. For hidden widths divisible by512,
each later worker reduces two eight-element slices in the same token row,
separated by256 elements. Across a warp each slice is contiguous: the two
128-bit copies therefore do not create the half-sector accesses of adjacent
16-element-per-thread packing. Scores, token division and loop work are shared
between both slices. Other hidden widths keep the original width-eight loop.
This is compile-time selection from the existing hidden dimension; no caller
alignment requirement, API option, autotuning dimension or tensor-layout family
is added. All copies and output alignment annotations remain16bytes.

Let Q=H/8, W=512*SM and N=rows*Q. The original first strip covers[0,min(N,W)).
Each later p=W/2+c+jW maps to q=64*(p//32)+(p%32), covering q andq+32. When
Q%64==0, both tiles stay within one token and these pairs partition[W,N).
The existing two CTA rendezvous and remote-return drain remain unchanged.
Each output follows the identical ordered FP32 multiplication/FMA recurrence
and final BF16 conversion; no accumulation is shared between slices.

The actual scheduling AST passes276 exhaustive ownership cases totaling
8,729,128 output tiles, including zero rows, noneligible widths, boundary tails
and canonical16K. Its fallback loop and per-element arithmetic match the base
AST. Scoped pre-commit checks pass. Independent source review/native compilation
and performance validation remain pending; CPU checks are not GPU qualification.

The tradeoff is a wider live state (16 FP32 accumulators and potentially more
route data) and a separate bulk body. The current role/register budgets are
unchanged. Benchmark first against the refreshed same-node retained baseline;
inspect generated register usage and route-load scheduling if performance or
compiler output indicates a problem. A tail register redistribution is only a
conditional follow-up, never assumed necessary from the source tensor sizes.
