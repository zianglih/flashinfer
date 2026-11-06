# CLC scheduler review

Read-only review of the initial `flashinfer-clc-scheduler-review` diff. Exact source hashes are in `clc_scheduler_audit_source.json`. The custom `sm_count` contract issue found by root is pending the kernel agent's r2 fix; no candidate performance sweep is authorized from r1.

## Queue and termination

| Mode | Metadata consumers per CTA | Producer | Terminal behavior |
| --- | --- | --- | --- |
| Inline epilogue | 128 operand/epilogue threads + 32 MMA threads = 160 | One scheduler warp | All 160 consume and release the sentinel before leaving |
| Overlapped epilogue | 128 operand + 128 epilogue + 32 MMA threads = 288 | One scheduler warp | All 288 consume and release the sentinel before leaving |

- `next_work` waits, copies the three used shared metadata fields into registers, releases that ring slot, advances its independent state, then tests the tile. No role skips the terminal release. Operand/accumulator pipeline state advances only for routed work; metadata state advances for routed work and the final sentinel.
- Allocated but unused routing slots do not enter the metadata ring. The scheduler still fetches/releases the CLC response for each valid hardware work item, so padding cannot strand a consumer. The first invalid CLC item publishes exactly one `tile=-1` sentinel per CTA and drains the metadata ring.
- Only CTA0 issues CLC queries. Both scheduling warps wait/read/release the multicast response; the empty-barrier count is 32 times the CTA group size. The installed SDK adds each CTA's rank to the returned M coordinate; division by group size maps both CTAs to the same logical channel tile before each consumer adds its local 128-channel offset.
- The final whole-CTA barrier includes the added scheduler warp. Scheduler barrier5 does not collide with final barrier1, TMEM deallocation barrier2, TMEM retrieval barrier3 or epilogue transpose barrier6.
- Initial barrier synchronization is inherited through TMEM allocation/retrieval after the new metadata/CLC barriers are initialized; the two-CTA path also has its cluster arrival/wait.

## Memory ordering

Installed CuTe4.7.1 source was inspected directly; snapshots are `clc_sdk_audit_source.txt`, `clc_sdk_release_audit.txt`, and `clc_sdk_arrive_audit.txt`. The local metadata ring uses ordinary shared loads/stores and `PipelineAsync`. Its consumer release reaches ordinary `mbarrier_arrive`; it does not use an asynchronous-copy arrival. A separate consumer async-proxy fence is not established as necessary for these generic shared reads.

PTX specifies release semantics for an unqualified `mbarrier.arrive` and acquire semantics for unqualified waits. These order the metadata loads before slot reuse. The existing producer proxy fence plus scheduler-warp synchronization is retained. [NVIDIA PTX mbarrier semantics](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier-arrive)

## Boundaries

No further definite queue-ordering or sentinel defect found by source review. GPU smoke must still demonstrate zero routed work with padded capacity, partial final tiles, one/two-CTA operation, and all active producer/epilogue/MMA roles; kernel agent owns these checks. This review is not a race-sanitizer result. Larger metadata depth must keep identical release counts and be tested as its own frozen candidate.

## R2 completion

The frozen reservation-aware source is `flashinfer-clc-scheduler-reservation-review`, HEAD `fca8462cbd9096059d0019a206aa760fb34ca8c4`, full-index patch `eb431be438ba9ffabf0f160d283d9bcdb7106d37f0f63ed65255f6e0457f8d03`. Its 83 file hashes were independently checked against `evidence/clc-regular-tma-r2/source.json`. The wrapper obtains the physical device SM count and enables CLC only if the requested budget is at least that count and allocated work exceeds resident cluster capacity. A smaller explicit reservation therefore retains the bounded static launch. The effective scheduler choice is part of the compiled cache key.

Kernel-agent evidence `evidence/clc-regular-tma-r2/gate.json` reports 360 actual-layout policies and 57 exact persistent configurations passed, including explicitly asserted CLC in zero-live one/two-CTA cases and explicitly asserted static fallback with `sm_count=2`. Output payload and scale bytes match the static control; source remained unchanged. The one-CTA zero-live case uses 8 channel tiles times 97 allocated route tiles, exceeding 148 SMs, so it actually exercises CLC termination. No further definite correctness issue was found in this read-only audit. Native AUTO A1 screening is authorized for R2 only.

## R2 scope and cache review after the native quartet

The three-file patch is 246 inserted and 18 removed lines. It is confined to the
existing shared SM100 kernel and its two call sites. No public API, weight layout,
tactic list, activation contract, quantizer, combine, MegaMoE or W4A16 source is
changed. Both private caller sites pass the direct compile-time scheduler and
metadata-depth knobs explicitly. No additional call site was missed.

The cache key includes the **effective** CLC choice after the SM-budget/work-count
check and the metadata depth, alongside the existing device/geometry/SM-count
fields. Dynamic route capacities can therefore reuse a specialization inside the
same policy while crossing the static/CLC boundary selects a separate entry.
`get_num_sm` is already cached by device; the extra unconditional lookup when an
explicit SM budget is supplied does not repeatedly query hardware. The disabled
scheduler still carries a depth key, but all retained call configurations use
one; there is no observed duplicate specialization to remove in R2.

The shared `next_work` loop is a material implementation change for **static FC2
as well as CLC FC1**. It avoids duplicating the operand/MMA/epilogue loops, but the
static machine code need not remain identical. The independent compile-only audit
indeed found FC2 register/SASS differences with CLC disabled. Attribute native
measurements to the whole R2 patch, not solely CLC scheduling. Removing or changing
that structure would make a new candidate and invalidate the current source-bound
measurements; no such edit was made during this review.

The four-word metadata stride stores three values; the extra word keeps the
existing W4A16-style 16-byte record convention. The producer fence and 32-lane
publication barrier also follow that established implementation. No high-confidence
unnecessary surrounding edit or cache-correctness defect was identified that
justifies disturbing this frozen candidate. The scheduler SDK emits deprecation
warnings in CuTe 4.7.1; existing W4A16 uses the same API. That is a future dependency
migration boundary, not a numerical failure in this gate.

## Existing focused gate on R2

`evidence/clc-r2-focused49/validation.json` records **49 passed, zero failures,
errors or skips**, with 98 deprecation warnings, in 10.40 seconds of pytest time
on GPU4 (`GPU-9b1e25f5-48e6-f126-6d93-160b7ea7dd32`). Exact source HEAD, full-index
patch and all83 file hashes matched before/after. Existing test selectors were
reused; the working directory, logs, JUnit, pytest cache and compiler cache were
outside the frozen source checkout. No broad suite or sanitizer was run.
