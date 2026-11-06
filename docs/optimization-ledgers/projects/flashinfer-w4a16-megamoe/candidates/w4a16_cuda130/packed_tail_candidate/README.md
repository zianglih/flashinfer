# FP16-product tail audit

This is a separate follow-up to the rejected register-table FP4 decoder. Native E2M1→FP16 and E4M3→FP16 conversion and the packed FP16 products are retained. No active public API or direct13.2 branch is changed. Baseline is clean6315, shared decoder SHA256 `c36c5fce4e8132dd19f1928fbc72100a1d7ddc8d90cc8db88cfe24b8d3e722c9`.

## Packed integer form

For finite inputs, nonzero NVFP4×E4M3 products are normal FP16 in `[2^-10,2688]`, with exact BF16 representation. A packed32-bit word `p` containing two such products can therefore be rebased by shifting its two magnitudes right by3 and adding the exponent-bias difference0x3800 independently. The normal-value calculation requires signed-zero and NaN handling; an unconditional rebias is incorrect. A shared scale-NaN predicate can select the observed canonical result0x7fff for both halves of every pair. This is a constrained NVFP4-product conversion, not a general FP16→BF16 algorithm.

Independent CPU proof `verify_integer_tail_cpu.py` passes all65,536 packed pairs (131,072 lanes), including1,024 NaN lanes and17,152 signed-zero lanes. Its NaN target0x7fff is explicitly the previously observed GPU baseline contract, not a claim established by CPU arithmetic. `integer-tail-cpu-proof.json` retains the proof.

The documented [half comparison](https://docs.nvidia.com/cuda/archive/12.9.1/parallel-thread-execution/index.html#half-precision-comparison-instructions-set) supports a packed integer mask. Ordered `ne` is false for zero and NaN. The SIMD video instructions provide per-half arithmetic/comparisons but no two-lane shift-and-bias fusion. The straightforward exact PTX probe uses seven emitted per-pair instructions plus a shared NaN predicate. Systemptxas13.0.88 produces104 total SASS instructions (including padding), compared with72 for the existing standalone probe; both use22 registers and zero stack/spills. This form is rejected before GPU timing because it does not produce the short, efficient sequence sought. `probe_ptx.py`, `probe.ptx`, `probe.sass` and `ptxas-002.log` retain the compiler evidence. `ptxas.log` retains the first operand-type syntax failure; no GPU was launched by either compile-only probe.

## Documented scalar hardware alternative

The same ISA audit found [scalar BF16-from-FP16 conversion](https://docs.nvidia.com/cuda/archive/12.9.1/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cvt), supported since PTX7.8/SM90. No packed `bf16x2.f16x2` form exists in the documented PTX8.8 syntax. `scalar/` substitutes two scalar conversions and a pair pack for the existing two FP32 widenings and BF16 pack. It is a native hardware alternative, not an integer packed conversion. `make_scalar.py` proves the original direct branch AST unchanged and generates an unapplied single-file patch.

Actual DSL4.7.1/nativecompiler12.9/B300 gate `logs/cu130-scalar-tail-exact-001/` passes all65536 output-bit comparisons: every16 E2M1 codes×256 scale bytes×16 positions. All65024 finite outputs match the independent reference; all512 NaNs match baseline canonical0x7fff. Signed zeros and subnormal scales are included. The original oracle/assertions are reused without tolerance. The result field `blocks=4096` counts logical16-value NVFP4 blocks; the actual CUDA launch has32 CTAs of128 threads. Source1572 before/after inventories match clean6315. Candidate SHA256 is `735beaa0697ac948c26f8ecb8ec16a70ec369a686f4f776e3effbcb36cb4f26e`.

| Actual native12.9 standalone codegen | Baseline | Scalar tail |
| --- | ---: | ---: |
| SASS instructions, including8 NOPs each | 72 | 72 |
| FP4 conversions / scale conversions | 8 / 1 | 8 / 1 |
| FP16 packed products | 8 | 8 |
| FP32 widening / BF16 pair conversion | 16 / 8 | 0 / 0 |
| Native scalar F2F.BF16.F16 | 0 | 16 |
| PRMT, including original unpack preparation | 2 | 10 |
| Registers | 24 | 27 |
| Stack / local bytes | 0 / 0 | 0 / 0 |

The result is still three tail instructions per pair. Scalar F2F conversion uses a different hardware path and scoreboard-managed result, followed by PRMT; the baseline uses two HADD2.F32 results and a BF16 pack. Static instruction counts do not establish latency or throughput. `logs/cu130-scalar-tail-exact-001/codegen-counts.json` preserves exact SASS hashes and opcode counts. The separate bounded A/B/A experiment below is complete and rejects the scalar tail.

`run_scalar_tail_aba.py` differs from the already-reviewed register-decoder driver only in candidate/helper/stack identifiers. CPU overlay guards, negative tests, exact driver delta and Python3.12 grammar pass in `logs/cu130-scalar-tail-aba-helper-cpu-001.json`. It uses the unchanged primary benchmark, fixed CONTROL, global tokens1/256/4096,100 CUPTI iterations, fresh DSL/driver caches for each arm and source/library attestation. Exactly one shared decoder file changes in B, affecting both split and Mega; split retunes and is not an unchanged control. Clean6315 restoration is guarded after workers finish. No NCU run or profiling timing is part of this comparison.

## Completed A/B/A: rejected

All three processes completed with exit0. The original1572 source files are restored to clean6315; all24 contemporaneous rank records have identical nativecompiler12.9/NVSHMEM3.4.5/NCCL2.28.8 loaded paths and hashes. No GPU or compiler process remains. The experiment validates72 actual compiled records and72 split tactic selections; split retunes under the changed decoder in B.

| Global tokens | A1 split ms | A1 Mega ms | B split ms | B Mega ms | A2 split ms | A2 Mega ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.086929 | 0.112449 | 0.105201 | 0.130721 | 0.106881 | 0.107297 |
| 256 | 0.310961 | 0.274786 | 0.493972 | 0.417843 | 0.300291 | 0.275859 |
| 4096 | 0.568085 | 0.539011 | 0.670246 | 0.716805 | 0.572595 | 0.539686 |

B Mega is16.25–21.83%,51.47–52.06% and32.82–32.99% slower than the two controls at1/256/4096 tokens respectively. Baseline Mega max/min spreads are4.80%,0.39%,0.13%. The scalar hardware form is rejected; no full13 run or expanded integrated numerical suite is warranted. The result does not replace the final performance tables. The one-file change establishes a regression for this substitution, without attributing a measured cost to an individual instruction or claiming a specific pipeline bottleneck.

Artifacts: `logs/cu130-scalar-tail-aba-001/{results.json,source-runtime-audit.json,restored-source.json}`, all three control raw/provenance/tactic directories and `logs/cu130-scalar-tail-restored-live-state-001.log`. Reproduce source/runtime verification with `python3 candidates/w4a16_cuda130/audit_decoder_aba_runtime.py logs/cu130-scalar-tail-aba-001`. The independent numerical/source/codegen audit is `logs/cu130-scalar-tail-exact-001/independent-audit.json`; its tensor-byte comparison reads saved ZIP storages without executing pickle.

Neither fallback idea is retained. The integer formula is exact in its CPU domain but too large in the straightforward lowering; the compact native scalar hardware alternative is bit-exact on GPU but substantially slower in the primary benchmark. Existing fallback FP16-product→FP32→BF16 code remains unchanged.
