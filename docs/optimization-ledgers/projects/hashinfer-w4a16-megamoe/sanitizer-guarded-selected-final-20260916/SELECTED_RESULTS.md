# Selected implementation: guarded memcheck

Source: HashInfer `dbd3cead8837a251d7fcefc57a79b8d7cc87e5af`, paired with FlashInfer `4d183b836bb8ceefea2fcd723f078b3a4935e6b6`. The early FC1 wait is retained; FC2 shares transpose completion waits across disjoint halves. HashInfer head `1ba33fa` changes only the README source reference.

Each EP batch runs GLM-5 H6144/I2048/E256/top-k8, random/skewed routing and global tokens 1/16384. Every case scans all four tactics, O2/O3, eager execution and CUDA graphs against the full reference. Compiler TMEM guards preserve O2/O3 and maxregs96. Compute Sanitizer 2026.3 runs memcheck with bulk-copy checking and stream-ordered race tracking; tensor-form TMA checking is disabled for the independently reproduced legal group2 peer-barrier checker false positive. No kernel filters or reference cache are used.

| EP | Cases | Execution configurations | Reference checks | Output-pair checks | Repeat checks | Memcheck |
|---:|---:|---:|---:|---:|---:|---|
| 4 | 4/4 | 64/64 | 192/192 | 480/480 | 160/160 | zero errors on all four ranks |
| 8 | 4/4 | 64/64 | 192/192 | 480/480 | 160/160 | zero errors on all eight ranks |

EP4 completed all five supervisor phases with exit zero. All comparisons require finite BF16 bit equality, including signed zero; all numerical error maxima are zero. The guarded phase took 3068.072286 seconds including compilation and instrumentation. All owned processes exited and selected GPUs 4–7 were idle; the independent original racecheck remained active on GPUs 0–3. No all-eight-idle claim is made.

EP4 full evidence: `evidence/collected/20260916T073633Z-d14c00f647fe4eb081b3ac11fcef71bb`, 835 raw files / 532,130,565 bytes. Archive: 57,561,687 bytes, SHA256 `02fea0f52dcc484aa88793d432087cb9447d54d0ae12bde1bc98650d650d79d4`. Root independently rehashed every manifest file and archive, and checked exact-count, source and scoped closure records; see `root-collection-review.json` in that snapshot.

EP8 completed all five phases with exit zero and exact finite BF16 bits throughout. The guarded phase took 3323.205032 seconds. All eight GPUs were idle and owned processes had exited at collection closure. Full evidence: `evidence-ep8/collected/20260916T075520Z-ed095d9e6d754b86b49d81a81bdaf181`, 1,631 raw files / 1,086,651,891 bytes. Archive: 116,743,748 bytes, SHA256 `5e2e7e3eb736ae50b34a4c59d1dcf513589c98a2c55b5dec1db79db6a05c232b`. The first collection attempt exceeded its inherited 120-second transport timeout during compression; its failure is preserved separately. A transport-timeout-only retry collected the same terminal evidence without rerunning GPU tests or changing the runtime.

This is instrumented memcheck coverage of the selected source, separate from the completed ordinary 60-case numerical matrix. It does not establish arbitrary global-memory or cross-rank NVSHMEM race freedom. The original unfiltered EP4 racecheck and selected worker-capped EP8 follow-up retain their own source, scope and completion records.
