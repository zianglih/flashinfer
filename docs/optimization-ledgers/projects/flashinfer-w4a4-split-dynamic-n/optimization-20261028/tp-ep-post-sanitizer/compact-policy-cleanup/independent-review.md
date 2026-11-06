# Independent compact FC2 policy audit

Status: the kernel/planner cleanup and host workspace encapsulation pass the CPU
source equivalence audits. No source blocker was found.

Base: `9e3cb4d5fa0f45bba7014f67e968bf04e3cffa0f`.
Reviewed kernel: `flashinfer-compact-policy-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`,
SHA256 `9482459f3dad6bb31cc43323fc523504263304b3a2cec6a0b91f54ea75416b7c`.
No repository source, GPU job, benchmark, or sanitizer was changed or launched by
this audit.

## Equivalent kernel changes

`bulk_output_element_bytes` remains the sole admission point. It already returns
zero for route tiles below 128. Removing the repeated threshold in
`_k_stage_capacity` and `_select_k_steps` therefore leaves every admitted production
plan unchanged. Direct private calls that supply contradictory capability bytes
are outside this equivalence claim.

The overlap replacement is also equivalent on the current SM100/SM103 capacity:

```
acc_cols = allocated_n * channel_tiles
can_overlap => 2 * acc_cols == 512
```

Consequently, under `can_overlap`, `allocated_n == 256` is equivalent to
`channel_tiles == 1`. The new expression states the actual ownership constraint
instead of repeating a derived dimension. The scale limit, accumulator windows,
operand stages, scratch sizes and synchronization remain unchanged.

`independent_planner_audit.py` executes the actual extracted old and new planner
methods, rather than a separately maintained copy of their formulas. Its receipt
is `independent-planner-audit.json`:

| Check | Coverage | Result |
|---|---:|---|
| Planner combinations | 154,224 | Identical outcomes |
| Admitted plans | 40,824 | Identical K steps, stage counts, scratch and overlap |
| Rejected plans | 113,400 | Identical rejection strings |
| Automatic-depth combinations | 9,072 | Identical |
| Explicit-depth combinations | 145,152 | Identical |
| Output/flag eligibility cases | 240 | Identical |
| JIT overlap truth cases | 177 | Identical |

The enumeration covers logical M128/256/512; route N16/32/64/128/256; FP4/FP4
with SF16 or SF32, FP8/FP8, and FP8/FP4 with SF32; 128/1024-byte operand
alignment; static/CLC scheduling; metadata depths 1/2/3; automatic or explicit
operand depths 1–16; overlap `False`/`None`/`True`; and K4/K8/automatic selection.
The output admission table separately checks six output dtypes and all
scatter/fused/generate-scale flags. The modeled capacities are the implementation's
current 227 KiB SMEM and 512 TMEM columns, not a claim about a different architecture.

All 1,836 admitted automatic bulk plans realize a nonzero bulk slab. Ninety-six
admitted forced-depth plans fall back to zero bulk slabs in both versions. The
production wrapper uses automatic operand depth; forced-depth fallback remains a
low-level diagnostic contract.

The planner outcome stream hash is
`cb951f15fe4f22157d0b101ba8d800cb9819f1ed58562d755c5fb579e2e2a9c6`.
The only changed kernel methods are `_k_stage_capacity`, `_select_k_steps` and
`__call__`; the latter changes only the equivalent compile-time overlap expression.
The other GPU method bodies are AST-identical.

## Required ownership versus performance choices

The current output capability restrictions have different purposes:

- Nonfused scatter, BF16/FP16 output, and no generated output scales match what
  the bulk epilogue implements. It does not perform fused atomic finalization or
  quantized output-scale generation.
- Scratch must fit after operand slots and barrier metadata. The existing
  capacity calculation includes 1024-byte operand alignment for K96 and the
  epilogue's unchanged 128-byte alignment.
- Each selected slab must fit and divide the routed tile. Full TMA stores require
  enough live rows; partial rows use the existing bounded fallback.
- The overlap path requires one channel-tile owner. The epilogue is invoked once
  per channel tile, and each invocation releases after reading its first protected
  64 columns. Allowing two channel tiles with this protocol could release the
  wrong physical interval and release the same pipeline state twice. Capacity
  alone does not establish safe ownership.
- The N128 cutoff is an inherited performance choice coupled to the current slab
  implementation, rather than an ISA restriction or an absolute SMEM limit.

In particular, removing the remaining N128 cutoff alone would be incorrect.
`_epilogue_storage` currently selects 64-row/two-stage scratch when it fits,
without consulting route N. A newly admitted N32 tile can therefore receive a
64-row slab, and `_run_bulk_direction` executes zero iterations because its loop
count is `tile_n // tokens`. The receipt contains an arithmetic example of this
failure to cover the tile. N64 can fit and execute a 64-row slab today, so its
exclusion cannot be justified by capacity alone.

The 64-row/two-stage preference and 32-row/one-stage fallback are performance
choices among supported TMEM/stmatrix shapes. Their sizes are 34,816 and 8,704
bytes for two-byte output elements. They are not required universal buffer counts.

## Why the retained eligibility was introduced

The local `fc2-tma/compact-r2` ledger records the cost of enabling compact prefix
and dense-index metadata even when the selected kernel had no bulk output path:
all 28 decode cases regressed, with geometric means of −1.072% for EP decode and
−4.164% for TP decode. The subsequent R3 policy coupled metadata allocation to the
existing bulk-output eligibility. It did not prove that every narrower TMA slab
would be slow or that every remaining prefill loss was fixed.

The retained combined K96/R3 screen in `fc2-tma/eligible-r3-k96/RESULTS.md` was
approximately neutral on EP and positive on TP prefill: affected EP decode
−0.009%, EP prefill +0.027%, TP decode −0.000%, and TP prefill +4.678%. These are
historical experiment results explaining the retained policy, not measurements of
this cleanup. The full public result matrix remains bound to its measured source.

## Host workspace contract

`independent_workspace_audit.py` executes the actual extracted workspace factory,
the core's allocation block, and the launch/combination unpacking statements with
CPU tensor metadata stand-ins. Its separate receipt,
`independent-workspace-audit.json`, binds the final four-file revision. It covers
240 allocation cases: 120 swap-AB and 120 non-swap; 480 FC1/FC2 binding cases;
empty and nonempty metadata; five route tile sizes; six output dtypes; and fused
versus separate finalize.

The result is a concrete two-field `_CompactOutputWorkspace` or `None`, with no
duplicate boolean state. The same `empty_like` allocation order and tensor
shape/stride/dtype/device are preserved, and neither buffer aliases its source or
the other buffer. Ineligible, fused and non-swap calls allocate no workspace.
Non-swap launcher options remain unchanged.

FC1 receives the prefix buffer for preparation, retains expanded output, and
passes neither metadata pointer to the FC1 GEMM kernel. FC2 derives routed-output
specialization from the workspace and receives both the prefix and dense indices.
Combine obtains that same indices tensor from the same object. All existing GEMM
cache-key and kernel argument expressions remain identical after the three new
host unpacking assignments. The combine body after its one unpacking assignment
and all combine GPU class bodies are AST-identical. Launcher bodies are identical
after normalizing the changed metadata binding and separately checking the fused
guard.

Allocation remains immediately after the identical `moe_sort` assignment and
before the same preparation/GEMM/combination chain. The core local variable and
both launcher option dictionaries retain the workspace through the combine call.
There are no added streams, device reads, waits, frees, or CUDA graph operations.
This establishes unchanged source-level lifetime and capture ordering; no new
PyTorch allocator or graph replay execution is claimed by the CPU stand-ins.

Contradictory direct private calls, such as independently supplying compact offsets
and a false routed-output flag, are deliberately replaced with a single workspace
contract. Supplying a workspace with fused atomic output is rejected before
launch. Public factory calls never create that contradictory state. W4A16 omits
the new optional argument and keeps its existing default behavior.

## Possible broader simplification

A separate experiment could make the actual bulk plan the shared host/kernel
contract: supported slab rows, scratch stages, scratch bytes and release scope.
Candidate slab shapes would be filtered by `rows <= route_tile`, divisibility,
output capability and calculated resource capacity. Metadata would be allocated
only when that selected plan uses bulk output. This could admit N32 with a
32-row slab or N64 with a 64-row slab without model or dtype heuristics. N16 would
remain direct until a supported smaller slab exists.

That change is not behavior preserving: it introduces compact metadata and new
store paths on decode tactics. Capacity is a safety condition, not evidence of a
performance benefit. Generalizing multi-channel overlap is a further, separate
change requiring global traversal of protected columns and a single correctly
placed release across channel tiles.

For the current equivalent kernel cleanup, the CPU proof plus scoped source
checks is sufficient; no full benchmark rerun is justified by this audit. Optional
codegen confidence can be bounded to an overlapping M256/N256 case and a
nonoverlapping M512/N128 case with the existing CLC/PDL variants. Broader admission
would need the existing exact/metadata/canary harness on new N32/N64 slabs and
tails, one/two CTA, static/CLC, PDL off/on; resource/codegen checks; and a bounded
frozen-winner CAAC screen across four models in EP and TP. Existing noneligible,
fused and W4A16 behavior must remain unchanged. No new autotuning axis is needed.

## Validation boundary

This is CPU source and planner equivalence under the current architecture
contract. It does not claim GPU compilation, output validation, sanitizer results
or new timing. Historical results above are explicitly attributed to their local
ledgers. The planner receipt retains the earlier raw-metadata host hashes for
provenance; its unchanged kernel hash remains valid. The separate workspace
receipt supplies current hashes for all four files and supersedes that earlier
host-only 120-case check.
