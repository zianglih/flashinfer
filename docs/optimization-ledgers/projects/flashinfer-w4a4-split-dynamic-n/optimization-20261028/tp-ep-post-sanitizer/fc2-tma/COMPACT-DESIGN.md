# Compact routed FC2 follow-up

The first candidate is unretained: +8.91% TP prefill, −1.31% TP decode, −0.72% EP prefill, with0.5–0.95GiB extra TP16k output storage. Paired NSYS shows the ordinary TMA mechanism reduces V3 TP FC2 by200.6us but routed combine costs42.7us; EP saves5.8us FC2 and costs8.9us combine.

## Compact output and metadata

Allocate the existing `tokens*topk` BF16 output capacity. One warp in prepare CTA0 scans the valid row counts `min(route_tile, limit[t] - t*route_tile)` and writes exclusive offsets per live route tile. These counts are nonnegative, each local route appears in exactly one tile, and their sum is at most `tokens*topk`. No CPU readback, new kernel, atomic allocation or grid barrier is needed. All other prepare warps retain their existing payload/SF ownership and consume no prefix data.

FC2 uses the prefix for output addresses. Only the channel-start-zero CTA writes a separate dense inverse index for every valid local expanded route. Static or CLC ownership gives each `(route tile,channel tile)` exactly one owner; the second CTA in a two-CTA pair starts at channel128 and cannot write these indices. Separate index storage preserves caller-provided `moe_sort_buffers`. Nonlocal dense entries are intentionally uninitialized and never read.

Combine retains the original inverse mapping only as a validity mask, which it may preload with scales before its PDL wait. It reads the new dense index **after** the FC2 wait, then consumes output. This removes division and an additional prefix lookup from the combine hot path; unlike the original routed metadata, the new index is not published by FC1.

## PDL and lifetime

Prepare waits for routing before scanning. Its early signal only allows FC1 independent weight/startup work: FC1 activation and epilogue readers still wait for the whole prepare grid. FC2 epilogue readers wait for FC1 (and the optional per-token quantizer); the published ancestor chain therefore includes completed compact prefix writes. The prefix is read only by FC2 epilogue threads, never by the running-ahead scheduler/weight warps. FC2 may signal combine early, but the dense index is read after combine's existing grid dependency wait. All tensors are held by graph closure/allocation lifetime exactly as existing temporaries.

## Full slabs and tails

A full32/64-row slab writes at `compact_base + group*slab_rows` with ordinary2D TMA. Its end is at most that tile's compact valid end, so it cannot overwrite another tile. A partial last slab selects the original **unswizzled row-major** STMatrix scratch layout and per-valid-row bulk stores. This choice occurs before shared writes, not by applying a linear bulk copy to SW128 data. The complete slab uses the existing two SW12864-column halves. Both reuse the same capacity/stage stride and publication/reuse/drain barriers; no extra transpose or intermediate arithmetic is introduced. All logical output channels remain multiples of128, as already required.

The tail branch follows actual valid rows, not a model/dtype/topology policy. It reuses required irregular-row handling. No new tactic axis or public API argument is added. Non-swap, fused and W4A16 core behavior remain unchanged; their optional compact metadata is absent.

## Validation plan

Keep d1767 control and first-candidate evidence immutable. Freeze a new remote source snapshot. Check final output bytes plus compact prefix/index bounds on balanced, skewed, empty and reactivated graph routes for all four formats, static/CLC, PDL off/on, one/twoCTA,32/64-row bulk storage and short/long K. Inspect native source identity and spills. Repeat the eight fixed-winner C–A–A–C jobs only after this gate. Host descriptor/allocation overhead remains outside warmed CUPTI graph timing, and is reported separately.
