# Route-padded activation scale factors

Audited clean `1e69d0a391fd926d21a35388cacf2df3c1c22baf`. The implementation is now unstaged in the shared `flashinfer-warp-specialization-review` checkout. No new MoE frontend argument, tactic, kernel launch, payload transpose, or quantization arithmetic is introduced.

## Why narrow SF loads were not TMA

The old preparation and FC1 output layouts pack all logical routed rows into canonical 128-row × four-scale atoms. N16/N32/N64 route starts can lie inside one atom; the MMA needs its route at the beginning of the local SFB atom. The old kernel therefore gathers each route's four-byte scale fragments into shared memory with four producer warps and a separate cp.async readiness path. N128/N256 already use the desired 3D TMA descriptor.

This is a global-storage alignment issue. Every admitted N already reserves at least one complete 128-row SFB atom per stage. Group-2 MMA reads a complete local SF copy in each CTA, even though activation payload rows are split between CTAs. There is no shared-memory increase in this proposal.

Source anchors at the audited base:

- `moe_swap_ab_kernel.py:1439–1455`: logical route N, physical accumulator N, full SF atom size, and narrow fallback selection.
- `moe_swap_ab_kernel.py:2103–2127`: byte-preserving Int16 TMA descriptor with separate K and row-atom axes.
- `moe_swap_ab_kernel.py:2674–2818`: compact activation payload tile and narrow SF gather/TMA coordinates.
- `moe_swap_ab_kernel.py:2430–2461,3054–3079`: shared expected-byte barrier, extra cp.async barrier and group-2 publication join.

## One private layout for every route N

For logical route tile N, define `P = ceil_div(N, 128) * 128`. The physical SF row corresponding to logical routed row r is:

```python
sf_row = (r // N) * P + r % N
```

For a payload capacity C divisible by N and `S = ceil_div(K / sf_vec, 4) * 4` SF columns, allocate `(C / N) * P * S` SF bytes. Payload rows and per-token scales retain their original compact row indices. No routing metadata values change.

The SF atom's byte order is unchanged:

```python
byte_offset = (sf_row // 128) * (S // 4) * 512
byte_offset += (scale_column // 4) * 512
byte_offset += (sf_row % 32) * 16 + ((sf_row % 128) // 32) * 4
byte_offset += scale_column % 4
```

TMA uses Int16 shape `(256, K_blocks, route_count * P / 128)`, strides `(1, 256, 256 * K_blocks)`, and tile `(256, tile_K / (4 * sf_vec), 1)`. Its row-block coordinate is `route_index * (P / 128) + row_block`. Separate K coordinates retain zero fill for a short final K stage rather than wrapping into another route's SF atom.

| Logical N | SF row pitch P | SF workspace factor | Existing local SFB rows |
|---:|---:|---:|---:|
|16|128|8×|128|
|32|128|4×|128|
|64|128|2×|128|
|128|128|1×|128|
|256|256|1×|256|

N128/N256 are byte-identical to the prior layout. At every N, each CTA loads `P * tile_K / sf_vec` SFB bytes per stage. Two-CTA mode retains two complete local copies; total expected bytes include both. This is not a multicast proposal. The prior `scripts/perf_round_20261027/mainloop/README.md` multicast experiment was rejected, and `scripts/two_cta_experiment/README.md` documents why removing the peer CTA's local source would be incorrect.

`sf_layout_proof.py` verified 1,130,880 address checks across 50 N/SF/K geometries, both CTA group sizes, odd route counts and K-tail descriptor bounds. This is a CPU arithmetic proof, not a CuTe compile or TMA execution claim. `sf-layout-proof.json` pins the audited source.

## Publication in the existing operations

- **Preparation:** `allocate` receives the existing route tile; payload storage stays compact. `PrepareRouted` walks logical rows and maps only SF destinations to their physical route atoms. Invalid logical rows have zero SF; unused physical slots are untouched. The unscaled W4A16 path keeps its original logical row traversal.
- **FC1 fused output:** the existing epilogue quantizer maps only its SF store row. Activation fusion, payload stores, per-token scale reads, dynamic MMA N, and output channels remain unchanged. Its `tile_n` is the logical route N. The caller allocates complete atoms per route and rejects an undersized supplied SF buffer explicitly.
- **Per-token NVFP4:** the same existing quantizer is reused. An optional `sf_rows_per_group` controls its physical SF row pitch, paired with existing `rows_per_group`. It enters the compiled cache key; omitted/None retains the old cache identity, row layout and allocation. Swap-AB passes P, then reuses the existing view-only `convert_sf_to_mma_layout` with the physical SF row count. Public quantization before FC1 does not pass this option and retains its old behavior.
- **FC2 input:** payload and SF descriptors use their separate logical and physical row extents. All generated tactics use one shared route N for both GEMMs; their independent channel tiles, K steps, and CTA groups do not change SF row ownership.

The prepare and standalone per-token quantizer retain zero-defined inactive logical SF rows in the same operation. The fused FC1 epilogue continues to define only live output SF rows. Arbitrary invalid-row SF bytes, including NaN encodings, were already qualified by the retained wide-SFB TMA experiment (`scripts/sfb_tma_experiment/README.md`, 96 strict comparisons plus canaries). Token columns are independent, and all output/metadata operations mask inactive rows. Therefore no extra memset is required.

The first frozen revision initialized all physical padding, then `gate_padding_poison.py` replaced only slots `[N,P)` with `0xFF` after prepare and before FC2. All 64 public captured replays matched retained-source output bytes across narrow N16/N32/N64, one/two CTA, NVFP4/per-token/MXFP8/MXFP4x8, static/CLC, PDL off/on, and live/empty/reactivated routing. The 112 poison hooks and source/config identities are recorded in the original remote `padding-poison/receipt.json`. That proof justifies the second revision's logical-row iteration: no padding CTAs, no physical-padding zero loop, unchanged logical-row values.

## Remaining gate and performance boundaries

The initial shared source is frozen in `sf-source-freeze.json`; the final logical-row revision is `sf-source-freeze-r2.json`. Both pass Ruff, Python compilation and diff checks. Each revision passed six default-layout comparisons against retained `1e69` and 110 captured routed-pitch replays, including all N, PDL on/off, 4over6, SF-column tails, and the existing two-pass large-K quantizer. The final revision additionally verifies that physical-padding bytes remain at their initial canary while invalid logical SF rows become zero. Its source/config-verified receipt is `r2/quantizer-gate/receipt.json`; both control and candidate exited successfully. Final route-preparation and public replay checks are tracked by the combined gate manifest. No sanitizer or performance claim is made by this note.

The extra narrow-N global SF allocation and TMA read footprint are real costs. Their benefit must come from fewer SF load/control instructions and the simpler producer pipeline in whole-chain timing. The final design does not write or launch work for unused physical rows. No dtype/model threshold or new autotune axis is proposed to hide those costs.
