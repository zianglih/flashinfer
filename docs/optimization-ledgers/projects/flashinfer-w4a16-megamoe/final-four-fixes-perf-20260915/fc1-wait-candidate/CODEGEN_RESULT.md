# FC1 duplicate-wait ordinary codegen result

**Result:** the deletion changes machine code for both tested specializations; it was not already a machine-code no-op. All output checks remain exact. No performance timing was run.

Native a48e5706 → isolated, unpushed 979ac4bd; the sole source change is the three-line early FC1 wait/comment deletion. The centralized R1 wait, release waits, current warp addressing and scheduler fixes remain.

| Global tokens | Rank pairs | PTX load waits | PTX store waits | SASS slots | Executable text before → after |
|---:|---:|---:|---:|---:|---|
| 128 | 8 | 18 →16 | 14 →14 | 5,424 →5,424 | `cc98894fd895` →`d5f1c72c668e` |
| 512 | 8 | 18 →16 | 14 →14 | 5,424 →5,424 | `84d39252e86c` →`ea802497f4d0` |

The retained PTX differs by the two early load-wait deletions. Representative SASS removes interior NOPs at baseline PCs 0x9250 and 0x9d20, changes a small FC1 MUFU/FMUL/LEA/register/address schedule, and grows trailing padding from 13 to 15 NOPs. The last non-NOP branch moves from 0x15220 to 0x15200. Thus total opcode counts stay equal (including DEPBAR/FENCE counts), while the executable path loses two NOP slots. Large raw-PC differences include shifted instructions and control encodings; they do not represent 3,115 new operations. No assertion about two dedicated hardware wait instructions or runtime speedup follows.

- Scope: EP8, global tokens 128/512, fixed N64 epi winner proven against all 64 corresponding rank/winner records in the completed native ABBA. Exact same external PDL-disabled fixture producer. Ordinary O3 with initial maxrregcount96; no sanitizer or additional guardrail option. Existing epilogue 144 register redistribution is unchanged.
- Validation: 32 rank/token outputs across two sources matched canonical BF16 hashes, remained finite and bit-repeatable; 16 raw tensor files verified on CPU. All 32 core compilations retained executor-equal PTX/CUBIN/SASS. No timing records.
- Evidence: 175 files / 44,447,440 bytes collected and hashed; full source/helper/environment and supervisor/two-launcher ownership closure passed before and after transfer. All 8 GPUs idle. Original source/runtime/cache artifacts remain unchanged.

Snapshot: `/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/final-four-fixes-perf-20260915/fc1-wait-candidate/collected/20260916T031645Z-377734b09b374f709601f2d8ad669eb4`
Final closure SHA256: `c892b2765232ca48cfe071b9ae92bb067b908ca7d9f58444f06b21b3129f6108`
Runtime handoff SHA256: `84bacbdf1feb2c6807857968c6bbdced1349271e3fbdd83333bd7b2d6d80ba6b`

The exact executed command (its output directory is immutable and must be changed for any future rerun):

```bash
/workspace/hashinfer-w4a16-megamoe/.venv-hashinfer/bin/python -B /workspace/flashinfer-w4a16-megamoe/final-four-fixes-perf-20260915/fc1-wait-candidate/run.py --before /workspace/flashinfer-w4a16-megamoe/fence-perf-20260915/scheduler-copy-fix/source --after /workspace/flashinfer-w4a16-megamoe/final-four-fixes-perf-20260915/fc1-wait-candidate/source --output /workspace/flashinfer-w4a16-megamoe/final-four-fixes-perf-20260915/fc1-wait-candidate/capture-001 --native-validation /workspace/flashinfer-w4a16-megamoe/final-four-fixes-perf-20260915/prior-native-validation.json --dependency-cache /workspace/flashinfer-w4a16-megamoe/fence-perf-20260915/abba-o3-001/cache/after --closure /workspace/flashinfer-w4a16-megamoe/final-four-fixes-perf-20260915/fc1-wait-candidate/prior-closure.json --execute
```

Recompute the local instruction comparison using `compare-code.py` on the snapshot’s `evidence/capture-001/baseline` and `candidate` directories, choosing a new `--output` path. The comparator parses exact CUDA ELF text sections and validates complete retained SASS PC coverage; it does not load a CUDA module.
