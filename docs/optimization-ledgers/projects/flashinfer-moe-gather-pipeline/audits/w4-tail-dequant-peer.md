# W4 K-tail dequantization: independent semantic review

Status: no source-level pipeline blocker in the currently inspected prototype; ownership-layout proof and native qualification remain required. No source edits or GPU work by this reviewer.

## Exact contract

The internal argument is the compile-time **K extent consumed by MMA**, not unconditionally the original logical dimension. Split MoE supplies `mA_mkl.shape[1]`, matching its existing peeled K loop (`moe_w4a16_kernel.py:1982` in retained02de). Shared MegaMoE supplies `_fc1_k_tiles * mma_tiler[2]` / `_fc2_k_tiles * mma_tiler[2]`: its MMA loop still issues a complete K256 stage for every ceil-div tile (`megamoe_kernel.py:1414–1450`). Those padded transformed values cannot be left stale. The explicit padded handoff preserves Mega behavior without a fallback/default or another public knob.

## Pipeline lifetimes

For every raw/decoded stage and every dequantization participant, the prototype retains:

1. Raw full-barrier consumer wait.
2. Decoded empty-barrier producer acquire.
3. A clone of the current raw state before advancing it.
4. Exactly one raw state advance and optional peek of the next raw stage. The live branch preserves the original final-fragment location; the inactive branch only advances: it can occur only in the final stage, so the next-raw peek condition is necessarily false. That local peek status is reinitialized on the next helper call.
5. Common `_finish_transform_stage`: unchanged TMEM fence (or SMEM proxy fence), raw consumer release, decoded producer commit.
6. Exactly one decoded state advance and next-stage acquire peek; unchanged terminal producer tail.

The raw pipeline waits for all transform warps across its original multicast consumer set. The decoded pipeline still requires all `32 * num_transform_warps * cta_v_size` producer arrivals. Thus an inactive group's earlier arrival cannot publish a decoded stage before active groups finish or free raw memory still used by another group. No barriers, expected-byte counts, metadata records, CLC/static scheduling or PDL waits/signals change.

The predicate is warpgroup-uniform: loop stage and transform group are uniform for every lane participating in a transform copy. Warp-wide store operations are either executed by the whole group or skipped by the whole group. A skipped group does not read its registers; the subsequent MMA must not address those TMEM K columns. The next tile is protected by the same release/acquire phases, so stale columns are safe only because the current MMA excludes them, not because they are zeroed.

## Scope and remaining gates

- Current public split tactics have stage K256, 128 rows per CTA, M128 or M256/two-CTA and N8/16/32/64/128/192 where stage resources permit. The initial 10-geometry ownership probe covers those and all MegaMoE geometries. Gated-row64→row16 remapping changes M ownership only; it must leave K ownership unchanged.
- `can_implement` delegates to generic CUTLASS checks that admit a broader private geometry set, including 64 rows per CTA. Do not describe the initial probe as proving every generic helper configuration. Extend actual-layout proof to those constructible cases or establish the predicate directly from their partition K range; avoid a new shape whitelist.
- K-major NVFP4 tensor alignment implies K divisible by32; a wholly skipped group's K begin must lie at or beyond the rounded legal MMA tail. BF16 MMA K16 therefore does not round a valid public K tail across the skipped group boundary.
- Preserve partially live groups exactly, including their previous padded decode/store. This proposal removes only whole groups that no MMA reads.
- If the final tail touches every group (e.g. remainder160/192/224 for two groups ×128), the runtime predicate can be eliminated at compile time as well as for full-K. It would otherwise add work while skipping nothing.
- Full-K split and explicitly padded Mega specializations should retain native PTX/SASS/resource behavior. Signature changes alone can affect CuTe specialization/codegen; source similarity is insufficient proof.
- GPU qualification must exercise short K, multiple stages with a short last stage, ring reuse across work tiles, CLC/static, one/two CTA, both row contracts and unchanged full-K. No performance claim is made by this audit.
