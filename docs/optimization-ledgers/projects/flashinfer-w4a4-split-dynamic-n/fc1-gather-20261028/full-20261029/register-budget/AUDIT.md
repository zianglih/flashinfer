# Gathered FC1 register budget audit

Base fork head: `fb66a27e6b40bdbbefd1b8bf0c0fc3f3ada8af90`.
This diagnostic captures fresh executable CUBIN/SASS before launch using
`--keep-cubin`, per-call `no_cache=True`, and `CUTE_DSL_NO_CACHE=1`; timing from
these capture runs is not retention evidence. Normal persistent native caches
remain intact.

## Pool arithmetic

All430 FC1 instances in the completed full campaign reserve168 registers/thread
with384 threads. The128-thread role budgets80/128/256 use59,392 registers of
the64,512 initially reserved. Raising the control budget to112 uses63,488 and
leaves1,024. The control and gather warpgroups donate
128×[(168−112)+(168−128)]=12,288 registers; the epilogue consumes
128×(256−168)=11,264. Both producers remain donors, and the unchanged
non-reconverging scopes keep their donated register lifetimes separate.
All budgets are compile-time, independent of dtype, model, topology
and tile. The guarded executable must preserve the expected3 role instructions
and reserve sufficient initial pool before its first launch.

## Actual codegen at16384 tokens

| Model/topology | FC1 backend | Stack | LDL sites | STL sites |
|---|---|---:|---:|---:|
| N3U EP8 | W4A4 |16B|28|8|
| N3U EP8 | Per-token |16B|27|8|
| V3 TP8 | MXFP8 |0|0|0|
| V3 TP8 | MXFP4x8 |0|0|0|

No PTX local operations exist in these FC1 kernels; the LDL/STL sites are
introduced by ptxas. N3U spills three common scheduler/tile-loop values before
role donation (W4A4 offsets0x620,0x650,0xce0), reloads them across the control,
epilogue and gather paths, and updates the spilled tile index at persistent
work-loop boundaries. They are not isolated to gather-local payload operands.
V3 TP MX modes provide a no-spill control. FC2 has no local traffic in either
case and no register-policy changes.

Candidate: one line `setmaxregister_decrease(80)`→`(112)` for the FC1 control
warpgroup. Gather128 and epilogue256 remain unchanged. The independent local
`flashinfer-fc1-gather-register-review` clone keeps this change unstaged.
Fresh candidate SASS eliminates every N3U EP FC1 local load/store and stack
allocation in both W4A4 and per-token. V3 TP MX modes remain spill-free and
FC2 resources are unchanged. Binary register-policy and pool guards pass.
All applicable file-scoped pre-commit checks pass. Correctness tests and a
five-job C-A-A-C screen now run using normal compiler caches; diagnostic
codegen timing is excluded from retention evidence.

Evidence: `codegen-evidence/base-codegen/`, including CUBIN, PTX, SASS, resource
usage, ELF, exact source manifests and binary register guard receipts.

Partial paired evidence (full screen pending): N3U EP W4A4 gains3.117% at4096
and4.619% at16384, with low repeat spread; per-token gains1.944% and0.500%.
The completed N3U EP job mean is+1.262%. Other model16K cells show larger
phase drift and should not be used alone for retention.
