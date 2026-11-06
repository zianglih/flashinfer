# Delay the scratch-read wait until buffer overwrite

Held source-only follow-up after compact rank selection; primary is unchanged.
Exact hashes are in `proposal.json`. This is a scheduling change, with no new
scratch, stage, runtime predicate/state, public knob or token mapping.

For flag batches larger than one, the current partial-batch path waits for the
pool store to finish reading the shared input buffer immediately after commit.
The proposal lets subsequent tracker bookkeeping and the next token's prefix,
rank and source-address selection run first. It executes the all-lane READ0
wait immediately before the next elected input TMA overwrites the same buffer.
The F1 path is removed from this change at compile time.

The intervening operations use lane-local state or immutable dispatch metadata.
They do not read or overwrite the scratch buffer, nor consume the uncompleted
pool destination. Tracker phase is always0; a change of task-counter address
only records a per-lane address and does not fire the batch. The threshold path
still has its full destination wait and warp synchronization before release.
The partial tail also retains full wait, warp synchronization, fire and final
handoff. Therefore moving READ0 does not allow early FC1 readiness publication.

Before any new scratch write, all lanes execute READ0, including the previous
bulk-store issuer, and then participate in the existing full-mask input
election. Preserve the existing full-warp/issuer protocol in native validation;
an election is not claimed to be a memory fence. Input mbarrier phases, the
pre-store full wait that limits outstanding destination groups, metadata/weight
stores and all publication synchronization are unchanged.

The [PTX election contract](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-elect-sync)
was checked live: a fixed member mask selects the same leader on each election.
This supports the same-issuer argument for the unchanged full-mask sites; it
does not add a memory-ordering property to election.

The [PTX bulk wait specification](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-bulk-wait-group)
distinguishes completion of source reads from completion and visibility of
destination writes. Only the source-read wait moves. A full destination wait is
still required before readiness publication. This source scheduling argument
is an inference using those semantics and the owned transport's dataflow.

The simple constexpr F>1 form executes one READ0 per admitted token, including
an empty wait before the first token and after full batches. It avoids adding a
pending-write predicate and removes the old post-store else arm. Those empty
waits are an explicit cost, not a free-performance claim. No wait is executed
for an entirely idle warp; the terminal full drain covers its unchanged tail.

Native review must verify actual pre-overwrite wait placement, no early
publication or local-memory regression, and preserve the mainline versus
election-recovery routing-load scoreboard qualification. Existing F1/F4/F8,
empty, full-batch/partial-tail, uneven-source and both-return numerical cases
cover the affected protocol. Full AUTO before/after decides retention; no
candidate compile, numerical or timing result exists yet.


The held source was formatted with the repository-pinned Ruff0.12.8 before
execution. `formatting.json` records exact AST equality and current hashes;
`before_format/` retains the original reviewed patches and snapshots. Earlier
independent reviews describe the same executable AST. Primary remains unchanged.
