# Warp-specialization follow-up

Base: PR7290 retained `99f4d0c277746fb706d10a4bb303c98c5f31e0a9`.
All candidate code stays unstaged in independent active review clones. The
canonical checkout remains clean until a candidate is retained.

## Isolated screens

| Candidate | Review checkout | GPUs | Scope |
|---|---|---|---|
| descriptor-prefetch | flashinfer-producer-polish-review | 0–1 | Producer-owned TMA descriptor startup prefetch |
| follower-mma | flashinfer-scheduler-polish-review | 2–3 | Remove non-issuing CTA MMA bookkeeping and metadata arrivals |
| pair-barrier | flashinfer-epilogue-polish-review | 4–5 | SF32 exchange synchronizes only each sharing warp pair |
| sf-cache | flashinfer-sf-cache-polish-review | 6–7 | Activation payload and SF use the same existing cache priority |

The first screen preserves native winners from the last full current-head
campaign. Every candidate runs V3 EP8, V41F EP4, K3 EP8 and N3U EP8 in W4A4,
per-token, MXFP4x8 and MXFP8. Tokens: 1, 2, 4, 64, 512, 4096, 16384; tokens 1/2
are excluded from retention. Two fresh candidate passes use 10 warmups and
100 cold-L2 CUDA-graph CUPTI samples, event fallback forbidden, public functional
API, unfused finalize and NV input quantization. Saved 99f4 A1/A2 measurements
are the initial comparison; this is not a newly interleaved control experiment.
All route and selected-tactic identities must match those saved measurements.

Remote source and artifacts are under
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/warp-polish`.
Each candidate has a private CuTe compilation namespace and reuses the nine
verified native C++/generated-source/cubin cache links in persistent storage.
Native sources are unchanged. Devbox: `fi-moe-nvfp4-port-1026`, C3, eight B300,
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2/CuTe4.8.

After screening, qualify retained synchronization changes with the existing
source-paired exact public replay/codegen harness, then run the full token list
for the retained combination. Sanitizers remain skipped as requested. Do not
claim small historical-baseline differences as causal wins without resolving
noise; neutral reductions in redundant instructions can be retained on their
own merits if the broader screen and correctness proof support them.

No legacy, Rubin, MegaMoE, W4A16 kernel, public API or tactic-space changes are
part of these four candidates. Existing shared operand, accumulator, CLC fetch,
PDL publication and TMEM lifetime requirements remain separately audited.
