# Composed W4A16 host/cache review

Scoped static review passes at the file hashes in `composed-host-review.json`.

- The wrapper compile-time arguments are M, K, top-k and max-active-clusters. All four now enter the kernel cache key. M/K are removed from the compiled callable runtime invocation; routed N, output token count, tensor pointers and stream remain runtime values.
- Every variable constructor field is keyed directly or derives from a keyed value: group count, activation contract and constants, fused-finalize/PDL/scheduler booleans, tile/cluster/raster geometry, transform fragment size, M-tail alignment and gated weight row group. Accumulator/MMA types are fixed in this launcher. The two-CTA choice derives from tile M.
- The existing missing max-active-clusters key is fixed. It is baked into the static persistent grid and must not reuse a previous full/clamped-grid compilation. This should be checked across both caps without clearing `_kernel_cache`.
- The shared tactic appends exactly one boolean, exposes 46 unique choices, forwards the same value to both grouped GEMMs, validates its type, and changes the persistent tuner cache namespace. The launcher contains no phase/shape scheduling heuristic. Existing forced-tactic tests now use the three-field tuple.
- Shared preparation keys payload width, SF columns, route tile, top-k, vector width, grid, PDL and device. Thread count and alignment derive from these keys. Runtime route count and mappings remain dynamic; absent SF storage is explicit and only accepted for BF16. The optional 16-byte path preserves the former contiguous BF16-view alignment contract.

No additional missing W4A16 constexpr key was found. Device-context ownership predates this change and is outside this narrow review. Runtime exactness and final public measurements remain separate root-owned validation.
