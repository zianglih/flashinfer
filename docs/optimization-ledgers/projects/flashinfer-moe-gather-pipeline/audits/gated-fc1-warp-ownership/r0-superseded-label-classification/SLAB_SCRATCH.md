# Slab-indexed SF32 maxima scratch: close without a prototype

The compile-time slab array is lifetime-feasible but has no credible exposed-wait signal in the requested saved profile. It also removes an operand stage in three recorded prefill configurations. Do not implement or run it on this evidence.

The [CPU replay](slab_scratch_audit.py) and [full result](slab-scratch-audit.json) preserve the measured source distinction: native PCs came from control `82254e20`, while the storage model extracts the retained `bf072d26` planner and verifies it is AST-identical to current `49c91adf`. The current 364 recorded swap choices are unchanged and their FC1 geometry/dtypes match the saved driver receipts. This is a storage counterfactual, not a compiled candidate or performance prediction.

## Actual barrier attribution

The V3 TP8 MXFP8 T16384 FC1 capture is bound to actual returned ELF SHA `92a692100c0022ea87929ad0cf08ea60cc6757d41d5d1e5f93efd332b2d41b9d`. Its eight unrolled SF32 exchanges have the same instruction pattern:

```
STS local maximum
BAR.SYNC.DEFER_BLOCKING 6, 128   # publication
LDS adjacent-warp maximum
BAR.SYNC.DEFER_BLOCKING 6, 128   # reuse
FMNMX local, adjacent
```

Publication/reuse PCs are `(6050,6070), (72f0,7310), (8560,8580), (97d0,97f0), (aa30,aa50), (bca0,bcc0), (cf10,cf30), (e180,e1a0)` in hex offsets. All are present and executed; the combined 16 sites have 135,040 warp instruction executions in this diagnostic.

| Saved PC observation | Samples |
|---|---:|
| Publication barrier and following LDS: barrier stalls | 92 |
| Reuse barrier and following FMNMX: barrier stalls | 0 |
| Following FMNMX: short-scoreboard dependency | 353 |
| Terminal all-role join: barrier stalls | 3,557 |
| Entire kernel: barrier stalls / all samples | 3,672 / 27,253 |

The deferred-barrier form requires looking at the following dependent instructions rather than interpreting zero samples on BAR itself. The LDS-to-FMNMX short-scoreboard dependency survives deleting the reuse barrier. These samples do not prove the barrier is free, nor give a percentage of removable kernel duration; they fail to establish a substantial exposed reuse wait. The terminal join is a different lifetime boundary.

## Exact historical comparison

The old project's `scripts/perf_round_20261027/sf32-scratch/{README.md,source.patch,disposition.md}` preserves an implemented two-slot experiment, not just an idea. It kept one publication per live slab plus one helper-end drain, reducing `2L` joins to `L+1`. Its overlapping traversal used a dense live rank to avoid aliasing across partial channel tiles. It added 512 B, five-file planner/admission plumbing (+78/−13), and 64 static instructions; its 18-cell CAAC aggregate was **−0.410%**, prefill **−0.619%**. The exact/resource gate passed, and it was rejected for complexity without useful benefit.

The proposed full slab array is distinct: every virtual slab has unique scratch, so no alternating phase or dense live rank is needed. Its synchronization saving is the same `L−1` joins per nonempty work tile, in exchange for more shared storage. No identical full-array trial was found in the bounded ledger search. This difference does not supply the missing performance signal.

## Lifetime and storage bound

Use a unique 512-byte slot for every channel/token slab of one work tile. In cyclic overlap order, a compile-time traversal-step slot is sufficient: each iteration executes at most once, and skipped slabs leave holes rather than aliasing a live slot. Preserve the existing TMEM completion and accumulator release point; SF scratch is owned only by the epilogue warps. A 128-thread drain after the entire work tile must precede any next work tile's scratch write. The kernel's one final CTA join cannot protect scratch reused by intermediate persistent work tiles. Ordinary multi-channel epilogues must either use distinct channel offsets and drain after the channel loop, or keep a separate drain at each channel-helper boundary; the latter is a different saving.

The conservative one-drain-per-work-tile requirement is:

```
scratch_bytes = 512 * max(1, logical_m//256) * ceil(max(32, route_n)/32)
```

It applies only to gated activation with generated SF32 output. K3's SiTU and N3U's ReLU2 are not gated and already have warp-local maxima; SF16 and per-token BF16 output do not use this exchange. No model-specific condition is needed, but the exact activation/output contract would have to reach both automatic K/stage admission and actual allocation. Updating only the storage struct would be incorrect.

Across all 364 frozen swap cells, 78 invoke the gated SF32 exchange (66 after excluding tokens 1/2), spanning 27 distinct native configurations. Of these, 58 have one slot and cannot save a join; 20 have more than one slot. Their storage is:

| Array bytes | Cells | Increase over current |
|---:|---:|---:|
| 512 | 58 | 0 B |
| 1,024 | 2 | 512 B |
| 2,048 | 5 | 1,536 B |
| 4,096 | 13 | 3,584 B |

The source-derived planner loses one operand stage at these fixed native choices:

| Cell | Route N / K steps | Operand stages | Scratch |
|---|---|---|---|
| V3 EP MXFP4x8 T8192 | 128 / 4 | 9 → 8 | 512 → 2,048 B |
| V41F EP MXFP4x8 T4096 | 128 / 4 | 9 → 8 | 512 → 2,048 B |
| V3 TP MXFP4x8 T4096 | 128 / 4 | 9 → 8 | 512 → 2,048 B |

Each has only 1,024 B of old planner slack. Five same-geometry automatic-K evaluations would change K steps 4→8; the current recorded winners explicitly fix K, so that is a separate future default-policy effect. The profiled V3 TP MXFP8 T16384 choice keeps three stages and rises from 206,592 to 210,176 modeled shared bytes. Actual future struct alignment/resource/codegen would still require qualification; none is claimed here.

The old experiment's lack of benefit, no sampled exposed reuse wait in the requested native profile, and concrete stage losses close this lead without source changes or GPU work.
