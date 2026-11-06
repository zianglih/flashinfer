## Native-code parity and retained raw-probe reduction

Fresh `cleanup-codegen-1` completed all five serial stages on C2 `hu-pdx-38`, EP4 NVIDIA B300 SXM6 AC, `nvcr.io/nvidia/pytorch:26.05-py3`, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CUDA 13.2, CUTLASS DSL 4.8.0 and CUPTI 13.4.0. The fixed uniform fixture is H6144/I2048/E256/top-8, 256 source tokens per rank (1,024 total), M256/K256, G512, two-CTA clusters, `epi_warps`, atomic scheduling, deterministic combine, and two scheduler stages. The launch uses the native full grid.

- **Cleanup parity:** measured raw-probe-only x8 commit `5f2094b` → shared-helper cleanup `d453eb4`. All four input ABIs at both N64 and N128 have byte-identical PTX, CUBIN and complete SASS files, identical native instruction text/PCs, and identical complete resource records. The inherited transform and transport cleanup changes no ordinary generated code in these eight specializations.
- **Optimization diagnostic:** original x8 commit `002ef145` → cleanup x8 commit `d453eb4`, fixed N64. The actual full kernel has 16 fewer static instructions in every ABI; repeated FC1/FC2 K-loop bodies have 5/8 fewer respectively. This is a fresh x8-to-x8 comparison, not a subtraction from the withdrawn x16 experiment.
- **Resources:** every one of the 20 compiled variants reports `REG=96`, `STACK=0`, `LOCAL=0`, `SHARED=1024`; none contains native `LDL`, `STL`, or `PMTRIG`. Constant-bank usage is also unchanged within each comparison: bank 2 is 16 bytes; bank 0 is 2,208 bytes for vector hidden inputs and 2,224 for strided inputs.
- **Execution checks:** each stage used the unchanged checked wrapper (3 warmups, 100 untrimmed cold-L2 CUDA-graph CUPTI samples), then passed finite output, repeated BF16 bit equality and the independent `finite_bf16_bits` reference on all four ranks: 20 rank checks, each covering 1,572,864 output elements. Source/fixture hashes, cross-stage input/weight/output hashes, helper identities, subprocess exit receipts and all sample/log closure checks pass. Only one ABI executes per stage; the other three receive compilation/codegen coverage.
- **Boundary:** the codegen timings are diagnostic and excluded from end-to-end speedup tables. Static counts are not executed-instruction counts and establish no speedup. This fixed G512 uniform workload does not prove code identity for every capacity, tactic, or native H7168 shape. Final-source performance, IKET tracing and the strict numerical suite are reported separately.

| N | ABI | Whole instructions, measured → cleanup | FC1 K-loop | FC2 K-loop | PTX/CUBIN/SASS/resources equal |
| ---: | --- | ---: | ---: | ---: | --- |
| 64 | int32-strided | 5168 → 5168 | 228 → 228 | 231 → 231 | yes |
| 64 | int32-vector | 5112 → 5112 | 228 → 228 | 231 → 231 | yes |
| 64 | int64-strided | 5168 → 5168 | 228 → 228 | 231 → 231 | yes |
| 64 | int64-vector | 5112 → 5112 | 228 → 228 | 231 → 231 | yes |
| 128 | int32-strided | 5656 → 5656 | 228 → 228 | 231 → 231 | yes |
| 128 | int32-vector | 5600 → 5600 | 228 → 228 | 231 → 231 | yes |
| 128 | int64-strided | 5656 → 5656 | 228 → 228 | 231 → 231 | yes |
| 128 | int64-vector | 5600 → 5600 | 228 → 228 | 231 → 231 | yes |

| N64 ABI | Whole, original → cleanup | FC1 K-loop | FC2 K-loop | Native TRYWAIT, whole |
| --- | ---: | ---: | ---: | ---: |
| int32-strided | 5184 → 5168 | 233 → 228 | 239 → 231 | 106 → 102 |
| int32-vector | 5128 → 5112 | 233 → 228 | 239 → 231 | 106 → 102 |
| int64-strided | 5184 → 5168 | 233 → 228 | 239 → 231 | 106 → 102 |
| int64-vector | 5128 → 5112 | 233 → 228 | 239 → 231 | 106 → 102 |

The source removes initial/next raw-TMA lookahead probes while retaining the blocking raw wait and both TMEM availability probes. In each native FC1/FC2 K-loop, `SYNCS.PHASECHK.TRANS64.TRYWAIT` sites decrease from four to three. The blocking wait still lowers to native TRYWAIT instructions; their presence does not mean the removed lookahead remains. Both loops retain eight weight-store instructions and 136 conversion/scale-family instructions. No loop wait helper is removed: each phase still has two identified out-of-line wait paths.

For the representative Int32/vector N64 ABI, the per-K native wait sites are:

| Phase | Original raw wait / TMEM wait / raw lookahead / TMEM lookahead PCs | Cleanup raw wait / TMEM wait / TMEM lookahead PCs |
| --- | --- | --- |
| FC1 | `0xe600`, `0xe660`, `0xe800`, `0xf3f0` | `0xe5b0`, `0xe610`, `0xf350` |
| FC2 | `0xf500`, `0xf580`, `0xf740`, `0x10380` | `0xf440`, `0xf4b0`, `0x10230` |

FC1 opcode delta (cleanup − original): `BRA −1, LEA −1, S2R −1, SHF.L.U32 −1, TRYWAIT −1`. FC2: `BRA −1, IADD3 −1, ISETP.GT.U32.AND −1, LEA −1, LOP3.LUT −2, S2R −1, SHF.L.U32 −1, TRYWAIT −1, VIADD +1`. Full instruction bodies, addresses and resource records are preserved in the per-ABI reports.

| Source | Commit | Package SHA-256 |
| --- | --- | --- |
| original | `002ef1454cbacde09972ed5e2ec7dcfe37e55749` | `c366a5e7d7c7aa82034f339a959a058945948381157618bee9139d9005f77eff` |
| before | `5f2094b3b9f7cfbc724d84794632e278331ffd98` | `a0ee8df00da58df7b871ab7a45a93c89df3c5ed221a7cdc3daa0429dba686b8a` |
| after | `d453eb4f49f0bb38cf828f94c5588ec05d1b5b2c` | `b522ae25090f152c4fda9c364de7fdb256e542eaf1bb4c95c622a4b62670264e` |

Reproduction uses the frozen helper set in `optimization/cleanup-20260925/codegen-frozen-bundle.json`:

```bash
python cleanup-20260925/cleanup_codegen.py --label cleanup-codegen-1 \
  --output /workspace/hashinfer-trace/optimization/results/cleanup-codegen-1 --execute
```

All five process exits and the final native-parity gate succeeded. The collector copied 180 selected files without compiler caches. Local re-audit passed independently.

Project-local evidence: `optimization/results/cleanup-codegen-1-collected/` (raw artifacts, logs and receipts), `optimization/results/cleanup-codegen-1-local-audit/audit.{json,md}` (re-audit), and `optimization/cleanup-20260925/CODEGEN.md` (protocol). The top-level completion receipt binds remote audit SHA-256 `412a2b1620b449db7db61a1b296b9aab43e12faa2b6592e7c2f815644b4b6e27` and driver-provenance SHA-256 `e9adc52d4fd8daa749f98b2727164c9ac98ce8b81d6c7f05d4b545e70e7aac9f`.
