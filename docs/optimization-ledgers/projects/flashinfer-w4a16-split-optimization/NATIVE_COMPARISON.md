# Top-k constexpr native comparison

**PASS for the intended native specialization.** This review compares completed compile-only dumps; it performs no compilation or GPU execution. The returned kernel callable was not invoked by the capture helper. Numerical results and normal timings are separate evidence.

BEFORE is upstream `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`, host/kernel hashes `cd11e0c1` / `4a870648`. AFTER is that commit plus the three-line top-k patch, host/kernel hashes `acc26260` / `8142abdc`; each [candidate result](native/candidate-topk-fused2/result.json) records the full hashes. The matching [baseline result](native/baseline-fixed-fused2/result.json) records its source. All three cases use M256/N256/K512, eight groups, C1 `(128,64,256)/(1,1)/M-major`, max-active-clusters 148, activation None, PDL false and CLC false. Fused cases use 65 output tokens and top-k 2/3; ordinary0 uses zero output-token argument and no fused-finalize descriptors.

All PTX headers identify target `sm_103a`, PTX 9.3 and NVVM CUDA 13.3.27. This is the compiler inside the selected DSL stack, distinct from the image/Torch CUDA 13.2 identity. Both arms use the same header/toolchain. Artifacts are in `native/baseline-fixed-{fused2,fused3,ordinary0}/dsl` and `native/candidate-topk-{fused2,fused3,ordinary0}/dsl`.

| Case | SASS instruction rows, before → after | Delta | REG | STACK / LOCAL | Static SHARED | CONSTANT[0], before → after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fused2 | 1640 → 1584 | −56 | 128 → 128 | 0 / 0 → 0 / 0 | 1024 → 1024 | 1904 → 1888 |
| fused3 | 1640 → 1584 | −56 | 128 → 128 | 0 / 0 → 0 / 0 | 1024 → 1024 | 1904 → 1888 |
| ordinary0 | 1664 → 1664 | 0 | 128 → 128 | 0 / 0 → 0 / 0 | 1024 → 1024 | 1856 → 1856 |

Counts include padding NOPs and are static instruction rows, not instructions executed per invocation. All cases retain `.reqntid 512,1,1`, CONSTANT[2] 12 bytes, four register-decrease sites at 80 and the epilogue increase at 176. The PTX also declares external dynamic shared memory; these dumps do **not** establish its launch-time allocation, so 1024 is not presented as total shared memory or as a measured stage-fit result.

## Actual arithmetic

- **Baseline fused2 and fused3 are identical:** whole PTX SHA256 `76f19c2025f684ba7ca1dc4378282181857f99a04c2cd8d1713469ec3c6b3255`, whole SASS `c7921e16d01ff84fd6ff79bf375a813b23c666823df04a2d6e0e73421e633dc8`.
- **Runtime divisor provenance:** baseline PTX loads the scale tensor extent from `param_16+16` into `%rd37`, converts it to `%r46` at line 2541, then uses `div.s32` at line 2675 (source 2161, scale lookup) and 2958 (source 2210, output scatter). The remainder at source 2162 is multiply/subtract at PTX 2676/2682. It is not an I64 divide and is not a separate top-k `rem.s32`.
- **Baseline SASS:** divisor `LDC` at PC `0x36f0` reads `c[0x0][0x720]`; the two quotient paths include `MUFU.RCP` at `0x39f0` and `0x4410`, with conversion/refinement/correction instructions. Both top-k reciprocal sequences disappear in each candidate. The unrelated scheduler `div.s32` / `rem.s32` remain.
- **fused2:** candidate PTX 2669–2679 uses mask/select/or for the guarded scale-table index, including `and ... 1` for its remainder. Scatter PTX 2945–2953 uses shifts and signed-floor correction; SASS includes `SHF.R.S32.HI ... 0x1` at `0x41a0`. This preserves the original signed expression rather than assuming every scatter index is nonnegative.
- **fused3:** candidate PTX 2669–2677 uses constant `mul.hi.u32` with `1431655766` (`0x55555556`) and multiply/subtract for the remainder. Scatter PTX 2943–2951 uses signed high multiply and floor correction. SASS uses that immediate at `0x39c0` (scale path) and `0x4180` (scatter). Neither path contains a runtime-divisor quotient sequence.
- **Arithmetic/store scope:** each fused arm retains 34 PTX `mul.f32`, 32 `cvt.rn.bf16.f32`, and the one `cp.reduce.async.bulk.global.shared::cta.bulk_group.add.noftz.bf16` site. The source patch does not change the floating-point calculation, routing validity or store protocol; these counts complement that source proof and do not replace numerical tests.

## Parameters and ordinary0 control

Fused GPU parameter declarations remain 25; only the scale descriptor `param_16` shrinks from 32 to 16 bytes. Its dynamic top-k extent and corresponding row stride disappear. All other declarations are identical. The route pointer (`param_15`), scale pointer (`param_16`) and final-output pointer (`param_10`) still load from actual kernel parameters and feed global loads/output reduction. The compile-only null descriptors did not turn these memory accesses into constant-address or dead code. Removing the Python compiled-call top-k argument is a separate host ABI change.

**ordinary0 is exact:** whole PTX SHA256 `7116e64842c957a0d640e51e525f62589963d0f171826fe4e965636329ba83f5` and whole SASS SHA256 `6fbd931aceb7fe9b4549ac2764aa95b4b42744474c59a56523737c8e440550ed` match before/after. All 1664 PCs, disassembled instructions, both encoded words and scheduling bits are identical. All 23 parameter declarations and the complete resource text also match. No whole-cubin identity claim is needed for debug/name sections.

Candidate fused SASS hashes: fused2 `8c0a016e175079788c9001d8586c019fc8c0f93887610246f4b927ad873879e8`; fused3 `4766046fecf3d4c8716a29a6bf5bd394056baf31d504e8ee4f2d15fb8d3e5d3d`. Candidate PTX hashes: fused2 `5f8c7ba10be1a3575288f780f9375c7d79deede025220d7c048bef9eaab98094`; fused3 `33051eb524faa92c16aae2f9cd2952410ca177b6e15641c34ff8827877bfaf7a`.

The normal benchmark uses top-k 8 and its selected tactics; the fixed top-k 2/3 compile cases establish power-of-two/non-power-of-two lowering and the ordinary0 control, not a direct native capture of that benchmark's selected GEMM2. See [the complete first timing pair](TOPK_BENCHMARK_COMPARISON.md) and [the complete repeat pair](TOPK_BENCHMARK_REPEAT_COMPARISON.md) for measured latency and its scope. The repeat reuses the same native/numerical evidence; it does not imply another native or numerical run.
