# CTA-convergent handoff review

The unexecuted859 prototype placed the second640-thread named barrier in two
warp-conditional branches. Although participant counts and barrier IDs matched,
that is insufficient for the aligned PTX instruction contract. NVIDIA PTX ISA9.4
states that `bar.sync` is equivalent to `barrier.sync.aligned`, and aligned CTA
barriers require CTA-convergent use. Different warp paths may use the unaligned
forms; warp-uniform predicates alone do not establish the aligned contract.

Primary reference:
https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-bar-barrier

Decision: do not execute or promote859. Preserve its frozen source and staged
helpers. Revise the owned kernel to prepare metadata conditionally, execute one
shared second-handoff source site, then consume or perform dispatch cleanup.
Keep stable score storage and scalar state across that shared site; inspect
actual PTX/SASS placement and dispatch resource effects after compilation.
No added rendezvous, fence, or change to the existing ready-data dependency.

The published04 ownership refactor has one shared second-handoff site and is
unaffected. Its baseline timing continues. The broader pre-first-rendezvous
prototype must also keep aligned rendezvous convergent, rather than splitting
its arrival between different warp-dependent call sites. Any future owned
transport refactor should separate the rendezvous from the collective drain
cleanly and keep one common rendezvous site.

Earlier source reviews established arithmetic and participant counts but did
not catch the aligned-instruction constraint. They are superseded for859's
barrier qualification by this finding; no GPU result existed for859.

The pinned4.7.1 toolchain's qualified04 PTX confirms the instruction form:
`ownership-refactor/collected-codegen-first/evidence/comparisons/h6144-t128-k0/normalized/h6144-t128-k0/rank0/Sm100W4A16MegaMoEKernel.candidate.ptx.txt`
lines6180 and6273 each contain `bar.sync 8, 640;`. Thus the review addresses the
actual existing lowering, not only a hypothetical library default.
