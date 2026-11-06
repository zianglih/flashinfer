# W4A16 full-tile TMA / partial-tile SIMT experiment

Source: independent `flashinfer-w4a16-hybrid-output-review` clone. Paired control: immutable padded-output R2 candidate; W4A16 there matches retained HEAD `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`. Freeze verifies that the only source change from R2 is `moe_w4a16_kernel.py`.

Capacity: existing `fi-moe-descriptor-recover-1028`, C3/ziangli, eight B300 GPUs, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2. No new capacity request. Initial inventory verifies348 R2 source files and all9 persistent native compilation-cache links.

Fresh source-paired C-A-A-C timing, same GPU for each control/candidate pair, strict CUPTI,100samples,10warmups, cold-L2 CUDA graphs, frozen saved winners, no AUTO. Public functional benchmark API, swap-AB enabled, fused finalize disabled. Preserve NVFP4-family include-input-quantization flag; W4A16 backend behavior remains unchanged.

Workloads: V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8, tokens4/64/4096/16384. Only W4A16 is measured:32cells. Start with TP V3 T64/T16384 on GPU0 after first correctness pass; reuse those two valid cells and collect the remaining30. Descriptor04 values may appear as historical context only.

Validation initially reserves GPUs1–3. Remaining screen assigns TP models to GPUs0–3 and EP models to GPUs4–7. Every launch requires a fresh idle check and recorded UUID. No sanitizer, PR changes, commits or pushes.
