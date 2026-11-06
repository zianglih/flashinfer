# Elements/scales TMA ownership experiment

The full A/B ownership changes and smaller W4A16 FC1-only follow-up were rejected. No experiment source remains in an active review checkout. Integration, accuracy cleanup and GLM-5 publication are complete.

## Current decision and active work

- Full A/B: 64 matched qualified cells per variant, across all four models and EP/TP at tokens 4 and 4096. A averages −3.826%; B averages −3.690%. Both add cursor/polling complexity. Four N3U mixed-MX jobs remain unqualified because candidate MXFP8 FC1 allocates 8 local bytes. See [the independent final audit and full tables](final-ab-audit/RESULTS.md).
- The rejected full review worktrees were removed after verifying they contained only the approved kernel changes. Their measured source files, patches, manifests and results remain in `frozen-elements-scales-a/` and `frozen-crossed-b/`. See `rejected-workspace-cleanup.json`.
- The W4A16 FC1-only follow-up moved weight scales to the otherwise idle warp and preserved FC2, adding 33 net lines. The independent [40-cell audit](w4-fc1-only/combined40-peer-audit/RESULTS.md) reports +0.1075% overall, +0.3653% decode and −0.1013% prefill, with all 14 negative cells retained. This is effectively neutral and does not justify added role handling.
- Its rejected review checkout was removed after [final source validation](w4-fc1-only/final-source-validation.json) verified the exact measured file and absence of unrelated changes. Measured sources, patch and validation evidence remain in `frozen-w4-fc1-only/` and `w4-fc1-only/`.
- No experimental change was committed or pushed. Implementation cleanup now proceeds on retained upstream PR7290 in `../flashinfer/`.

## Completed A/B setup

- Retained control: `658a0c8942c7454050f990c0be3083aa61b6a89f`, clean and pushed on primary `flashinfer/` branch `codex/w4a4-split-dynamic-n` (PR7290).
- Variant A split the TMA roles by elements/scales.
- Variant B used weight elements / activation elements + weight scales for W4A16, and weight elements + activation scales / weight scales + activation elements for swap-AB. FC1 gathering remained separate, with swap's existing scale-completion relay following its activation-scale role.
- W4A16 source owner: `/root/integration_design_audit`, only `moe_w4a16_kernel.py` and its launcher if essential.
- Swap-AB source owner: `/root/w4a16_table_audit` (repurposed agent), only `moe_swap_ab_kernel.py`.
- GPU/harness owner: `/root/megamoe_glm5_regression`; root reviews and combines decisions. Use immutable source snapshots before GPU validation/timing, never a changing checkout.
- Node: existing C2 `fi-mega-scale-1029`, eight B300s, CUDA13.2 image `nvcr.io/nvidia/pytorch:26.05-py3`. Access/cache details are in [the completed-run handoff](../upstream-integration-20261029/megamoe-glm5/HANDOFF.md).

Read [DESIGN.md](DESIGN.md), [CACHE.md](CACHE.md) and [BENCHMARK.md](BENCHMARK.md). Preserve the four-warp FC1 gather group, all existing layouts/tactics, regular-TMA FC2, CLC/static scheduling, one/two-CTA behavior and partial K. Element and scale producers should retain dependency-free weight runahead before payload waits. Keep existing pipeline lifetimes and one full-barrier announcer. Avoid new public knobs, shape-specific branches or a large metadata framework.

Both variants passed source review and 32 fresh exact smoke cases each, across all five modes. All 128 kernels loaded by that smoke matrix had zero local memory; the larger N3U MXFP8 specializations subsequently failed the resource gate. The approved hashes are in `approved-smoke-sources.json`; earlier W4 v1 smoke is historical evidence only. Both final variants use warp-uniform votes over nonblocking barrier probes before cursor advancement.

The completed A/B triage contains 51,200 qualified CUPTI samples across 128 cells. Independent GPU lanes were exclusive; no tests overlapped performance on a GPU. No larger A/B screen is planned. The existing native benchmark harness and persistent native caches were reused. The native path preflight proved byte-identical compiler commands and warm cache reuse. No sanitizer was run. Added kernel complexity is not retained for neutral performance alone.
