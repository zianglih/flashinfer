# Scatter4 issue-loop review

Read-only review of frozen scatter4 kernel `d86d47a34cbb4d7c23c64ad3de279fd79b1895ce17b0dc77d46b050864e1e8c6`.
No source edit or GPU launch. Sole-announcer source remains frozen.

Config7 FC2 SASS confirms implicit serialization despite no MATCH instruction.
The first half's `0x2530..0x25f0` loop contains five R2UR/R2UR.OR, six PLOP3,
one UTMASTG.SCATTER4 and one BRA.U.ANY backedge; the second half repeats this
at `0x2630..0x26f0`. Bulk64 selects four lanes whose shared source addresses
are distinct, requiring four command issues per half. Thus the current warp
executes eight command-loop iterations per slab. `config7-issue.sass` preserves
the bounded generated-code evidence.

The proposed general change is a constexpr loop over `tokens//16` four-row
groups, with `copy_row = warp*(tokens//4) + 4*group`. All four row-coordinate
shuffles execute across the full warp before lane0/election. Both channel
halves then issue from that single lane; all four epilogue warps remain active.

Within each iteration, copy_row is warp-uniform: warp is identical across its
32 lanes and group is a compile-time constant. The source pointer derives only
from that value, shared-stage base and constant half offset. The selected
output_rows register group is also uniform, even though its contents initially
vary by lane. A shuffle from a common source-lane index broadcasts one value
to every lane. Channel coordinate and descriptor are already uniform. The
coordinates therefore become semantically warp-uniform before divergence.
Do not move the shuffles inside the single-lane branch: their full-warp mask
requires participation from the source lanes.

Source issue-control target per warp/slab:

| Slab tokens | Commands | Current predicate/backedge instructions | Added shuffles |
|---|---:|---:|---:|
| 32 | 4 | 28 | 4 |
| 64 | 8 | 56 | 12 |

This counts six predicate instructions plus one loop backedge per command.
It excludes coordinate moves, the TMA instruction and future election costs;
it is not a measured gain or a promise of final compiler output. Explicit
unrolling can increase static code while decreasing dynamic issue-control
work. Generated SASS must confirm that no grouped-lane backedge remains.

Prevalidating the positive OOB row sentinel when output_rows is produced is
compatible and useful: it eliminates the current four comparisons/four selects
per slab and avoids replicating them in every explicit row-group iteration.
The helper default must preserve other callers' current invalid-row contract.

Group ownership remains safe if commit_group stays once per slab after all
groups and both halves. Lane0 owns eight commands for bulk64 or four for
bulk32; other threads commit empty groups. Every thread still performs the
existing wait_group.read before the 128-thread shared-stage join. The join
cannot complete until every issuing thread's source reads complete, so no
thread may overwrite shared storage early. Final source reuse is protected by
the same wait0 plus join. Do not add a commit inside the constexpr group loop:
the stage policy counts one committed group per slab. Existing destination
completion/publication behavior remains unchanged.

The [PTX bulk-group contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async-bulk-commit-group)
defines groups per issuing thread, including empty groups; the
[read wait](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async-bulk-wait-group)
protects source reads. `source-proof.json` checks complete identical command
coverage, source alignment and metadata register selection for both slab sizes.
No protocol blocker found; the next decision requires actual codegen and the
already-planned bounded exact/performance gate owned by the epilogue agent.
