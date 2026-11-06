# Direct FC1 SF publication, frozen442d

Isolated prototype; both arms are closed and rejected after bounded NV testing. Baseline commit`442d2aa53f68b4640c3ab5118a76f1599ff60d34`; no production changes. GPU5 on replacement C1`fi-w4a4-pipeline-1025` was released after bootstrap and all-three-format native prewarm. Source hashes are recorded in`manifest.json`; `build_snapshot.py` reads Git objects at442d and does not depend on the mutable checkout.

## Hypothesis and prior rejection

FC1 currently uses per-row4-byte `cp.async` fragments into canonical SFB shared memory, waits for CTA-local completion on both MMA warps, then relays completion to the group2 leader. The new arm converts every FC1 SF transfer to an ordinary register load/shared store and publishes directly to the leader with`PipelineAsyncUmma`. Payload order, stage count, allocation, SF layout, SF arithmetic, MMA issue/release, epilogue, and public shape/alignment contracts remain unchanged. FC2 retains442d behavior.

This is deliberately a direct-publication experiment. `../sfload_experiment/README.md` already rejected synchronous128-bit SF loads with the old local-completion/relay path: balanced16K,N128 baseline281.472us versus496.641us, or354.113us with prefetch before stage acquisition. Those tests predate the current Gather4/NB2 composition, but demonstrate the cost of losing asynchronous overlap. `../sfasync_experiment/README.md` also rejected scratch-based asynchronous vectorization and2/3/5-slot producer prefetch. Neither extra scratch nor extra stages are introduced here. No speedup is assumed from fewer global-load instructions.

## Legal raw-word copies across all formats

The byte width is the largest of16,8,4 that divides both compile-time row stride`K/SFvec` and stage extent`tileK/SFvec`. K already specializes the host/JIT cache. No new runtime argument, public alignment restriction, dtype fallback, or runtime loader switch is added.

Examples:

| Operand/stage | SF bytes per row/stage | Width when row stride permits |
| :--- | ---: | ---: |
| FP4,K256,SF16 |16|16|
| FP4,K256,SF32 |8|8|
| FP8/mixed,K128,SF32 |4|4|
| Wide FP8/mixed,K256,SF32 |8|8|
| FP4,K512,SF16 |32|16, twice|

Short K and non-16-byte row strides statically select4/8 bytes. For example,K64/SF16 selects4 bytes andK384/SF16 selects8. Because the vector width divides the complete row extent and stage extent, a tail vector is entirely in-bounds or entirely zero-filled. Invalid rows are zero-filled. Raw Uint32 words preserve all SF encodings.

Each lane keeps only the current vector (1–4 Uint32 values) before scattering each word to its existing512-byte-spaced SF block. The retained row permutation is`row=8*warp+32*(lane//8)+lane%8`. For each32-bit store, bank`(4*(row%32)+row//32)%32` equals`4*(lane%8)+lane//8`, a permutation of all32 banks. This needs no new shared storage or data reformatting. Register pressure and actual LDG width require CUBIN/SASS verification; the CPU audit does not establish them.

## Publication and ownership proof

Every one of128 SF writers per CTA executes:

1. Acquire the local empty stage.
2. Synchronous global-to-register load and shared stores (including tail zeros).
3. `fence_proxy("async.shared", space="cta")` after its stores.
4. Unconditional`producer_commit` once per stage.

`PipelineAsyncUmma` uses the supplied count directly:128 for group1 and256 for group2. All producer full arrivals target the group2 leader; leader UMMA release signals both CTAs' empty barriers. Therefore the replacement full wait is leader-only. Keeping the old both-CTA wait would deadlock the peer. The leader still releases SF storage only after all MMAs reading that stage, including NB2. Each CTA keeps the producer tail. Old cp.async/relay code compiles out for FC1; existing relay allocation is retained unchanged to isolate the mechanism. Marker names`producer_sf_issue`,`producer_sf_commit`,`mma_sf_ready` remain meaningful; old relay markers are inactive on this arm.

W4A16 precedent in`/Users/ziangli/playground/projects/flashinfer-w4a16/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`:

-535–547: transformed registers→SMEM, each-writer proxy fence, direct producer commit.
-914–923: expected arrivals explicitly multiply by`cta_v_size`.
-1683–1724: leader-only full wait, GEMM, empty release.

CUTLASS source under that checkout's`3rdparty/cutlass/python/CuTeDSL/cutlass`: `pipeline/sm100.py:403–422` passes the count directly;443–450 routes full arrivals to the leader and empty releases across both CTAs;473–477 emits UMMA release. `pipeline/helpers.py:172` uses cooperative-group size;251–283 provides per-thread ordinary arrivals. [PTX mbarrier specification](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier) permits256 expected arrivals.

## CPU evidence and proposed GPU gate (historical plan)

```bash
python3 scripts/fc1_sf_register_experiment/build_snapshot.py
python3 scripts/fc1_sf_register_experiment/check_source.py
```

Checks pass576 K/vector combinations throughK8192, the full128-row/32-bank mapping, per-writer fence/arrival placement, group2 expected count, leader-only wait, unchanged shared allocation, and unchanged S2T/MMA/release. They parse sources without importing CUDA. The executed NV checks and codegen evidence are summarized below; the broader proposed matrix was not launched.

After parent release, synchronize this folder only and run a bounded one-case smoke on assigned GPU5 with`SFREG_GPU_RELEASED=1`,`CUTE_DSL_KEEP_PTX=1`,`CUTE_DSL_KEEP_CUBIN=1`. The first default case is shortK64 NVFP4, logicalM512/N128,twoCTA. Inspect SASS for legal load widths, zero local spills, direct cluster-arrival count256, absence of FC1 LDGSTS/relay waits, and unchanged SMEM footprint. Then use the paired probes:

```bash
SFREG_GPU_RELEASED=1 ../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_paired.py --limit 1
SFREG_GPU_RELEASED=1 ../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_paired.py
SFREG_GPU_RELEASED=1 SFREG_M=256 SFREG_N=128,256 ../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_paired.py
SFREG_GPU_RELEASED=1 SFREG_M=128 SFREG_CTA=1 SFREG_N=16,64,128,256 SFREG_PDL=1 ../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_paired.py
SFREG_GPU_RELEASED=1 ../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_paired.py --script probe_fc2.py
```

Default FC1 probe: six formats×three K extents(short,384,512)×quantized/per-token output=36 paired cases per geometry. Source SF allocation has an extra poison row so over-wide reads at the final real row can be detected; output/SF padding starts identically and all bytes are compared. The unchanged FC2 control contributes24 cases. Native timing should initially use current442d N128/NB2 actual-routing NVFP4 at8K/16K, then MXFP8/mixed only if exact and promising. Repeat adjacent ordering, preserve full samples, use10 warmups/100 cold-L2 graph/CUPTI samples with fallback fatal, and record FC2 as an unchanged drift control. No primary benchmark or source integration is authorized by this CPU preparation.

## Initial direct arm and bounded overlap follow-up

The direct arm passes8 NV pairs (K64/384/512/7168, per-token/quantized), plus the first short-K smoke. Forward/reverse native8K/16K are bitwise exact. It trades about2% full-chain improvement at16K for2.3–2.6% regression at8K; no retention or all-format expansion follows from that tradeoff. Initial raw evidence is safely local in`../../evidence/fc1-sf-register-442d2aa5/`, archive SHA256`b61c32403cbbe1dff06bb6e5795c7c6c4a7b23c1ab4f437fa372a13e8a1555dd`.

Parent authorized one bounded follow-up: `split_core.py` loads current-stage SF words before Gather4 and stores them afterward, then uses the same per-writer fence/direct publication. The existing stage's SF register tensor lives across Gather4 (four words/lane for nativeNVNB2); there is no extra payload/shared stage or geometry exception. `producer_sf_issue` covers the register fetch; new`producer_sf_store` covers the delayed scatter. Publication and all subsequent code are byte-identical to the direct arm. `build_split.py` checks that ordering and records both module hashes in`split-manifest.json`. Run with`--variants baseline,split` for exact probes and`--candidate split` for the native runner. Only NV8K/16K is authorized before a repeatable gain; no T-specific branch is permitted to hide the8K regression.

## Final disposition: both arms rejected

Both direct and split arms passed eight NV pairs each plus one short-K smoke, then both native timing orders. Each arm covers K64/384/512/7168 with quantized and per-token BF16 output, route/channel/K tails, and a poisoned SF guard row. All native output comparisons are byte-exact. The complete experiment contains24 native arms and72 arrays of100 cold-L2 graph/CUPTI samples. No SF32/all-six-format matrix, sanitizer run, NCU run, primary benchmark, or production integration followed this rejection.

Using the mean of adjacent same-arm medians, direct regresses full chain at8K by2.30%/2.60% (forward/reverse) while improving16K by1.41%/2.13%. Split regresses8K by2.03%/2.28%, while improving16K by1.41%/2.46%. A token-count-specific policy was explicitly excluded. Neither arm provides a uniform improvement.

Codegen is consistent with the intended static16/8/4-byte selection, zero spills, and removed relay: native NV quantized FC1 remains80 registers/thread, per-token remains111. LDGSTS sites fall4→0, LDG.E.128 sites increase4→5, STS sites2→6, and barrier try-wait sites50→38. Split adds no native register increase. K384 uses8-byte LDG; K64 uses4-byte loads.

The split source order does not establish full overlap of SF readiness with Gather4. In both native-K quantized/per-token SASS, the SF load appears at0x2680, its first dependent register move at0x2910, four Gather4 instructions at0x2a50/0x2ab0/0x2b10/0x2b20, and the first SF store at0x2b30. Thus41 independent instructions precede the dependent move, and that move can wait for the load before TMA issue; delaying STS alone does not force the intended latency overlap. `inspect_order.py` records candidate windows using any matching register, including address registers, so the manually inspected dependency is the basis of this conclusion. Complete SASS is saved by CUBIN hash for independent inspection.

Final raw timing table, immutable sources, receipts, PTX/CUBIN/SASS, archive digest, and verification counts are in[the evidence summary](../../evidence/fc1-sf-register-442d2aa5/README.md). The initial direct-only archive and summary are preserved separately. GPU5 was released after the reverse run with no compute processes,0 MiB,0% utilization.
