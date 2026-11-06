# Current-best W4A16 profiles — 056ce / 0909d

Downloaded **10/10 reports**: two Nsight Systems captures and eight Nsight Compute rank reports.

Published commit `056ce0d090d425ee09171e47f6faea61c76c9551`; exact captured source `af938d808556e72925933208f0844cd92f44dff5cc7f407b050897c5660b2e9e`. The source was restored after the unpromoted K128/B6 trial. These reports profile the retained eight-tactic implementation.

| Capture | Report | Bytes | SHA256 |
|---|---|---:|---|
| NSYS T32 | [ep_w4a16_megamoe_t32.nsys-rep](../current-best-0909d-nsys-t32-001/ep_w4a16_megamoe_t32.nsys-rep) | 1,621,664 | `0d154e31b42b825835a3783276d49d95d0c418889ef9f71daef1b7aa366a9ea2` |
| NSYS T4096 | [ep_w4a16_megamoe_t4096.nsys-rep](../current-best-0909d-nsys-t4096-001/ep_w4a16_megamoe_t4096.nsys-rep) | 1,621,647 | `c6679fff0ee36ae37e5a106fb524f73d38e5aa5c84646833d8e40e579a8f311d` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank0.ncu-rep](../current-best-0909d-ncu-t4096-001/ep_w4a16_megamoe_t4096.rank0.ncu-rep) | 1,986,249 | `e40fecb61984a4ce0127e48b5fff9ab5a4e32d2aa4ac7e243c10186d050a6d72` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank1.ncu-rep](../current-best-0909d-ncu-t4096-001/ep_w4a16_megamoe_t4096.rank1.ncu-rep) | 1,221,725 | `3df6bd6e4ae318ea61f1e106cfc2632980fbd559f430cd2cbb57f62eab521955` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank2.ncu-rep](../current-best-0909d-ncu-t4096-001/ep_w4a16_megamoe_t4096.rank2.ncu-rep) | 1,952,617 | `e4714cd0720abfa74795f4025ae4944e58cf07d60e79d85687f6a7a6e3911078` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank3.ncu-rep](../current-best-0909d-ncu-t4096-001/ep_w4a16_megamoe_t4096.rank3.ncu-rep) | 1,938,828 | `79378c14e6c15fb685c81a93aedc513e4043374c7ac942066e9b45af7b6adb4b` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank4.ncu-rep](../current-best-0909d-ncu-t4096-001/ep_w4a16_megamoe_t4096.rank4.ncu-rep) | 1,976,745 | `ed2614ac8e21ba59524ae09d2cf0ca8294a1dad61ef19b2dff1a95f6109af4af` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank5.ncu-rep](../current-best-0909d-ncu-t4096-001/ep_w4a16_megamoe_t4096.rank5.ncu-rep) | 1,969,420 | `3935f9c87f2ddc798f3203dc176e548baa3d88a70e024bc4df12f7f38a2de59b` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank6.ncu-rep](../current-best-0909d-ncu-t4096-001/ep_w4a16_megamoe_t4096.rank6.ncu-rep) | 1,223,304 | `a1019250cf8e2c1eb493855aff2bcd0984ee72050eeef2c0a2df20c62146166c` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank7.ncu-rep](../current-best-0909d-ncu-t4096-001/ep_w4a16_megamoe_t4096.rank7.ncu-rep) | 1,950,505 | `6ddc6b513ec3d5c9f449d04b6ef66528de5d35d9913743c0e4fad1fc81c03626` |

The adjacent capture folders include original commands, logs, source manifests, preflight, hardware UUIDs, tool versions, timestamps and closed execution/download receipts. NSYS SQLite exports and kernel CSV summaries are included. [manifest.json](manifest.json) and [SHA256SUMS](SHA256SUMS) cover the downloaded files and supporting metadata.

## Capture setup

Container `nvcr.io/nvidia/pytorch:26.05-py3`; eight NVIDIA B300 SXM6 GPUs, driver 590.48.01; PyTorch 2.12.0a0+5aff3928d8.nv26.05 with CUDA 13.2; system nvcc 13.2.78. CUTLASS DSL 4.7.1 reports its separate CUDA 13.3 backend. Nsight Systems 2026.2.1.210; Nsight Compute 2026.1.1.0.

Both shapes use EP8, BF16 activations/NVFP4 weights, H7168/I2048, E256, top-k8, M256/K256/C2/S2/F4, atomic-counter scheduling and group_hint=512. T32 uses N64/epi_warps; T4096 uses N128/reuse_dispatch_warps. These exact dictionaries come from the completed retained AUTO run `1a763323d8f36f670ac2213f3580236a884a0fb033fe799ce21cfb31ec4575da`. Full dictionaries and original shell commands are in [metadata/binding.json](metadata/binding.json) and the capture folders. The binding's original `bound_not_launched` status is preserved; capture completion is established by each completion.json.

NSYS records two eager calls per rank after three warmups, with cuda-sw tracing. NCU requests one profiled Mega call per rank, application replay and PC-sampling sample-count/warp-stall-reason metrics; it targets Sm100W4A16MegaMoEKernel. The saved NCU log confirms eight Mega profiling entries, one application replay pass per communicator rank. The report filename suffix comes from NCU's `%q{RANK}` macro and names the torchrun distributed rank. NCU communicator peer IDs are a separate numbering scheme; their mapping is preserved in manifest.json and ncu.log. Per-report CUDA device metadata, when inspected, is the direct device identifier. No separate NCU action/source export was supplied; raw reports remain available for inspection.

## Reading the timing

These instrumented eager calls show substantial inter-rank launch skew. Their kernel durations, whole-device spans and aggregate CSV GPU time are **not** the AUTO cold-L2, per-iteration rank-MAX latency and do not replace the published timing table. Each NSYS trace contains exactly 2×8 Mega kernels, with 96 registers/thread, 640 threads/block and zero local memory.

| Tokens | Eager call | Across-device start skew (µs) | First start to last end (µs) | Shortest rank kernel (µs) |
|---:|---:|---:|---:|---:|
| 32 | 1 | 909.747 | 1064.084 | 154.337 |
| 32 | 2 | 716.643 | 870.201 | 153.345 |
| 4096 | 1 | 1110.277 | 1540.957 | 430.531 |
| 4096 | 2 | 199.200 | 637.008 | 437.316 |

These saved observations join CUPTI_ACTIVITY_KIND_KERNEL.demangledName to StringIds, filter Sm100W4A16MegaMoEKernel, then pair calls by per-device start order. Raw rows and arithmetic are in [nsys-observations.json](nsys-observations.json).

## Source mapping

Open the .nsys-rep files in Nsight Systems and the .ncu-rep files in Nsight Compute. For source lookup, check out commit 056ce0d090d425ee09171e47f6faea61c76c9551 and map the captured repository prefix `/workspace/flashinfer-w4a16-megamoe/flashinfer/` to that checkout. The main Mega class is in `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/kernel.py`; shared decode/MMA routines are in `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`. Per-capture source-manifest.json records exact hashes. The included publication association confirms all 1,575 measured source files match that commit; remote Git HEAD is not used as a source identity. Driver/DSL compilation caches are deliberately omitted, so generated/cache paths may require source-prefix mapping or the recorded DSL installation.

## Verification and reproduction

All indexed captures have passed completion receipts and closed original/download sessions. Local report sizes, SHA256 hashes and file headers were checked against the receipts; the NSYS SQLite exports were read without modifying them. No profiler or benchmark was rerun for packaging. The final [source/native/idle closure](../current-best-0909d-closure-001/closure.json) confirms the exact retained source, unchanged native inventory and no remaining GPU compute processes. Use SHA256SUMS from the project root (or archive root) to verify the included paths.
