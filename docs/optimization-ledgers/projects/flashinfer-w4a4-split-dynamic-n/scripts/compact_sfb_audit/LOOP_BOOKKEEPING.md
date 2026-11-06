# Warp3 persistent-loop bookkeeping audit

Read-only, 2026-10-25. Two concrete source-backed leads are worth preserving: reduce compact SFB copy/address sites through lane ownership, and specialize the existing TMA issuer loops so role selection occurs outside K. Neither is implemented or measured here. No new GPU work, production/source changes, warp-count change, or register-cap proposal.

## Evidence boundaries

Current source: [localwait core](../../flashinfer-sf-warp-localwait-review/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py), SHA `7f0fdbc4c53c9c0a7ac222e87d548269184b1fcce333d8a76f1af543bd880b4d`, including the per-iteration async-shared proxy fence after the local cp.async wait. The core changed from `dfcf99ba` during this review; the two leads below do not depend on that change. Current localwait SASS was not yet available.

PCs below refer **only** to archived predecessor warp-reuse core `2c4fee747528dc2bf6586b171c2757de5a3aaf4283867d0f233e7a3c7362319e`, pinned by archive manifest `cd05cf70297112cd8321117e444db27eb3fdf09d024b4ff002cc751fe6836476`. Files are [publisher SASS](../../evidence/sf-warp-reuse-98fd/raw/logs/sf-warp-reuse/resources-r1/publisher-fc1-n16.sass) and [control SASS](../../evidence/sf-warp-reuse-98fd/raw/logs/sf-warp-reuse/resources-r1/control-fc1-n16.sass).

The [NCU evidence](../sf_readiness_profile/README.md) belongs to earlier readiness core `0f570a27`: executed warp instructions6,575,874→7,639,172 (+16.17%), branch instructions304,195→643,155, unchanged useful MMA/TMA counts and nearly identical DRAM bytes. It establishes additional executed work for that earlier source. It does **not** attribute the delta to a particular role, PC, or the later warp3/localwait code.

Published TRT N16 source is [PR2917 architectural prior art](../trtllm_gen_decode_audit/README.md), head `64ed071e23bf8d5d2d5af5c91577e5b8e036a1cf`, not the source identity of the newer measured TRT cubin. All TRT line references below use `sources/src/Bmm_E2m1_E2m1E2m1_Fp32_bA16_bB16_bC16_t128x16x512u2_s5_et128x16_m128x16x64_cga1x1x1_16dp256b_rM_TN_transOut_schPd2x1x2x3_biasM_bN_ldgsts_ldgstsSf_rgTma_clmp_swiGlu_dynB_sm100f.cu` under that audit directory.

## 1. Distribute useful SFB words across all32 lanes

**Verified:** current core1464–1483 emits four atoms × two halves =eight4-byte cp.async/address/predicate sites per K512. Each lane owns one row, so lanes16–31 always issue zero-fill work under this physical-N16 specialization. The predecessor SASS has exactly eight LDGSTS sites at PCs `0x2400,0x2430,0x2460,0x24a0,0x24e0,0x2520,0x2530,0x2540`, surrounded by separate address/predicate setup. TRT `LoadSfBTask`1135–1268 has four4-byte copies per lane per K512; its lane layout distributes the useful16×32 scale bytes across all32 lanes. TRT's routed row-major source layout differs from our prepared canonical layout, so copying its addresses directly would be incorrect.

**Concrete prospective mapping:** use `row = lane % 16`, `half = lane // 16` and one copy per atom. Keep our current address expressions with those coordinates:

```text
channel = k_tile*tile_k + (2*atom + half)*sf_block_k
shared = stage*sfb_stage_bytes + atom*512 + row*16 + half*8
source = canonical_sf_offset(source_row,0,padded_k) + (channel/sf_block_k)*512
```

[CPU ownership receipt](loop_bookkeeping_receipt.json) proves the32 lanes × four atoms cover exactly the128 current active-row even-word destinations with no duplicates. All2048 stage bytes remain covered by those words plus immutable padding.

Safety requirements for any later implementation: change **both** source-row selection and cp.async validity to `row < valid`; retain `channel < K` zero-fill. Initialize the upper-row even words (rows16–31) in **every** source stage once, in addition to existing odd-word initialization. Rows0–15 outside the current dynamic valid count must still zero-fill every reuse, including grow/shrink across persistent tiles. Keep every lane participating in commit/wait/proxy-fence/warp-sync and the existing S2T publication protocol.

**Inference:** this could halve issued LDGSTS/address/predicate sites in the SFB loader and move invariant upper-row zero stores to initialization. It does not halve useful global-memory bytes—the current zero-fill lanes already perform no valid global read—and it does not prove a whole-kernel speedup. It is a non-TMA ownership change; payload TMA, canonical layout, public API, and scale lifetimes remain intact.

## 2. Select each TMA issuer role outside its persistent K loop

**Verified:** current core1094–1136 gives warps0–2 one common persistent-loop body, then1155–1259 repeats runtime `warp==1`, `warp==0`, and `warp==2` selections for every K stage. The different source-empty versus payload-empty waits and per-issuer transaction announcements also sit inside that multiplexed loop. In predecessor SASS, role branches survive at `0x0fc0/0x10a0/0x1110`, then `0x1300/0x1400/0x1470` in the second unrolled body. The role-specific wait/arrival region `0x0e00–0x0f30` contains BSSY/BSYNC and branch-around paths; it is emitted runtime work, despite role predicates being warp-uniform.

TRT makes `LoadTaskA::isSelected`208–210, `LoadTaskB::isSelected`404–406 and `LoadSfATask::isSelected`646–648 decisions in the outer kernel dispatch3983–4000. Each then enters its own persistent task's execute/K loop. It therefore exposes constant operand roles to that loop body instead of repeatedly multiplexing three TMA kinds inside one loop. TRT still has substantial pipeline/work-ID control and is not generally a simpler scheduler.

**Inference / bounded future lead:** an outer role split or role-constant helper could retain exactly the same three existing warps, byte arrivals, barriers, stage counts and lifetime policy while allowing unused descriptor construction, issuer tests and expected-byte selection to disappear. This is a code-organization hypothesis, not permission to merge SF and payload lifetimes or remove required completion operations. Check emitted SASS first; PC-level executed counts would still be needed to establish the runtime contribution.

## Static count correction and non-candidates

The previously reported1109control/1585publisher static counts omitted mixed-case TMEM mnemonics. The omitted sites are control7LDTM +3STTM +16UTCCP =26, publisher2LDTM +12UTCCP =14. Both correctly omitted nine trailing padding NOPs. The consistent totals are:

|Convention|98fd control|Warp-reuse predecessor|
|---|---:|---:|
|Including trailing padding|1144|1608|
|Excluding nine trailing padding NOPs|1135|1599|
|BRA including uniform variants|79|138|
|BSSY / BSYNC|1 /1|6 /6|
|TRYWAIT sites|30|52|

The root's derived summary now uses the corrected counts; raw archives remain unchanged. The [receipt](loop_bookkeeping_receipt.json) reproduces every mnemonic and relevant PC range with SASS/CUBIN hashes.

Static growth also includes twofold producer-K-body unrolling: publisher has ten static UTMALDG sites versus control five. The two corresponding groups are `0x1070/1080/10f0/1190/11a0` and `0x13d0/13e0/1450/1500/1510`. That is code duplication, not twice as many executed TMA loads. Do not equate the static count ratio with the separate NCU executed-instruction ratio.

A lower-priority observation is separate four-slot `sf_loader`/`source_consumer` wrap bookkeeping even though their indices advance in lockstep; SASS has two increment/compare/select sequences near `0x26e0/2700/2750/2770` and `0x2930–29a0`. Producer and consumer phases are opposite, so simply reusing a state object is unsafe. No evidence here establishes this as a larger cost than the two leads above. Likewise, source-level CuTe descriptor reconstruction is not enough to claim expensive rebuilding: emitted descriptors use uniform address adds, and TRT itself also updates descriptors.

Reproduce the read-only checks with `python3 scripts/compact_sfb_audit/check_loop_bookkeeping.py`. This reads existing files and writes only the local audit receipt; it performs no CUDA import, GPU operation, or source mutation.
