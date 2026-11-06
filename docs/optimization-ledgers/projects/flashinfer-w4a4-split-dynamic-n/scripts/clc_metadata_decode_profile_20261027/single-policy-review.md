# Single-policy scheduler review after the depth rejection

The selected direction is depth1 with the180-tactic four-field all-CLC search. No depth autotune axis is pursued. This is a read-only review of the frozen b85eff41 core; no implementation or GPU experiment was added.

## Smallest simplification: local metadata tail wait

`info_pipe.producer_tail(info_producer)` is immediately followed by the final all-thread CTA `NamedBarrier(id1)`. The metadata producer publishes its terminal `m_tile/tile=-1` record, advances, and never publishes again. Every nonscheduler role can reach that final barrier only after `next_work` waits for, reads, releases and advances past the terminal record, then exits its persistent loop. Payload producer/MMA tails finish before those roles reach the same barrier. Therefore, the existing final barrier already protects the local metadata storage lifetime. Removing the local info-pipeline tail wait appears to remove redundant control/synchronization without changing queue depth or work reservation.

Preserve `clc_pipe.producer_tail`: its response storage/consumer completion crosses the two-CTA cluster boundary, whereas the final named barrier is CTA-local. Do not generalize the local proof into removal of remote completion. An exact source-paired empty/reactivated-route and one/two-CTA gate would still be required before retaining a change. Expected timing gain is small; simpler code and fewer executed waits are the reason to consider it.

## General arithmetic simplification: publish decoded work coordinates

CLC already returns physical `(m, route)` coordinates. The scheduler currently flattens them to `tile = route * total_m_tiles + m / cta_group_size`; all producer, epilogue and MMA consumers then repeatedly recover route by integer division and channel tile by remainder. The existing metadata payload reserves four int32 words but uses only `(tile, expert, valid)`.

A single-policy representation `(m_tile, route_idx, expert, valid)` fits the same storage. `m_tile=-1` remains the terminal record. Consumers use `route_idx * route_tile` and `m_tile * mma_m * channel_tiles + cta_rank *128` directly. The weight loader accepts m_tile directly and no longer repeats `% total_m_tiles`. Startup weight prefetch uses `initial_work` coordinates directly, retaining its existing prerequisite-publication guard and payload wait. Both ranks derive the same logical m_tile using `tile_idx[0] // cta_group_size`; their channel offsets remain rank-specific.

For the low-level static control, retain a separate explicit static cursor (`block`, advanced by grid per iteration). Decode it once inside the work-record helper. Do not overload the meaning of `tile` between CLC and static scheduling. Keep one tile per cancellation ticket, the one-slot response protocol, acquire-before-cancel, terminal ordering and current PDL signals.

Actual profile evidence: the retained depth1 V3 mixed FC2 cubin has three consumer reciprocal-multiply division sequences for total_m_tiles56, including SASS `IMAD.HI.U32 ...0x24924925` at0x1530,0x27b0,0x2fe0, and an additional startup signed divide. PTX contains corresponding `mul.hi.u32` operations. The transformation is general; no branch on divisibility, model, dtype or token count is needed. Models/geometries whose divisor is a power of two already lower to cheap shifts, so speedup is uncertain and must be checked broadly.

Do not make packed publication a prerequisite: current selected geometry emits `STS.64+STS32`, and several consumers already emit `LDS128`. `tile_info` itself is a MemRange without explicit16-byte alignment across all geometries. If explicit alignment is later justified, account for its actual storage padding in the capacity calculation; do not assume the observed selected offset proves general alignment. Eliminating flatten/decode arithmetic is useful independently of store width.

## Evidence boundary

The depth profiles establish extra indexing/control instructions and unchanged bytes/registers/operand capacity. They do not isolate reservation hoarding as the sole source of slowdown. Decoded metadata and local-tail removal are unmeasured simplification hypotheses, not speedup claims. No new GPU run is scheduled until the parent selects a concrete experiment.

## Prior decoded-coordinate evidence found

Do not pursue the coordinate proposal above: `scripts/clc_route_metadata_20261027` and `clc_route_uniform_20261027` already tested it. Both passed40exact/source20core pairs, but produced net99extra SASS instructions and up to10extra registers from changed uniform propagation/allocation. Uniform annotation left19/20SASS files byte-identical and only reordered the remaining one. Both variants are rejected. Only local metadata tail removal is proceeding, independently, on current4e155c30.
