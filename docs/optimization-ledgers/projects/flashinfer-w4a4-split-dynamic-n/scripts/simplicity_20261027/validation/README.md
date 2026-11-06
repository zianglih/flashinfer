# Simplicity cleanup validation

Frozen base `ed67c4857ce4e8d8cc047cf3808e2efa65e874b2`; candidate patch
`d7cb185e35f55c39c67eb3ae0a0edaf5f9aa1838a777cdd26d6afd39bf4c1087`.
Both source copies are immutable under the existing c3 B300 devbox's persistent
`simplicity-20261027` campaign. The 4,389 native source hashes match the retained
C++ cache; each source has its own DSL namespace. No production edits or commits
are made by these helpers.

The clean ed67 source matches all87 source hashes of the retained prior composed
candidate. `cleanup/control-equivalence.json` records this equivalence. Fresh
paired controls are still used because the task-local observer now moves the
inline/overlap diagnostic selection from the removed private wrapper argument to
the same kernel constructor setting, in both arms. The shared five-field tactics
and separate FC1/FC2 scheduler assertions remain unchanged. PrepareRouted codegen
is captured as well. `helper-origins.json` preserves prior helper hashes.

The main paired gate covers four formats, one/two CTA MMA, static/CLC scheduling,
both PDL modes, inline/dedicated epilogues, changing/live/empty/padded routing and
terminal drain. Supplemental natural N256 standard/per-token stage reuse and
M512 narrow CLC/static cases bring coverage to120 replay comparisons and60 core
pairs, including repeated geometry for supplemental telemetry. Existing CPU
tests cover13 tactic-enumeration and29 can_implement cases. A bounded NativeDump
IKET smoke uses one one-CTA and one two-CTA geometry against the saved exact
control output hashes.

`compare_codegen.py` ignores only function/header names and whitespace. It
compares normalized assembly, all instruction encodings and scheduling-control
words, NOP padding, and register/stack/shared/local resources. Equal instruction
counts alone do not satisfy codegen parity. No performance rebenchmark is needed
when those executable comparisons match; this gate makes no new timing claim.
This is focused exact/codegen coverage, not exhaustive correctness or sanitizer
coverage. Native AUTO and public benchmark scripts are unchanged.

Completed validation is recorded in `cleanup/final-validation.json`. All 120
source-paired exact replays passed; all 60 GEMM and 22 PrepareRouted compiled
pairs have identical executable instruction encodings, scheduling-control
words, normalized assembly and resources, with no spills. The existing tests
passed all 42 cases. The actual IKET tracker/profile processes each compiled
eight variants and passed 16 exact replays; 52 traced GEMM launches contain
174,588 paired scheduler ranges. The 908-file collected manifest is verified,
and the large raw traces remain remotely available with recorded SHA256 hashes.
`cleanup/retained-source-binding.json` independently verifies all 87 tested
source-file hashes against commit `1fab0dc8d9da5ac0f4ca81a9fecad7cda9e95729`
using Git blobs, without reading the now-changing review clone. No timing rerun
was performed.

The final structural follow-up is pinned in
`structure-final/final-validation.json` at patch `9d32a299`. It reuses the
explicitly attributed phase1 candidate controls and passes 48 exact replay
comparisons, 42 existing tests and the W4A16/prepare dependency import smoke.
Of 24 GEMM and eight preparation pairs, 31 are instruction/control-word identical.
The remaining FC1 per-token PDL-off pair has a reviewed descriptor-register
live-range permutation (17 instruction words); scheduling-control words,
opcodes, ordering, branch offsets and resources are unchanged. The strict
identity result stays false for that pair. All 294 collected artifact hashes
are verified, and no performance rerun was performed.
