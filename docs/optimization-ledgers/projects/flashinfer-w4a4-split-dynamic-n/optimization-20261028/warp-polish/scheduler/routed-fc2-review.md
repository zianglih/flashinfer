# Independent routed-FC2 source review

No blocking source finding in layout patch
`de9df7d5b2f458e76af4c3882549a34b8f32bb4525b734890a8b6f971087312e`
against frozen combined kernel `b45b218b`. The review is read-only; the epilogue
agent owns GPU exactness and performance qualification.

- **Scope/defaults:** only high-level `swap_ab=True, use_fused_finalize=False`
  selects routed FC2 scratch. `output_is_routed` is an internal compile-time
  behavior parameter, default false in the low-level launcher/kernel/epilogue.
  False preserves the previous expanded or atomic-fused output; invalid
  routed+fused and routed+non-FC2 combinations are rejected. Public MoE
  signatures and tactic definitions are unchanged. No autotune axis is added.
- **Address ownership:** the producer writes at the same routed row already
  assigned by `moe_sort`; the combine reads it through the inverse mapping.
  The output allocation and kernel tensor view both use the same mapping
  capacity. Each valid route row is unique, and channel tiles remain disjoint.
  Scalar stores retain `token_start + lane < valid_tokens`; bulk stores retain
  `group * tokens + copy_row < valid_tokens` and the lane ownership guard.
  Finalize skips every negative inverse mapping before loading scratch, so
  padded/nonlocal/unused rows need not be initialized. A fully masked token
  still writes positive zero.
- **Numerics:** only the destination/source row addresses change. FC2's
  per-token scale still uses the routed source row, and alpha multiplication,
  scale-dtype rounding, packed multiplication, output conversion and combine's
  ascending-slot multiply/FMA ordering are unchanged. The direct routed bulk
  address removes an index shuffle without changing its scaling path.
- **PDL/barriers:** the main kernel body is AST-identical to combined control.
  Existing routing publication and dependency waits therefore remain; combine
  may read inverse metadata early but reads expert payload only after its wait.
  Epilogue scratch barriers and accumulator-release locations do not change.
- **Shared finalize:** `match_row_extent=False` preserves old callers. Only
  high-level swap-AB enables it, preserving the prior expanded-output combine
  geometry while changing input addressing. The resulting vectors-per-thread
  is already part of the compile key, so the knob creates no cache alias.
  `_MoeFinalizeKernel` is entirely AST-identical, and W4A16's caller bytes are
  unchanged. Legacy non-swap and W4A16 retain their former layout/tiling choices.

One material tradeoff should remain explicit: the new allocation uses padded
routing capacity, not the number of live routes. If `T * top_k <= local_experts`,
the existing capacity helper returns `T * top_k * route_tile`; relative to the
old expanded scratch allocation this can be a 16–256x increase for small
batches. For T4/top-k8/local32/N16/H7168 BF16, scratch rises from 32 to 512 rows
(0.4375 MiB to 7 MiB). Live data traffic is unchanged, and this is not an
out-of-bounds issue, but it is not accurate to describe allocation growth as
always slight. Watch graph-pool footprint alongside decode timings. No
shape-specific workaround is proposed.

`routed-fc2-review.json` freezes source identities and independent AST checks
for the main kernel, shared finalize class, FC1 launcher, public signatures
and unchanged W4A16 source. This review does not establish runtime correctness
or a performance improvement.
