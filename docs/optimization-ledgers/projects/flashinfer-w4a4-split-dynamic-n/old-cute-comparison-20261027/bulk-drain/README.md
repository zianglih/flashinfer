# Deferred bulk shared-read drain

Rejected experiment, formerly in the local `d02c487a` review, one kernel file only. Deployed measurements remain frozen at `0b7fe901` plus the exact committed `cf5cd581` benchmark; `local-remote-equivalence.json` verifies all87 recorded source bytes equal the local d02 candidate. Move the existing final `wait_group.read 0` and 128-thread transpose join to the next bulk epilogue entry, after its routing metadata loads. Add an unconditional final drain for the actual epilogue owners after their scheduler loop. No buffers, ring phases, public APIs, AUTO tactics, shapes or policy knobs change.

The entry wait completes every issuing thread's old shared-memory reads; the same named barrier joins all 128 readers before scratch can be overwritten. This is the PTX [bulk wait-group contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async-bulk-wait-group). `.read` protects source lifetime, not completion/visibility of all global writes. The existing kernel-completion/dependent-wait contract is unchanged.

- Metadata and the caller's accumulator wait use distinct global/TMEM storage. They may precede the old shared-read drain. Operand buffers and epilogue scratch are distinct allocations.
- Every helper invocation resets its local stage index and drains before the slab loop. Two channel tiles therefore cannot overwrite each other's pending scratch. No cross-call group count is carried.
- Entry draining is outside the live-slab predicate: reverse traversal may skip its first slabs. Forward/reverse order, local reuse waits, commit groups and early accumulator-release boundaries remain unchanged.
- A no-channel call can bypass the helper, and no-work CTAs can bypass its loop entirely. Both still reach the final drain in their actual 128-thread epilogue owner path. The final common CTA/TMEM teardown follows it. Two-CTA scratch is local, so no new cross-CTA publication is needed.
- Normal epilogues release accumulator ownership after TMEM loads finish, independently of shared-to-global reads. The overlapping-accumulator prefix releases at the same existing boundary. Neither can make old scratch mutable before the next entry drain.
- Inline epilogues drain after their loop before producer exit/tail; separate epilogues drain after their loop. Producers, MMA and scheduler warps do not join the 128-thread transpose barrier.

Prior `scripts/sync_audit_20261027/scheduler/v2-bulk-wait` moved the *within-call* stage-reuse wait after register preparation and retained the terminal drain. The scheduler audit deferred a stateful cross-call ring; this experiment instead retains a full drain at every next entry, with a one-time empty entry wait and final tail. No measured prior terminal-deferral candidate was found.

The expected opportunity is overlap with next-work metadata and accumulator wait, plus earlier ordinary accumulator release. The added empty first wait and final join can offset it on short/nonpersistent grids. Codegen and a source-paired exact gate are required before the requested fixed native-winner performance bracket; no benefit is assumed.

`check_source.py` proves the full executable AST differs only by this motion and the two owner-path tails. Gate scope: NVFP4/MXFP8, native M256/N256 overlapping forward/reverse windows and M512/N128 two channel tiles, PDL off/on, balanced/zero-local/reactivated partial routing. Eight graphs and 24 replays per source, 48 paired replays total.


## Bounded result and remaining retention checks

The initial source-paired gate passed48 exact replays (24/source). Eight FC1 PTX/executable sections remain byte-identical; all16 paired resource plans agree and no LOCAL/STACK allocation appears. Helper-only metadata failures and the exact unused benchmark exception are documented in `gate-notes.md`; performance sources have identical benchmark bytes.

The first fixed native-winner C–A–A–C bracket completed16legs/1600rawsamples onGPU2. Control/candidate ratios: V3 NV1.001755×, V3 MXFP8 1.018712×, K3 NV1.004297×, Nemo NV1.006377×. V3 MX drift exceeds its paired effect and K3 repeats disagree; these do not establish a robust general speedup. Raw samples, source/cache/dispatch checks and independent arithmetic review are under `perf-fixed-r1/`.

The supplemental CLC/inline gate passed 24 exact replays (12/source), including empty/reactivated routes, persistent CLC work and inline two-channel epilogues. All 16 compiled resource plans match; see `gate-owners-r1/audit.json`.

`decode-inactive-proof/receipt.json` binds all 16 saved T128 model/format winners: 15 compile the changed paths out; Nemo NVFP4 is the only affected decode case. Four representative decode C–A–A–C brackets and an independent four-case prefill repeat completed under `perf-retention-r1/`, with process-boundary clocks/power/temperature and compiler artifacts. All 3,200 samples and 344 inputs passed independent audit. Decode stayed neutral; prefill effects were inconsistent/drift-sensitive. Parent rejected the change. `disposition.md` records the final comparison and `cleanup-{local,remote}.json` records removal of the verified candidate source trees with caches, symlink targets and experiment evidence preserved. No AUTO sweep or source-policy expansion was used.
