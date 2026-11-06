# Scheduler metadata-depth history and current gather pipeline

Read-only audit, 2026-10-30. Current source base `82254e20`; exact file/evidence hashes in `scheduler-depth-history.json`. No production edits, compilation, GPU work, or new performance claims.

## Decision

Do **not** reopen metadata depth for the profiled N3U TP W4A4 16K ordinary-scheduler winner. The ordinary path is already static persistent, and it has no metadata queue to deepen. The one-stage setting in `moe_swap_ab.py:244` affects CLC only. A deeper CLC queue is an old, rejected policy, not a new explanation for this ordinary-path profile. No new autotune axis, model branch, or source experiment is justified by this audit.

The supplied profile (M128/N256/one CTA, tile-K256, eight K iterations, four operand stages; ~16.24% tensor/~14.9% DRAM) establishes low utilization, not repeated CTA initialization or metadata starvation. Ordinary grid size at kernel:2402 is bounded by resident capacity and live work; each role advances by `tile + grid` inside its persistent loop. TMEM allocation, pipeline creation, TMA partitioning, and role register reconfiguration sit outside those loops.

## Exact historical trials

All measured queue-depth trials below precede the dedicated gather warpgroup introduced in `fc1-gather-20261028` from retained base `d35fcfda`. The Oct29 post-gather metadata audit was an analytical physical-stage-cap rejection, not a new depth performance trial. A targeted search of the post-gather Markdown ledger found no later metadata-depth timing campaign.

| Trial/source | Change | Recorded result / decision |
|---|---|---|
| Historical W4A16 ledger, summarized by `scripts/pr7290_scope_cleanup/clc-w4a16-history-resource-audit.md` | Static metadata 2→3; CLC 3→2→1 | Static3 improved old TP8 ~3.2–3.5%, EP8 approximately neutral; static4 regressed. CLC2→1 yielded 1.015828× EP8 /1.010503× TP8. Different dequantization kernel and old 1–4096 grid including1/2; not present-source evidence. |
| Oct25 regular-TMA, base `fca8462c`; `SCHEDULER_OPTIMIZATION_2026-10-25.md` | CLC depth1→2, fixed V3 T16 tactics/routes | W4A4 71.712→73.960 us; MX8 114.680→118.336 us; MX4x8 73.9045→80.752 us. Rejected. |
| Same Oct25 campaign | Introduce global static metadata queue, depths1/3 | 39 exact /360 layout checks passed; NV decode0.2–0.7% slower, MX8 decode flat/slower, V41 MX8 16K lost5.5%/3.5%; mixed decode+0.5–1.1% insufficient. Rejected. This would add a ring to today's ring-free ordinary path. |
| Oct27 `b85eff41` + candidate patch `5920de4f` vs matched all-CLC patch `97cf417d`; `perf-general-20261026/clc-info-depth/` | Depth=accumulator stages | 64 exact replays passed. V3 T16 C/A: W4A4 .99405×, per-token .99883×, MX8 .96868×, MX4x8 .93227×. K3 16K published geometry W4A4 1.04118×/per-token1.03503×; native all-CLC W4A4 remains depth1 and1.00080×, per-token1.02279×. Rejected as a universal policy. |
| Oct27 `b85eff41` + `ab24777c`; `perf-general-20261026/clc-info-lookahead/` | Depth=accumulator stages+1, giving2/3 slots | 64 exact replays including non-power-of-two depth3 passed. V3 T16 C/A: W4A4 .96271×, per-token .97035×, MX8 .96730×, MX4x8 .93395×. K3 16K native W4A4 1.01459×/per-token1.03028×; published1.05482×/1.04062×. Rejected because decode regressed. Operand depth/K choices were held equal; prefill benefit did not justify a new tuning axis. |
| Oct27 W4A16 base `1496b557`, patch `f126288d`; `w4a16-perf-20261027/clc-stage/` | CLC depth=accumulator count; ordinary stays3 | Forced-CLC 12-point CAAC (32/128/4096/16K×V3/V41/K3): overall model GMs .987764×/1.000236×/1.007616×; V3 16K .972090×. Rejected. |

The old documents sometimes call the combined diagnostic expansion “1→2 or1→3”; the separate source manifests distinguish the actual policies above. Work hoarding is a hypothesis, not proven causality. The measured decode regressions remain valid without that hypothesis.

The request-before-metadata-acquire variant is also closed: 48 affected points, GM .999956×, decode .997000×, all24 decode points slower. One logical tile per CLC ticket, acquire-before-cancel, and no extra tuning dimension remain the retained policy. Elected CLC owner/consumer-arrival and padded-ticket exit are separately closed and not reopened here.

## What the current one-slot queue actually permits

`next_work` (kernel:2490) waits, copies tile/expert/valid into private registers, immediately releases the info slot, then advances. Thus one shared slot does **not** mean one tile in flight: every role can hold its current tile privately, while the scheduler publishes the next tile after all roles have copied the current one. Weight producer and gather warpgroup can start following work while MMA/epilogue still process their current tile, subject to operand/accumulator ownership.

The CLC epilogue reads/releases its current metadata before `acc_pipe.consumer_wait`; it requests its next metadata after completing its body (3287–3389). A second slot would allow an additional tile of producer lookahead beyond the slowest role, not eliminate a missing basic next-tile overlap. That was exactly the motivation of the rejected accumulator-derived/extra-slot trials.

The ordinary path does not call any info-barrier wait/release: `next_work` is only a terminal bound check, and each role independently computes its route/expert/valid. Stage indices/phases persist across tile boundaries; the operand ring is not drained and reinitialized per work tile. The existing metadata-stage-cap audit correctly distinguishes logical lookahead from physical asynchronous retirement; no physical-stage clamp follows from short K.

## Current reference comparison

FlashMLA official remote HEAD was freshly checked with `git ls-remote` and remains `395cb3afbb331fef7b1b21e9340861b9436b42d8`, identical to the project-local source reviewed Oct26. Its fused sparse-attention core uses one CLC response slot, backpressure before query, direct first-job coordinates, and workers copy/decode next-job state before releasing response storage (`kernel.cuh:440–515,1188–1212`). Its elected owner is already a rejected transfer. It is not a deeper-ring precedent.

FlashMLA also issues the first QK of the next job before the last SV of the previous job (`kernel.cuh:1175–1185`). That is useful evidence of explicit cross-job pipelining, but its alternating attention GEMMs and accumulator lifetimes differ from a single MoE GEMM plus quantizing epilogue. Our ordinary producers already cross tile boundaries independently, and the accumulator overlap path already protects and releases TMEM prefixes. Copying that source ordering is not a new applicable optimization by itself.

Current local Rubin gather-MoE at base822 uses a static persistent scheduler with a two-slot decoded metadata ring (`rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:3747`). It publishes five fields, waits for slot reuse, and includes a proxy fence plus scheduler-warp synchronization before commit (1741–1828). Consumers copy/release immediately (1886–1897). It has no CLC stealing in this path. This corresponds closely to the old global-static-queue experiment, not a newly demonstrated improvement over our ring-free ordinary scheduler. Rubin's stage count is an implementation choice, not performance evidence for Blackwell.

## Remaining evidentiary boundary

No new simple scheduler-publication candidate emerged. If the supplied source counters show time at `epi_acc_wait`, `producer_tma_empty`, or gather coordinate/SF issuance, investigate that specific tile boundary under the current persistent ordinary design. If a future **CLC** trace shows scheduler info-producer acquire or worker metadata waits dominating while operand buffers are available, a focused mechanism audit could revisit the cause; dedicated gather changes the role mix but does not itself justify repeating the closed queue-depth policy. No experiment is requested by this audit.
