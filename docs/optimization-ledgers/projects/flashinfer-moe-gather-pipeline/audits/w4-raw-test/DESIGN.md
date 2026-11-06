# Existing W4 raw peek: TEST instead of TRY

Source-only assessment on retained `2b8eb9d8`, W4 kernel `5e61d045`. The bounded
history search found no prior replacement of these raw readiness query
primitives. A small native qualification is justified; no source/GPU change or
performance claim is part of this audit.

The current V41F TP4/T4096 ELF groups two raw LDS.128 operations and the early
next-stage TRY under write-dependency barrier 5. The next conversion waits that
group after 40 intervening instructions and has 587 long-scoreboard observations.
The later loop branch waits a different mask. This is a concrete mixed
dependency, not proof that all 587 observations are query latency. Full loaded
ELF/PC replay is in `profiling/v41f-tp-w4a16-4k/` and the independent
`audits/v41f-w4-scoreboard-peer.json`.

The [CUDA 13.2 PTX 9.2 contract](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier-test-wait-mbarrier-try-wait)
defines TEST as nonblocking and TRY as potentially suspending; an omitted TRY
hint uses a system-dependent bound. Both successful acquire forms establish
the barrier's memory ordering. Installed CuTe 4.8 reflects this distinction:
`consumer_try_wait` delegates to `MbarrierArray.try_wait` and then NVVM TRY;
the existing `MbarrierArray.test_wait(index, phase)` delegates to NVVM TEST.
Both use the same full barrier pointer and parity. Previously captured TEST PTX
from this exact SDK emits `.test_wait.parity.acquire.cta.shared::cta.b64`.

The compact candidate would replace only the two existing raw query calls in
`_transform_tile` with:

```python
a_load2trans_pipeline.sync_object_full.test_wait(
    a_load2trans_consumer_state.index,
    a_load2trans_consumer_state.phase,
)
```

No private helper, new persistent state, cursor, flag, or timing policy is
needed. Both the initial and next-stage raw queries use the same policy.
`consumer_wait(state, token)` remains unchanged: false follows the original
blocking wait; true relies on that same phase's successful acquire. Decoded-slot
TRY, raw/decoded advances, release/fence/commit, PDL, stages and layouts remain
unchanged. The existing SDK TEST wrapper omits the named `_mbar_scope` metadata
used by TRY, but both split and Mega construct this raw pipeline without a
`name`, so TRY's scope is already a null context. Existing iKET ranges remain.

The next query observes the already-advanced raw state after the current raw
fragment loads. A true token cannot become stale: this consumer has not yet
released that next slot, so its producer cannot complete another reuse cycle.
A false token may become ready during decode; the unchanged mandatory wait
handles that safely. With one raw stage the next parity cannot complete until
the current release, but TEST returns without suspending current decode/release.
All threads retain their own acquire/false-fallback path; no cursor advance is
made conditional on lane readiness. The wholly unused K-group branch occurs
only at the last stage, and each new work tile overwrites the initial token.

The shared method is called by split FC1/FC2 and `_MegaMixedInput` FC1/FC2 at
`megamoe_kernel.py:1597,1607`. Mega passes its padded K extent and overrides only
stage completion ordering; neither behavior changes. Dense W4 has its own
method and is outside this scope. If a candidate qualifies for retention, it
needs native/exact coverage for both split and Mega plus the established GLM5
before/after measurement, not a split-only knob.

History exclusions are explicit: the original W4 ledger's accumulator/activation
and dual-operand probes at 1852/1927/1991/5311 change placement or add polling;
the later `w4a16-raw-wait-b52` removes the raw token; the rejected swap readiness
experiment adds a persistent Boolean and an earlier next-slot query. None is
this two-call primitive substitution. This bounded search does not assert that
every unindexed file was examined.

Qualification must check actual PTX acquire/scope, native TEST placement and
scoreboard grouping, registers/local storage and all unchanged fallbacks.
TEST can return false more often and add blocking fallback traffic; initial
query plus immediate wait may become less efficient. Even with an unchanged
source-level query count, compiler scheduling/resources can change. The hot
group also contains real LDS work, so there is no predicted percentage gain.
