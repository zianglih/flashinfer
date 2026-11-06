# Raw4 saved native schedule review

**PASS for the planned numerical and timing gates.** Reviewed the actual candidate-only N64 capture002 and N128 capture001; no reviewer compilation, GPU call or production modification. Performance owns the original resource/source/native/process checks. The failed N64 capture001 had its dump environment set too late; it supplies no disassembly evidence and remains preserved.

N64 actual stage observations are B3/raw4/decoded3/S2 in both FC1/FC2. PTX initializes four raw full barriers at0,8,16,24 with count1, and four raw empty barriers at32,40,48,56 with count8. Decoded full/empty bases are64/88 with three slots and counts512/1. B full/empty bases112/136 retain three slots; accumulator160/176 retains two. These shifted addresses are required by the shorter raw barrier array, not a new synchronization protocol.

Producer packed/SF TMA stage strides remain16384/2048 bytes; their bases are58752/124288. B starts132480, and its3×16384 payload gives181632 bytes by the existing allocation model. Each A+SF transaction still expects18432 bytes. Native code establishes offsets/ring dimensions; static SHARED1024 alone does not attest the launch's actual dynamic allocation. The runtime observer must record it.

Both FC1/FC2 producer paths compare index+1 to4, select zero at wrap and XOR the phase. FC1 state feeds FC2 without resetting physical index/phase; only work K counts reset. The generated producer tail performs exactly four parity waits with three intervening modulo4/phase advances. Consumer modulo4 checks are0x6430 and0x7480, and the release uses the consumed stage while the next-raw probe addresses the advanced state. The independent decoded ring retains modulo3.

| N64 path | Raw / decoded blocking waits | Next-raw probe | First STTM | Final TMEM fence / raw release / decoded commit |
|---|---|---|---|---|
|FC1|0x62d0 /0x6330|0x68c0|0x68d0|0x70d0 /0x70e0 /0x70f0|
|FC2|0x7360 /0x73c0|0x78f0|0x7910|0x81e0 /0x81f0 /0x8200|

No payload is loaded before a newly inserted ownership wait. Final TMEM stores precede the existing fence/release/commit; slow paths retain their barrier predicates and scratch registers with the decoded-empty displacement shifted from0x68 to0x58.

For a bounded saved-code comparison, historical actual S2/B3/raw5 N64 at `profiles/scheduler-depth2-activation-b3-m256n64c2-001/candidate/codegen` has the same descriptor geometry and device design. Its global scheduler default2 differs from current explicit2/default3, so it is historical native context, not a freshly rerun production control. The corresponding complete transform spans compare exactly after only raw depth, shared/barrier offsets and label relocation:236 FC1 rows and253 FC2 rows. No load, conversion, TMEM-store, packet-move or math instruction is added. Each span still contains four packed LDS128, two SF LDS and eight STTMx8. Whole addressed rows5528→5512; removed work is raw barrier initialization plus one tail slot/slow path, with two extra trailing padding NOPs. There are no new spill or control-flow dependencies in the decode loops.

N128 actual B3/raw4/decoded2/S2 confirms unchanged fit. Every one of its5840 addressed SASS instruction bodies and PCs equals the prior actual S2/B3/raw4 N128 capture. Cubin/source labels are not claimed identical. This directly rules out a new N128 instruction schedule or ring change in these fixtures.

Both actual candidate results retain640 threads, initialREG96, caps80/144/64, two decode WGs retaining96, zero stack/local accesses and16 MMA. These resource observations concur with performance's original gate; they are not a second resource-admission framework. The numerical long-K/return tests and actual launch allocation still gate runtime. No performance improvement is claimed.

## Reviewed file identities

- `profiles/raw4-fixed8-s2-m256n64c2-002/codegen/result.json` SHA `d2a06df08bc133c73617f3f6cffdfe8ed930c198f13354c86749e9b6955f9d19`
- `profiles/raw4-fixed8-s2-m256n64c2-002/codegen/sass.txt` SHA `4df4b0df0b7dc36addd91cd2e67d8f6c680fb4590bd9141d4d5e0f722f671455`
- `profiles/raw4-fixed8-s2-m256n64c2-002/codegen/dsl/cutlass___call___flashinfermoe_epkernel_srccutedsl_megamoeshim_reuse512_compile_onlykernelSm100W4A16MegaMoEKernel_object_at__FakeTensorBFloat16div1div1i64div11_FakeTensorInt64div1d.sm_103a.ptx` SHA `111a0ce698a51299c540c53c6710668a2ab94033a4755aaae10944624f228094`
- `profiles/raw4-fixed8-s2-m256n128c2-001/codegen/result.json` SHA `5b2ce5ca40ccc7815784b98cf5d9d5ed27586bd1f63a1e6311bf0b51ee97a3e3`
- `profiles/raw4-fixed8-s2-m256n128c2-001/codegen/sass.txt` SHA `349396a3b77fbe4bbe1ad52e9b6ba47804dc28c8cffe2ba9ed676882b4d9e9d3`
- `profiles/raw4-fixed8-s2-m256n128c2-001/codegen/dsl/cutlass___call___flashinfermoe_epkernel_srccutedsl_megamoeshim_reuse512_compile_onlykernelSm100W4A16MegaMoEKernel_object_at__FakeTensorBFloat16div1div1i64div11_FakeTensorInt64div1d.sm_103a.ptx` SHA `acbdf4bc27196554739ce2b22120525d9123991e819abf3676ac70e5b120d0fa`
