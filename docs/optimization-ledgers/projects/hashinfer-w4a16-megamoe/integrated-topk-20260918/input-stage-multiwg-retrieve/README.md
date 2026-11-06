# Three-WG staging using the existing TMEM retrieve barrier

Prepared independently from exact `7dc9626909834bc70209e09784e9dfdebadceff2`.
This is the preferred **source prototype** over the preserved pre-init `69c36e20`
variant. No GPU validation, performance claim, promotion or queue change.

Only owned `megamoe_kernel.py` and `token_comm.py` change. Keep the original
relaxed init arrival, init wait, and two-CTA allocation order. Immediately after
the allocator call, dispatch plus both decode WGs copy activations. Allocation
is performed only by warp 0 internally, so the copy WGs can run concurrently.
All actual copy writers retain the generic-to-async proxy fence.

The existing TMEM retrieval barrier 2 becomes the copy handoff as well: fused
calls use 544 threads (warps 0–4 and 8–19), raw pre-staged calls retain 416
(warps 0–4 and 12–19). There is one source wait site, one phase and no new
barrier. Compile-time optional-input selection sets the count and the first
included high warp. Every included warp participates even for empty inputs.

After this wait, dispatch stages IDs/scores and capacity-tail ID=-1 using the
original prep ownership, then runs the unchanged preparation/publication/pull
body. The activation helper uses 128-lane WG-striped chunk ownership: the first
strip retains original dispatch ownership across all CTAs, with decode WGs
covering later strips. Both source layouts, both ID dtypes, deterministic and
IKR paths keep their existing arithmetic and transport behavior.

## Memory and lifetime proof

```text
original common init arrive/wait -> original warp0 TMEM allocation
copy WGs: global activation stores -> each writer async.global proxy fence
all544 participating threads: existing barrier2 sync
all128 dispatch threads: routing/prep -> existing grid synchronization
                        -> system/NVLink publication -> remote TMA pulls
```

The [PTX CTA-barrier semantics](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-bar-barrier)
order prior accesses of participating writers relative to participating readers.
`wait_for_alloc` is a real CTA named barrier, not an operation restricted to TMEM:
collected `TmemAllocator` lines 492–504 call `NamedBarrier.arrive_and_wait`;
collected pipeline helpers lines 689–702 call `cute.arch.barrier`; arch wrappers
lines 826–852 emit `nvvm.barrier`. `runtime-evidence.json` binds all file hashes.
The original init wait still establishes the peer-start guarantee needed by
two-CTA allocation. Neither `.alloc.sync` nor relaxed init arrival is used as
an activation-publication fence. The original pointer consumers still wait for
the allocator result. No shared/protected transport file changes.

Every CTA hands its own completed copies to its dispatch group; the existing
grid/system chain then aggregates readiness before remote consumers read.
Routing and counter-reset lifetimes are unchanged. Raw pre-staged calls compile
out both staging helpers and retain the original barrier membership and kernel
AST after resolving the new compile-time selector.

Register redistribution remains at original source sites: initial 96, epi 144,
control 80, dispatch 64, both decode groups 96. No blocking increase precedes
activation-copy completion. Control warps 5–7 are excluded from retrieval and
can reach their existing scheduler/ready-dependent work. There is no added
phase flag, public knob, geometry choice or kernel tactic.

## Checks and boundaries

`audit_source.py` passed full kernel AST reversal; exact raw specialization;
copy-body equivalence apart from partition; routing-body equivalence under
existing equal-live-row validation; unchanged other owned transport methods;
exact fused/raw participant counts; 1/2/3/148-CTA copy bijections, first-strip
preservation, contiguous per-warp chunks, empty/tail/large prefixes; and 90 routing
ownership cases including top-k17/32. Scoped production pre-commit hooks and
artifact Ruff checks passed. `git diff --check` passed.

These are CPU/source checks. Actual PTX/SASS must confirm the 544/416 barrier,
copy/fence ordering, absence of unintended runtime selector work, vector/generic
loads, role budgets and spill behavior. Existing native, queued/multirank and
numerical validation plus the full 1–8192 paired sweep must decide retention.

TMEM allocation may overlap staging, but its pointer consumers now wait for all
three copy WGs too. That can delay initial decode/epilogue work versus the
original dispatch-only path. Increased copy concurrency, compiler effects and
that extra consumer dependency are unmeasured tradeoffs. Preserve the older
pre-init trial and all evidence; do not combine cache hints in this control.
