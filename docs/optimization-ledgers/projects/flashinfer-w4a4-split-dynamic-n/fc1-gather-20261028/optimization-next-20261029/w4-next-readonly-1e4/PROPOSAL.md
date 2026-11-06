# Read-only W4 follow-up after1e4

No source changes or GPU experiment. Current full104 refresh owns4/5.

## Concrete new lead: combine scale selection with the retained duplication

The retained helper now duplicates its low input byte with a singlePRMT. The fragment wrapper still selects that byte first. In actual source-bound1e4 SASS, each FC1 capture has sixSHF scale selections before eight0x4400PRMTs. TPV3FC2 has the same sixSHFs. Other capturedFC2 paths instead retain six byte-extractionPRMTs and twoLOP3 masks before the duplication; the different lowering comes from the existing two-scale fragment path. This is concrete additional instruction work, not a pipeline-wait inference.

A compact prospective contract is to keep each independent16-value block helper but supply the original packed scale word plus a required compile-time byte index0–3. Its immediate becomes `0x4400 | (byte_index * 0x11)`. This performs selection and duplication in one instruction. The wrapper can pack scales into words of `min(32, scale_count*8)` bits: the32-value/two-scale fragment uses one16-bit word widened once;64/128-value fragments use their existing32-bit words. It then passes the word and byte index without shifts or individual byte extension. No backend argument, autotune axis, runtime branch, quota, stage, synchronization, arithmetic or16-value opaque-region widening is proposed.

The low-level helper is exported from its internal utility module, so changing its signature is an interface consideration even though source search finds only the fragment-wrapper production caller. Prefer a required explicit compile-time byte index instead of hidden default semantics; root should decide whether that handoff is worth the source change. Do not add a second duplicated decoder. The CPU selector proof covers all32input-bit basis vectors at allfourbytepositions. Actual source-level proof and compiled resources would still be required.

Expected benefit: remove scale-selectionSHF/PRMT/mask instructions from the dequant warp, potentially reducing its issue time. No register/performance gain is assumed: original packedword lifetime can extend to the last block helper, and compiler scheduling must be measured. Preserve the current independent helper boundary and direct/fallback conversion order.

| Native capture | Tokens | FC | Current source-register definitions before duplication |
|---|---:|---|---|
| ep-kimi-k3-w4a16 | 4096 | FC1 | {'LDS': 2, 'SHF.R.U32.HI': 6} |
| ep-kimi-k3-w4a16 | 4096 | FC2 | {'PRMT': 6, 'LOP3.LUT': 2} |
| ep-kimi-k3-w4a16 | 8192 | FC1 | {'LDS': 2, 'SHF.R.U32.HI': 6} |
| ep-kimi-k3-w4a16 | 8192 | FC2 | {'PRMT': 6, 'LOP3.LUT': 2} |
| ep-v41-flash-w4a16 | 4096 | FC1 | {'LDS': 2, 'SHF.R.U32.HI': 6} |
| ep-v41-flash-w4a16 | 4096 | FC2 | {'PRMT': 6, 'LOP3.LUT': 2} |
| tp-nemo3-ultra-w4a16 | 16384 | FC1 | {'LDS': 2, 'SHF.R.U32.HI': 6} |
| tp-nemo3-ultra-w4a16 | 16384 | FC2 | {'PRMT': 6, 'LOP3.LUT': 2} |
| tp-v3-w4a16 | 8 | FC1 | {'LDS': 2, 'SHF.R.U32.HI': 6} |
| tp-v3-w4a16 | 8 | FC2 | {'LDS': 2, 'SHF.R.U32.HI': 6} |

History exclusion: the original compact-scale experiment retained word+shift selection; this proposal removes that *remaining selection* by folding it into the newly explicit duplicationPRMT. It does not repeat rejected two/four-scale conversion fusion (larger assembly dependency region), custom dequant ownership, raw-ready/decoded-slot wait changes, scale preload, quotas, or stage balancing. Targeted currentpatch/Markdown and originalW4ledger searches found no0x4411/4422/4433 or required-byte-index helper experiment. This is bounded historical evidence, not an exhaustive claim.

## Rubin/MegaMoE comparison: no new gather proposal justified

Current Rubin gen-specialized mainloop uses four gather warps, eight-row index runs, dynamic omitted-row transaction accounting and elected Gather4 issue; W4 already uses four gather warps and static K/row issue ownership. The obvious transfers are closed: W4 batched route IDs, runtime live-group pruning, predicated gather and elected-issuer restructuring all have recorded qualification/performance failures. The recent W4 iKET output-acquire and decoded-slot waits remain near marker resolution, so late-acquire/raw-preload is not a new supported lead. I do not propose another gather/stage/quota experiment from this review.

Source references: W4 helper `moe_w4a16_utils.py:169–248`; actual captures in `scale-origins.json`; Rubin `block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1049–1075,1180–1285`; `CLOSED_LEADS.md`; originalW4ledger compact scales1586–1624, contiguous block ownership2985–3006, rejected multi-scale helpers1133–1154/2022–2068.
