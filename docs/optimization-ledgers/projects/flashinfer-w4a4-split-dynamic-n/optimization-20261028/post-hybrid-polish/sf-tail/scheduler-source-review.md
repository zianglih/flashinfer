# Independent SF-prefix source review

No source blocker found in the frozen one-file patch. `_copy_sf` rounds logical stage K to complete four-scale words with `ceil(stage_k / sf_block_k)`, matching the existing SF copy granule. For SF16 this is K64; for SF32 it is K128. The native K96 plan rounds to its K64 base atom before decomposition, so its last consumed scale remains covered by this prefix. Native K32 mixed/MX updates are likewise covered by the SF32 K128 word granule.

Both descriptor and target views change only their K-word extent, preserving the original iterator and every stride. In particular, the dynamic-N K96 SFB row-bank remap is retained before this narrowing. Its compact or wide publication addresses are not recomputed from the smaller extent. A second channel tile follows the same helper and valid extent. Full-stage `words == target.shape[3]` preserves the old copy statement/view.

This review does not establish SDK copy legality or exact hardware behavior; the paired compile/output gate supplies that evidence. TMA transaction bytes, operand acquire/release, ring capacity, and SF storage allocation are unchanged by the patch.
