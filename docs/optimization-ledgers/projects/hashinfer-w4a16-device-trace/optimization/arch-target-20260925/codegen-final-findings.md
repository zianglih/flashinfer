# Architecture generated-code findings

CPU audit passed for all 640 completed winner exports and 3289 consumed input files. The frozen helper and report preserve source, target, configuration, fixture and export-hash bindings. This is winner-export qualification, not an audit of every candidate/ABI compiled during tuning.

**No static instruction reduction was observed among matching `sm_100f` / `sm_103a` winners.** All 384 eligible cross-target pairs have equal instruction counts, full opcode histograms and cuobjdump resources. Their encoded `.text` and normalized instruction sequences differ. Actual differences include instruction reordering, changed register choices and `.reuse` annotations; “only rescheduling” would be too narrow. These observations do not establish the cause of any timing difference.

| Scope | Cross-target pairs | Same-target repeat pairs |
|---|---:|---:|
| Native EP4 | 136 | 92 |
| Native EP8 | 240 | 136 |
| Uniform T128 EP4 | 8 | 0 |
| Total | 384 | 228 |

All 228 eligible same-target repeat pairs have identical complete CUBINs, `.text`, normalized instructions and resource reports. All 640 exports report REG 96, STACK 0, LOCAL 0, static SHARED 1,024 bytes. The 384 cross-target comparisons represent 152 exact configuration groups and 22 distinct pairs of normalized code sequences; repeated ranks/trials are not independent compiler configurations.

Across those 22 distinct code pairs, 422–594 instruction positions differ. This is a positional disassembly difference count, not additional work or executed instruction count. Each export contains one relocation section associated with `.text`; matching text alone would not prove relocation/metadata equivalence.

**Exclusions:** 108 groups / 164 exports have no opposite-target exact match. Their source/config/fixture keys are retained in `codegen-final-1.json`; no architecture delta is inferred for them. In particular, native EP4 T4, T8 and T16384, and EP8 T32 and T64 have no matching cross-target winner pair. Uniform T128 changes group hint across trials, so only A1–B2 (G512) and A2–B1 (G1024) match, across four ranks.

**Representative actual SASS difference:** native EP4 T1, rank0, A1 → B1, same N64/G512/epi tactic:

```text
offset   sm_100f                                  sm_103a
0x23c0   IMAD R6, R10, -0x40, R27                SEL R2, R2, 0x2, !P1
0x23d0   SEL R2, R2, 0x2, !P1                    IMAD R6, R10.reuse, -0x40, R27
0x4f50   FMUL2 R30, R22.F32x2.HI_LO, -1.442...   FMUL2 R32, R22.F32x2.HI_LO, -1.442...
```

The first two instructions reorder and add a reuse annotation; the FMUL2 example also changes register choice. Full, unabridged strings and 22 representative pairs are in `codegen-final-analysis-1.json`. The 22 full-instruction multisets differ, so opcode histogram equality must not be described as identical instruction streams.

| Scope / EP / global tokens | Cross-target pairs | Repeat pairs |
|---|---:|---:|
| native / 4 / 1 | 8 | 4 |
| native / 4 / 2 | 8 | 4 |
| native / 4 / 4 | 0 | 8 |
| native / 4 / 8 | 0 | 8 |
| native / 4 / 16 | 16 | 8 |
| native / 4 / 32 | 16 | 8 |
| native / 4 / 64 | 16 | 8 |
| native / 4 / 128 | 16 | 8 |
| native / 4 / 256 | 16 | 8 |
| native / 4 / 512 | 8 | 4 |
| native / 4 / 4096 | 16 | 8 |
| native / 4 / 8192 | 16 | 8 |
| native / 4 / 16384 | 0 | 8 |
| native / 8 / 1 | 16 | 8 |
| native / 8 / 2 | 16 | 0 |
| native / 8 / 4 | 16 | 0 |
| native / 8 / 8 | 16 | 8 |
| native / 8 / 16 | 16 | 8 |
| native / 8 / 32 | 0 | 16 |
| native / 8 / 64 | 0 | 16 |
| native / 8 / 128 | 16 | 8 |
| native / 8 / 256 | 16 | 8 |
| native / 8 / 512 | 32 | 16 |
| native / 8 / 4096 | 32 | 16 |
| native / 8 / 8192 | 32 | 16 |
| native / 8 / 16384 | 32 | 16 |
| uniform128 / 4 / 128 | 8 | 0 |

**Reproduction:**

```bash
python3 optimization/arch-target-20260925/compare_arch_codegen.py \
  --campaign optimization/arch-target-20260925/final-evidence/abba-v2 \
  --output /absolute/new/path/codegen-comparison.json
```

`sm_100f` is preserved in PTX; CUDA 13.2 cuobjdump renders its target as bare `sm_100`. `sm_103a` target is checked strictly. Static counts include padding and non-loop instructions, not dynamic execution. `SHARED` is static metadata, not total dynamic allocation. Resource reports are function-matched and read-hashed, but their hashes were not part of the original worker sidecar; PTX/CUBIN/SASS hashes were. See the separate performance auditor for timing/numerical qualifications.
