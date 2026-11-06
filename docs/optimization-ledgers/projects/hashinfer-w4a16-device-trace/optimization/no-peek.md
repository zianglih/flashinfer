# Direct transform waits experiment

Base: `002ef1454cbacde09972ed5e2ec7dcfe37e55749`; isolated worktree `optimization/no_peek`, with common Git metadata inside the current effort. No GPU operation or commit performed.

One shared decoder file changes by **22 deletions, no additions**. Remove the initial and lookahead raw `consumer_try_wait` and decoded-TMEM `producer_try_acquire` calls plus their cached status variables. Keep the existing blocking `consumer_wait(raw_state)` and `producer_acquire(transform_state)` at their original positions, ahead of decode. State reset/clone/advance, packed loads, scale decode, TMEM store, early raw release, completion fence, ready publication and all markers remain unchanged. Frontend exception/lifecycle semantics are untouched.

Hypothesis: the next raw-stage probe currently occurs after the last current-stage packed load but before its final conversion and TMEM store. If the emitted try-wait can suspend, that can delay publication of otherwise available current work. The next empty-slot probe similarly sits after current publication. Direct waits remove cached-status/control overhead and move all waiting into the instrumented ownership boundary. A source-level `try` name does not establish nonblocking hardware behavior; generated SASS is the relevant evidence.

This is **not** full or partial predecode: no register payload is intentionally moved across the TMEM ownership wait. It is also distinct from historical Entry057's MMA-control-warp readiness probe change; this patch affects transform producers.

Validation completed: Ruff check/format, git diff check, Python AST parse, and a full-module AST normalization check proving the only differences are removed peek assignments/empty branches and cached-status arguments. See `no-peek-source-audit.json` and `no-peek.patch`.

The helper is shared with split W4A16, so any retained change needs shared-path numerical/generated-code checks as well as Mega correctness and paired performance. It adds no branch or private flag to maintain during upstream sync. Generated-code resources, real wait semantics, GPU correctness and performance are not yet validated.

The separately prepared FC2 first16 adaptation is **paused** and preserved in `partial_predecode` plus `partial-predecode-paused.patch`. It touched three files (+114/-40), including a new half-fragment helper and 16-value decoder support, making future sync more costly. It was not GPU-tested or applied to the active candidate.
