# Prepare scale-store coalescing, 2026-10-28

One isolated experiment from pushed `d1767be1f42fdc371f90db4fb06598299ea32845`.
Review copy: `flashinfer-prepare-sf-review` (changes remain unstaged).
Only `moe_swap_ab_prepare.py` is changed; no W4A16 or quantization arithmetic,
new tactic, dtype/model heuristic, barrier, shared scratch, or kernel launch.

## Why revisit

The earlier `scripts/prep_linear_sf_experiment` tested B200 decode tokens 32/128
only. It did not establish TP prefill behavior. Current K3 TP8, EP1, tokens 16384,
MXFP4x8 dispatch uses an all-local top-16 route and writes about 940 MB of activation
payload. Its current prepare kernel already uses 256-bit payload copies.

Fresh NCU 2026.1.1 `SourceCounters` plus LSU counters on the unchanged public
functional call show:

| Quantity | Value |
|---|---:|
| Payload store sectors (32B) | 29,360,128 |
| SF store sectors (32B) | 8,873,984 |
| Measured total LSU store sectors | 38,234,112 |
| SF share of store sectors | 23.21% |
| Useful SF bytes written, including logical invalid-row zeros | 35,495,936 |
| SF excessive theoretical sectors | 7,606,272 |
| Excessive SF theoretical bytes | 243,400,704 |
| Excessive SF share of total store sectors | 19.89% |
| DRAM read/write bytes | 529,373,696 / 998,279,680 |
| Instrumented kernel duration | 297.056us |
| Warp instructions / registers | 110,530,112 / 32 |

The SF scalar store is at PC `0x748c759fc410`, with each adjacent active lane
writing 4 B at a 512 B stride. The 256-bit payload store is at PC `0x748c759fc1c0`.
The profiler's per-PC 256-bit theoretical counts are incomplete; deriving one
32 B sector per aligned payload lane and adding the reported SF sectors exactly
reconciles the actual aggregate LSU store counter. Excessive theoretical sectors
are not DRAM bytes or an expected latency improvement. NCU timing is diagnostic,
not the CUPTI retention measurement.

Raw report and exports are in `ncu-evidence/`. `analyze_ncu.py` produces the
machine-readable attribution. Source and observer selection are pinned by the
receipts; no tuning or external baseline was repeated.

## Candidate and ownership proof

Keep the existing row-owned payload loop. Move SF copying into a separate
physical-word loop, assigning consecutive 32-bit destination words to consecutive
threads. The inverse layout is:

```
atom = word // (128 * sf_blocks)
block = (word // 128) % sf_blocks
position = word % 128
physical_row = atom * 128 + (position % 4) * 32 + position // 4
route = physical_row // sf_rows_per_tile
local_row = physical_row % sf_rows_per_tile
logical_row = route * route_tile + local_row
```

Only `local_row < route_tile` may write. Then the original routing limit decides
whether the word is loaded from the original token or zero. This preserves:

- Exact valid payload and scale bytes, including arbitrary bit patterns.
- Untouched invalid payload rows.
- Zero SFs for invalid logical rows, without reading their poisoned mappings.
- Untouched unused physical padding and the suffix beyond live tiles.
- Empty/reactivated graph replay, unchanged routing inputs and PDL publication.

Word-loop ownership is disjoint (`start=block*threads+thread`, stride=grid*threads).
The inverse layout is a bijection on precisely the original destination set;
`cpu_ownership.py` checks 192 geometries and 1,161,472 addresses, including non-128-row
multiples. There is no scratch or cross-CTA data dependency. W4A16 has no SFs:
its generated SASS must remain identical, checked separately in the GPU gate.

The tradeoff is another loop and repeated routing lookups; removing the original
SF preload can lose latency overlap. Thus EP/decode and TP/prefill must both be
measured before considering retention. No shape switch will hide a regression.

## Gate and timing

`gate_prepare.py` adapts the earlier graph byte gate to the current per-route
physical SF allocation, checks poisoned invalid mappings and both padding types,
and saves PTX/cubin/SASS. Both control and candidate run 384 graph replays over
route tiles 16/64/128/256, PDL on/off, zero/partial/full/reactivated counts, FP4
SF16/SF32, FP8 SF32, and unscaled BF16 with 128/256-bit copies. Unscaled codegen
must match across all 24 configurations.

Results and retention decision pending. Native compilation caches stay persistent.

## R1 result: rejected

The first screen passed all source, frozen-winner, routing, CUPTI, raw-median,
and cache-immutability checks: 12 cells, four CAAC phases, 4,800 raw samples.
The full table is in `perf-table.md`, with raw outputs under `perf-evidence/`.
The separate loop loses 5.51%/9.34% on V3 TP decode tokens 4/64, and 2.69%/3.11%
on K3 TP decode. Its 4.30% K3 EP prefill gain does not justify those regressions.
No shape-specific bypass was added.

The candidate NCU pass confirms a load/store trade rather than free bandwidth:
SF store sectors fall 8,873,984→1,109,248, but SF input theoretical load sectors
rise 1,048,576→7,340,032. Total LSU load sectors rise 32.73M→40.23M, and store
sectors fall 38.23M→30.47M. Warp instructions fall 110.53M→75.80M, but diagnostic
latency is nearly unchanged (297.06→295.46us). See `ncu-r1-comparison.json` and
`candidate-ncu-evidence/`. Neither instrumented duration is retention evidence.

The single active review copy now holds R2. R1's source patch, source receipts,
full byte/codegen gate, and performance evidence remain here; it is not retained.
