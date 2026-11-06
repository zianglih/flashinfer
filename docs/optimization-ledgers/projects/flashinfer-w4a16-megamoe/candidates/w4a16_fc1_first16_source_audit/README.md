# FC1 first-x16 predecode: source-only feasibility

**Go for a later narrow private constexpr prototype, after the scalar/register trials. Do not merely enable the existing flag or change FC1's fragment cap to32.** No blocking prior FC1-specific first-x16 result was found. This is source/history and existing-native inspection only; no patch, new framework, native compilation, remote or GPU work was performed.

## Current shapes and row mapping

The private Mega kernel requests FC1 fragment128 in `_fit_raw_stages` (`kernel.py:328–337`) and FC2 fragment32 (`kernel.py:644`). The shared setup clamps that cap to the coalesced leading extent (`moe_w4a16_kernel.py:407–425`), so a requested cap alone is not proof of every instantiated shape. The saved a9 M256/N128 and M256/N64 captures show FC1's actual128-value fragment: four packed LDS.128 operations, two packed scale-word loads, then one final-fragment raw-state advance before its eight x16 conversions. For example N128 control PTX lines2914–2925 load all sixteen packed U32s/eight scales, and2926–2942 perform the single advance/probe. FC2 partitions the same128 values per thread into four32-value fragments. Other curated M/cluster geometries still need their actual view extents checked if a candidate is implemented.

Both FC phases use the same two-group partitioning and existing packed/BF16 RMEM tensors (`shared kernel:346–425`). FC1 additionally composes the packed and SF sources with the same row permutation (`private kernel:1173–1176`). The layout maps successive logical16-row bands to source offsets0,32,16,48,64,96,80,112, turning prepared gate32/up32 into gate16/up16 bands. It permutes feature rows, not K or the16-value scale block. Packed values and their scale therefore remain paired; no gate/up arithmetic or global alpha is part of this transform. Both groups retain disjoint ownership and the same TMEM destination layout.

The current `_decode_transform_block` asserts32 values/two scales (`shared kernel:442–469`), and the prologue also asserts32 (`521`). Adding `predecode_first_block=True` to FC1 would fail that assertion. Simply broadening it while copying the whole128-value idx0 before acquire would hoist all four packed loads and retain112 undecoded values across the wait. That is a broad preload, not the narrow first16 mechanism.

## Minimal potential edit outline

Preserve FC1's128 fragment/output tensor, its whole compact SF copy, both decode WGs and the collective TMEM store. Within the selected first fragment, use existing `flat_divide` views into32-value packed chunks and16-value decode blocks:

1. After the existing raw-ready wait, copy only chunk0 (32 FP4 values /16 packed bytes), then decode block0 (first16) into its existing BF16 subview. Do not load the remaining three packed chunks yet.
2. Keep the one decoded-stage acquire. After it, copy the remaining chunks into their original positions, retaining the existing final-fragment raw-state advance/probe after the last required packed copy. Decode blocks1–7 into the corresponding existing output subviews with the existing x16 arithmetic and one matching SF-byte view per block. Do not decode block0 again.
3. Keep the one collective store, TMEM store fence, raw release, decoded commit/advance/probe and sentinel tails exactly where they are. Both current FC2 and default split specializations must remain unchanged after constexpr resolution.

This needs a small generalization of the current block-view helper and a selective first-fragment packed-copy path, not a wholesale FC1 cap32 setting. The latter changes every fragment's SF extraction/loop scheduling and would be a separate experiment. The proposed source design introduces no RMEM allocation or semantic BF16 gather. Actual compiler packet gathering and load/store placement remain native gates; they cannot be guaranteed from views alone. Only two packed words for the second16 values need remain live with the first eight BF16-pair outputs and the already-copied scale containers, rather than all fourteen remaining packed words of the full128 preload.

Raw readiness already covers packed weights and scales. No TMEM write moves before acquisition; the saved current raw slot stays owned until the original release. Views act on the already-permuted per-thread source, avoiding any new gate/up or inter-thread data movement. The prologue remains inside the K loop so empty/sentinel behavior and padded K tails retain the existing ownership contract. This is within the current K stage, distinct from existing work-tile overlap and rejected generic lookahead.

## Prior evidence and limits

The old split ledger retained a combined barrier cleanup/fragment64→128 change (lines285–293), and describes broad x32/256 transform variants rejected at489–503. The label x32 does not establish an isolated FC1 fragment32 trial. Later128→64→32 trials explicitly target GEMM2 and leave fused GEMM1 at128 (5020–5027,5356–5363). No documented isolated FC1 cap32 or first-x16-before-acquire trial was found in the main/old ledgers or candidate notes.

The prior full decode-before-acquire and whole-loop x16 trials also explicitly leave GEMM1 unchanged (old ledger5486–5501 and5419–5431). Full packed preload and next-fragment lookahead were rejected (1268–1309); they caution against broadening the first16 prologue but do not answer this specific FC1 placement. Current native FC1 has a real blocking decoded-stage wait in its generated control flow, but no current phase-specific measurement establishes how costly that wait is.

A later gate must confirm actual views for all supported geometry families; exactly one first packed LDS.128 before acquire, unchanged total packed/SF loads and x16 conversions; correct gate/up scale pairing; no new output gathers/locals or unexpected register/CFG growth; first16 slow-wait liveness; and unchanged TMEM/raw publication order. Preserve the scalar/register trials as separate controls. No speedup is predicted.
