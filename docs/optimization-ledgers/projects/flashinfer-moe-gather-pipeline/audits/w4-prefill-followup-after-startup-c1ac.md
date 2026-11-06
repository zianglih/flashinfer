# W4 prefill follow-up after startup-cache screen

**No new simple instruction-removal opportunity was established.** This is a
bounded read-only conclusion, not a benchmark rejection or a claim that W4
cannot improve. Canonical c1ac still has W4 kernel `cbef9186`; no source,
compiler, GPU, or harness work follows.

The current cutoff native gate covers 26 paired kernels with unchanged
resources and zero local memory. Its already-retained K640 FC2 cleanup removes
the affine ULEA/USHF validity calculation; full-K/all-live paths and both Mega
specializations remain identical where captured. The source at
`moe_w4a16_kernel.py:725–769` already computes the group cutoff once. Rewriting
that comparison again would repeat the completed lead.

Current aligned gated FC1 capture (case0) remains 1,660 non-NOP instructions,
96 registers/640 threads and LOCAL0, byte-identical across the cutoff. It uses
native BF16 unpack plus packed BF16 multiply/FMA for dequant, paired FP32
activation arithmetic, and 16 scalar BF16 shared stores. The prior source-bound
V41F TP4/4K profile found those stores have N-way1 and zero excess wavefronts;
603,520 store instructions were about0.34% of executed kernel instructions.
No redundant arithmetic operand or expensive unclosed store-layout defect was
identified. The earlier profile is explicitly measured2b8, not a new c1ac run.

`alpha_val` is already loaded before the accumulator wait once per work tile
(`:2291`); scalar conversion spelling at its consumers is not evidence of
another native load. W4 raw weight/SF transport already shares completion,
and route IDs are cached before K. The apparent producer commits are SDK
no-ops. Their source calls cannot justify an instruction-saving claim.

The two closed-lead indices and current lifetime/native notes already cover
shared-SF bank remapping, raw/decoded preload, route batching, wider gated
stores, output-slot arithmetic, M-zero transforms and elected issue scopes.
No newly exposed native signal distinguishes another trial. Quota, producer
tails, raw-readiness and stage-ring proposals were excluded as requested.

Evidence boundaries:

- [Current cutoff native summary](../experiments/w4-tail-cutoff/qualification-summary.json).
- [Gated output and native PC profile](../profiling/v41f-tp-w4a16-4k/RESULTS.md).
- [N3U FC1/FC2 profile](../profiling/n3u-tp-w4a16-16k/RESULTS.md): measured02de; its unused-K transform lead is already retained in bf072/c1ac.
- [W4 ownership/lifetime audit](w4-gather-lifetime-2b8.md) and [c1ac control follow-up](gather-control-followup-c1ac.md).
- [Current closed leads](../experiments/CLOSED_LEADS.md) and [prior index](../../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/CLOSED_LEADS.md).

Recommendation: stop this bounded lead search without a prototype. Reopening a
closed mechanism requires a distinct measured cause, not fewer source calls or
static instructions alone.
