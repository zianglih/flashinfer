# One elected issuer per static B-stage issue batch

Active codegen-only candidate based475cae6b, unstaged in `flashinfer-w4a16-elected-issue-review`. No runtime test or performance claim yet.

Rubin's TMA gather producer (`rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:2024–2073`) enters one `elect_one` scope around its static gather issue batch. Retained W4A16 enters `elect_one` individually around everyGather4 call. This candidate moves only that scope around the existing unrolled row/K64 loop; the elected lane now performs destination-coordinate arithmetic and TMA issue.

All four issuing warps still acquire/advance/release their existing directB pipeline. All32 lanes retain their route-ID loads/shuffles outsideK and outsideelection. The gathered IDs, row/K ownership, multicast masks, fixedtransactionbytes, padding, fiveWGregisterroles, stagecounts, scheduler, PDL andFC2 are unchanged. Every calculation inside the new scope was warp-uniform before the change. Flattening elect_one scopes makes the entire before/after PythonAST identical.

Prior generated code already CSEs the ELECT instruction itself (8sites for16/24TMAgathers), so this may produce no benefit. The question is whether a larger issuer scope removes residual guard/argument-transfer control. ActualSASS on K3EP N128/N192 and narrowdecode is the first gate; no performance campaign unless it gives a concrete reason.

Rejected directions were checked first: runtime live-group loops lose5–10%stableprefill; inlinePTXpredicatedTMA alreadyloweredto extraSASSbranches inearlierlive-predicate experiment; unsignedW4 gather offset alreadyusesUSHF/masks inretainedSASS. None is repeated here.
