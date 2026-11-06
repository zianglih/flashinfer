# a65d5b09 versus13ca1475: native NVFP4 source audit

Baseline source is read with `git show a65d5b09:<path>`. Current snapshot is frozen13ca1475, regardless of later local production commits. No production mutations.

- B: `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py` at a65d5b09.
- C: `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py` at13ca1475.

Baseline already directly gathers original token rows. Payload is activations-A/token-M via16-byte `cp.async.cg` copies (B1701–1725,1890–1926), activation SFA via4-byte `cp.async` (B1929–1967), and weight B/SFB via regular TMA. Current weights-A/channel-M and activations-B/token-N uses Gather4 (four128-byte rows per instruction, C70–102), activation SFB via4-byte cp.async (C948–950), and weight A/SFA via regular TMA. Both avoid a routed-input GMEM payload intermediate.

Both native inputs use packed token/K-contiguous payload and linear token×K/16 activation SF. Baseline benchmark420–423 quantizes with unswizzled SF; B4030–4038 creates those views. Current C467–482 retains original source rows, C1021–1026 maps routing to original tokens, and C1037–1045 uses linear SF. Weight SF remains MMA-swizzled; baseline benchmark453–456 and B908–911, current C623–634. Weight gate/up interleave differs: baseline benchmark451 uses group64; current prepare.py2495–2499 uses group16 for Blackwell. Keep revision-specific native preparation.

SF ownership moves with operands. Current C299–305 keeps full-N SFB in each CTA even though group-2 B payload holds half-N. Baseline SFA follows each CTA's distinct128 token-M rows (B673–677,1817–1838). Source-derived nominal per-CTA activation payload/SF bytes for NVFP4 K256:

| Geometry | Payload bytes | Activation SF bytes |
|---|---:|---:|
|Old token-M256/channel-N256|16384|2048|
|Current channel-M256/token-N256|16384|4096|
|Current logical channel-M512/token-N128|8192|2048|

The last row reuses B/SFB across two physical M256 channel tiles. These are issued useful-copy volumes, not measured HBM bytes.

Old uses12warps: epilogue0–3, activation/SFA4–7, MMA8, weight TMA9, scheduler10, relay11 (B510–530). Activation and weight producers have independent pipelines (B1317–1366); relay11 waits local cp.async and publishes cluster readiness (B2047–2054). Current uses9warps: combined producer0–3 (warp0 also weight TMA), epilogue4–7, MMA/relay8 (C948–958,1056–1099,1209–1260,1323–1331). Current grid-stride scheduling is duplicated by each role.

Current NVFP4 logical M512/N128 has K256, four operand stages, doubled A/SFA slots, and one compound accumulator stage/twoN128 banks. Physical M256/N128 uses K512/3stages; M256/N256 uses K256/5stages. Baseline stage count is capacity-derived (B3494–3565); expected fixed256×256 uses five stages, one accumulator stage, and two tile-info stages. Verify compiled resource usage in NCU before treating this expected count as observed.

## Current13ca FC1 SASS barrier map

Shared-storage source declares A/TMA barriers first (64bytes), then SF cp.async barriers (64bytes), accumulator barriers (16bytes), and relay barriers. Full barriers occupy each pipeline's first half, empty barriers its second. For NVFP4 M512/N1284stage specialization, SASS offsets relative to shared base are:

| Offset | Meaning |
|---|---|
|0x00|MMA TMA-full wait|
|0x20|producer TMA-empty acquire|
|0x40|MMA SF-full wait|
|0x60|producer SF-ring-empty acquire|
|0x80|epilogue accumulator-full wait|
|0x88|MMA accumulator-empty acquire|
|0x90|MMA peer-relay-full wait|
|0xb0|MMA relay-empty acquire|

Current16K-r2 source-sampling hotspots: producer-empty+0x60 initial branch3420 not-issued samples; epilogue acc-full+0x80 initial branch1558 and sleep2905; MMA SF-full+0x40 branch486; relay-full+0x90 branch29; TMA-full+0x00 branch29; accumulator-empty+0x88 branch93. These source PCs establish where sampled stalls wait, not the causal duration of independent producer/consumer stages. Long-scoreboard labeling on mbarrier predicate consumers must not be equated with payload-load misses. Correlate retained iKET timings before selecting pipeline changes.
