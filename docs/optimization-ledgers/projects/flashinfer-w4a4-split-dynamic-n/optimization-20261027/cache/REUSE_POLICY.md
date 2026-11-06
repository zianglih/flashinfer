# Routing-based weight reuse experiment

Base: `e2728a2908f38cbcfa997c031bea059e3724ccde`. Active source:
`../../flashinfer-cache-perf-review`; only `moe_swap_ab_kernel.py` differs.

The uniform-normal cache screen is rejected. Its eight frozen-winner CAAC
cells show a stable 9.51% improvement for Nemo W4A4 at 16K, but 4.7–13.2%
decode regressions. The result motivates identifying actual weight reuse,
not a model, dtype, token-count or tile-geometry threshold.

The new candidate uses NORMAL weight payload loads when an expert has more
than one routed tile, and EVICT_FIRST otherwise. The router emits each
expert's tiles contiguously, so a matching preceding or following expert
index identifies reuse. Both neighbor addresses are clamped to the live
route range; boundary predicates exclude the clamped self-reference. The
helper runs only after live-work validation, including startup prefetch.
There is no access for empty work. The hint is computed once per work tile,
outside the reduction loop, and passed as an Int64 TMA policy operand.

`RoutingKernel.cuh:474–485` clamps each `mn_limit` to the individual tile end;
it cannot identify a following tile. An initial unmeasured prototype that
used this limit was superseded. No result from that prototype is retained.
`reuse-policy-proof.json` checks the corrected neighbor predicate on 75,460
tiles, including empty experts, exact tile boundaries and multi-tile experts.

The additional metadata reads follow the existing routing publication/PDL
contract. Weight-scale and activation hints, buffers, scheduling, MMA,
outputs, public APIs and autotune tactics are unchanged. Normal priority is
an eviction preference; this does not assume a global order among consumers
or claim that any particular tile is the last consumer.

Retention requires source-bound runtime-policy codegen and existing exact
test checks, then matched current/candidate/candidate/current public CUPTI
measurements. First screen: Nemo W4A4 and V3 MXFP4x8, tokens 4/128/4096/16384,
with the frozen native winners and input/timing contracts from the complete
four-model campaign. Promising results will be expanded across all models
and formats before retention. Native C++ cache artifacts remain shared in
persistent cluster storage after source/header identity checks.
