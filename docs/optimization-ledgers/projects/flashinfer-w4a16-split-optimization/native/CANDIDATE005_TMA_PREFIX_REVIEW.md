# Candidate005 ordinary TMA-prefix native review

**PASS: no emitted-code blocker found.** Actual kernel `1fe29f6f802508034c2fc5daaf7a24271e35bf98a0ca1b052548bfc955f5f97b` is compared with retained b90 kernel `22fefac2a21e2efb5f9b5e0f2b402202dddf8f7136c1c50585105466ae2794a0`. Wrapper `aa446d91adfd1335d59bf30acb8ed240f6b592bd78724d02f230cde7806fd90d` is unchanged. All captures are compile-only, without returned-call invocation. This review performed no GPU work, compilation, or benchmark-reader replay.

## Exact captures and resources

| Specialization | Before | Candidate | SASS count | Result |
|---|---|---|---:|---|
|ordinary0|`native/candidate002-full-m-ordinary0-m256`|`native/candidate005-tma-prefix-ordinary0-m256-tile-n64`|1624 → 1624|New prefix condition; existing plain store and SIMT bodies present|
|fused2|`native/candidate002-full-m-fused2-m256`|`native/candidate005-tma-prefix-fused2-m256-tile-n64`|1568 → 1568|Whole raw SASS byte-exact including encodings/scheduling; PTX exact after removing only `.file`/`.loc` metadata|

Fixture: logical M256/N256/K512, MMA128/N64/K256, cluster(1,1), static scheduling, PDL disabled. M256 in the path is logical feature extent, not MMA M256. All PTX kernel parameter declarations match (ordinary23, fused25). Both preserve REG128, STACK0, LOCAL0, CONSTANT[2]12, and static SHARED1024; CONSTANT[0] stays1856 ordinary/1888 fused. Static SHARED1024 is not total dynamic allocation. No launch geometry, stage-fitting or storage-layout source changed.

## Actual ordinary store and C-state proof

Line numbers refer to the sole PTX under the candidate ordinary directory's `dsl/`.

- **No reduction opcode:** PTX2770–2771 uses `cp.async.bulk.tensor.2d.global.shared::cta.tile.bulk_group.L2::cache_hint`. These store from C SMEM offsets1024/5120 plus the selected C stage into the output tensor-map coordinates. SASS0x3d50/0x3d60 is `UTMASTG.2D`; no ordinary PTX `cp.reduce`, `atom.*`, or `red.*` instruction exists. This is a plain store into routed scratch, not a lower-precision combine.
- **Correct dynamic prefix test:** PTX2666 computes `%r310 = %r970 + 32`;2668 compares actual route distance `%r965` with that end. `%r970` is0 for the first subtile and32 for the second (2614,3078); each full32-route slab qualifies independently. SASS0x38e0 adds0x20 and0x3920 compares. No per-element or per-thread divergent readiness decision was introduced.
- **Same destination geometry:** PTX2766 adds `%r970` to the current route base `%r967`. The two stores share this N coordinate and use feature coordinates `%r49`/`%r51`, with the second feature half64 later (2611). These are the original output descriptor and partitions. The SIMT fallback keeps its route-coordinate comparisons against `%r965` before `st.global.b16` stores (e.g.2993–3003); it does not write invalid suffix routes.
- **Precision:** the TMA arm retains FP32 packed alpha multiplies2674–2689 followed by `cvt.rn.bf16x2.f32`2692–2722. The SIMT arm retains its corresponding multiply/conversion and BF16 stores. Neither branch performs top-k combination. The unchanged external ordered-FP32 `moe_unpermute` contract is source-traced in `candidates/nonfused_tma_prefix/INDEPENDENT_REVIEW.md`.
- **Conditional persistent C-ring state:** `%r969` is initialized once at2576 and incremented only in the TMA arm at2724. Its modulo2 calculation2726–2729 selects the two C buffers; the branch to SIMT skips this update. Both arms join at3076 and the loop advances to the second subtile. The next work-record load3106 updates feature/route/expert/distance only, retaining this actual-TMA count.
- **SMEM lifetime and final drain:** after shared writes, PTX2757 proxy-fences and2759 synchronizes all128 epilogue threads. The designated TMA warp issues both stores, commits2773 and waits for at most one outstanding source-read group2775. The second128-thread barrier2778 protects progression. Final `cp.async.bulk.wait_group.read 0`3141 remains. SASS0x3d70 `UTMACMDFLUSH`,0x3d80 `DEPBAR.LE SB0,0x1`,0x3d90 barrier and0x4a80 `DEPBAR.LE SB0,0x0` confirm the sequence. SIMT neither consumes nor overwrites C SMEM, so a prefix→SIMT-tail→next-work sequence retains valid buffer ownership.
- **Accumulator release:** the original final-subtile TMEM-load fence and ACC release remain2643–2663, before the store-method branch. No early ACC reuse or missing last-subtile release was found.

Native scope is the two C1/N64/full-M fixtures. Other N widths, C2, partial M, graph and PDL behavior require the existing source proof and actual runtime results; no claim is made that these two captures cover all cases. Root reports the prior baseline bitwise cohort passed and is running candidate bitwise plus66 focused tests separately. This note does not infer numerical success or latency benefit from native instruction counts.

## Immutable pins

- Ordinary before result: `532d3e31b2f23c850a49ff9d13521cfc69146e9dd2c5c6d098562fb84212df84`.
- Ordinary candidate result: `d13f84860aad8052d0004bfd549836773d8251b64d267a4a3270148ea5458c1a`.
- Fused before result: `8f0739f6320cc1873203127f04594f1545cbb763387e9879be5ee3c626c2f586`.
- Fused candidate result: `2cc21d7cf8a842dd415cadad1d9b596c54c5e1fb462e67ac2b54ba800a92eadd`.
- Ordinary candidate raw SASS: `c7eaf31627a4b35da75f5b83b5675e9b426c7f7b588592ed9d2ec6c823f4eeef`.
- Fused identical raw SASS: `f83b7182fc53effcb21fd94a6cd14f9c47b6cf683d51f10c9832306e77382e1a`.
