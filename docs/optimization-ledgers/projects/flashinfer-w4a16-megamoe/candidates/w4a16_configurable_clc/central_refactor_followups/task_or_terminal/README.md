Held CLC protocol trial on central source57e2. Only `clc.run` changes; all other
module ASTs and the current bundle-lifetime helper remain unchanged. Primary
source, runtime manifests, remote source and GPU execution are untouched.

The elected claim lane now encodes an unsuccessful pop that observes global
termination as -2. Successful task IDs remain nonnegative, while ordinary empty
polls remain -1. One existing cluster broadcast communicates this outcome,
replacing separate task and terminal broadcasts. Terminal counters are read
only after an unsuccessful pop. No new pipeline, helper, knob or synchronization
primitive is added, and the idle bundle broadcast is deliberately unchanged.

The claim pipe must receive every successful pop, including the final FC2 task.
This implementation checks termination only when the pop failed, so a final
successful pop cannot be overwritten by the sentinel. Its worker may perform
one additional cancellation/fallback iteration before observing completion.

Termination still requires all FC1 rows to have release-published and all FC2
feature tasks to have been claimed. It does not mean FC2 arithmetic has finished.
Each scheduler still waits for its own submitted epilogues, then publishes DONE;
the fixed finish launch still waits for the complete compute grid. Another
worker can observe termination while the final owner is submitting its claim:
that owner remains live and must drain its own claim pipe and epilogue before
exiting. Existing queue publication, CAS ownership and phase mapping are intact.

For an unpublished queue hole or stale empty observation, a head below the total
task count prevents termination. A head at the total can only result from
successful claims of previously published slots. The acquire counter loads and
published-row condition remain unchanged. C1/C2 synchronization uses the same
single outcome broadcast and explicit returned pipeline state.

Ruff, syntax, read-only patch admission, and all non-run AST comparisons pass.
Independent progress review, native lowering, numerical/replay checks and full
CLC8 before/after timing are still required. No performance gain is claimed.
Patch SHA256: e8662a2a21ad1346825b4d477c700ef3489a82c626da6ec3a7887e3b0acfd0c6.
