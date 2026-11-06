# Retained fallback decoder and compiler12.9 codegen audit

**Result:** this capture shows no transform spill or register-pool defect. Keep the existing decoder, FC1fragment128/FC2fragment32 and fixed two transform warpgroups. No source change or new candidate is justified from codegen alone.

## Exact scope and durable evidence

- Published source6315f94ceb279db53ec3149a7d81e19b332c8dd0, kernel34bbdfba91e4743a7079d436c3181e3825ca771fe584f910c4ee1c37a4165152. Local source verified clean and byte-identical to this commit during audit.
- Untimed EP8 codegen `cu130-dsl471-cu12-codegen-001`: global4096, H7168/I2048/E256/top8; M256/N128/K256, physicalC2, raw5/decoded2/activation2/accumulator2, flag4, epi_warps, group512, atomic_counter, epiflag(2,4), IKRfalse. This is the N128 control, not an N64/stage3 capture.
- Real image `nvcr.io/nvidia/pytorch:25.11-py3`, systemnvcc13.0.88, imageTorch CUDA13.0. Matching isolated DSL4.7.1 base/core/cu12 package selects nativecompiler12.9. The import-time decoder gate uses `cutlass.CUDA_VERSION`, not systemnvcc or Torch CUDA. PTX confirms the gate rather than inferring coverage from the image name.
- Raw archive: `profiles/cu130-dsl471-cu12-codegen-001.tar.gz`; original provenance and resources: `logs/cu130-dsl471-cu12-codegen-001{.provenance.log,-summary.log}`. Archive is unchanged.
- Reproduce CPU-only audit: `python3 candidates/w4a16_cuda130/independent-codegen-audit-001/audit.py`. Outputs: `audit.json`, `all-rank-hashes.json`, `local-instructions.json`, `sass-instructions.json`, retained rank0PTX/SASS/cubin. No GPU import, query or launch.
- All8 ranks have identical fused-kernel PTX/SASS/cubin bytes: respectively00eeb50e7a71895b6b46102871d6af26cccc2dcb1c83b661a2dca2920e2a36b2, af1d23f8bc311318de36535cba0a35516d057de14e776c34633496e844fcea43, f7643cc2c4d32c40e71c199be0737d38a1d3eba34d8c5e5a8397df33b8c7c340.

## Source/dataflow identity with PR4048

Reference PR4048 head8ed63e75d218cfef01d86ee14f8f834e2d5d4d95 is available locally. Its `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py` is **byte-identical** to current source (c36c5fce4e8132dd19f1928fbc72100a1d7ddc8d90cc8db88cfe24b8d3e722c9). `_setup_transform_partitions` and `_transform_tile` in `moe_w4a16_kernel.py` are AST-identical, including attributes other than source positions.

- `moe_w4a16_utils.py:13–15,64–150`: E2M1/E4M3 decode and scale multiplication use FP16x2; each FP16 lane widens to FP32 before BF16x2 packing. One scale conversion per16 weights. Relative to the direct branch, this adds16 scalar FP16-to-FP32 plus8 paired FP32-to-BF16 conversions per16 weights. These are PTX operation counts, not cycles.
- `moe_w4a16_utils.py:167–247`: existing supported fragments32/64/128; once-per-fragment packed-word bitcast and compact scale handling. No new Mega fallback implementation.
- `moe_w4a16_kernel.py:346–438`: complete16-value scale blocks divided across the two transform groups, exact compact scale fragments and local thread ownership.
- `moe_w4a16_kernel.py:460–550`: persistent ring index/phase survives work-tile transitions, only count resets; raw-ready and decoded-free waits precede scale/packed loads; decode writes registers, then existing collective register-to-TMEM copy/fence, raw release and decoded commit. Mega passes group-localtidx0..127 (`shim/w4a16/kernel.py:1150–1153`) and calls the same method for FC1/FC2 (`:1197–1224`). Precision and release boundaries are unchanged.
- Split default fragments are128 for activation/one-K-tile cases and32 otherwise (`moe_w4a16.py:128–130`). Mega explicitly constructs FC1fragment128 and FC2fragment32 (`shim/w4a16/kernel.py:332,639`).

## Actual generated decoder and role-local memory

PTX8.8 targets sm_103a and requires640threads. It contains the FP16 fallback forms and contains neither direct E2M1-to-BF16 nor direct E4M3-to-BF16 conversion. Whole-PTX `cvt.rn.bf16x2.f32` count176 includes48 epilogue conversions; do not label all176 as decode.

| Static evidence | Captured result |
| --- | --- |
| Whole fused SASS |6288 instructions |
| cuobjdump resource record |REG96, STACK112, SHARED1024, LOCAL0 |
| Transform body in this binary |PC[0x62b0,0xb2b0),1280 instructions; largest explicitly named registerR77 |
| Transform decoder |128 `F2FP.F16.E2M1.UNPACK_B`,16 `F2FP.F16.E4M3.UNPACK_B`,128 decode HMUL2/HFMA2,256 `HADD2.F32`,128 `F2FP.BF16.F32.PACK_AB` |
| Transform TMEM writes |16 `STTM.x8`,8 per static FC1/FC2 body; TMEM stage addresses+0x100…+0x138 through computed ring base |
| Tensor mainloop |16 static `UTCHMMA.2CTA` instructions |
| Whole-kernel local operations |8 STL.64+8 STL+1 LDL.128+4 LDL.64=21; all at0xcc10–0xdb10 |
| Transform local operations |0 |

The transform body has one additional HFMA2 outside the128 decoder multiplies. Source line information for inline assembly is expanded/scheduled beyond the Python method's physical line range; classify by actual role PCs and surrounding dataflow, not only `line<=554`.

The21 local instructions implement `Fc2OutputRouter.prefetch/get_dst` (`src/moe_nvfp4_swapab/epilogue_refactor.py:2343–2399,2444–2445`): eight64-bit destination pointers plus eight32-bit validity entries occupy the declared96-byte local depot. Stores fill offsets0x00…0x38 and0x40…0x5c; dynamic-index loads read these arrays. Some optimized line labels point to a generic kernel location or custom_ext, so those labels alone do not change ownership. These operations are in the176-register epilogue role; control, dispatch and both transform groups add no LDL/STL. `STACK112/LOCAL0` must not be paraphrased as no local-memory accesses. It also does not prove the router is a performance bottleneck.

The largest namedR77 is a static operand observation, not a measured live-register count. The source's common TMEM-copy call does **not** imply all128 decoded BF16 values remain live simultaneously: this compiler interleaves STTM.x8 with later decode and reuses registersR4/R12/etc. Therefore a fragment-size change cannot be justified by a presumed64-register simultaneously live output alone.

## Register budget and conditional optimization stop rule

Existing Mega roles are176/80/64/80/80 registers for epilogue/control/dispatch/transform0/transform1. Each is128threads: total61440 equals640×96 launch allocation. Generated USETMAXREG sites are control0x1250→80, transforms0x62b0→80, epilogue0xb2b0→176, dispatch0xeef0→64. No allocation imbalance is evident. PR4048's512-thread epi176/control80/two-transform128 budget is65536; copying transform128 into640-thread Mega would exceed the existing budget. **Do not change group count or redistribute registers from this evidence.**

Only if a repeated, controlled fallback slowdown is significant and source-correlated PC evidence implicates FC1 conversion/dependency issue, a bounded FC1fragment128→64 specialization is worth a probe. This already-supported fragment size changes one existing constructor input; keepFC2fragment32,640threads, two groups, all register targets, geometry, stages and barriers fixed. First require same-source numerical gates, own codegen/no-new-locals check and same-node adjacent A/B/A fixed-tactic timings. It may alter instruction scheduling without removing any conversion; no gain is predicted. With no observed spills, this is a low-priority conditional experiment, not a proposed production change.

The earlier split ledger rejects blindly repeated mechanisms: register redistribution to136-transform registers (lines4753–4793), FC2fragment32→16 (5417–5440), late decoded-stage acquire (5487–5509),32-value fragment lookahead (5511–5533), immediate fragment-to-TMEM store (5535–5570). Its later FC2fragment64→32 result (5356–5415) supersedes the earlier failed32 trial and is the retained source. Generic inter-work-tile overlap already exists structurally. No additional lookahead pipeline or FC2 widening candidate is recommended.

This capture is untimed and covers one geometry. It establishes emitted fallback instructions and role-local resource attribution, not dynamic stalls, production latency or other geometry's spills. Cross-image/runtime/compiler comparisons do not isolate decoder cost; retain actual nativecompiler12.9 versus systemCUDA13.0 distinction and separately disclose NVSHMEM loaded-library differences. No source or runtime-helper changes were made by this audit.
