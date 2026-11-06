# Buffer alignment ownership: SGLang and the public MegaMoE API

Source audit only. SGLang local clean16c1b8638b462ca1b896e2b76d5c002caf06988b; current FlashInfer PR5019 checkout74ba96d551640938edde68d628b36ba404a7f331; HashInfercd7cc07. The old FlashInfer clone beside SGLang was not used for current frontend internals.

Normal SGLang integration constructs MoEEpTensors with hidden states, routing and scales, then calls MegaMoE forward. It supplies no output storage (python/sglang/srt/layers/moe/flashinfer_megamoe.py:650–664). Profile workspaces are likewise created with mega.create_workspace(capacity), not allocated directly by SGLang (flashinfer_megamoe_autotune.py:314–324).

Current FlashInfer allocations:
- Internal route partials combine_output: W4A16 frontend.py:838–841 calls sym_zeros; shim/comm.py:109 delegates to nvshmem.core.tensor. This is FlashInfer-owned symmetric storage.
- Final y: moe_ep/modes/mega_layer.py:425–430 calls torch.empty before staging, then passes output=y to the backend. W4A16 does not override the base supports_output_view=False, so this normal path allocates an owned output.
- W4 backend.compute at backend.py:312–323 passes y into bf16_nvfp4_mega_moe; W4 frontend.py:901–902 uses it as reduced_output when in_kernel_fc2_reduce=False. If the optional atomic path is selected, y receives a copy from internal result instead. Ownership is unchanged.

Therefore adding a256-bit combine path should not require SGLang to allocate/realign these buffers or learn an internal32-byte requirement. FlashInfer owns the responsibility to establish the alignment and communicate a truthful assumption to CuTe. This source audit establishes ownership, not a fresh measurement or proof of all allocator addresses.

The lower-level bf16_nvfp4_mega_moe(y, ...) API accepts caller-provided output. Its shape/dtype/CUDA/contiguity checks at frontend.py:879–882 do not check pointer32-byte alignment. A contiguous view may have a byte offset. The256-bit candidate must validate/select based on actual alignment, with a safe fallback for supported existing views. This general raw-caller case, not the ordinary SGLang path, motivated the earlier caution. Keep the existing128-bit implementation until a candidate is separately qualified.

Remote runtime introspection was attempted but the previous C2 pod devbox-fi-w4a16-trace-0925-0 was not found. No allocation was tested, and no devbox was created or released by this audit.
