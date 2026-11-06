# Epilogue scale codegen diagnostic — 2026-10-26

This is codegen/resource evidence, not timing or retention evidence. The unchanged public benchmark profiler ran with the saved current-control tactics on B300 GPU0. Each process appended only `--keep-ptx --keep-cubin` to the two bound core compilations and ran one profiling replay. NVFP4 included initial activation quantization. Every completed receipt verifies source and saved-cache immutability and successful native tactic lookup.

The common source parent is `0def601d6603df828ea39679b41ccbce64f7f09e`. Control core SHA256 is `bfcc8b0c1d673415f8cec598d6599717c91af85db29c7e9e8c14d9e2d73bf57e`; the candidate is `4a56dea9848b410bb1bae1e589728e06b44e06fca4c3ab7014964c2886806bbc`. The only candidate change moves invariant norm and per-tile expert alpha loads ahead of the accumulator wait. Sources, artifacts, full saved tactics, commands, cache hashes, and driver resources are in the adjacent receipts.

Cache reuse uses `prepare_workspace_cache.py` after verifying native source/header identity. CuTe object files use separate source-keyed namespaces under remote `cache/codegen-epilogue-prefetch-20261026`, while verified native artifacts are shared with the persistent control cache. No ongoing AUTO timing cache was written. The remote image/runtime is `nvcr.io/nvidia/pytorch:26.05-py3` / CUDA13.2; the emitted PTX compiler header identifies NVVM CUDA13.3, V13.3.27, PTX9.3 targeting `sm_103a`.

## NVFP4 results

Both public cases completed with exactly FC1 and FC2 captured. They use V4.1-Flash EP4 and saved route N32 at32 tokens, N128 at4096 tokens. Both cases select CLC for FC1 and static scheduling for FC2; all four kernels use dedicated epilogue warps.

| Tokens | Phase | Route N / MMA M | Registers control → candidate | Dynamic shared bytes | Local bytes / LDL / STL | Active CTAs per SM |
| ---: | --- | --- | --- | ---: | --- | ---: |
|32|FC1|32 /128|78 →78|197504|0 /0 /0|1|
|32|FC2|32 /128|92 →92|197504|0 /0 /0|1|
|4096|FC1|128 /256|80 →80|230272|0 /0 /0|1|
|4096|FC2|128 /256|112 →112|207232|0 /0 /0|1|

SMEM, registers, TMEM, operand/accumulator stage counts, thread counts, and driver occupancy are unchanged in each pair. Static SASS LDL/STL counts and driver local memory are zero.

Manual PTX dataflow and SASS control-flow inspection confirms that the compiler retained the requested movement:

| Case | Expert-alpha load and accumulator wait, control | Candidate | Invariant norm |
| --- | --- | --- | --- |
|NV32 FC1|PTX752 after wait740; SASS LDG `0x2460` after TRYWAIT `0x2360`|PTX736 before wait744; SASS LDG `0x23f0` before TRYWAIT `0x2400`|PTX748 →701; SASS `0x24d0` →`0x2220`, outside the tile backedge and before the initial CLC tile wait|
|NV32 FC2|PTX1053 after wait1045; SASS LDG `0x43e0` after TRYWAIT `0x4270`|PTX1037 before wait1048; SASS LDG `0x42b0` before TRYWAIT `0x42c0`|Not supplied to this output epilogue|
|NV4096 FC1|PTX848 after wait838; SASS LDG `0x2980` after TRYWAIT `0x28f0`|PTX834 before wait842; SASS LDG `0x2970` before TRYWAIT `0x2980`|PTX844 →788; SASS `0x2990` →`0x2760`, outside the tile backedge and before the initial CLC tile wait|
|NV4096 FC2|PTX1398 after wait1388; SASS LDG `0x5910` after TRYWAIT `0x5750`|PTX1379 before wait1391; SASS LDG `0x5750` before TRYWAIT `0x5770`|Not supplied to this output epilogue|

The NV32 FC1 alpha pointer comes from parameter8 (SASS constant offset `0x5b0`) and its value feeds the accumulator `FMUL2`; norm comes from parameter9 (`0x5b8`). At NV4096 FC1 those are parameters9/10 and offsets `0x630`/`0x638`. FC2 alpha provenance additionally includes the expert-index parameter because that value indexes the alpha array. The PTX indexes are only conservative provenance aids; the stated ordering was checked against the actual branch/loop paths and SASS. This demonstrates earlier issue, not a measured amount of latency overlap.

## MXFP8 results

Both cases completed with saved route N16 at32 tokens and N128 at4096 tokens, again using CLC FC1 and static FC2 with dedicated epilogue warps. MXFP8 does not provide the NVFP4 norm scalar, so this comparison exercises only the expert-alpha movement.

| Tokens | Phase | Route N / MMA M | Registers control → candidate | Dynamic shared bytes | Local bytes / LDL / STL | Active CTAs per SM |
| ---: | --- | --- | --- | ---: | --- | ---: |
|32|FC1|16 /128|78 →75|216064|0 /0 /0|1|
|32|FC2|16 /128|90 →90|215936|0 /0 /0|1|
|4096|FC1|128 /256|82 →82|205696|0 /0 /0|1|
|4096|FC2|128 /256|110 →110|188800|0 /0 /0|1|

Only MXFP8 token32 FC1 register allocation changes (78 →75). Geometry, shared memory, TMEM, pipeline stages, thread count and occupancy remain equal. All16 captured kernel artifacts across both families have zero local memory and zero SASS LDL/STL sites.

| Case | Expert-alpha load and accumulator wait, control | Candidate |
| --- | --- | --- |
|MX32 FC1|PTX930 after wait919; SASS LDG `0x2bc0` after TRYWAIT `0x2b10`|PTX919 before wait927; SASS LDG `0x2b80` before TRYWAIT `0x2b90`|
|MX32 FC2|PTX854 after wait846; SASS LDG `0x2b50` after TRYWAIT `0x29d0`|PTX837 before wait849; SASS LDG `0x29f0` before TRYWAIT `0x2a00`|
|MX4096 FC1|PTX855 after wait846; SASS LDG `0x2a10` after TRYWAIT `0x2950`|PTX841 before wait849; SASS LDG `0x29b0` before TRYWAIT `0x29c0`|
|MX4096 FC2|PTX746 after wait736; SASS LDG `0x2840` after TRYWAIT `0x2680`|PTX727 before wait739; SASS LDG `0x2680` before TRYWAIT `0x26a0`|

The load address uses the alpha pointer plus the known expert index; its result feeds the epilogue accumulator multiplications. Both PTX branch paths and their actual SASS issue order show the requested movement. No norm load exists in either MXFP8 kernel.

## Scope boundary

All8 public profiling processes completed, covering16 core kernel artifacts. No claim is made for untaken tactics or the inline epilogue role. The selected cases cover both one-CTA and two-CTA MMA and small/large routed widths without forcing a tactic. Functional checks and final AUTO retention decisions are handled separately by the parent campaign.
