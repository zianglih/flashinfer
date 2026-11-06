# No signed-remainder or full-K predicate rescue

Read-only follow-up on the two frozen pilots; no source edit or GPU rerun.

In the failed MXFP8 N256/K256 G2 image, `gather_thread % 2` is already reduced to low-bit extraction. PTX lines 3779–3780 compute `shl.b32 %r129,%r2,7; and.b32 %r73,%r129,128`, where `%r2` is the thread index. This is `(tid & 1) * 128`, the channel offset. Lines 3763–3764 similarly compute the shared word contribution as `(tid << 9) & 512`. No PTX remainder/division instruction survives. SASS at `0xd440` combines the lane contribution and current K base with `LOP3.LUT ... 0x80 ... 0xf8`; it does not contain signed-remainder correction work. The narrow G4 pilot also lowers the word lane directly to `and.b32 ... %r2,3`.

Both pilots have full-K FC1 specializations. In the failed G2 candidate, PTX lines 3902–3919 build the four `ignore_source` inputs only from each row's comparison with `valid`; lines 3924–3970 perform the K-stage address calculation and four 4-byte copies without any `channel < logical K` comparison. The control similarly has two row-valid predicates reused over four copies. Therefore the extra predicates in this candidate are row ownership/validity work, not residual full-K channel guards. Partial-K variants were never reached and are not covered by this conclusion.

The native stop remains genuine register spilling: 43 LDL and 15 STL sites, driver LOCAL_SIZE_BYTES64, and STACK64 in cuobjdump. Replacing `% G` with `& (G-1)` would restate an optimization already present in the generated code. It is not a reason to rerun this candidate.
