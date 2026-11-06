# CPU audit: one remaining preparation work-distribution candidate

Frozen98fd, CPU/source-only. No kernel, shared sort, MegaMoE, source-copy or GPU change. The TMEM permit audit took priority when requested; this note completes the bounded preparation review.

## Verified constraints

The retained preparation has already removed invalid payload writes and uses256-bit payload copies. `flashinfer-profile-98fd/flashinfer/fused_moe/cute_dsl/blackwell/moe_prepare.py:97–107` derives active rows from the device tile count, adds the bounded N16 physical tail and rounds SF coverage to128 rows. Lines115–119 guard mapping loads by each tile’s valid prefix. Lines145–169 still write every SF word with a row-owned CTA, including zero words for padding. Payload allocation and SF padding remain invocation-local.

Its host grid at249–258 is bounded by the tight worst-case capacity and hardware thread capacity. `moe_utils.py:117–144` derives that tight routing-capacity bound. The actual decode grids launch more CTAs than there are active SF rows, but the host cannot replace capacity with the device-produced live count without changing the launch workflow. Merely reducing the hardware grid factor repeats an already measured axis and risks the retained prefill benefit: `scripts/fc1_regular_tma_experiment/GRID_PREPARATION.md` records grid4/8/16 forward/reverse experiments.

There is no safe sorting-order shortcut:

- `csrc/moe_utils_binding.cu:382–396` forwards precomputed top-k IDs to routing, with the optional direct token-index mapping null.
- T32/T128 use the shared cluster path. `include/flashinfer/trtllm/fused_moe/RoutingKernel.cuh:365` assigns positions within an expert by atomic addition. Lines429–435 preserve only coarse block-window ordering. Neither case guarantees contiguous source-token runs.
- The count at509–510 is written before the final mapping stores at540–543 and PDL completion at557. It is not a readiness flag. The preparation wait at95–96 and valid-prefix checks must remain.

## Bounded candidate: linear destination SF ownership

Keep the valid-row256-bit payload loop, grid, allocation, interface and PDL unchanged. Remove SF work from the per-row loop and add a separate scalar SF loop in the **same kernel**, assigning consecutive canonical destination Uint32 words to consecutive threads. This is a work-ownership change, not a wider-load or shared-memory-transpose change.

For canonical word index `i`, let `B=sf_columns/4`:

```text
atom = i // (128*B)
sf_block = (i // 128) % B
p = i % 128
row = 128*atom + 32*(p % 4) + p//4
```

Write zero when that row is outside the active extent or its tile’s valid prefix; otherwise read the original scalar SF word from `mapping[row]//top_k * B + sf_block`. Iterate exactly `sf_rows*B` words. This is the algebraic inverse of the existing canonical address formula at159–164, so every destination word has one owner. Payload and SF are different allocations; their loops need no inter-CTA ordering or additional barrier. Existing4-byte SF alignment, original-token indexing, arbitrary byte encodings, full128-row zero padding, zero-route no-write behavior and untouched suffix capacity remain expressible without new dispatch branches.

The current native decode receipts quantify why this is worth at most one bounded screen:

|Saved tactic|Valid rows|SF rows written|Zero SF rows|Zero fraction|
|---|---:|---:|---:|---:|
|T32 N16|31|384|353|91.93%|
|T32 N32|31|768|737|95.96%|
|T128 N16|108|512|404|78.91%|

Current SF word stores vary by512B between adjacent lanes. A full32-lane store instruction therefore touches32 sectors for128 useful bytes; consecutive destination ownership can touch4 sectors. These are **address-level request estimates**, not measured DRAM traffic or an8× kernel speedup. The native SF output is only172032/344064/229376 bytes in the three cases. The complete preparation costs roughly4.1us including launch, so any full-chain opportunity is small.

Tradeoff: valid source SF becomes a gather, and limit/mapping checks repeat across SF blocks. Dense prefill can lose coalesced source reads or suffer metadata/branch overhead. The ledger already rejected a128-row shared-memory transpose with two barriers, reduced CTA count and16,896B scratch (`scripts/regular_tma_sf_tile_experiment/README.md`); that mechanism is not repeated here. Source-vector width selection (`scripts/prep_sf_vector_experiment/README.md`) is also distinct: it retains row ownership/scattered stores and changes alignment/width. No extra source alignment is proposed here.

If pursued later, first prove byte ownership with existing preparation oracles for N16/32/64/128/256, shortK, all actual byte layouts, graph counts0→grow→shrink→0 and poison/canaries. Then compare only prep on the saved T32 N16/N32 and T128 N16 routing, both orders; prefill NV8K and MX16K guard against the source-gather regression before any full-chain or retention claim. No such experiment was performed by this audit. The parent’s ongoing GEMM experiments remain higher priority.
