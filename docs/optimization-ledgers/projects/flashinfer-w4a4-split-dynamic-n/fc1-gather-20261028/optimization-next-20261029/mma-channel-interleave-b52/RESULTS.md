# MMA channel-interleave compile result

**Stop at the resource gate. No numerical or performance qualification was run.**

Base `b52e4e09649dc180fc7583a25ec35ff55f04654d`; frozen candidate `3b0114ea7b8099d759d9c62808d8752d2fa94fdda720f77024f4a6c4b8be64ac`. The actual-source AST proof passes, but ptxas moved live common values into local memory in the first M512/N128/K8 MXFP4x8 capture. Stack size shrank from128 to48 bytes while LDL sites increased16→38 and STL sites changed16→11. This fails the predeclared no-new-local-sites criterion.

The planned26 captures stopped after19. Both native probes, the second inherited MX spill and remaining matrix captures were deliberately not attempted. The compiler wrapper intercepted every owned MoE callable: this campaign contains setup and compilation only, with no owned MoE launch, numerical assertion or timing evidence.

## All captured pairs

| Capture | Phase | Channels | N | K stage | Static instructions Δ | Branch sites Δ | Stack old/new | LDL old/new | STL old/new | PTX/CUBIN identical |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 000 | FC1 | 1 | 256 | 512 | +0 | +0 | 0/0 | 0/0 | 0/0 | yes |
| 001 | FC2 | 1 | 256 | 512 | +0 | +0 | 0/0 | 0/0 | 0/0 | yes |
| 002 | FC1 | 1 | 128 | 512 | +0 | +0 | 0/0 | 0/0 | 0/0 | yes |
| 003 | FC2 | 1 | 128 | 256 | +0 | +0 | 0/0 | 0/0 | 0/0 | yes |
| 004 | FC1 | 1 | 16 | 256 | +0 | +0 | 0/0 | 0/0 | 0/0 | yes |
| 005 | FC1 | 1 | 128 | 512 | +0 | +0 | 0/0 | 0/0 | 0/0 | yes |
| 006 | FC1 | 1 | 16 | 512 | +0 | +0 | 0/0 | 0/0 | 0/0 | yes |
| 007 | FC2 | 1 | 16 | 512 | +0 | +0 | 0/0 | 0/0 | 0/0 | yes |
| 008 | FC1 | 1 | 16 | 256 | +0 | +0 | 0/0 | 0/0 | 0/0 | yes |
| 009 | FC2 | 1 | 16 | 256 | +0 | +0 | 0/0 | 0/0 | 0/0 | yes |
| 010 | FC1 | 2 | 128 | 256 | -7 | +0 | 0/0 | 0/0 | 0/0 | no |
| 011 | FC2 | 2 | 128 | 256 | +2 | +0 | 0/0 | 0/0 | 0/0 | no |
| 012 | FC1 | 2 | 128 | 256 | -7 | +0 | 0/0 | 0/0 | 0/0 | no |
| 013 | FC2 | 2 | 128 | 256 | +2 | +0 | 0/0 | 0/0 | 0/0 | no |
| 014 | FC1 | 2 | 128 | 128 | +8 | +0 | 0/0 | 0/0 | 0/0 | no |
| 015 | FC2 | 2 | 128 | 128 | -11 | +0 | 0/0 | 0/0 | 0/0 | no |
| 016 | FC1 | 2 | 128 | 128 | +8 | +0 | 0/0 | 0/0 | 0/0 | no |
| 017 | FC2 | 2 | 128 | 128 | -11 | +0 | 0/0 | 0/0 | 0/0 | no |
| 018 | FC1 | 2 | 128 | 256 | +25 | +0 | 128/48 | 16/38 | 16/11 | no |

All10 one-channel PTX and CUBIN pairs are byte-identical. The preceding8 two-channel K4 captures stay at zero local storage. The failing capture has25 more static non-NOP instructions and unchanged total branch-site count; neither number establishes dynamic cost.

## Failed-case locality

The retained case contains32 reachable local sites in the control role and none in gather or epilogue. The candidate has36/6/5 reachable sites respectively; these sets overlap at shared final-join helper code and must not be summed as distinct global sites. CFG traversal reports no unknown flows. Assigned register endpoints are not peak liveness.

- At0x0440, the candidate spills the shared cluster/barrier base to `[sp+0x28]` before role donation.
- At0x04c0, the candidate spills a halved grid value to `[sp+0x20]`.
- At0x0c90, the candidate spills the global routed-tile count multiplied by2 to `[sp+0x24]`.
- Those common slots reload across control, gather, epilogue and late barrier helper paths. In addition, MMA-local descriptor values use eight32-bit stack slots. The source has unchanged barriers, so attributing a specific timing regression would require execution; none was performed.

Raw failed capture: `evidence/matrix/candidate/capture/018-fc1.*`. Matched retained capture: `../control128-epilogue248-ce4/evidence/matrix/candidate/capture/048-fc1.*`. `codegen-analysis.json` records each role-local PC and instruction. `source-proof.json`, `control-reuse.json`, the source/geometry/resource guards and `frozen-verification.json` bind all artifacts to the frozen source.

The evidence archive SHA is `da196c5a2a3c6e5d7527954c1d89d866d038063efebc2107fa6b40a90a6ad844`. All121 archived files were hash verified. No quota or shape-specific rescue, source composition, exact run or benchmark has been performed.
