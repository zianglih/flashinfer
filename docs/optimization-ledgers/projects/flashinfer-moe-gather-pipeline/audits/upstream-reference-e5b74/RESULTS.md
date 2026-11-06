# Upstream staging/reference audit

**Conclusion:** no additional launch, padding, or validation elimination from these commits transfers directly to the measured retained gather pipeline. Keep the current source unchanged. The reference changes remove wrapper work that our split backend already avoids; they do not supply a new GEMM pipeline optimization.

Scope: retained `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`, upstream interval `a65d5b09..e5b74c056710162be3803ed742ea84e9d1e57aa7`. `receipt.json` pins exact commits, all inspected retained-file hashes, and archived reference patches. Source was clean before and after; no GPU commands, tests, timings, or rebases were performed.

| Reference change | Current retained path | Transfer decision |
|---|---|---|
| `8cc2453f0` / #7806 fuses routing-value checks into input quantization. `d7c651346` / #7913 extends this to NVFP4. | `moe_sort` receives caller route tensors. Its host checks inspect shape/dtype/layout; there is no separate route-value validation kernel in the benchmark chain. | No launch to remove. Do not interpret the upstream fusion as permission to remove validation: upstream still checks range, duplicate IDs, and finite unmasked scores, and preserves a fallback validation launch when fusion is ineligible. |
| Quantization staging also masks the unused capacity tail of a symmetric route buffer. | Routing metadata buffers are `torch.empty`; routing writes the active prefix and GEMMs consume its device count. There is no separate full-capacity route-tail fill in this split path. | Already avoids that work. Live expert-tile padding is different: gather and epilogue need the per-tile row limit and defined scale/output ownership. |
| `d7c651346` fuses BF16 activation, route-ID, route-score copies and route-tail fill into one staging kernel. | W4A16 FC1 gathers directly from caller BF16 activations. Swap-AB FC1 likewise consumes the quantized input directly through gather. | Our no-standalone-permutation design avoids these copies altogether. Introducing a staging kernel would add traffic. |
| `8cc2453f0` binds live caller output directly for Rubin's separate TopkReduce; `d7c651346` does the same for the compatible BF16 Mega form. | `moe_unpermute(..., output=moe_output, num_tokens=num_tokens)` writes caller output directly. Its grid is `num_tokens * hidden_tiles`; the return slice is a view. | Already implemented. FC2 routed-row scratch is the deterministic reduction input, not a redundant final-output copy. |
| NVFP4 default scalars now bind stable all-ones storage instead of filling mutable session tensors on each call. | Split launchers pass caller alpha/global-scale tensor pointers directly. Benchmark constants are prepared outside the timed callable. | No per-call three-fill/copy sequence to remove. The upstream graph/layer default-isolation fix is specific to its mutable session-scalar ownership. |
| Live-output binding includes pointer, shape, and stride in the cached host signature. | Finalizer caches a kernel by static dimensions/types and passes output pointer plus dynamic token count on every call. | It does not retain the same stale output-binding hazard. No extra signature cache or public option needed. |

## Current chain and boundaries

- `cute_dsl/fused_moe.py:646–663` calls routing; `:798–835` passes caller activations/scales directly into FC1. W4A16 uses the equivalent direct path in `blackwell/moe_w4a16.py:435–478`.
- Ordinary quantized swap modes fuse FC1 activation and output quantization. **Per-token NVFP4 additionally runs its required inter-GEMM per-token quantizer** (`fused_moe.py:837–865`), using existing valid-row/per-tile limits and the established scale layout. The reference commits fuse *input staging*, not this intermediate row reduction/quantization, so they do not justify erasing it.
- Initial activation quantization is benchmark-option dependent (`bench_moe_deepseek.py:654–695`); W4A16 uses BF16 directly. The published NVFP4-family contract includes initial quantization. MX input-quantization timing remains its existing benchmark contract.
- Routing is a logical stage, not a promise of exactly one kernel: the C++ routing implementation may use several kernels for large inputs. The reference route-copy/validation fusion does not perform our expert counts, scheduling metadata, or expanded/permuted maps.
- `moe_utils.py:699–712` preserves conversions for noncontiguous or non-int32 user input. Those are compatibility paths, not redundant launches for the frozen contiguous/int32 benchmark routes. Do not tighten that public contract merely to imitate the wrapper optimization.
- `moe_finalize.py:134–135,199,205–326` bounds output to live rows and has host metadata checks without device-value reads. Fused atomic output zeroing remains a distinct, excluded performance path.

## Other relevant interval changes

- `5240384d8` / #6950 is the only change in this interval under the retained legacy `cute_dsl/rubin` and `moe_ep/cute_dsl/megamoe` GEMM trees. It adds Rubin deterministic/unfused FC2 output through bulk plain stores and skips routing-scale multiplication in that mode. Our Blackwell path already has unique-row FC2 output and deterministic finalize; its different ownership/layout means this is not a missing launch elimination.
- `7bce78b15` preserves masked-route semantics and enables fused staging for int32 route buffers. `4e8d3cbcd` wires Blackwell MXFP4/MXFP8 standard support and shares route staging. They are contract/wiring references, not grounds to remove our required routing or change the measured backend.
- The two highlighted commits modify staging/backend/shim code, **not the shared W4 dequantization helper or the GEMM kernel being evaluated by the raw TRY→TEST experiment**. Their published timing improvements are not evidence for an expected speedup here.

No new candidate is proposed from this audit. GLM5 remains held until the parent reviews the separate full104 raw-peek split campaign and explicitly authorizes the eight-GPU causal run.
