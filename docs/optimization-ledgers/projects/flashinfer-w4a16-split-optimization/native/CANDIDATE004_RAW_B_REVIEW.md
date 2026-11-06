# Candidate004 unequal raw/B rings: native review

PASS for the two captured specializations. This is a source/native protocol and resource review, not a latency claim. No compilation, callable invocation, GPU execution, or benchmark-reader replay was performed by this review.

Actual candidate kernel SHA256: `7a2bf6ca032fbfb6733fed5255684203d7b9f2300bdf6146e88dec1fd55838f0`; wrapper `aa446d91adfd1335d59bf30acb8ed240f6b592bd78724d02f230cde7806fd90d`. The comparison kernel is candidate002 `22fefac2a21e2efb5f9b5e0f2b402202dddf8f7136c1c50585105466ae2794a0`. Source hashes, rather than the helper's unchanged checkout HEAD field, identify the compiled bytes. Candidate003's raw-release reorder is not combined here.

## Captures and whole-code comparison

All captures use logical M256/N256/K512, top-k2 fused finalize, MMA128×N×256, cluster(1,1), static scheduler, PDL disabled. The directory suffix `m256` is logical M, not MMA M256.

| MMA N | Before directory | Candidate directory | SASS instructions | Result |
|---|---|---|---:|---|
|16|`baseline004-fused2-m256-tile-n16`|`candidate004-raw-b-fused2-m256-tile-n16`|1616 → 1632|Eligible raw7/B7 → raw8/B7|
|64|`candidate002-full-m-fused2-m256`|`candidate004-raw-b-fused2-m256-tile-n64`|1568 → 1568|Ineligible: whole raw SASS byte-exact, including encodings/scheduling; PTX exact after removing only `.file`/`.loc` metadata|

Directories above are relative to `native/`. Each contains the actual PTX, cubin, raw SASS, line-attributed SASS and resource output under `dsl/`.

Both pairs preserve every PTX kernel parameter declaration (25), REG128, STACK0, LOCAL0, CONSTANT[0]1888 and CONSTANT[2]12. The cuobjdump SHARED1024 value is static shared memory; total dynamic allocation is not recorded by these compile-only results, so this review does not present 1024 bytes as total shared usage. Native N16 operand addresses show the additional actual storage, described below. Root/executor separately report all42 focused tests and six long-K wrap calls passing, including all eligible families; these tests were not rerun here.

## Eligible N16: actual independent ring protocol

PTX line numbers below refer to the sole `.ptx` in `candidate004-raw-b-fused2-m256-tile-n16/dsl/`.

- Barrier initialization is raw full/empty8 each (offsets48–104 and112–168), decoded full/empty3 each (176–192 and200–216), B full/empty7 each (224–272 and280–328), ACC full/empty2 each (336–344 and352–360), and metadata full/empty3 each. There are46 total initializations versus44 before. The extra raw pair shifts later arrays by16 bytes without overlap.
- B producer retains8192 expected bytes (522–523), `stage << 13` local stride (528), and wrap7 with phase toggle (565–570). Its global K coordinate uses its logical iteration counter, `count << 8` (526), independently of its stage index. The final B producer tail contains seven waits (614–778).
- Raw producer retains18432 expected bytes (850–851): A16384 and actual SF2048. Its A slot address is `5120 + (raw_stage << 14)` (864–868), SF is `136192 + (raw_stage << 11)` (879–884). The producer wraps at8 and toggles phase (887–892); its final tail contains eight waits (945–1138). Expected bytes match the unchanged individual payload sizes, not the fitter's conservative BF16 SF charge.
- B's first buffer moves from134144 to152576, an18432-byte shift for the additional actual A/SF payload. B's own stage size and depth stay8192×7. This address proof is distinct from a host-recorded total dynamic allocation.
- The decoder waits on raw full at48 and decoded empty at200 (1233–1239). Raw consumer index/phase wraps8 (1741–1746); decoded producer independently wraps3 (2026–2030). The logical K termination checks remain separate from both physical indices. Final decoded-producer draining remains three slots (2083 onward).
- The MMA loop waits on decoded full and B full independently. It releases decoded empty at200 and B empty at280 through the existing `tcgen05.commit` operations (2555/2562), then advances decoded modulo3 and B modulo7 separately (2565–2576). ACC publication and modulo2 advancement remain at2597–2604; the final ACC drain keeps its two-stage contract (2645–2675).
- Existing decode/store/release order is retained: final TMEM store → TMEM store fence → raw empty arrival → decoded full arrival. Actual SASS sites are0x2540 STTM,0x2560 FENCE.VIEW.ASYNC.T,0x2570 raw arrival,0x2580 decoded arrival; the baseline counterparts are0x2520,0x2540,0x2550,0x2560. No candidate003 release-before-fence change appears here.

No accidental raw/B physical-index coupling, missing tail slot, parameter growth or spill was found. Native evidence covers eligible MMA128/N16/C1 and unchanged MMA128/N64/C1. It does not independently capture the other two eligible families or CLC/PDL specializations; their source bindings are covered by `candidates/unequal_raw_b/INDEPENDENT_REVIEW.md`, and runtime coverage is attributed to the executor's separate tests.

## Immutable result pins

- Before N16 result: `0d205a8a82d67d1f98937c1c10135c1e54b2af962096f4b9a434e1ca56cb593a`.
- Candidate N16 result: `5e27ec5afcc6c396b03242dd47bb8d17ccf319694e43fbd5e0b31fa91fb7123c`.
- Before N64 result: `8f0739f6320cc1873203127f04594f1545cbb763387e9879be5ee3c626c2f586`.
- Candidate N64 result: `25848dd9fcb5599c1c3978021cfe7698e4dcf7827a4b31139c74d1d74835c24f`.
- N64 identical raw SASS SHA256: `f83b7182fc53effcb21fd94a6cd14f9c47b6cf683d51f10c9832306e77382e1a`.
- N16 before/candidate raw SASS SHA256: `d86b23b1c3f5f70d8eb6c58395f430f00fd8737e153d3ba64be292eadbcd43df` / `8943d1cc598e6fa000eea5d4410ea0b1950242c939a717c78f70834f13a460f2`.
