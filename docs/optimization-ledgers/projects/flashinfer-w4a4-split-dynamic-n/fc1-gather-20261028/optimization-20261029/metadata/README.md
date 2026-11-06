# R6 FC1 metadata issue experiments

Both variants start from the exact R6 kernel `deba8b639fba89e6f76381e8c6bf8bc323ccaf850b973c836f476f8144c4cc0a`.
The snapshot, builders, patches, and static evidence live only here. Neither review checkout nor the canonical repository was edited. No GPU compilation or execution was launched.

## Route vector128

`route-vector128.patch` replaces four scalar mapping loads with one explicit 128-bit CuTe universal copy for a complete four-row group. Integer division by top-k, the four warp ownership, flattened row/K task ordering, two-CTA row split, and invalid-row TMA coordinates remain unchanged. A partial four-row group keeps the original individually predicated loads; no uninitialized padding entry is read.

Alignment follows from the existing geometry: route starts are multiples of the routing tile (at least16), row groups are multiples of4, and the two-CTA ownership offset is `round_up(valid,16)/2`, a multiple of8. Thus every vector source is16-byte aligned. The full-vector predicate guarantees all four entries are valid. This changes metadata once per routed tile, before the K loop; SF indexing and SF copy instructions are untouched.

Current catalog coverage is route tiles16/32/64/128/256, CTA groups1/2. No model, dtype or problem-size branch was added. The source uses CuTe's existing `CopyUniversalOp`, as in the shared finalizer, rather than adding an inline-PTX helper.

## Publication after Gather4

`publish-after-gather.patch` is independent of vector128. It moves only `cp_async_mbarrier_arrive_noinc` from before the Gather4 issue loop to after it. SF copies are still issued first; Gather4's expected-byte announcement still precedes all copies. All128 SF producers still arrive once on the same local barrier, and stage advance still follows publication. The relay cannot observe completion until both the async SF arrivals and expected Gather4 bytes complete.

The intended diagnostic is whether issuing payload requests before publishing SF completion improves issue order. It does not add a stage, wait, barrier, CTA role, scheduler step or PDL transition. A neutral result is not a reason to retain an ordering change.

## Static gate and required GPU gate

`python3 build.py` recreates both full candidate kernels and unified patches from the frozen R6 source, with SHA receipts. `python3 static_audit.py` verifies mapping and vector bounds across every valid-row count for the current route/CTA catalog:43,964 groups,23,824 safe full vectors and1,053,504 flattened Gather4 task mappings. It checks all changes remain inside the existing `gather_input` producer-warpgroup branch. FC2 and W4A16 stay byte-identical outside that branch.

Before performance interpretation:

- Compile representative N16/group2, N128/group2 and N256/group2 cases, including partial rows and partial K, for NVFP4 and MX formats.
- Confirm the vector case emits an actual128-bit global load (PTX `ld.global.v4` or corresponding SASS128-bit load); instruction width is not established by the static source check.
- Compare registers, stack/local traffic and spills against R6. In particular inspect whether the temporary four-register vector coalesces with `row_ids`; do not accept extra spills to reduce load instructions.
- Confirm generated FC2 remains unchanged, run existing exact coverage and then a matched R6 comparison. Keep the established persistent native compilation cache.

These files are experimental, unstaged and unretained. Static success is not a runtime correctness or performance claim.
