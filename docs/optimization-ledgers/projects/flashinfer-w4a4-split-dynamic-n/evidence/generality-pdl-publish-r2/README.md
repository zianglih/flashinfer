# Immutable-ancestor publication owner experiment

This isolated experiment reduces redundant GPU release fences while preserving every dependency wait and trigger location. It changes only the blockscaled common core and routed-input prepare kernel over retained `dea2c065dc8e75ae26fe1ef8123e964db7b4eadb`. It does not modify the shared review checkout.

Decision: the parent approved integration on 2026-10-26, subject to the combined-source gate and performance screen. Small decode gains justify the subpercent prefill boundary under the user's stated priorities. The isolated measurements below are not relabeled as measurements of the combined candidate. See [retention evidence](retention-evidence.json).

- Source: [source.json](source.json), [candidate.patch](candidate.patch), patch SHA256 `6cbb9c460e5567d5402da45c800fd8e1adfe4ef499544c120df47150cda8087b`.
- Static grid: physical CTA `(0,0,0)` republishes completed immutable ancestors. Every CTA still triggers; the dependent wait still protects this grid's own payload.
- CLC: each executing cluster's rank-zero CTA publishes. A fixed physical CTA0 is insufficient because it could be canceled before starting. The singleton-cluster owner folds to compile-time true.
- The uncommon all-thread startup branch keeps its original trigger participation: every thread in its publishing CTA fences before that thread's first trigger. No payload writes are moved before the fence.
- Publication proof and references: [audit](../generality-pdl-publication-audit-r1/review.md), [generated-code proof](codegen-proof.json), [independent review](independent-owner-review.json).

## Exactness and code generation

The broader R1 source passed 114 byte-exact changing-input/route replays, including PDL on/off, empty local routes, persistent tiles, per-token scaling, static one/two-CTA, actual group-two CLC, and the uncommon all-thread startup branch. Six additional R1 replays captured prepare code generation. The only R1→R2 source change is the singleton-owner compile-time tautology; six R2 replays passed and singleton-CLC PTX matched clean `dea2` byte-for-byte with PDL on and off. These source-specific checks are deliberately reported separately.

- [R1 gate](../generality-pdl-publish-gate-r1/raw/validation.json)
- [Prepare capture](../generality-pdl-publish-prepare-codegen-r1/raw/validation.json)
- [R2 singleton capture](../generality-pdl-publish-singleton-codegen-r2/raw/validation.json)

Generated PTX confirms physical-XYZ ownership for static grids, rank-zero ownership for group-two CLC, and release before the publishing CTA's first trigger. All captured PDL-off PTX remains unchanged. No broad sanitizer claim is made.

## Bounded performance evidence

Both screens use the public benchmark, NV W4A4 and per-token arms with initial activation quantization timed, plus unchanged W4A16 as a control. Tokens are 4/128/4096; V3/K3 EP8, V41 EP4; 10 warmups and 100 cold-L2 CUDA-graph/CUPTI iterations. Each model's source arms run sequentially on the same GPU (V3 6, V41 5, K3 7).

1. [Native AUTO C1→A1](../generality-pdl-publish-auto-r2/comparison.md): actual tuner choices may differ. V3 reused its immediately preceding exact-source control rather than rerunning it.
2. [Fixed-tactic A2→C2](../generality-pdl-publish-fixed-r1/comparison.md): both sources load the byte-identical saved A1 cache using `--no-autotune --cache`. All 27 actual selected choices and compiled resource-plan records match. This is a separate causal diagnostic, not an additional native AUTO pair.

The fixed diagnostic improves all six affected four-token cases by 0.67–1.63%. Overall fixed C/A ratios for W4A4/per-token are V3 1.00786/1.00615, V41 1.00304/1.00040, and K3 1.00194/1.00016. Larger-token noise remains: V41 per-token T128/T4096 is 0.99652/0.99805, and both K3 T4096 arms are about 0.994. Unchanged W4A16 T4096 moves by +1.67% on V41 and +3.12% on K3. These data support a small decode benefit, not a universal speedup or standalone retention decision.

The source-bound JSON comparisons verify all 87 file pins, before/after source identity, same-GPU chronology, software/compiler versions, exact routing identities, arm quantization contracts, command flags, timing settings, helper hashes, raw stdout/CSV medians, and saved tactic caches. Native and fixed metrics are not pooled. No TRT performance result is attributed to this source change.

All performance/gate source copies, logs and generated artifacts remain unchanged. Prelaunch cache-generation and argument-size transport failures are preserved separately; none launched a GPU benchmark or produced a performance result.
