# Control120 codegen follow-up

All four FC1 instruction streams (N3U EP W4A4/per-token and V3 TP MXFP8/MXFP4x8)
are identical to the112-budget version except `USETMAXREG.DEALLOC` changing
`0x70` to `0x78`. Both policies have zero stack/local accesses; all binary
register and pool guards pass. No120 performance campaign was run.

Keep112:120 adds no codegen benefit and consumes the remaining1,024 registers
in the existing initial CTA pool. The rejected120 local source copy was removed;
`candidate.patch`, `local-source.json`, `comparison.json` and complete codegen
evidence preserve the experiment details.
