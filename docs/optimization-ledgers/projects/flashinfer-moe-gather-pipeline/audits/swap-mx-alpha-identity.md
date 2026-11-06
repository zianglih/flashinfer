# MX expert alpha: public contract and identity specialization boundary

Read-only audit of retained `c1ac8ce7` (swap SHA `482b636a`). No source or GPU changes. This is separate from the active scalar-prefetch experiment.

**The MX alpha tensors are not guaranteed to be ones by the public API.** The convenience weight preparer and benchmark create ones, but callers may supply nonidentity per-expert scales. There is no existing `None = identity` alpha contract to preserve.

| Path | Current behavior and source |
|---|---|
| `CuteDslConfig.prepare_weights` → `prepare_cute_dsl_weights` | Quantizes canonical BF16 weights and creates one shared `torch.ones(E)` buffer for `w1_alpha` and `w2_alpha` (`prepare.py:2555,2682–2690`). This convenience also uses ones for NVFP4; it is not an MX-only invariant. |
| Public `cute_dsl_fused_moe` | Requires tensor `w1_alpha`/`w2_alpha`, documents them as per-expert global scales, and forwards them to the shared core (`cute_dsl/fused_moe.py:1681–1761`). No identity check or overwrite. |
| Public `CuteDslMoEWrapper.run` | Same tensor contract and direct forwarding, including MXFP8/MXFP4x8 (`fused_moe.py:1357–1408`). |
| Deprecated MXFP8×MXFP4 function/wrapper | Still accepts caller alpha tensors; only `fc2_input_scale` is filled with `None` (`fused_moe.py:2174–2231`). Do not confuse that existing optional normalization scale with expert alpha. |
| Unified `CuteDslRunner` / manual weight pack | Reads `v["w1_alpha"]` and `v["w2_alpha"]` unchanged (`runners.py:5233–5303`). `MoEWeightPack.prepare_for` stores caller-created views without inspecting tensor values (`api.py:3786–3815`). |
| Published native benchmark | Independently creates ones at `bench_moe_deepseek.py:623` and passes that buffer at lines 804/808 and 824/828. It does not use prepared-view alpha fields. Allocation is outside the timed `run` closure. |

The private swap FC1/FC2 launchers accept these tensors (`blackwell/moe_swap_ab.py:300,515`). `_run_blockscaled_gemm` converts them to pointers at line 157. The JIT wrapper unconditionally builds an alpha tensor at `moe_swap_ab_kernel.py:2153`; the epilogue loads `alpha[expert]` at lines 3354 and 3387. FC1 applies alpha to both up/gate before activation (`:626–637`); FC2 incorporates it into the output/routing scale (`:1097–1116`, `:1151`). Nonidentity alpha therefore has real semantics, independent of the MX block scales. The exact reference likewise uses supplied expert alpha (`tests/test_helpers/cute_dsl_moe_swap_ab_reference.py:869,918`). Replacing alpha by one based only on dtype would be incorrect.

The smallest **swap-private** optional-identity implementation is technically bounded, without another runtime knob or new helper arguments:

1. Keep the existing alpha argument, permit `None`, and add alpha-presence to `_blockscaled_kernel_cache`'s key. `_blockscaled_ptr` already passes `None` through, but the current key at `moe_swap_ab.py:173–212` does not distinguish alpha presence. Reusing a compiled pointer ABI for a `None` specialization would be wrong.
2. Make `alpha_ptr` optional and conditionally construct the tensor; supply a compile-time one instead of the expert load when absent. The same scalar epilogue arguments can remain. Removing packed multiplication instructions is a compiler/native question, not proven by this source audit.
3. Preserve tensor inputs exactly, including caller-provided nonidentity values. No GPU value inspection or synchronization should be used to guess whether a tensor happens to contain ones.

That private change alone removes neither the prepared nor benchmark allocation: both currently pass real tensors. Reaching normal users requires a deliberate public optional-argument contract, corresponding docs/trace metadata (`trace/templates/moe.py:4209` currently requires alpha), and a prepared-view/runner convention. The common preparer returns `Dict[str, Tensor]`; the common pack stores the same type. Omitting alpha keys could avoid widening every dictionary, but would introduce missing-key semantics where the runner currently requires keys. Returning `None` requires optional-value typing. Either approach must account for `swap_ab=False`: the existing FC1/FC2 launchers unconditionally call `alpha.data_ptr()` (`blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:907`, `blockscaled_contiguous_grouped_gemm_finalize_fusion.py:660`). A generic public identity contract thus needs legacy-path support or a documented execution-path restriction, not just the swap edit.

The autotuner itself already preserves `None` inputs (`autotuner/autotuner.py:4237–4252`) and distinguishes non-tensors in input-size keys (`:3480`); no new tuning axis is needed. W4 already loads `alpha_val` before its accumulator wait (`moe_w4a16_kernel.py:2291`) and needs no change for the current prefetch experiment.

**Recommendation:** do not pursue this as a small MX cleanup in the present kernel experiment. Identity specialization is possible without a new knob, but it is an additive API/prepared-view contract and compilation-cache change, not preservation of existing semantics. Keep arbitrary tensor alpha supported and let the independent prefetch probe evaluate its general load-latency mechanism first. No implementation or performance conclusion follows from this audit.
