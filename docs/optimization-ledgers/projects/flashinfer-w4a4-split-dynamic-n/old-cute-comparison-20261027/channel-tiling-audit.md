# One-CTA logical-M256 channel tiling review

No static correctness blocker found in the two-file candidate in `flashinfer-channel-tiling-review` (base `0b7fe90151340d4fca6a5ec41a91019dde743819`). The candidate takes the already-keyed `cluster_shape_mn[0]` as the MMA CTA group, then derives channel tiles as `logical_m / (128 * group)`. This exposes physical-M128, two-channel-tile M256 in one CTA without changing device instructions or adding AUTO tactics.

## Proof and scope

`channel-tiling/resource-proof.json` binds the before/after core and host source hashes. Its executable source-extracted CPU census checks 8,640 old configurations across all six admitted dtype/scale combinations, all existing M/N tiles, K automatic/4/8, dedicated/inline epilogue, FC1/FC2, explicit/automatic stage counts and static/CLC requests. All constructor attributes, selected K, operand stages, accumulator stages, TMEM size, overlap eligibility, symbolic layout-call arguments, epilogue scratch and errors are identical. The hardware bounds are explicitly 232,448 SMEM bytes and512 TMEM columns; actual CUDA SDK layout lowering is not executed by this CPU proof.

For 360 new resource cases, M256/group1 admits N16/32/64/128 and rejects N256. M512/group1 is rejected because it needs four channel tiles; M128/group2 is rejected because it has no complete physical tile. There is no shape-specific new policy. N256 needs512 accumulator columns before adding any scales and therefore fails the existing TMEM capacity check.

Only constructor, K-capacity calculation, K selection and `can_implement` ASTs change. Every device MMA, epilogue, producer, scheduler and wrapper method is identical. The launch wrapper differs only by `cta_group_size=cluster_shape_mn[0]`; public signatures, launch-cache identity and AUTO candidate lists remain unchanged.

## N128 automatic plans

Analytical plans with dedicated epilogue, default stages, static scheduler and reduction2304 (NV uses the same quantized activation plan for per-token):

| Format | Phase | Existing group2: K×stages | New group1: K×stages | New TMEM cols | New overlap | New analytical SMEM |
|---|---|---:|---:|---:|---|---:|
| NVFP4 | FC1 | 512×4 | 256×4 |512|yes|221952 B|
| NVFP4 | FC2 | 512×3 | 256×3 |512|no|200960 B|
| MXFP8 / MXFP4x8 | FC1 | 128×9 | 256×2 |512|yes|203520 B|
| MXFP8 / MXFP4x8 | FC2 | 128×7 | 128×3 |512|no|187136 B|

The new geometry changes operand-ring depth and accumulator overlap materially; this is a resource tradeoff, not evidence of a speedup. It reuses B/SFB across two channel tiles while retaining two A/SFA payloads and two MMAs. The existing group2 control already divides B rows across CTAs, so an aggregate activation-byte reduction versus group2 must not be assumed.

Source review confirms the two weight stages use distinct `producer.index * channel_tiles + channel_tile` slots, separate SFA TMEM offsets and accumulator column windows. Both MMAs finish reading their shared B/SFB stage before the existing UMMA release. Output-channel offsets advance by physical MMA M, which becomes128 for this candidate; block/CLC mapping uses logical M = physical M × channel tiles. Group1 removes the cross-CTA SF join naturally while preserving local cp.async/TMA completion ordering.

The prior `evidence/narrow-channel-reuse-r2-fixed/summary.md` measured N16 at32/128/512 tokens and rejected broad narrow reuse: FC1 NV ratios were0.967–0.993× and mixed ratios0.970–1.001×. It did not measure this N128 prefill candidate on the current source. Those old results neither justify retention nor rule out a bounded wide-tile experiment.

## Pending validation

The task-local `channel-tiling/probe_chain.py` will compare actual public `CuteDslMoEWrapper.run(tactic=...)` calls on fixed saved quantized inputs/routes, unfused finalize, N128, K4/K8, old group2 control vs FC1-only/FC2-only/both group1. It covers standard/per-token NV, homogeneous/mixed MX, SiTU, ReLU2, PDL off/on and changing route states including zero local routes. For MX only, the helper registers its exact forced tuples in the in-process candidate list so the existing canonicalizer accepts the diagnostic choice; normal AUTO remains unmodified and all actual capability checks still run.

No production edits or GPU launches were made during this review. CUDA layout/compilation and exact replay results remain pending; no performance or retention claim is made.

The prepared `--quick` gate selects NVFP4 and homogeneous MXFP8, K4, group2 control versus both phases at group1, PDL off/on and all three route states: 8 captures and 24 replay comparisons. MX uses H384/I2304 for a partial output-channel tile, reduction tail and FC2 ring rollover. Full mode remains available only if later requested. The exact deployed command is `channel-tiling/quick-command.sh`; it does not launch automatically.
