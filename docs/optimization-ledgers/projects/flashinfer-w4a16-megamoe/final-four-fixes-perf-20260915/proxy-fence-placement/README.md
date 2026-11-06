# Earlier proxy-fence placement proposal

Unapplied alternative based on local 979ac4bd. Move the existing FC1 fence and compile-time dispatch-return FC2 fence from completion signaling to each epilogue body's end. All 128 writers still fence once per appropriate tile. Direct epilogue return still adds no FC2 fence. No arithmetic, TMEM completion wait, release flag, tile guard or register setting changes.

The proposed order is each writer's stores → its proxy fence → next-work-record consumption → existing 128-thread rendezvous → existing batched completion publication. A fast writer can reach the fence while peers finish their stores. Every writer must have completed its own fence before any lane leaves the rendezvous and publishes readiness. Zero-token/OOB tiles retain the same conservative participation, and phase-change/final batch flush behavior is unchanged.

This changes placement, not fence count. It may overlap the ordering work with scheduler/peer progress; it may instead expose it earlier or alter code scheduling adversely. No performance gain is claimed. Python parsing, narrow AST placement checks and git apply --check passed. Generated ordering and numerical/sanitizer checks are still required before promotion.

The proposal remains a separate artifact while the FC1 wait-deletion trial runs. It can be applied independently of the paired FC2 transpose proposal. Source and patch hashes are recorded in manifest.json.
