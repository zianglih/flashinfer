# Alpha batching: SGLang reload validation

The external `check_sglang_alpha_reload.py` complements HashInfer's own graph,
shared-workspace and alias tests. It imports SGLang's actual
`python/sglang/srt/layers/utils/common.py` unchanged, without importing the full
server. That module only requires PyTorch and Python standard-library modules.

The SGLang source inspected is `16c1b8638b462ca1b896e2b76d5c002caf06988b`.
`modelopt_quant.py:2708-2725` uses FP32 weight-only alphas for W4A16, recomputes
derived alpha tensors, and publishes them through `copy_or_rebind_param`.
For an existing `Parameter` with the same shape and dtype, the helper copies the
new values into its storage and preserves both the parameter and its address.
`flashinfer_megamoe.py:656-659` passes those per-layer alpha parameters into each
forward because the workspace is shared across layers.

## What the harness checks

- Two actual HashInfer public layers share one workspace. A single graph captures
  an A/B/A layer sequence with distinct per-layer alphas.
- Activations, routes and packed expert weights stay fixed. Each alpha is changed
  independently by recomputing a fresh FP32 tensor and calling SGLang's helper.
- The `Parameter` object and `data_ptr()` must remain unchanged.
- The graph is replayed before any eager forward following the update, so an
  eager call cannot mask stale captured data. Captured output must change only
  for the updated layer and exactly equal the updated eager result.
- Both token-return tactics can be checked on EP4 and EP8.

Copy the script, the unmodified SGLang `common.py` and the candidate HashInfer
checkout to the devbox. Example, with HashInfer importable and its source tests
present:

```sh
torchrun --nnodes=1 --master-addr=127.0.0.1 --master-port=29764 --nproc_per_node=4 check_sglang_alpha_reload.py \
  --sglang-common common.py --token-back-mode epi_warps
torchrun --nnodes=1 --master-addr=127.0.0.1 --master-port=29764 --nproc_per_node=4 check_sglang_alpha_reload.py \
  --sglang-common common.py --token-back-mode reuse_dispatch_warps
torchrun --nnodes=1 --master-addr=127.0.0.1 --master-port=29764 --nproc_per_node=8 check_sglang_alpha_reload.py \
  --sglang-common common.py --token-back-mode epi_warps
torchrun --nnodes=1 --master-addr=127.0.0.1 --master-port=29764 --nproc_per_node=8 check_sglang_alpha_reload.py \
  --sglang-common common.py --token-back-mode reuse_dispatch_warps
```

The result prints a digest of the SGLang source file used at runtime.

## Boundary

This tests the real update helper and the real distributed kernel/graph lifetime;
it does not execute an SGLang server, its weight-sync transport, or complete
`process_weights_after_loading`. The previous adapter smoke includes full packed
weight reload but imports the SGLang package and its additional dependencies.

Changing values in stable alpha storage is supported. Replacing the source with
a different tensor pointer after graph capture is a different operation: the
captured graph retains its original source pointer. Shape/dtype changes can make
`copy_or_rebind_param` rebind storage; those require graph rebuilding and are not
covered by this same-geometry reload contract. As with the previous sequential
copies, an update must finish before the next replay; concurrent unsynchronized
updates during replay are not a supported weight-sync contract.

At script creation only Python syntax was checked locally; GPU validation is
performed separately on C2 and must not be inferred from this document.
