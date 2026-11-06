# Rubin and MegaMoE Gather4 audit

Sources inspected in project-local flashinfer checkout at d35fcfda (read-only source reference; no Rubin changes). Current fork8 remains fb66a27e.

- `flashinfer/fused_moe/cute_dsl/rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1973`: four elected warp issuers own disjoint row quarters. Routing IDs stay live outside K loop. Gather payload and weight TMA share AB transaction completion. SF remains independent cp.async/transform pipeline.
- Its `:1187` shared AB pipeline uses four gather arrivals plus one weight producer. Hardware multicast avoids a payload peer relay. This is not a drop-in replacement for our hybrid Gather4+cp.async SF publication: both memory systems must complete before the MMA can read B and its scales.
- `flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/sources/kernel_src/blackwell/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:57`: four gather warps bound uniform-register pressure; row identifiers use eight-element /256-bit vector loads. Interleaved row runs spread short windows across issuers.
- Same mainloop `:1041` and `:1221`: dynamic gather subtracts omitted row bytes from expected TMA transactions and only issues live 16-rounded row windows. This is directly applicable to our dynamic-N instruction contract, without model/dtype branches or new tactic axes.
- Same mainloop `:1206`: a five-warp named barrier orders token-TMA expected bytes before Gather4 issuance. Our local129-arrival hybrid barrier already includes explicit transaction arrival and128 SF issuers; replacing it with this pattern requires accounting for SF completion, and is not automatically simpler.
- Corresponding sm107/Rubin `tma_gather.py` supports one/twoCTA and multicast variants through compile-time PTX construction. Use architecture-valid shared scope and peer-bit routing; do not import Rubin MMA/pipeline capacities into Blackwell.

First experiment from this audit: bound swap-AB Gather4 payload issue and expected bytes to actual 16-rounded dynamicN/CTA. Preserve SF copies, current publication/acquire chain and source layout. Other directions: 256-bit aligned row-ID loads, separate token/weight stage sizing only if profiling supports the extra control state, and direct hardware completion only with a proven combined SF contract.
