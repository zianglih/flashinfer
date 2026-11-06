# Shared FP32 epilogue transpose feasibility

Read-only design on ce4a7d8c. No repository edit, GPU launch or speedup claim yet.

Keep the current native Ld16x64 fragments, arithmetic placement, lane=token/register=channel output ownership, exact quantization, and all accumulator release points. Replace only the FC1 ownership transpose with a warp-private shared-memory exchange. FC2 retains its existing TMEM/bulk paths. This is distinct from the rejected native-output design: it does not move quantization/reductions into distributed channel ownership or add packed lane-shuffle reordering.

For native lane L/register i, token=2*i+((L>>1)&1) and channel=8*(L&1)+(L>>2). Store to `(token*16+channel)^((token&7)<<2)` within each warp's 512-word slab. After a warp memory rendezvous, each lane loads its sixteen channels using four aligned 128-bit shared loads. A second warp rendezvous protects scratch reuse by the following fragment or token slab. A pure exchange preserves all FP32 bits.

The CPU proof checks all512 addresses, all16 scalar-store bank waves, and all16 eight-lane vector-load transactions. It is not compiled bank-counter evidence. Hypothesized cost is16 scalar stores,4 vector loads and2 warp rendezvous per fragment, versus the existing three TMEM-store phases and six TMEM-load operations with completion waits. Fewer data round trips is not automatically faster: instruction issue and shared bandwidth could dominate.

Four warp-private slabs require8192B. Keep the existing512B SF32 cross-warp maximum exchange separate: aliasing it with a warp-private slab would let other warps overwrite that slab before its owner finishes. Total fixed FC1 scratch8704B. This must be reserved in the same compile-time storage/K-step planner; do not borrow a live operand stage or conditionally enable by model/dtype/tile. If buffer loss or codegen cost is large, reject without a broad timing run.

Two-fragment calls may reuse each warp's slab serially; the input values are already in registers. No TMEM scratch stores are made, but the initial source-load completion and existing early-release/tile-end completion requirements remain. The first TMEM load can overlap ordinary arithmetic only through real dependencies, not by assuming asynchronous completion. No new API/tactic knobs.

Gates: independent history/mapping/lifetime review; compute actual native-winner stage impact; compile-only representative all-dtype/gated/non-gated cases without new spills; exact changing-route/partial/output coverage; predeclared bounded same-GPU CAAC if qualification passes. Native/cold comparison resources must be source bound. No sanitizer.
