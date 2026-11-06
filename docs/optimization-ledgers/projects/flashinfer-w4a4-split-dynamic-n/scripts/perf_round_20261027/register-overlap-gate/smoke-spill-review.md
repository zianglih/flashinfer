# Composed register/overlap smoke review

Frozen source `651b8a96` is unchanged. The original guard stopped before launching FC1 PDL-on. Its actual initial168 and role96/240 budgets consume exactly53760 registers for320 threads, so the pool constraint passes.

The sole spill is a32-bit dynamic-SMEM base, stored at startup (`0x120`) and reloaded only in the SDK two-CTA TMEM deallocation wait slow path (`0x246a0`), after final CTA barrier1 (`0x239e0`). The normal wait uses `UR23+0x300`; the compiler-generated slow wait uses the retained general-register pointer. SDK `TmemAllocator.free` accepts no replacement barrier pointer; rebuilding allocator state or changing budgets solely to avoid this cold spill would complicate the kernel.

No local instructions occur in the producer, MMA, or epilogue steady-state. Actual accumulator-release instruction distance from first TMEM read changes709→169 without PDL,703→169 with PDL. The last TMEM read-to-release distance is3 instruction-address steps in the candidate (two intervening instructions), versus2 in the control. These are static scheduling evidence, not latency measurements.

The eight-byte stack allocation contains one four-byte stored address: startup executes1280 bytes of local stores perCTA (320 threads). A slow deallocation wait iteration reloads128 bytes across allocator warp0. This is an explicit startup/teardown cost, not zero-overhead behavior.

A task-local guard exception may be considered only after independent review and must bind exact PTX/SASS identity, exact one-STL/one-LDL sites, eight-byte frame, unchanged thread/budget/physical-pool checks, and absence of hot spills. No wildcard spill threshold, production fallback, source mutation, or budget tuning. Original failed artifacts and original strict guard remain preserved.
