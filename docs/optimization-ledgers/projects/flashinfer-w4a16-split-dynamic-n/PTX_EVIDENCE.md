# Runtime N PTX evidence

Candidate: `9ec90d0696752c72ff826c8880e58515ace84e60`. Inspected the actual retained PTX from the M128/N64/one-CTA and M256/N192/two-CTA grouped-GEMM tests, using CuTe DSL 4.7.1 on the recorded B300 environment. Both source paths were clean at this revision. These are two shape samples; GPU correctness coverage is recorded separately in `VALIDATION_SECTION.md`.

PR-ready paragraph:

> **Generated-code check:** retained PTX for M128/N64 and M256/N192 traces the live route-boundary load through shared tile metadata into the register used as the instruction descriptor by every `tcgen05.mma.cta_group::{1,2}.kind::f16` atom. The descriptor N field is `align8(clamp(valid,1,64))/8` for one CTA and `align16(clamp(valid,1,192))/8` for two CTAs. The two-CTA activation TMA coordinate uses the matching `align16(valid)/2 - 192/2` peer shift. Both artifacts report CUDA compilation tools **13.3.27**, based on **NVVM 23.0.0**, PTX **9.3**, target **sm_103a**; this compiler receipt is distinct from system CUDA/nvcc **13.2.78** and the installed compiler/NVVM package version **13.3.73**.

Artifact SHA-256 (files are preserved under the following directories; each has one `.ptx`):

| Artifact | SHA-256 |
|---|---|
| `ptx/cta-group-1/cutlass_wrapper_flashinferfused_moecute_dslblackwellmoe_w4a16_kernelSm100W4A16GroupedGemmKernel_object_at__Ptrgmem_Ptrgmem_Ptrgmem_Ptrgmem_Ptrgmem_Ptrgmem_Ptrgmem_Ptrgmem_None_None.sm_103a.ptx` | `b6b7449a8cb4e7f5aac82cbde65d2838ccd006bd8270ff2e4c1405d2b6967c88` |
| `ptx/cta-group-2/cutlass_wrapper_flashinferfused_moecute_dslblackwellmoe_w4a16_kernelSm100W4A16GroupedGemmKernel_object_at__Ptrgmem_Ptrgmem_Ptrgmem_Ptrgmem_Ptrgmem_Ptrgmem_Ptrgmem_Ptrgmem_None_None.sm_103a.ptx` | `710c3e17b6f975081295e1355085a212c7c2eea2efc2b559059b0b225e9f3dab` |

Both PTX headers, lines 4–10:

```text
// Compiler Build ID: CL-37800683
// Cuda compilation tools, release 13.3, V13.3.27
// Based on NVVM 23.0.0

.version 9.3
.target sm_103a
```

One CTA, M128 with allocated N64:

- PTX line 57 loads the `tile_idx_to_mn_limit` pointer from kernel parameter 12 into `%rd43`. Lines 245–251 compute `route_start = route_tile_idx * 64`, load the live route limit from global memory, and subtract the start into `%r891`. Line 259 writes this as the fourth field of the shared tile record. This matches the kernel signature and scheduler stores at `moe_w4a16_kernel.py:931` and `:1378–1392`.
- Lines 1443 and 1829 load/reload that fourth field into `%r916` for each persistent work tile. Lines 1489–1494 clamp it, round it to N8 granularity, and insert N/8 into the descriptor; this calculation is outside the K-tile loop.
- All 16 K16 MMA atoms in the K256 loop use the same runtime `%r506`, at lines 1543–1768. Descriptor base `134218896 = 0x08000490` specifies M128, BF16 A/B and FP32 accumulation.

```ptx
// 1443: fourth field is the live routed-token count for this tile.
ld.shared.v4.b32 {%r433, %r434, %r435, %r916}, [%r1];
// 1489–1494: ((align8(clamp(valid, 1, 64)) / 8) << 17) | 0x08000490
max.s32 %r444, %r916, 1;
min.s32 %r445, %r444, 64;
shl.b32 %r446, %r445, 14;
add.s32 %r447, %r446, 114688;
and.b32 %r448, %r447, 4063232;
or.b32 %r506, %r448, 134218896;
// 1543: descriptor is a register derived from live metadata.
tcgen05.mma.cta_group::1.kind::f16 [%r504], [%r459], %rd141, %r506, p;
```

Two CTAs, M256 with allocated N192:

- PTX line 57 loads the `tile_idx_to_mn_limit` pointer from kernel parameter 12 into `%rd44`. Lines 283–289 compute `route_start = route_tile_idx * 192`, load the live global route limit, and subtract the start into `%r915`. Line 299 writes it as the fourth shared tile field.
- Lines 1471 and 1854 load/reload the fourth field into `%r940`. Lines 1517–1522 produce the runtime N16-rounded descriptor `%r542` outside the K-tile loop.
- All 16 K16 MMA atoms use `%r542` at lines 1570–1795. Descriptor base `268436624 = 0x10000490` specifies M256, BF16 A/B and FP32 accumulation.

```ptx
// 1471: same live routed-token field.
ld.shared.v4.b32 {%r469, %r470, %r471, %r940}, [%r1];
// 1517–1522: ((align16(clamp(valid, 1, 192)) / 8) << 17) | 0x10000490
max.s32 %r481, %r940, 1;
min.s32 %r482, %r481, 192;
shl.b32 %r483, %r482, 14;
add.s32 %r484, %r483, 245760;
and.b32 %r485, %r484, 8126464;
or.b32 %r542, %r485, 268436624;
// 1570
tcgen05.mma.cta_group::2.kind::f16 [%r540], [%r495], %rd145, %r542, p;
```

The two-CTA B-loader independently reads the same fourth shared field as `%r918` at line 375. Lines 394–400 clamp to [1,192], compute `(valid+15)>>1 & 248`, subtract 96, and select zero shift for the leader. This is `align16(valid)/2 - 192/2` on the non-leader. Lines 401–402 add it to the original token coordinate in `%r23`; the activation TMA consumes `%r23` at lines 438, 447, 456 and 465.

```ptx
// 393–402; %r4 == 0 identifies the leader.
setp.eq.b32 %p64, %r4, 0;
max.s32 %r174, %r918, 1;
min.s32 %r175, %r174, 192;
add.s32 %r176, %r175, 15;
shr.u32 %r177, %r176, 1;
and.b32 %r178, %r177, 248;
add.s32 %r179, %r178, -96;
selp.b32 %r180, 0, %r179, %p64;
add.s32 %r181, %r919, %r22;
add.s32 %r23, %r181, %r180;
```

The descriptor arithmetic was also checked numerically against its stated rounding formula for every valid count in each tile capacity, including the zero-count private-test fallback; all values matched. The PTX has 16 MMA issue sites per shape, with no alternate constant descriptor MMA issue sites.

Capture receipt:

- Initial dump request passed its two tests but had no precreated dump directory and retained no PTX. The split launcher uses plain `cute.compile` and only process-local `_kernel_cache`; installed DSL `compiler.py:1515` forces `no_cache=True`, while `dsl.py:2855–2859` independently disables caching for retained PTX. A persistent FlashInfer cache hit is not the supported explanation.
- The successful retry precreated the absolute dump directory and a fresh isolated DSL cache directory, used `CUTE_DSL_KEEP=ptx`, `CUTE_DSL_NO_CACHE=1`, `CUTE_DSL_DISABLE_FILE_CACHING=1`, `CUTE_DSL_DUMP_DIR` and `CUTE_DSL_CACHE_DIR`. Existing benchmark caches were not modified. The two cases passed: `2 passed, 70 warnings in 4.61s` (`logs/dynamic-n-ptx-confirmed.log`).
- Both shapes use the same mangled dump filename, so the second case overwrote the first in that directory. The two-CTA artifact was preserved in `ptx/cta-group-2`; the one-CTA case was rerun into its own precreated `ptx/cta-group-1` directory: `1 passed, 37 warnings in 3.61s` (`logs/dynamic-n-ptx-one-cta.log`). Future captures must use a separate dump directory per shape. These repeat existing tests, not additional independent correctness cases.
