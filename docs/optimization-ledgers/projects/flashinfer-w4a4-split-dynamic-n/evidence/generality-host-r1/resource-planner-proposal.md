# Static resource planning proposal

This is a candidate design, not a retained policy or performance result. All bytes below come from the actual installed CuTe4.7.1 layouts and extracted SharedStorage; the census launches no GPU kernels.

## Shared helper boundary

- A pure core planning helper owns operand-stage bytes, metadata reservation, scratch reservation, accumulator columns, and scale columns. Both launchers request direct behavior (dedicated epilogue, automatic K, automatic accumulator overlap) rather than repeat M/N/dtype tables. Existing explicit K/depth overrides remain for diagnostics.
- The constructor can resolve K before descriptor/tensor creation using a formula cross-checked against all480 SDK layouts. The compiled wrapper must still assert actual layout/storage equals the plan, preventing drift when layouts change.
- Prefer the largest supported K that retains at least two producer/consumer operand stages and preserves the available early-release accumulator window. Two is a proposed pipeline policy, not a hardware limit; benchmark it.
- Derive accumulator stages as min(2, floor((512 - scale_cols)/acc_cols)) for dedicated epilogues, otherwise1. This exactly reproduces all480 current stage selections without the N<=128/channel_tiles branches. The maximum2 represents the existing two-window design.
- The existing64-column release limit belongs to the actual bulk/activation epilogue protocol. Name/return that supported release extent from the epilogue instead of duplicating a literal in each host. Do not substitute TMEM capacity alone for lifetime safety.
- Dedicated epilogue is feasible for all current geometries; resource fit cannot prove it is profitable. Applying it uniformly changes FC1 M128 N128/N256 from inline to dedicated and requires measured validation.

## Quantified selections

| Format | M,N | FC1 Ksteps/stages | FC2 Ksteps/stages |
|---|---|---:|---:|
| fp4_e8_sf16 | 128,16 | 8/4 | 8/4 |
| fp4_e8_sf16 | 128,32 | 8/4 | 8/4 |
| fp4_e8_sf16 | 128,64 | 8/4 | 8/4 |
| fp4_e8_sf16 | 128,128 | 8/3 | 8/2 |
| fp4_e8_sf16 | 128,256 | 4/4 | 4/3 |
| fp4_e8_sf16 | 256,128 | 8/4 | 8/3 |
| fp4_e8_sf16 | 256,256 | 4/5 | 4/5 |
| fp4_e8_sf16 | 512,128 | 4/4 | not admitted |
| mxfp4 | 128,16 | 8/5 | 8/5 |
| mxfp4 | 128,32 | 8/5 | 8/5 |
| mxfp4 | 128,64 | 8/4 | 8/4 |
| mxfp4 | 128,128 | 8/3 | 8/2 |
| mxfp4 | 128,256 | 8/2 | 4/3 |
| mxfp4 | 256,128 | 8/4 | 8/3 |
| mxfp4 | 256,256 | 8/3 | 8/2 |
| mxfp4 | 512,128 | 8/2 | not admitted |
| mxfp4x8 | 128,16 | 8/5 | 8/5 |
| mxfp4x8 | 128,32 | 8/5 | 8/5 |
| mxfp4x8 | 128,64 | 8/4 | 8/4 |
| mxfp4x8 | 128,128 | 8/3 | 8/2 |
| mxfp4x8 | 128,256 | 8/2 | 4/3 |
| mxfp4x8 | 256,128 | 8/4 | 8/3 |
| mxfp4x8 | 256,256 | 8/3 | 8/2 |
| mxfp4x8 | 512,128 | 8/2 | not admitted |
| mxfp8_e4 | 128,16 | 8/5 | 8/5 |
| mxfp8_e4 | 128,32 | 8/5 | 8/5 |
| mxfp8_e4 | 128,64 | 8/4 | 8/4 |
| mxfp8_e4 | 128,128 | 8/3 | 8/2 |
| mxfp8_e4 | 128,256 | 8/2 | 4/3 |
| mxfp8_e4 | 256,128 | 8/4 | 8/3 |
| mxfp8_e4 | 256,256 | 8/3 | 8/2 |
| mxfp8_e4 | 512,128 | 8/2 | not admitted |
| mxfp8_e5 | 128,16 | 8/5 | 8/5 |
| mxfp8_e5 | 128,32 | 8/5 | 8/5 |
| mxfp8_e5 | 128,64 | 8/4 | 8/4 |
| mxfp8_e5 | 128,128 | 8/3 | 8/2 |
| mxfp8_e5 | 128,256 | 8/2 | 4/3 |
| mxfp8_e5 | 256,128 | 8/4 | 8/3 |
| mxfp8_e5 | 256,256 | 8/3 | 8/2 |
| mxfp8_e5 | 512,128 | 8/2 | not admitted |
| nvfp4 | 128,16 | 8/4 | 8/4 |
| nvfp4 | 128,32 | 8/4 | 8/4 |
| nvfp4 | 128,64 | 8/4 | 8/4 |
| nvfp4 | 128,128 | 8/3 | 8/2 |
| nvfp4 | 128,256 | 4/4 | 4/3 |
| nvfp4 | 256,128 | 8/4 | 8/3 |
| nvfp4 | 256,256 | 4/5 | 4/5 |
| nvfp4 | 512,128 | 4/4 | not admitted |

## Narrow two-CTA admission

CUDA13.2 PTX9.2 table9.7.16.1 admits cta_group::2 dense M128/M256 with N16..256 step16 for the three block-scaled kinds. Installed CuTe4.7.1 successfully creates all18 operand/scale layouts (six formats × N16/32/64) with M256 and physicalN=max(32,logicalN). The current N>=128 restriction is an implementation admission. Full kernel address/ownership, epilogue release, and persistent/zero-route exact gates are still needed before adding tactics.

Reference: https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#tcgen05-mma-instructions

The current static two-CTA producer already computes CTA B offsets from dynamic validN/2; dynamic N16 occurs for sparse N128 tiles today. Small-N additions mainly need canonical-SFB cp.async publication and per-CTA physical B-prefix/descriptor verification, rather than a different MMA instruction. This is a source-traced hypothesis pending full codegen/exact proof.
