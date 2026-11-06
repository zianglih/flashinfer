# Integrated finalize: exact store-completion audit

Reviewed dispatch source `5362e5357607cade5ecb4385e432708f4f7ca9c2` and the
isolated decode2WG handoff. No production edits or GPU launches.

**Verdict:** no missing completion/visibility edge identified in either supported
BF16 return mode. The old external reducer's kernel boundary is not needed to
complete these writes: both paths already establish the required order before
`kernel_tail` returns to the participating dispatch warps. Do not add a new
proxy fence, system fence, or bulk wait based on this audit.

Paths below are relative to the reviewed HashInfer source. Source and archived
runtime/codegen hashes are recorded in `integrated-store-completion-review.json`.

## Epi-warps return: generic stores throughout

`cute_dsl/megamoe/bf16_nvfp4/tmem_epilogue.py:585–625` emits the FC2 BF16 return
via CopyUniversalOp global stores, using the source-rank destination router.
This path does not issue an asynchronous bulk/TMA global output store. Constructor
validation in `megamoe_kernel.py` requires `non_ubulk_fc2_store=True`.

Each epilogue thread executes `fence_acq_rel_sys` after its final epilogue stores
(`megamoe_kernel.py:1342`), before TMEM release/free and the complete 640-thread
`kernel_tail` rendezvous (`1355–1357`). Tail dispatch warps then run the grid and
cross-rank release/acquire protocol described below. The local/peer generic stores
are ordered before that publication. Releasing the MMA accumulator earlier does
not permit this thread's final store to bypass the tail rendezvous.

## Dispatch return: both async stages have explicit completion

1. FC2 first stores the BF16 local expert output using the same generic STG
   helper. Its epilogue WG rendezvous follows all tile stores
   (`epilogue.py:160`). `signal_fc2_done` performs `fence_proxy("async.global")`
   before publishing the GPU-release done counter (`epilogue.py:196–210`,
   `flag_batch.py:93–119`). This is the generic-to-async publication required
   before dispatch reads that pool with TMA.
2. Dispatch's `spin_wait` is acquire-scoped (`moe_utils.py:105–115`), including
   the first already-ready load. `token_comm.py:1332` waits for the expert's
   complete FC2 publication count before initiating its transfer.
3. For every token chunk, `token_comm.py:1391–1401` issues the global-to-SMEM
   async copy and waits its transaction mbarrier. It then issues the SMEM-to-
   local/peer-global bulk store (`1409–1413`; `ptx_helpers.py:75–91`). The shared
   staging data is produced by the async copy itself; no intervening generic
   SMEM write requires a new generic-to-async fence.
4. **Each chunk commits its bulk group and waits group0 without `.read`**
   (`token_comm.py:1415–1416`). This is a full destination-completion wait,
   not merely permission to recycle the SMEM source. No final token/chunk
   escapes this wait. The loop then finishes with `fence_acq_rel_sys`
   (`token_comm.py:1480`) before joining the 640-thread tail rendezvous.
   The dispatch issuer belongs to that rendezvous, so non-issuing lanes cannot
   publish overall completion without it.
5. BF16 return has no scale-factor payload; `push_sf` is compiled out.
   The lower-precision opt-in IKR path is excluded from integrated deterministic
   finalize and has not been repurposed by this change.

The captured installed CuTe wrapper (`nvvm_wrappers.py:1058–1071`) passes
`read=None` when omitted. Retained generated PTX confirms this wrapper emits
`cp.async.bulk.wait_group 0`, without `.read`. **The cited PTX5384 is an input-pull
copy, not a generated dispatch-return copy**; it verifies the API lowering, not
that particular compiled tactic. No fresh integrated dispatch-return PTX was
available to this audit. Checking its full-wait spelling during the already
planned codegen collection would strengthen the receipt without another run.

## Cross-rank and local consumer visibility

The unchanged `token_comm.py:1791–1795` full-CTA rendezvous collects all producer
roles. The first tail NVLink barrier (`1829–1840`) includes dispatch grid sync
before and after system-release signal updates / system-acquire signal waits
(`1534`, `1547`). `grid_sync.py:98–134` uses GPU-release atomics, a GPU acquire
fence, and participant barriers to relay the completion to all dispatch lanes.
The second tail publication barrier and local reset remain unchanged.

Thus dispatch-only reduction starts after its own participating lanes have
observed all ranks' completion. Decode2WG uses the additional all640-thread
next-phase barrier8 to hand that readiness to decoder lanes before their loads.
No new asynchronous operation is launched between final store completion and
the integrated reads. The transport uses peer-mapped addresses into the symmetric
heap, not queued NVSHMEM put operations requiring a separate library `quiet`.

## Primary semantics checked

[CUDA13.2 PTX bulk wait](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-bulk-wait-group)
distinguishes full completion (source reads, destination writes, and visibility
to the waiting thread) from the optional read-only form.
[Async-proxy semantics](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#async-proxy)
specify an implicit generic/async proxy fence on observed bulk-copy completion.
That supplies async-to-generic visibility before the existing release/acquire
relay. A source read-only wait would be insufficient here, but it is not what
the current API calls emit.

## Boundaries

This is source and retained-runtime/codegen evidence, not a fresh GPU hazard
proof. Native, racecheck, synccheck and numerical qualification remain necessary.
No claim is made for unrelated quantized MegaMoE backends or arbitrary concurrent
reuse of one workspace. The previously documented next-invocation dispatch
barrier protection remains applicable to both worker assignments.
