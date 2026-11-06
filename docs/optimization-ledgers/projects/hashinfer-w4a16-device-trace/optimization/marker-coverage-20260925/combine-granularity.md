# Combine granularity follow-up

Current source cd7cc07, audited September 25, 2026. Read-only analysis; no kernel modification or new GPU benchmark.

`Bf16TopkReduce.hidden_per_thread = 8` at topk_reduce.py:18 determines output granularity. Each lane accumulates all top-k contributions for eight contiguous hidden elements; for H6144 each warp owns 256 elements, giving 24 warp chunks per local token. A WG owns 1,024 output elements per iteration. The source requests 128-bit BF16 loads and stores and retains ordered packed-FP32 arithmetic. This parameter is independent of MMA tile N/M/K and is absent from the current native eight-tactic sweep.

| Elements/lane | Elements/warp | Copy width | Thread chunks at 32 local rows | Active WGs in recorded CTA0/1 |
|---:|---:|---:|---:|---|
| 8 | 256 | 128 bits | 24,576 | WG3, WG4 |
| 4 | 128 | 64 bits | 49,152 | WG3, WG4, WG0 |
| 2 | 64 | 32 bits | 98,304 | all four; some groups require a second worker iteration |

These alternate-width rows are exact assignment arithmetic, not executed kernels. Width4 would require both copy atoms and derived alignment to track the narrower width. Total BF16 payload traffic and ordered accumulation work stay fixed; narrower width creates more warp work and repeats score/address work across more lanes. It may improve latency hiding at the cost of narrower vector accesses; there is no measured speedup for current EP4/H6144. All 148 CTAs already have some reduction at32 local rows, so additional active WGs do not mean additional active SMs here. At one local row, width8/4/2 activates6/12/24 CTAs under current group-major mapping.

A separate assignment experiment would stripe by32-thread warps instead of128-thread groups while retaining width8. For one H6144 row that spreads the24 warp chunks over24 CTAs instead of6, preserving16-byte copies; at32 rows it distributes768 warp chunks as5–6 perCTA rather than4–8. This changes placement, not the count of useful warp instructions. Neither modification creates earlier return readiness or removes the common tail barriers.

## Prior measured evidence, freshly read from historical files

These are older EP8/H7168 results, not current EP4 performance:

- Weighted width4 candidate54301c6, parentd01: `../hashinfer-w4a16-megamoe/integrated-topk-20260918/combine-width4/RETENTION.md` reported decodeT4–512 GM1.002624x against A3,0.993639x against historicalA1. T1 latency regressed11.50%, T8/64/512 also regressed versusA3. Numerical checks passed; no stable benefit; rejected. Source experiment changed width8→4 and128-bit→64-bit copies, leaving arithmetic order/barriers/register policy unchanged.
- Score-free FC1-weighted width4: `fc1-combine-quad/decode13-benchmark/terminal-summary-table.md`, GM0.995858x; not retained.
- Warp32 striping58dd: `integrated-topk-20260918/EXPERIMENTS.md:1189` reports GM1.000708x across historicalT8–8192, mixed rows and aT64 regression; rejected. The preparation README is stale about pending GPU results; the completed ledger is authoritative.
- No executed width2 trial found in the focused search; this is not proof that none exists anywhere.

A bounded current EP4 retest of width8/4/2 and an independent width8 warp-striping arm is reasonable. Keep matched baseline/current tactic for codegen and mechanism diagnosis, and use the established full-forward fresh before/after cold-L2 CUDA-graph CUPTI comparison for retention, with EP8 and larger-token guards. Preserve exact per-element top-k order and validate bit equality. Retain only repeatable incremental benefit; do not promote merely to populate four WG tracks. The current tracing PR remains unchanged.
