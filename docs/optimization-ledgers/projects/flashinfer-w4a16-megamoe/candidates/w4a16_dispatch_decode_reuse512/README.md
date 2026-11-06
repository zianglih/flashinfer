# Two decode groups with a reused dispatch group: isolated 512-thread candidate

This is an **unapplied research artifact** based on the current C1 overlay of commit `6315f94ceb279db53ec3149a7d81e19b332c8dd0`. The exact base and proposed source hashes are in `manifest.json`. It changes only authored W4A16 code: `kernel.py`, `frontend.py`, and new `communication.py`. The vendor tree, epilogue, dynamic-N helper, geometry catalog and public interface are unchanged. It does not include the inactive-half guard or empty bulk-drain removal.

The candidate reuses the existing split W4A16 allocation and decode arrangement while preserving two decode groups for every supported tactic. It has not been CUDA-compiled, numerically tested, or measured. Its main tradeoff is losing overlap between all input pulls and decode group 0, and between compute and dispatch-warp token return.

## Role and register contract

| Warp IDs | Role sequence | Initial registers/thread | Compute registers/thread |
|---|---|---:|---:|
| 0–3 | Epilogue | 128 | 176 |
| 4–7 | MMA, weight TMA, activation TMA, scheduler | 128 | 80 |
| 8–11 | Input prep/barrier/pull → decode group 0 → optional token push | 128 | 128 |
| 12–15 | Decode group 1 | 128 | 128 |

The proposed launch has 512 threads and requests `-maxrregcount=128`. Its intended allocation is `512*128=65536`; control's decrease from128 to80 frees6144 registers, matching epilogue's increase from128 to176. Neither transform group decreases its registers. This exactly mirrors the retained split W4A16 role budget, but **the compiler option is a maximum, not proof of the actual initial allocation**. Codegen must report actual REG128 before GPU correctness/timing promotion. If ptxas chooses less, this resource proof does not hold, and the candidate must be stopped or corrected before execution.

No claim is made that more registers automatically improve decode. Current CUDA13.2 transform code has no observed local spills. The older compiler12.9 path reaches a higher named-register index under the current80 cap, but its end-to-end cost also includes stack/environment differences. A fresh per-role codegen audit is required on each compiler under test.

## Vendor phase reuse and lifetime proof

`communication.py` subclasses `src.token_comm.TokenInPullTokenBackPush`. Its input method calls the same `dispatch_prep`, `dispatch_barrier`, and `dispatch_pull` methods with arguments identical to the vendor wrapper. Its output method calls the same `token_back_by_push` method with the same arguments. `validate_source.py` compares these call ASTs directly against the frozen vendor source.

The input phase's software-grid/NVLink synchronization is among dispatch warps, and dispatch pull writes full allocated FC1 token pools. It does not wait for FC1/FC2 completion and has no compute-consumer acknowledgment or bounded input ring to drain. Therefore it can finish while scheduler publication, MMA or the always-active decode group is waiting for shared group 0. The scheduler retains all480 consumers: its three-stage metadata ring cannot overwrite work that the shared group has not consumed yet. Both decode groups start from the same consumer/raw/transform state and eventually process the same complete work sequence.

Only the returned Int32 pull-mbarrier phase remains live across decode. The per-lane expert-count list is reconstructed immediately before token push using the exact low32 extraction of `expert_recv_count_sum`. Those counts are written during dispatch barrier and remain immutable until kernel-tail cleanup. The vendor's separate token-back warp path also reloads this same count tensor. The actual per-warp pull buffers and mbarriers are untouched by decode, which has disjoint raw/scale/TMEM pipeline storage. All real bulk-copy drains remain in the vendor phase methods.

For `reuse_dispatch_warps`, the output phase runs only after that group's unchanged `transform_pipe.producer_tail()`. The epilogue writes a full FC2 workspace and completion counters; it does not wait for token-return acknowledgment or reuse a bounded FC2 ring. Thus delayed push adds latency but does not create a compute/push backpressure cycle. Push still waits for the existing per-expert FC2 completion threshold and runs before kernel-tail rendezvous/reset. For `epi_warps`, this output method is omitted at compile time.

No raw/transform state reset was introduced at a work-tile or FC1/FC2 boundary. The existing helper resets only logical K count, retaining ring index/phase. Two or three transformed stages and both raw/activation/accumulator pipelines retain their original producer tails and waits.

## Participant accounting

| Synchronization | Required physical participants after reuse | Count |
|---|---|---:|
| TMEM retrieve named barrier | epi0–3 + MMA4 + decode8–15 | 416 threads |
| Scheduler consumer publication | all warps except scheduler7 | 480 threads |
| Dispatch-to-scheduler named barrier | dispatch8–11 + scheduler7 | 160 threads |
| Raw empty-stage arrival | both decode groups, multicast-A factor | 8 warps × A-multicast |
| Decoded full-stage arrival | both decode groups, CTA instruction-group factor | 256 threads × V |
| Accumulator empty-stage arrival | epilogue, CTA instruction-group factor | 128 threads × V |
| Kernel-tail named barrier | all sixteen physical warps | 512 threads |

`V=2` for M256 two-CTA MMA and `V=1` for M128 one-CTA MMA. Activation-release topology remains the existing cluster/V mapping. The raw-pipeline relative thread ID becomes `tidx-256` for transform warps8–15; both groups still have local IDs0–127, group IDs0/1 and disjoint K ownership in the established helper. `num_other_warps=12` counts unique physical warps outside dispatch, not logical role occurrences. The shared group joins TMEM retrieval **before** starting input dispatch, so the416-participant barrier cannot exclude or defer those required threads.

## CPU validation and limits

- `build_candidate.py`: exact input source hashes; isolated base/proposed snapshots; Ruff format; `git apply --check`. Does not edit production.
- `validate_source.py`: vendor phase-call equivalence, no compute-counter dependency in input phase, register redistribution calls, unchanged producer-tail order, physical membership counts, and a source-only ring-state model over multi-work FC1/FC2 K counts.
- `validate_cpu.py`: actual CuTe host construction/layout/fitter checks with `CUDA_VISIBLE_DEVICES=''`; imports dependencies from the independent `host-validation` clone and the proposed modules from an isolated package. No `cute.compile`, GPU query, or kernel launch. It covers accepted M128/N64 C1/C2, M128/N128 C2, M256/N64 C2 and M256/N128 C2; both return modes and schedulers; both fragment widths; small/tail and oversized-H shapes. Expected shared-memory-fit rejection is a passing gate, not a supported-launch claim.

Actual result: **220 host cases passed**, including **68 expected oversized shared-memory-fit rejections**. DSL4.7.1, CUDA hidden; the independent host-validation clone is at fe4f8132, and each recorded imported kernel/vendor dependency hash matches the current production checkout. All proposed modules are loaded from this artifact, not that older clone. The initial harness attempt rejected the new local communication module under a vendor-only provenance assertion; that assertion was corrected to inspect its vendor base class, and the full rerun passed. Both attempt logs are preserved.

The CPU checks cannot prove CUDA lowering of the phase scalar across dynamic control flow, GPU barrier liveness, register allocation, or performance. Historical timing/profile artifacts are not fresh evidence for this candidate.

## Parent-owned GPU gate and A/B plan

1. **Codegen before execution.** Use compile-only capture (do not let a benchmark warmup execute before inspecting the initial register allocation) separately for M256/N128 C2, M256/N64 C2, M128/N64 C2 and C1, plus explicit M128/N128 where it fits. Require512threads/actualREG128, expected dynamic SMEM/fitted raw depth, only control DEC80 and epilogue INC176, and no new transform-local loads/stores. Rebuild source-PC attribution rather than reuse old offsets. In dispatch-return mode inspect the phase scalar and expert-count reload placement, as well as inherited FC2-router locals.
2. **Numerical/liveness gate.** Run the public EP1 then EP2 fixtures with timeouts, including zero/empty/skewed experts, graph replay/reset, M257 ring wrap, H64/I64 and H192/I320 tails, H288/I448 multi-K tail and large-H stage-fit behavior. Run the existing16-candidate lifecycle oracle for EP1/EP2 so both flags/return modes/all curated geometries compile and execute. Preserve existing tolerances and the known all-route versus rank-partial BF16 final-reduction distinction.
3. **Matched fixed controls.** Start with same-source old-layout/candidate/old-layout source overlays and fixed established geometries/schedules at global1,16,64,256,4096,100CUPTI graph iterations. Split stays the same reference. Record source/stack/hardware/loaded libraries and actual selected split tactics. No autotuner expansion or shape selector. A full1–4096 sweep follows only if the initial controls and numerical gate pass.
4. **Mechanism validation only after benefit.** Compare source-correlated decode/raw/MMA/epilogue wait sites and active register/local-memory evidence under the same two-group setting. Profile input-pull completion versus decode start and dispatch-return delay, because either can erase the register benefit. Profile durations are not production CUPTI latency and cannot isolate a register mechanism by themselves.

Do not stack the half guard or empty drain for the first A/B. On failure, restore the exact parent-frozen source; preserve all logs, binary artifacts and timing rows, including regressions. All GPU launches remain parent-owned.
