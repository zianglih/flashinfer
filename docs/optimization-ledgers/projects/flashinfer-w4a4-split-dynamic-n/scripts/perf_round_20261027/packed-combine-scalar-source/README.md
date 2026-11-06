# Scalar metadata packed combine

Retained and pushed as `94a89e2cdef523da2bc57e262ab12b37f2ff064a`; the completed review copy was removed after all tracked files matched canonical source. Frozen2995-based patch and measured source identity remain in this directory.

Use raw BF16 pairs with packed FP32 multiply/FMA while retaining routing scales as FP32 metadata. Form the repeated scale pair inside each arithmetic helper; this removes the first variant's broadcast helper and avoids a doubled source-level metadata live range. No rounding, shape, launch, alignment or memory contract change. Actual register use is mostly unchanged from the first variant; code simplicity is the reason for selecting this version.

Fresh B300 validation:98 exact cases,74 compiled pairs, no candidate spills. Summed static instructions18,384→15,528 and all1,960 PRMT sites removed. The48-point fixed-tactic screen is neutral overall1.001934×, decode1.001416×, prefill1.002452×. This is an instruction-efficiency retention, not a meaningful speedup claim. See `../packed-combine-scalar/retention.json` and its raw screen evidence. Full public tables are refreshed only after the final composition is settled.
