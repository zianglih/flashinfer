# Independent W4 operand-stage qualification

Frozen candidate: `cf78403f1572bb8fe62f9ab5c3056d6d671bb82224631f572d127322887f44e2`, base `ce4a7d8c2836c0f8a871ebf5cfe87633172360d8`. Source remains unstaged in `flashinfer-w4a16-stages-review`.

- Five native fixed-winner FC1/FC2 pairs compiled on B300 SM103, CUDA13.2, CuTe4.8, `nvcr.io/nvidia/pytorch:26.05-py3`. Neither owned MoE kernel launched during this compile gate.
- Actual `SmemAllocator._smem_alloca` calls captured layout cosizes, sizes, alignment and offsets in compiler context. All allocations fit and do not grow.
- Loaded FC1 registers remain96 (640threads), FC2 registers128 (512threads); all20 kernels have LOCAL0 and no LDL/STL. N192 binaries are identical between arms.
- Existing39 tests passed:33 route-boundary/layout/activation/partialK tests,2 longK numerical tests and4 wrapper CUDAgraph tests. All40 loaded numerical kernels have LOCAL0; maximum observed allocation224,256B.
- LongK tests use default N128 with A2/B5/D2. FC1K1024 has4 stage iterations and many persistent worktiles; FC2K2048 has8 stage iterations and wraps B5 within each worktile. Both gated and nongated cases pass. Graph replay is separate repeated-launch coverage, not evidence of within-launch wrapping.
- The existing partialK case includes H384 with K256 stages. No new repository tests or sanitizer.
- Two harness-only failed attempts are preserved: allocation introspection outside MLIR context, then a missing dump-directory mkdir. Both stopped before the first guarded MoE launch; sources unchanged.

| Workload | FC | A/B/D/C old → new | Shared bytes old → new | Static non-NOP delta |
|---|---|---|---:|---:|
| ep-kimi-k3-w4a16 T4096 | FC1 | 4/4/2/4 → 2/5/2/4 | 222,208 → 218,112 | -16 |
| ep-kimi-k3-w4a16 T4096 | FC2 | 4/4/2/2 → 2/5/2/2 | 222,208 → 218,112 | -15 |
| ep-kimi-k3-w4a16 T8192 | FC1 | 3/3/2/5 → 3/3/2/5 | 224,256 → 224,256 | +0 |
| ep-kimi-k3-w4a16 T8192 | FC2 | 3/3/2/2 → 3/3/2/2 | 220,160 → 220,160 | +0 |
| ep-v41-flash-w4a16 T4096 | FC1 | 4/4/2/4 → 2/5/2/4 | 222,208 → 218,112 | -16 |
| ep-v41-flash-w4a16 T4096 | FC2 | 4/4/2/2 → 2/5/2/2 | 222,208 → 218,112 | -15 |
| tp-nemo3-ultra-w4a16 T16384 | FC1 | 4/4/2/2 → 2/5/2/2 | 222,208 → 218,112 | -16 |
| tp-nemo3-ultra-w4a16 T16384 | FC2 | 4/4/2/2 → 2/5/2/2 | 222,208 → 218,112 | -15 |
| tp-v3-w4a16 T8 | FC1 | 9/9/3/5 → 8/12/3/5 | 214,016 → 207,872 | +27 |
| tp-v3-w4a16 T8 | FC2 | 7/7/3/7 → 6/9/3/7 | 216,064 → 214,016 | +13 |

The narrow cases add terminal-drain instructions for additional B slots. Lower shared memory and larger B capacity are not sufficient retention criteria; the predeclared32-cell CAAC screen will include all five unchanged N192 controls and report per-FC/whole-chain latency, losses, and repeat spread.

Raw evidence: `codegen-evidence/MANIFEST.json`, `gate-evidence/MANIFEST.json`; checked reports: `codegen-analysis.json`, `gate-analysis.json`, `independent-codegen-audit.json`.
