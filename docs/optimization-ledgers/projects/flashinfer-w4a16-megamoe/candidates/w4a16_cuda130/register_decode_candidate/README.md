# Isolated register decoder candidate

Candidate `moe_w4a16_utils.py` SHA256 `77d2c23498e831ca40335d22f22ee118dba2fa683e25775023f30a21ffb2fd36` changes only the pre13.2 branch of the6315 decoder. Baseline SHA256 is `c36c5fce4e8132dd19f1928fbc72100a1d7ddc8d90cc8db88cfe24b8d3e722c9`. `candidate.patch` is unapplied and passes `git apply --check`. The candidate remains an effort artifact. The authorized one-file overlay on the CUDA13.0 box has completed; clean6315 is restored and verified. The candidate is rejected on performance.

The candidate directly transcribes the register PRMT tables and sign mapping in6315 `include/flashinfer/vec_dtypes.cuh:463–480` (PR4746). Two packed32-bit words produce eight BF16 pairs. E4M3 scale conversion uses the current hardware FP16 conversion, widened and packed once per16-value block; multiplication then uses packed BF16. The original direct13.2 branch AST and compile-time capability gate are unchanged. No activation/global-alpha/routing behavior or public option is introduced.

The generator first copies all three input operands into PTX temporaries before writing outputs, preserving the existing `=r` constraint contract. Magnitude/sign selection remains branch-free. The current `fast_dequant_f8f16x4` scale helper is deliberately avoided because its NaN mapping differs from hardware conversion.

CPU source emulation passed131072 packed patterns,1,048,576 LUT comparisons and all4064 finite E2M1/E4M3 code-pair products. Real compiler12.9/B300 exactness passed in `logs/cu130-register-decode-exact-002/`: all65536 values (every16 E2M1 codes×256 scale bytes×16 positions) match baseline bits. All65024 finite values also match an independent reference;512 NaN outputs have identical canonical payload0x7fff. Signed-zero and scale-subnormal combinations are included. No numerical tolerance is used.

| Standalone per-block generated-code observation | Current fallback | Register candidate |
| --- | ---: | ---: |
| Total static SASS instructions | 72 | 88 |
| FP4 conversions | 8 | 0 |
| E4M3 scale conversions | 1 | 1 |
| HADD2.F32 widening | 16 | 2 |
| BF16 pair packing | 8 | 1 |
| PRMT | 2 | 22 |
| LOP3 | 0 | 6 |
| Packed products | 8 FP16 | 8 BF16 |

The candidate removes the per-weight floating-point widening chain but adds integer instructions. This is a pipeline/dependency tradeoff, not evidence of fewer total instructions or improved latency. The integrated performance probe below is complete. Full MegaMoE codegen and numerical suites were not expanded because the candidate regressed every measured point; standalone exactness is not relabeled as an integrated numerical gate.

The authorized integrated probe uses the existing primary distributed benchmark in three separate processes: baseline, candidate, baseline at1/256/4096 tokens, fixed CONTROL,100 CUPTI iterations. Exactly the shared decoder file changes in the candidate arm, so **both split W4A16 and MegaMoE use the candidate**; split autotunes independently in each arm. Absolute latencies and actual split tactics must be reported without calling split an unchanged control. Each arm has fresh DSL and driver caches, actual decoder/compiler preflight, and full1572 source hashes before/after. Only the completed fallback stack's unchanged native C++ caches are reused. The identical derived benchmark shell changes only the timeout1800s to600s. The driver restores clean6315 in a final guard; a remaining owned worker prevents a premature source transition.

`run_register_decode_aba.py` and its CPU guard proof are effort-only. Run `cu130-register-decode-aba-001` completed all three arms with exit0. Full1572 source inventories before/after,72 actual compiled records,72 split tactic selections, and24 contemporaneous loaded-library rank records passed the source/runtime audit. Nativecompiler12.9, NVSHMEM3.4.5 and NCCL2.28.8 loaded paths and hashes were identical across all arms. The final Git tree is clean6315 and GPUs/compiler processes are idle. The native cache inventory establishes permitted reuse origin; it does not claim cache contents remained immutable after execution.

| Global tokens | A1 split ms | A1 Mega ms | Candidate split ms | Candidate Mega ms | A2 split ms | A2 Mega ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.099521 | 0.093392 | 0.100513 | 0.116897 | 0.079905 | 0.094209 |
| 256 | 0.312898 | 0.274754 | 0.346691 | 0.297252 | 0.311874 | 0.270754 |
| 4096 | 0.571365 | 0.543860 | 0.581239 | 0.573206 | 0.561204 | 0.545139 |

Candidate Mega is24.08–25.17%,8.19–9.79%, and5.15–5.40% slower than the two baselines at1/256/4096 respectively. The corresponding baseline max/min spreads are0.87%,1.48%,0.24%. Split also changes implementation in the candidate arm; its one-token baseline varies24.55%, so it must not be used as an unchanged control. These results reject this candidate and do not replace any full13 final-performance table.

Artifacts: `logs/cu130-register-decode-aba-001/{results.json,source-runtime-audit.json,restored-source.json,restored-live-state.log}`, all three arm raw/provenance/tactic logs, and the helper CPU proof `logs/cu130-register-decode-aba-helper-cpu-001.json`. The original primary benchmark/timing helper is unchanged, and no active decoder edit remains.

Reproduce standalone exactness on the existing fallback box/venv:

```bash
export PATH=/workspace/flashinfer-w4a16-megamoe/.venv-cu130-dsl471-cu12/bin:$PATH
export FLASHINFER_CUDA_ARCH_LIST=10.3a OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
CUDA_VISIBLE_DEVICES=0 timeout --kill-after=15s 180s python \
  candidates/w4a16_cuda130/validate_register_decode.py \
  --output /workspace/flashinfer-w4a16-megamoe/logs/cu130-register-decode-exact-FRESH
```

The first GPU attempt is preserved as `cu130-register-decode-exact-001`: codegen artifact setup failed because the DSL dump directory did not exist. The002 helper explicitly creates the directories and uses distinct baseline/candidate class names to retain separate PTX/SASS files. Production source was unchanged in both attempts.
