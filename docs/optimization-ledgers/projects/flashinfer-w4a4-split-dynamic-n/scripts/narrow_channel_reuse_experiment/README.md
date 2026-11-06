# Narrow one-CTA channel reuse

Independent unstaged source: `../../flashinfer-narrow-channel-reuse-review/`, based on clean retained `0c1e00fc3e4f913c8c241796c70a29673737c542`. No production, MegaMoE, or benchmark source edits.

## Motivation and scope

The final V4.1 NVFP4 and mixed decode sweeps select M128/N16 or N32 for both phases. At T32/128/512, mixed has the larger gap to matching TRTLLM. Current logical M512 already reuses an activation/SFB tile across two M256 operations in a two-CTA group. This experiment transfers that existing mechanism to two M128 operations in one CTA for N16/N32/N64.

This is distinct from the rejected small two-CTA experiment: CTA ownership and synchronization remain one-CTA, no cross-CTA scale publication is introduced. It also avoids repeating the rejected FC2 K512→K256 tail policy, physical-N16 epilogue transpose redesign, or deeper CLC queue.

- Add logical M256/cluster(1,1) for N16/N32/N64 to FC1 and FC2 choices. AUTO keeps all 13 old paired tactics and gains nine pairs (22 total), choosing reuse independently per phase.
- Pass physical MMA geometry and a direct `channel_tiles` compile-time count to the shared core. Existing logical M512 still maps to two physical M256 operations.
- Derive available accumulator columns from `cute.arch.get_max_tmem_alloc_cols("sm_100")` minus scale storage, using at most the existing two alternating accumulator windows. Use the same capacity-based SMEM stage allocator around epilogue storage.
- Preserve narrow K8, cache hints, CLC depth1/admission policy, PDL boundaries, per-token behavior, weight layout, packed arithmetic, iKET markers, and mixed FC1's inline epilogue.
- Keep all mainloop, scheduler, TMA/SF-copy, and epilogue function bodies unchanged. Channel reuse already threads through these functions; only geometry/capability/constructor policy expands.

For narrow NVFP4 N16/N32, the analytical per-stage operand bytes increase from 49152 to 86016, so automatic depth should move from four to two stages; total staged weight bytes stay the same while duplicate B/SFB work is reduced. Mixed FP4×FP8 should move from five to three stages, increasing staged weight bytes while still fitting capacity. The actual layout gate below confirms these stage counts. This alone is not a performance claim; sparse cases can still choose the original M128 tactic.

## Validation plan and current receipts

`check_static.py` extracts live host policy and constructors from source. All 90 old geometry/dtype/phase constructor states remain equal, including TMEM depth, cache policy, and warp roles. All 15 non-constructor/non-capability core function ASTs remain equal. All old tactics remain present. The static check uses SM100's architectural 512-column TMEM capacity; actual library/layout validation is separate.

`kernel_layout_audit.py` compiles the actual source SharedStorage definition for 252 policies (both model reductions, six dtype contracts, both phases, old and new geometries). It checks capacity, accumulator windows, TMEM bounds, and automatic sizing across object reuse. `probe_exact.py` compares old M128 to new logical M256 on identical input bytes in 18 focused cases: all three benchmark formats, both phases, N16/N64, actual V4.1 reduction sizes, channel/K tails, padded/zero routes, clamp, and per-token behavior. No dedicated upstream test file is added.

Scoped precommit passed after the formatter updated one file. Frozen patch receipt and static audit: `../../evidence/narrow-channel-reuse-r1/`. Patch SHA256: `ba51fa57b297abdbed523d4224a2b816661c74d98306fe372c2af9494fdd1d5a`.

The old B200 devbox was reclaimed, so this campaign uses fresh same-host B300 controls as described below. Any retained optimization must pass the same paired native V3 and V4.1 methodology; tokens1/2 remain measured but excluded from retention.

## B300 gate and fixed diagnostic

The replacement runtime is `fi-v41-gap-c2-1025` on c2, host `hu-pdx-150`, eight B300 GPUs, CUDA13.2 image `nvcr.io/nvidia/pytorch:26.05-py3`, CuTe4.7.1. This stream uses GPU5; GPU7 remains reserved for the independent mixed-overlap/K-tail stream.

Frozen R1 passed252 actual SharedStorage/layout policies and18 byte-exact old-M128/new-logical-M256 comparisons. Queried SMEM capacity232448B; selected automatic input depths2–7; maximum actual storage231296B. Source pins unchanged. Layout and exact checks took about26s and28s respectively. Raw output, commands and host/source receipts are in `evidence/narrow-channel-reuse-r1/`.

At V41 N16, NV M128→logicalM256 changes4→2 stages and197504→172928B FC1 storage; MX8 and mixed change5→3 stages and about216KB→231296B. Accumulator/TMEM allocation follows capacity calculation; this is not a hand-selected stage policy.

`launch_fixed.py` deploys a task-local screen with native benchmark routes, PDL, unfused finalize,10 warmups/100 cold-L2 CUDA-graph CUPTI iterations. Fresh baseline0c controls bracket FC1-only, FC2-only and both-phase reuse in forward/reverse order at V41 tokens32/128/512; both MX formats and NV are run sequentially on GPU5. Explicit fixed caches update MX architecture to10.3 and bind the entire valid-tactic list to each source. Old artifacts supply shape/route identities only; no old timings are reused. Every result verifies actual selected tactics and route hashes. This is a diagnostic, not AUTO retention evidence.

## Decision: rejected after fixed screen

R1's first native control exposed a host boundary: B300 preserved expert IDs but produced different sqrtsoftplus routing-weight bytes from the prior B200. The strict harness stopped before candidate timing. R2 binds to the fresh B300 control hashes and reuses the already completed fixed C1 outputs unchanged; all within-host route/tactic/source checks pass.

The repeated V41 N16 screen rejects this candidate. Across tokens32/128/512, paired geometric speedups for FC1-only / FC2-only / both are NVFP4 `.9831/.9959/.9785`, mixed `.9901/.9956/.9867`, MXFP8 `.9934/1.0009/.9904`. T32 FC1 reuse loses about3% in both NV and mixed. Baseline drift is below0.2%. No full AUTO or V3 sweep is justified for this rejected candidate. The nine additional tactics are not proposed for retention; the independent source copy remains unstaged for review.

Complete raw results and the resource-joined summary are in `../../evidence/narrow-channel-reuse-r2-fixed/`. The NV script also ran the untouched W4A16 column; its data is preserved but excluded from this decision. The narrow two-CTA and half-SMEM co-residency ideas remain separate: see `NARROW_TWO_CTA_AUDIT.md`; halving SMEM would allow two same-kernel CLC CTAs per SM and violate the intended one-CTA residency contract.
