# CLC metadata consumer release: read-only decision

Keep the current all-consumer release. There is no measured metadata-arrival bottleneck here and the proposed warp election adds coordination/issue work.

- Current `moe_swap_ab_kernel.py:2488–2499` acquires the metadata stage, loads tile/expert/live-row values into registers, releases once per consuming thread, then advances. Its expected count is32times the active consumer warp count at2678–2682; CTA1 excludes its inactive MMA warp. Ordinary scheduling compiles this metadata pipeline out.
- Installed CuTe4.8 source is copied with hashes under `installed-pipeline/`. `sm90.py:308–316` calls `sync_object_empty.arrive`; `helpers.py:403–418` calls `cute.arch.mbarrier_arrive` directly. There is no software warp election/coalescing in this path. `helpers.py:152–155` defines Agent.Warp as32threads for expected arrival count; changing the group agent alone does not create an elected warp arrival.
- An unpredicated arrival is one warp-issued instruction with per-thread arrival semantics. Do not equate32logical arrivals with32 separately issued instructions, or claim undocumented hardware microtransaction coalescing. The captured current ordinary-scheduler epilogue also uses the same direct arrival primitive, but it is not a captured CLC metadata specialization.
- A one-lane metadata release needs all consumers' loads to complete before the chosen lane releases storage for reuse. It therefore needs a warp synchronization plus election/predication and an expected-count adjustment. Election alone cannot establish cross-lane shared-load completion. This adds instructions/control while still issuing an arrival; whether fewer logical participants reduce hardware service work is not established.

Existing implementations support the current contract:

- FlashMLA `references/flashmla/csrc/cuda_kernels/sm100/prefill/sparse/fwd_for_small_topk/head128/phase1.cuh:206`: workers read the CLC response, then each participating thread arrives on `bar_clc_empty`. Its initialization counts worker threads. The fused norm/rope attention config explicitly documents the same per-calling-thread count at`core_attn/config.h:190`.
- Rubin `blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1547–1555` counts all non-scheduler consumer threads. Consumers load metadata then call release at1896/1968; no elected-release conversion.
- MegaMoE `kernel_src/schedulers/base.py:75–89` loads the work tile, fences, and releases the common PipelineAsync per consumer. This is not a one-elected-lane reference.

Evidence boundary: the new20-call swap exact gate used a correctness-only two-SM cap, which intentionally disables CLC in the current launcher. Its actual compiled configurations have been audited and the earlier overbroad static/CLC wording corrected. The fresh V3 TP MXFP8 winner also uses ordinary scheduling. No new GPU compile/launch, kernel edit, metadata count change, performance claim or hardware-coalescing claim was made for this audit.
