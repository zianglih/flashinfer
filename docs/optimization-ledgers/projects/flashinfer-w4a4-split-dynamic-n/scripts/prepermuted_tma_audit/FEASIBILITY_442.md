# FC1 pre-permutation and regular TMA feasibility

CPU/source-only audit of `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. No implementation, compilation, GPU execution, or performance claim. Source paths below are relative to the project's `flashinfer/` checkout.

Subsequent scope decision: the user explicitly authorized trying this W4A16-style regular-TMA contract. The separate immutable prototype lives in `../fc1_regular_tma_experiment/`; this note remains the source-only feasibility analysis preceding that experiment. Its final scope caveat is therefore resolved for that prototype.

**Feasible, but not a drop-in loader change.** A byte-preserving preparation kernel could materialize routed activation rows and their canonical scale bytes once, allowing FC1 to reuse the existing FC2 regular B-TMA/SFB-TMA machinery. It preserves fused SwiGLU and per-token arithmetic. The expected benefit is fewer gather instructions and removal of scattered SF loads and their readiness relay; the cost is a new global read/write pass and workspace.

## Existing precedents and gaps

- **W4A16 already does this:** `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py:419` sorts routes, `:441` calls `moe_permute` into `hidden_workspace`, and `:452` passes that buffer to FC1. `blackwell/moe_w4a16_kernel.py:756` creates the regular activation B-TMA atom. Its inputs are BF16, so no activation block scales need permutation.
- **Current blockscaled FC1 does not:** `cute_dsl/fused_moe.py:541` sorts metadata, then `:694` passes original `x/x_sf` and the route mapping to gathered FC1. The optional per-token quantization at `:734` is after FC1; it cannot prepare FC1 inputs. `cute_dsl/moe_utils.py:581` explicitly documents that sorting does not move payload.
- **The existing native permutation helper is incomplete for blockscaled inputs:** `csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu:66` copies payload from `mapping[row] / top_k`; `:97` explicitly defers FP4 SF handling. Its host launcher hardcodes SF vector 16 at `:113`, and the instantiations at `:147` cover FP16/BF16/E4M3/FP4 only. Python dispatch at `cute_dsl/moe_utils.py:198` also lacks E5M2. Its documented swizzled-SF result is therefore not implemented.
- **Useful complete reference, not a compatible call:** `csrc/fused_moe/cutlass_backend/cutlass_fused_moe_kernels.cuh:1571` has `expandInputRowsKernel`; the prequantized path at `:1713` copies payload and calls `writeSF`, whose implementation at `:1134` copies scale bytes from linear/swizzled input into 128x4 output. It also zeroes padded K scale bytes. Its expanded-index convention is rank-major (`source_row = expanded % num_tokens`), unlike this backend's token-major `expanded / top_k`, and it has per-expert scale bases. Reusing its indexing unchanged would be wrong.

## Internal contract required

1. Write routed payload row `r` from original row `mapping[r] // top_k`; copy packed FP4 nibbles and FP8 bytes without dequantization, requantization, or scale conversion. The six supported configurations reduce to three copy geometries: FP4/SF16 (E4M3 or E8M0 SF), FP4/SF32 (E8M0), and FP8/SF32 (E4M3 or E5M2 activation, E8M0 SF; including mixed W4A8).
2. Transform original linear SF bytes into the exact prepared layout in `blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:225`: for scale column `s`, offset is `floor(r/128)*ceil(K/(4*v))*512 + floor(s/4)*512 + (r%32)*16 + floor((r%128)/32)*4 + s%4`, with vector size `v`. Allocate complete 128-row/four-scale atoms. Zero inactive route rows and padded K SF bytes, and never read invalid mapping slots. The current helper skips inactive rows, so it does not establish this stronger initialization contract.
3. Keep per-token scale indexing unchanged: FC1 still uses `per_token_scale[mapping[r] // top_k]` (`blackwell/utils.py:563` and `:617`); retain the mapping for this and FC2 scatter. No per-token-scale permutation is necessary. FC2's intermediate routed-row scales remain unchanged.
4. Add an internal input-layout/loader choice independent of activation type. Today `activation_type is None` controls source extent (`:536`), B descriptor (`:706`), SF indexing (`:1149`), and producer ownership (`:1178`). Setting activation to `None` merely to enter regular TMA would break FC1. Retain FC1 epilogue, accumulator overlap, iKET markers and all activation/per-token logic.
5. Reuse existing B/SFB SMEM and TMEM layouts. At route N128/N256, canonical SFB TMA already exists at `:742` with separate K/row-block descriptor axes, preserving short-K zero fill. For N16/N32/N64, route starts can lie inside a 128-row atom; retain the prepared-SF cp.async fallback until a separately proved descriptor exists. Producer arrival counts and expected bytes must follow the regular-TMA path, not FC1's four-Gather4-producer count. Two-CTA SFB still has a complete local copy per CTA (`:356`); this proposal does not establish scale multicast.

## Traffic and storage

Let `R` be live local routed rows, `P` their padded extent, `H` hidden size, and `v` SF vector length. A preparation pass adds approximately `2*R*(H*activation_bits/8 + H/v)` logical byte transfers, plus padding writes. This is not an HBM-byte prediction: source duplicates and subsequent TMA reads can hit cache.

For the saved native 16K routing (`scripts/composed_pipeline_experiment/nvfp4-n128-r1.log`: `R=16,280`, 142 N128 tiles), `H=7168`:

| Activation / SF | Bytes per live row | Added read + write | Storage for 18,176 active padded rows | Conservative graph-safe capacity storage |
|---|---:|---:|---:|---:|
| FP4 / SF16 | 4,032 | 131.28 MB | 73.29 MB | 544.48 MB |
| FP4 / SF32 | 3,808 | 123.99 MB | 69.21 MB | 514.23 MB |
| FP8 / SF32 | 7,392 | 240.68 MB | 134.36 MB | 998.22 MB |

Decimal MB. The last column uses existing `get_max_num_permuted_tokens` (`moe_utils.py:111`), T=16,384/top-k=8/local-experts=32/N128: 135,040 rows, not the observed routing density. An asynchronous graph-safe implementation must not `.item()` the live count to allocate a smaller buffer. The deterministic FC2 expanded output buffer (`fused_moe.py:771`) is larger in bytes for this case and is dead during FC1, so lifetime-proved aliasing could avoid much of the *additional* allocation; small shapes, padding, fused-finalize and low-level APIs need separate capacity checks. This is an opportunity, not established aliasing correctness.

For logical M512/N128 NB2, FC1 has 4096 pre-activation channels in this workload, hence eight channel tiles (`core :285`, `:1056`). Pre-permutation does not remove their repeated activation reads; it replaces their access pattern. Per CTA/K256, N128 group-2 currently issues 16 Gather4 row-chunk copies for B; a regular tiled B-TMA operation describes that same tile. SFB also becomes canonical contiguous TMA traffic. These are instruction/transaction-efficiency hypotheses, not measured savings.

## Can it be folded into existing preparation?

Not without changing a native kernel. `csrc/moe_utils_binding.cu:357` exposes only route IDs/weights and metadata pointers. The routing permutation stages (`trtllm_fused_moe_routing_custom.cuh:620`, for example) publish index mappings, not activation payload. Fusing payload/SF writes into a final routing stage would require new pointers, dtype/vector/layout dispatch, and suitable row-copy parallelism across the routing kernel variants. It could keep launch count fixed, but is a larger change to shared routing code. Upstream activation quantization is outside this API and cannot be assumed available for fusion.

The smallest isolated future experiment is one internal byte-copy/SF preparation kernel followed by FC1 with regular TMA, timing the entire native chain including preparation. It must compare exact live outputs for all six input configurations, per-token NVFP4, short K, partial route tiles, and repeated CUDA-graph replay before any retention screen.

**Constraint boundary:** this preserves the public call and fused FC1 activation, but adds a separate activation-preparation kernel to the current W4A4/W4A8 workflow. It is distinct from the earlier rejected post-FC1 unshuffle/unfused-activation pass, yet it does not satisfy a literal “no extra payload stage” requirement. Keep it an optional future axis until that scope is accepted. No production change belongs in the frozen 442 benchmark checkpoint.
