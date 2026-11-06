# N32 FC2 source review

Independent source audit against native commit
`03e1840c2b964f7f6a9ddee9ccefbac0e44ea937` and provisional artifact
`evidence/candidates/n32-epilogue.patch`, SHA256
`3cdc47817e846a4dadee7dec9dd5c9173bd0992067bf053beb0f2780583591a2`.
The artifact admits only M256/N32/K256 with a two-CTA feature cluster.
No active source, GPU, queue, or sealed bundle was modified by this review.

**No concrete source correctness blocker found in the reviewed patch.**
CuTe construction, native compilation and runtime behavior remain unverified.

## Relationship to the prior N32 audit

The earlier audit is
`../flashinfer-w4a16-megamoe/candidates/w4a16_n32_audit/AUDIT.md`.
Its central findings still apply: an N32 tile cannot call the 64-token raw
load/reorder or run FC1's second 32-token half. Doing so would address the
next accumulator stage, or the decoded-weight region for the final stage.
The old vendored epilogue constructor restrictions no longer apply directly:
current W4A16 owns `W4A16Epilogue`, its FC2 router, and TMEM helper paths.

## FC2 layout and store

- `load_half_raw_acc` loads exactly the old first-top and first-bottom
  16-register fragments. The second token-half's `ptr + 32` views are absent.
  Pointer offsets remain Python constants, preserving TMEM load alignment
  information. Both feature halves are read before scratch reuses their TMEM.
- `fc2_f2fp` is unchanged: each original FP32 accumulator receives the same
  FP32 alpha multiplication and BF16 conversion. The new path merely passes
  two fragments instead of four.
- The new gather `((2,16),(16,1))` is exactly the old gather with token-half
  index zero. For a flat index `i`, it reads `16*(i%2) + i//2`. The scatter
  `((16,2),(2,1))` reads `2*(i%16) + i//16`, the corresponding inverse
  feature-pair ordering. These are the established half-zero maps, with
  no extra conversion or arithmetic on the packed BF16 bits.
- Thirty-two BF16 values become sixteen opaque 32-bit registers. The
  existing `TmemTranspose16x32` constructor accepts this shape and width.
  The single transpose performs the same rounds/fences as one member of
  the old pair, using columns 0–31 inside the current 32-column stage.
- The store mapping produces two 16-BF16 issues per thread. Its coordinates
  are `token = thread % 32` and
  `hidden = 32*(thread//32) + 16*issue + element`. Over 128 threads,
  two issues and 16 elements this covers all `32*128` elements exactly once.
  The unchanged generic STG helper derives two iterations from the smaller
  fragment; no four-issue constant remains on this admitted path.
- Peer routing therefore allocates one pointer/valid pair per thread,
  matching `iter_idx//2`. Local routing remains affine. H divisible by 32
  preserves the two adjacent 16-element stores' shared validity. Token
  metadata indices use the N32 tile base and valid-token predicate.

Source: candidate `tmem_epilogue.py` new raw-load/reorder helpers and store
mapping; unchanged `Fc2OutputRouter.prefetch/get_data_dst` and
`fc2_stg_store_function` in the same file.

## Accumulator release and completion

- The N32 FC2 path has one subtile. A positive valid-token count executes
  the load/reorder and then the common TMEM-load fence and exactly one
  `consumer_release`. Zero valid tokens take the existing final-subtile
  else arm and release once without accessing scratch.
- FC1 now iterates one half and releases on that half's final scratch
  reads. Feature addressing retains its independent 64-element stride;
  only token stride/half count changes to 32. Norm, alpha, activation,
  routing weight, BF16 rounding and store predicates retain their order.
- Release occurs before register packing/STG, as in the original path.
  Completion publication still occurs after all four epilogue warps meet
  the existing named barrier and execute the existing async-global fence.
  Smaller token tiles do not reduce this rendezvous or publish partial data.
- The new FC2 branch is constexpr. Its plain Python transpose object is
  created and consumed inside the helper; only a tensor leaves the helper.
  No Python helper object crosses a dynamic branch or loop-carried boundary.

Source: candidate `epilogue.py` constructor, `run_subtile`, FC1 half loop;
unchanged common epilogue run loop and `signal_fc1_done/signal_fc2_done`.

## Padding, readiness, token return and TMEM bounds

- Frontend passes N32 as `token_padding_block`. Kernel pool capacity,
  per-expert tail slack, arrival slots and FC1-done slots all derive from
  padding or `cluster_tile_tokens`; no fixed 64-token allocation was found.
- In inherited dispatch, both padded row prefixes and arrival-counter
  prefixes derive from those same parameters. Metadata and routing-weight
  rows use the padded pool index. The scheduler's CTA-valid count and
  cumulative token-block count derive from the actual tile shape.
- FC2's FC1-ready threshold counts feature CTAs and is unchanged by N.
  Dispatch token return waits for
  `ceil(expert_tokens / cluster_tile_tokens) * publishes_per_token_tile`;
  `cluster_tile_tokens` becomes 32, so the extra FC2 work tiles are counted.
  Epi-warp return uses the same per-token metadata, independent of N.
- The dynamic-N nonleader B shift remains applied in both phases. At N32
  it is -8 for valid counts 1–16 and 0 for 17–32, aligning static half-tile
  partitioning with the existing runtime N16/N32 MMA split.
- Two accumulator stages occupy columns 0–31 and 32–63. The existing
  capacity rule selects three decoded K256 stages at 64–191,192–319,320–447
  within the unchanged 512-column allocation. The split W4A16 helper also
  uses two accumulator stages for N32, so this is its established allocation
  rule rather than a new decoder arrangement.
- Decoder warp groups, warp identities, register partition, raw decode
  operations, pipeline roles and final deterministic combine are unchanged.
  No scheduler/raster/group strategy or AUTO catalog is added.

Source: unchanged `megamoe_kernel.py` constructor, `_pool_shapes`, workspace
specs and `_activation_task`; scheduler `fc1_fc2_fuse_sched.py` and
`custom_ext.py`; inherited SM100 `src/src/token_comm.py` dispatch-pull and
token-back-push methods. `dynamic_mainloop.py` only widens the allocation
whitelist; it retains the runtime descriptor and operand shifts.

## Remaining boundary

This establishes source-level consistency, not hardware transpose or
compiler validation. The bounded native perf screen must still compile
the actual N32 MMA/TMA/SMEM layouts and exercise the mapping. Dynamic MMA
already rounds valid tokens to 16, so N32 does not inherently reduce sparse
tile FLOPs. Its plausible benefit is smaller activation staging and one
epilogue half; experts above 32 routes require more tiles and weight decodes.
Follow the current perf-first policy and run existing exact checks only
after a useful gain. The review does not propose additional scheduler or
decoder experiments.
