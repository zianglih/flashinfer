# Post-tail shared W4 synchronization/staging audit

Source: retained `02de7785c10847b3528340840bed40bd405d85b4`. Read-only; no source edits, new GPU work or performance claim. The separate final-group K-tail candidate remains under its own qualification and screen.

**No additional simple candidate is justified by this pass.** The apparent duplicate waits protect different storage lifetimes; the source differences in newer Rubin/MegaMoE implementations either already exist here or match previously closed experiments.

## Distinct lifetimes that should remain distinct

- **Raw A plus scales → transformation:** `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1196–1209` already accounts for packed weights and scales in one TMA transaction barrier. Both transform warpgroups contribute the raw-release count. `_transform_tile:742–780` waits once, acquires a decoded stage, then loads SF/payload. There is no second independent SF-readiness wait to delete.
- **Decoded A versus activation B → MMA:** `:1213–1238` uses different rings and completion agents: decoded A is transform-produced TMEM; B is TMA-produced SMEM. The MMA waits and releases each at `:1993–2040`. Their indices can differ because decoded-stage count is TMEM-limited while B depth follows the raw/activation SMEM allocation. Sharing one barrier would require a new lifetime/ring policy or reduce independent progress, not remove a redundant arrival. The newer Rubin Mega mainloop also waits and releases distinct weight/token pipelines at `moe_ep/kernel_src/sm107/next_cutedsl_megamoe/src/sources/kernel_src/rubin/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1553–1609`.
- **Raw lifetime versus decoded publication:** `_finish_transform_stage:695–707` fences decoded writes before raw release and decoded commit. Inherited W4 MegaMoE overrides the ordering at `moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:114–125`, returning raw SMEM before the TMEM-store completion fence. That is the already closed early-raw-release mechanism, not a new work-removal opportunity. The TMEM fence itself still establishes the transform→MMA visibility edge.
- **Accumulator versus output shared stage:** The epilogue releases its accumulator immediately after the last relevant TMEM load (`:2358–2363`, `:2540–2545`). Its later shared-store fence/join (`:2506–2507`, `:2686–2691`) protects a different buffer used by TMA. All epilogue warps populate that buffer even though one warp issues the TMA. Removing the join or merging it with the earlier accumulator release would lose a cross-warp publication edge.
- **Output read completion versus next shared write:** Output TMA commit/acquire occurs only in its actual issuing warp (`:2508–2521`, `:2693–2700`). The following epilogue join prevents other writers from reusing a stage too early. There is no counterpart of the formerly empty swap-AB bulk commit left here. The current Rubin epilogue follows the same store/fence/join/TMA/commit-acquire structure at `fused_moe/cute_dsl/rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:3286–3302`.

## Tempting reference differences that do not reopen a lead

Rubin's SFA transform loads scales into registers before waiting for its TMEM slot (`rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:2261–2292`). The W4 SF-only reorder was already tested and rejected; moving the whole packed fragment would lengthen lifetimes and disturb native decode/store interleaving. The fresh N3U TP W4 profile identifies raw-input supply and epilogue accumulator readiness, not a newly exposed decoded-slot or output-reuse bubble.

The fresh profile is source-bound in `profiling/n3u-tp-w4a16-16k/RESULTS.md`: tensor activity is 86.88%/73.29% for FC1/FC2. Output-acquire PCs have only 2/6 samples, whereas the preceding shared-write joins have 307/922. Samples are warp PC observations, not removable latency fractions. The latter joins are necessary publication edges, so their larger sample count is not a deletion argument. This evidence supports the separate unused-tail work-removal candidate, which avoids arithmetic/TMEM work without changing stage lifetimes.

W4's four Gather4 issuers already cache route IDs outside K (`:2777–2806`) and account for four independent producer arrivals (`:1229–1235`, `:2768`, `:2810–2849`). Replacing this with a larger rendezvous or Rubin-specific ownership would add policy/state or reopen rejected route batching. A raw readiness lookahead query is also not an extra acquire: its result is passed into the existing wait to skip a slow polling path, and removing it previously regressed several decode cases.

## Closed evidence checked

- Previous project's `fc1-gather-20261028/optimization-next-20261029/CLOSED_LEADS.md`, including independent-stage balancing, raw-ready query removal, delayed output acquire, scales-before-decoded-acquire, role-local TMEM retrieval, and batched W4 route IDs.
- Current `experiments/terminal-pdl/RESULTS.md`: removal of one ACQBULK repeated losses and grew actual FC2 registers. Do not reopen terminal PDL.
- Current `experiments/cache-priorities/RESULTS.md`: both fixed priority policies lost materially. Do not replace adaptive routing reuse with a constant.
- Current `experiments/fc1-wide-store/RESULTS.md`: both register-tensor joins produced local storage and unchanged store width. Do not build another packed-store join.
- Current `audits/clc-consumer-arrivals.md`: elected arrival needs additional warp coordination; per-thread arrival count does not equal separately issued instructions.
- Custom producer-tail logic and producer-ownership A/B remain closed; no new state, participant count, public option or shape predicate is proposed.

A new candidate should start from a newly identified executed operation whose result is unused, as the K-tail work audit did. This pass found no second such operation with a complete dependency argument.
