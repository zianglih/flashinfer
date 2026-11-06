# Shared payload/SF route decode: ownership audit

Read-only source audit and CPU ownership proof. Retained475 is unchanged. No review clone, GPU compile, test or timing has been started for this proposal.

## Prior evidence and source contract

- Current payload cache: `blackwell/moe_swap_ab_kernel.py:3468–3497`; one lane-distributed mapping load/divide per four-row group, then four SHFLs outside K into the cached warp-uniform coordinates. SF independently loads/divides its rows at3508–3517.
- The retained lane-metadata audit explicitly identified why reuse was deferred: `full-20261029/lane-metadata/AUDIT.md:38–52`. It was not a measured shared-ownership attempt. Route-vector128 experiments also left SF untouched (`optimization-20261029/metadata/README.md`). No duplicate attempt was found in these local ledgers.
- Rubin uses separate payload and SF warp groups (`rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1973–2078,2092–2170`), so its implementation does not give a same-warp reuse solution. It reinforces caching payload IDs before K. MegaMoE interleaves eight-ID vector runs and caches them before K (`moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/sources/kernel_src/blackwell/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1150–1255`); importing its eight-row ownership directly can reduce narrow-tile issuing concurrency.
- Current SF row `8*w + 32*(lane>>3) + (lane&7)` gives32 distinct shared banks per instruction. A naive four-row interleave has two-way conflicts. SFB remains full-N in each CTA, while B payload uses a dynamic half-tile offset in two-CTA mode. Both properties must be preserved.

## One permutation

Let a four-row global group be `g`. Assign its SF owner with:

```python
owner(g) = (g & 2) + ((g & 1) ^ ((g >> 2) & 1))
```

Owners of the first eight four-row groups are `[0,1,2,3,1,0,3,2]`. Thus the first16 rows occupy all four warps. For warp owner `w` and lane `l`, its inverse row map is:

```python
v = (l >> 2) & 1
row = (l & 3) + 4*v + 8*(w >> 1) + 16*((w & 1) ^ v) + 32*(l >> 3)
```

The SF shared-bank index is `4*(row&7) + (row>>5)`. The lane map above hits every bank exactly once for every owner. All128 SF rows are covered exactly once across four owners. This is a bit permutation plus one XOR, not shared staging or a transpose kernel.

## Compile-time row/K partition

```python
row_groups = b_copy_rows // 4
k_chunks = k_steps // 4
k_warps = gcd(4 // min(4, row_groups), k_chunks)
row_warps = 4 // k_warps
sf_row_phases = k_warps
```

All supported K4/K8 geometries use one or two K warps. No N16/CTA/dtype/model branch is needed. The gcd keeps K work divisible for a future odd K-chunk count; four-issuer efficiency is proven here for the current K4/K8 catalog, not claimed for arbitrary future shapes.

At runtime before K, let `S = cta_payload_row_offset // 4`, always even. Warp `w` owns `r=w%row_warps` and K partition `w//row_warps`. Its SF row phase `p` uses `owner(S+r+row_warps*p)`. The phases cover the full-N SF rows; K warps own disjoint equal sets of SF K blocks. Because SF blocks per payload chunk is1,2 or4 and `k_warps` divides `k_chunks`, this split needs no tail predicate.

Payload group `q` uses local four-row group:

```python
local_group = row_warps*q + (r ^ ((row_warps//4) * (q&1)))
global_group = S + local_group
```

It always belongs to SF phase0 of the same warp. Select its SF row block (at most two current blocks) outside K, then broadcast from lanes `8*((global_group%32)>>3) + 4*(global_group&1) + [0,1,2,3]`. Keep the resulting four coordinates in the existing static cache. Nothing is shuffled, selected, divided or looped dynamically inside K.

The SF raw IDs only need to survive until the payload cache is built. For invalid rows, initialize the cached ID to the existing descriptor-OOB sentinel; the unchanged SF row predicate prevents its unused offset from being dereferenced. Alternatively preserve zero invalid SF offsets with an explicit select before scaling; that may cost more instructions and must not silently introduce speculative invalid loads.

The smallest two-CTA K8 tile has two row groups and two K chunks. Its two SF row phases partition the same full-N scales across the two K warp pairs, making the duplicated route decode useful to each warp’s own SF loads. All four payload issuers remain active. Other current geometries retain one SF phase.

## Load/divide and liveness accounting

The following is source-level upper-bound warp issue contexts per routed tile before K, not measured SASS or HBM traffic. Masked rows may suppress execution. Each entry counts mapping load plus its associated divide; SF data copies are unchanged in total count.

| N | CTA | K steps | Row/K warps | Mapping loads/divides before→after | Saved | SF offsets Int64/thread before→after |
|---:|---:|---:|---|---:|---:|---:|
| 16 | 1 | 4 | 4/1 | 8→4 | 4 | 1→1 |
| 16 | 1 | 8 | 4/1 | 8→4 | 4 | 1→1 |
| 16 | 2 | 4 | 4/1 | 8→4 | 4 | 1→1 |
| 16 | 2 | 8 | 2/2 | 8→8 | 0 | 1→2 |
| 32 | 1 | 4 | 4/1 | 12→4 | 8 | 1→1 |
| 32 | 1 | 8 | 4/1 | 12→4 | 8 | 1→1 |
| 32 | 2 | 4 | 4/1 | 8→4 | 4 | 1→1 |
| 32 | 2 | 8 | 4/1 | 8→4 | 4 | 1→1 |
| 64 | 1 | 4 | 4/1 | 20→4 | 16 | 1→1 |
| 64 | 1 | 8 | 4/1 | 20→4 | 16 | 1→1 |
| 64 | 2 | 4 | 4/1 | 12→4 | 8 | 1→1 |
| 64 | 2 | 8 | 4/1 | 12→4 | 8 | 1→1 |
| 128 | 1 | 4 | 4/1 | 36→4 | 32 | 1→1 |
| 128 | 1 | 8 | 4/1 | 36→4 | 32 | 1→1 |
| 128 | 2 | 4 | 4/1 | 20→4 | 16 | 1→1 |
| 128 | 2 | 8 | 4/1 | 20→4 | 16 | 1→1 |
| 256 | 1 | 4 | 4/1 | 72→8 | 64 | 2→2 |
| 256 | 1 | 8 | 4/1 | 72→8 | 64 | 2→2 |
| 256 | 2 | 4 | 4/1 | 40→8 | 32 | 2→2 |
| 256 | 2 | 8 | 4/1 | 40→8 | 32 | 2→2 |

- Cached payload coordinate count stays unchanged. Raw SF IDs add at most one/two temporary Int32 values per thread, ending before K; no new array is dynamically indexed in the K loop.
- One-phase geometries keep the original SF offset/row/shared-offset live state. The smallest two-CTA K8 case has one extra Int64 SF offset and approximately two extra Int32 row/shared offsets: roughly four additional registers across K, with zero mapping-load reduction. This is the main narrow-tile risk.
- Added before-K arithmetic is the owner/inverse bit permutation, CTA-offset selection and at most a two-bank scalar selection. Hot SF copies retain the same total static count; their row/K partition changes. Hot payload issue uses a static row-group XOR instead of the original linear row group; its pointers should be precomputed or folded where useful.
- No new shared metadata, barrier, runtime loop, publication, SF stage, CLC choice, PDL policy, tuning axis, or problem-specific predicate is required. Four SF producer warps still arrive once per stage; payload bytes/completion and physical B/SFB layouts do not change.

## Proof and prototype decision

`proof.py` passed3,006 geometry/live-row/CTA cases,526,752 payload row×K pairs and6,112,512 full-N SF row×K-block pairs. It checks the same-warp raw-ID lookup, exact disjoint coverage, all32 shared banks per SF instruction, no out-of-range cache access, and all four payload issuers when at least four tasks exist.

This appears implementable as one general static ownership permutation plus row/K geometry. A bounded prototype is justified only if it stays as compact as this description: preserve static payload caches, avoid a fallback for N16/twoCTA, and keep both SF phases as compile-time dimensions. If the source needs extra data-dependent cases or repeatedly reconstructs coordinates inside K, reject it on complexity.

Before timing, require current exact coverage including N16/twoCTA/K8 and full-N SFB, actual SASS/local-storage checks, and comparison of metadata LDG/divide/R2UR sites against added shifts/XORs and register liveness. Source-level savings do not establish a performance gain. Root’s native moe_utils rebuild must finish before GPU gates.
