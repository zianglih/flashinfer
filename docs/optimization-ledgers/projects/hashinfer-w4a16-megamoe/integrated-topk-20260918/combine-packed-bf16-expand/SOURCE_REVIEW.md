# Packed BF16 expansion candidate

Prepared from exact selected `3de81245c1f484177b8ca50b47fd0464068d230e`. Only owned `hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/topk_reduce.py` changes. No GPU/remote execution, benchmark driver, source ABI, alignment, CTA geometry, public knob, barrier, score preparation or register-budget change.

## Generated-code motivation

The actual C1 T16384/tactic1 int32-vector capture uses the identical reducer source as selected3de. Its rank0 artifacts are under `input-stage-pair-tail/codegen-selected/collected-codegen-candidate/evidence/candidate/h7168-t16384-k1/`.

- SASS `00-Sm100W4A16MegaMoEKernel-fused_int32_vector.sass.txt:11157-11443` (0x15c70–0x16560) contains8 LDG128,4 FMUL2,28 FFMA2 and4 packed BF16 output conversions. Seven route loads precede the first multiply. These parts are already vectorized and substantially prefetched.
- The same span contains32 PRMT plus35 IMAD-by-65536 and29 SHF-by16:96 integer instructions expanding32 packed BF16 pairs. The high half is extracted to low16 then shifted back; the low half is shifted directly. Example:0x15ce0/0x15cf0/0x15d50.
- PTX lines6761–6783 use one128-bit load, scalar `cvt.f32.bf16` per element, then `mul.rn.f32x2`; later routes use `fma.rn.f32x2`. Output is already `F2FP.BF16.F32.PACK_AB` at0x16530–0x16560.

The candidate reads each loaded BF16 pair through a Uint32 rmem view and writes two Float32 slots through a Uint32 view: `lo_bits=word<<16`, `hi_bits=word&0xffff0000`. This targets two integer instructions/pair instead of three:32 fewer expansion instructions per width8/K8 worker. The observed span has144 static instructions including interleaved address/control work; this is not a kernel-latency prediction. Codegen may optimize or schedule it differently.

The recast/write-bit-pattern idiom and exact shift/mask pair already appear in protected FP4 `hashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/moe_nvfp4_swapab/topk_reduce.py:103-145`. That source is read-only. The candidate uses ordinary CuTe rmem operations in the owned reducer, with no inline assembly.

## Numerical and lifetime proof

Each BF16 encoding occupies the high16 bits of its Float32 representation. For two packed encodings, `(word<<16)&0xffffffff` and `word&0xffff0000` recover those bits independently. Signed zero, finite/subnormal values, infinity and NaN sign/payload bits are retained. Current captured SASS performs equivalent bit operations without NaN canonicalization during expansion. No finite-only assumption is added.

Reproduce the CPU check:

```sh
/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/.venv-timing-audit/bin/python /Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/integrated-topk-20260918/combine-packed-bf16-expand/verify-packed-expansion.py
```

CPU Torch2.8 conversion matched all65536 bit patterns with zero mismatches:2 zeros,254 subnormals,2 infinities,254 NaNs,65024 normals. Both packed halves were checked. This proves representation algebra and the host oracle, not native kernel behavior. NaN payload behavior of subsequent floating-point instructions is not newly promised; the same operand bits enter unchanged arithmetic.

The term remains eight BF16 elements with the same128-bit copy. Recast changes register views only. Both Float32 slots are written before every use, then reused for each constexpr pair; no new value survives outside the current route. Each element keeps its first FP32 multiply, route-ordered FP32 FMAs and final output conversion. Restoring only the unpack statements makes the entire source AST identical to3de. Worker IDs and width8 ownership remain unchanged, including small/empty ranks.

Scoped pre-commit hooks including mypy/ruff, syntax and diff checks pass. `source-audit.json` records CPU numerical/source boundaries. Native codegen and performance remain pending.

## Decision criteria and alternatives

Use the existing full13 benchmark/control and exact outputs for an isolated trial. This source is independent of9f delayed donation and256 staging. Capture the actual winning tactic after timing; check expansion instructions, preserved4 FMUL2/28 FFMA2 forK8, unchanged128-bit loads/stores, and no spills/local traffic. Extra register moves or loss of route-load scheduling could erase the intended saving. Small-worker coverage is preserved; decode latency and prefill guards still decide value.

True256 reduction needs32-byte contracts or extra host specialization and is outside this candidate. Head8/bulk16 amortizes score/address work but increases accumulator/lane span and risks half-sector requests. Current scores use two128-bit loads with heavily shared warp addresses; shuffle distribution adds instructions and requires a token-boundary proof. Route addresses mostly use immediate offsets from one base, so no broad address refactor is justified by this capture.

PTX scope is CUDA13.2/ISA9.2. Mixed `fma.f32.bf16` converts both multiplicands and cannot preserve the Float32 score. Existing packed FP32 math remains appropriate; no newer-ISA operation is assumed available onB300. Primary references:
- https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#mixed-precision-floating-point-instructions-fma
- https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#floating-point-instructions-fma
