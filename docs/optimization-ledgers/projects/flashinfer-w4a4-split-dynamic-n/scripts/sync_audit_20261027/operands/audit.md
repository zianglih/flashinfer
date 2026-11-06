# Operand and MMA synchronization audit at retained9334

Canonical source: `flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`.
Base commit: `9334cb34fe9c81653dc4748632f44449e9aecd8d`.
Independent review checkout: `flashinfer-sync-operands-20261027`.
Only this checkout's one kernel source has unstaged changes. No GPU launch,
canonical edit, public API, Rubin, W4A16 or tactic change was made here.

| Boundary | Dependency and decision |
|---|---|
| Common pipeline init fence | Publishes all initialized barriers; keep the retained deferred-constructor/final-fence design. |
| Weight/SFA/B TMA full | One CTA0 expectation covers both CTAs' transaction bytes; keep the byte count and all TMA issue/expect ordering. |
| Local SFB cp.async full | 128 producers per CTA; each MMA warp must observe its local completion. Keep it. |
| SFB async-proxy fence | Required after generic cp.async completion before async S2T reads. Keep it, including one CTA. |
| Two-CTA SF-ready relay | Same consumer phase as TMA full; can be folded into the TMA arrival count while retaining cluster release/acquire. Independent V2. |
| Common operand empty | Protects all weight/activation/scale reads, including channel tile1. Already shared since the retained shared-empty change; preserve one owner release and all writer acquires. |
| Accumulator full/empty | Producer waits for ownership; full commit publishes UMMA completion; epilogue releases only its documented consumed TMEM range. No change. |
| Producer/accumulator tails and teardown | Keep the existing common owner tail, accumulator tail and final CTA/TMEM joins in these candidates; neither changes terminal-lifetime assumptions. |
| Wide unused cp.async full storage | No constructed pipeline or access exists on TMA-SFB path. Remove allocation and account for it at compile time. Independent V1. |

Prior history reviewed: `scripts/shared_empty_20261026`,
`scripts/merged_operand_ring_experiment`, `NARROW_PIPELINE_2026-10-25.md`,
`scripts/sf_readiness_profile/INHERITED_PROXY_ORDERING.md` and
`GENERALITY_CORE_AUDIT_2026-10-25.md`. No revival of rejected producer-role,
separate scalar publication or single-election variants. Local CUTLASS merge
pipeline examples support count-based synchronization as a design reference,
not as performance evidence or a substitute for this kernel's ownership proof.

The independent frozen patches, source receipts, CPU probes and source-level
protocol reviews are in `v1-unused-sf-ring/` and `v2-folded-sf-ready/`. Their
isolated gates pass44/88 and48/96 core-pair/exact-replay counts respectively.
V1 exposed a metadata-alignment side effect, so `v4-aligned-composed/` combines
both patches with an unconditional16-byte tile-info alignment. The intermediate
`v3-composed/` remains frozen for source comparison. Installed SDK struct checks
prove the alignment adds no storage. Root owns final composition/gate/timing.
The operand review clone has no unique untracked work and was released to
root for removal after snapshot verification; all helper evidence remains here.
