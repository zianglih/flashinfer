# Compact dispatch rank selection

Active trial after the received-total and three-exhaustion-check changes.
Root applied the reviewed patch and froze source71a1b688/manifest81193dfc in the
primary checkout. See `frozen/` and `execution/` for source and execution records;
`proposal.json` preserves the original held proposal identities. Native3 passes
with1,016 fewer instructions per case and unchanged resources/protected
operations; numerical14/38 passes including uneven sources. FullAUTO is running;
no performance outcome exists yet.

The existing mapper unrolls `world_size + 1` min-peeling rounds at compile time.
Each round has a runtime `decided == 0` guard. This proposal replaces the unrolled
rounds and their repeated guards with a single `while decided == 0`, retaining
the exact body. A local AST comparison confirms that is the only executable
kernel change. A single existing-oracle test round is added below. There is no round counter, public knob, shape selection, new storage,
changed rank ordering, division rewrite or payload/publication modification.
The native loop should exit after its first successful round instead of crossing
the remaining unrolled guard/reconvergence pairs. A loop backedge replaces code
replication when unequal rank counts require additional rounds.

## Termination and collective participation

For one selected expert, every warp lane has the same slot index and offset;
per-rank remaining counts differ by lane. Ballot and min reduction produce the
same active mask, positive minimum and active-rank count in every lane. Thus
all lanes take the same decided/continue decision and preserve full-warp
participation in subsequent collectives.

Every unsuccessful nonempty round removes `length * num_active_ranks` slots and
subtracts the positive minimum from each active rank's remaining count. At least
one rank becomes inactive. Therefore there can be at most `world_size` nonempty
rounds, followed by at most one empty round that sets decided. This is the same
maximum represented by the old `world_size + 1` bound. For valid admitted tokens,
the containing round is found before the counts exhaust, because their sum is
the expert count and the slot lies within it. The empty fallback remains in the
unchanged body. This uses the existing nonnegative, nonoverflowing Int32 count
and prefix domain; it introduces neither a larger domain nor a defensive path.

On a successful round the same fns selection, remainder, quotient and offset
produce the same source rank and source-token index. The old subsequent rounds
only tested decided and skipped their bodies. The new loop exits immediately.
All scalar initialization, selected-token load, scratch use, phase and release
counters remain outside and byte-identical to the proposed three-guard base.

## Existing native evidence

Current64a8 N64/F4/direct SASS contains nine separate VOTE/CREDUX.MIN sites in the
rank-mapping region, beginning at d6c0/d6d0 and ending at10f60/10f70. After the
first round, successive outer BSSY/decided-branch/BSYNC regions occur at de00,
e500,ec00,f300,fa00,10100,10800 and10f00. Even a successful first round traverses
the remaining guards; the compiler has not combined them into one exit.
`current-native-excerpt.txt` preserves relevant lines from the actual saved
capture. That capture precedes the held three-guard removal and is structural
motivation, not the candidate's direct native control or a latency estimate.

Native validation should confirm one peeling body, an early successful exit,
warp-uniform collective participation, unchanged mapping arithmetic/protected
transport and compute operations, and no register/spill regression. The existing public `_check_numerical` rounds now include an `uneven_sources`
round with5 tokens on rank0 and17 on rank1. For experts0/2, counts are3/9;
for experts1/3, counts are2/8. Later slots therefore require a second nonempty
peeling round. Existing equal-count and empty-source rounds exercise the
one-round exit. The same independent MoE oracle, tolerance, layer, weights and
workspace refill remain in use; no new numerical harness is added. Full 1–4096 Mega-only AUTO decides retention, using one
complete immediately preceding Mega run and excluding1/2/4 only from retention.
No performance gain is inferred from lower static code size.


The held source was formatted with the repository-pinned Ruff0.12.8 before
execution. `formatting.json` records exact AST equality and current hashes;
`before_format/` retains the original reviewed patches and snapshots. Earlier
independent reviews describe the same executable AST.
