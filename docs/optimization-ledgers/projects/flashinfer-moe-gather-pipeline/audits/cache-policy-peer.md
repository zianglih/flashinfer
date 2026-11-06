# Fixed weight-cache policies: independent qualification review

Both candidates pass this read-only source/native-artifact review. No new GPU calls or tests were run, and no production files were edited. This qualifies the existing 12-cell performance screen; it does not establish retention or a speedup.

## Source scope and semantics

Both workspaces remain at `82254e20` with exactly one unstaged tracked change: `moe_swap_ab_kernel.py`. An independent AST normalization reconstructs each complete candidate from the base using only removal of `weight_cache_hint`, its local result/private parameter/call argument, and the two weight-payload/SFA `cache_policy` keywords. All other source behavior is unchanged, including activation loading/hints, scheduling, PDL, barriers, MMA, epilogues, finalization, and W4A16.

The old heuristic reads adjacent routed-tile expert IDs to choose NORMAL when another tile belongs to the same expert, otherwise FIRST. The candidates remove that metadata work and use one fixed policy for both weight payload and weight scale loads. FIRST retains the existing FIRST constant; NORMAL omits the optional cache hint. Neither adds a public knob, tactic axis, dtype branch, or shape branch.

These are numerical/ordering-preserving hint changes, **not cache-behavior no-ops**. They deliberately change reuse/eviction behavior. The old neighbor reads are not synchronization: the current expert identity, explicit pipeline barriers/waits, and immutable weight/scale data still control the same TMA transfers. FIRST can reduce weight pollution of activation residency but can also sacrifice useful weight reuse. NORMAL avoids the hint itself but can increase competition with activation data. Only the complete native screen can decide which policy is preferable.

## Independently checked evidence

- All six exact calls and 18 returned native kernels passed; source-guard hashes and measured kernel hashes match the reviewed local workspaces.
- All PTX/cubin/SASS hashes were independently checked. The independent parser counts every address-bearing SASS instruction, including lower-case TMEM suffixes, predicated instructions, and zero-operand forms. Its complete opcode deltas match the parent analysis.
- Before/after tilers, MMA-K, CTA count, PDL, epilogue configuration, compile options, native CUDA resource attributes, and cuobjdump resource counts are identical. Registers are unchanged; all stack/local counts are zero and no LDL/STL instructions appear.
- Finalizer PTX and cubins are byte-identical. Both tested configurations use the ordinary scheduler; there is **no fresh CLC qualification in this six-call set**.

| Mode | FIRST FC1 | FIRST FC2 | NORMAL FC1 | NORMAL FC2 |
|---|---:|---:|---:|---:|
| W4A4 K96/N256/one CTA | −13 | −25 | −21 | −29 |
| MXFP8 logical M512/two CTA | −48 | −30 | −64 | −37 |

Counts are static non-NOP instructions, not measured runtime instruction counts. Every GEMM loses two `LDG.E` operations, consistent with removing the neighbor checks. Other compiler allocations/lowerings also change; this is not a claim that only those two loads disappear. `MOV.SPILL`/`R2UR.FILL` decreases in MXFP8 are register-transfer mnemonics, not evidence of eliminated local-memory spills: LOCAL remains zero on both sides.

The corrected release cache gate is `runtime/parallel-node/cache-release-warm.json` (SHA256 `37efd2c2b68007e4e481ec775da93a8e7a90e1339e1471128f58e28e7f039088`). It covers four native modules, preserves the original cache, uses non-hardlinked outputs, and records release preflights with no Ninja work. Its explicit release loader supersedes the earlier verbose/debug warm-up record. Qualification timings are not performance evidence.

Machine-readable replay and source-normalization proof: `cache-policy-peer.json`; reproducible CPU-only audit: `cache-policy-peer.py`.
