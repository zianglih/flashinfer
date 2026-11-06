# Post-wait expert-alpha reuse

The candidate caches each expert scale immediately after the existing accumulator wait and reuses that scalar across the tile epilogue. It changes three lines and adds no behavior knob, synchronization, or layout rule. Both the overlapping-FC1 and ordinary epilogue branches receive the same cached scalar.

The retained per-token M512/N128 FC2 image contains two `ld.global.b32` loads from exactly the same alpha address, lowered to `LDG.E` at PCs `0x3b80` and `0x79e0`; the address registers are unchanged between them. `native-motivation.json` binds the original captured PTX/cubin and exact locations. The first expert-alpha access remains after accumulator readiness; previous pre-wait alpha-prefetch experiments are not being repeated.

Alpha is a read-only per-expert scale tensor. The public MoE flow allocates output/intermediate storage separately. No alias assertion is added, and concurrent writes to alpha during the kernel are not introduced or synchronized. Public input/output aliasing that would race across CTAs is not a useful supported baseline for the earlier repeated reads either.

The source peer passes (`audits/epilogue-alpha-reuse-peer.json`) and scoped pre-commit checks pass. Qualification prepares nine paired signatures covering wide SF16/SF32/BF16, narrow M512/N16 two-channel epilogues, representative one-channel cases, and native one/two-CTA CLC with PDL. It keeps the existing exact oracle and compiler options.

The first deployment did **not** execute: HAI reported that the original devbox no longer existed despite returning exit code zero. That output is preserved in `qualification/launch-unavailable.json`. That attempt launched nothing; the separate recovery attempt subsequently completed the qualification below. The completed review checkout has been retired after rejection; its unstaged source/patch are preserved in `retirement/`. The retained swap implementation is unchanged.

## Exact/native qualification

All 18 exact calls passed on recovery GPU2, with 27 matched native image pairs. Both source inventories and all four current release-cache libraries passed pre/post checks. The original failed deployment receipt remains separate. GPU2 was verified idle and released afterward.

All seven changed images remove one expert-alpha global load; every remaining captured image is byte-identical (20 pairs). There is no register increase or local memory, and shared-memory footprint/residency remain equal. The four representative one-channel signatures cover one/two-CTA CLC+PDL as well as ordinary scheduling. Wide FP4/FP8/BF16 output and narrow N16 two-channel epilogues are covered.

| Case | Stage | Registers | Static non-NOP | Static global loads |
|---|---|---:|---:|---:|
| per-token-14-Relu2 | FC2 | 128 → 128 | 3041 → 3037 | 18 → 17 |
| w4a4-14-Relu2 | FC2 | 114 → 110 | 2687 → 2682 | 10 → 9 |
| mxfp8-14-Relu2 | FC2 | 102 → 100 | 2756 → 2753 | 10 → 9 |
| w4a8-16-Relu2 | FC1 | 168 → 168 | 2415 → 2412 | 20 → 19 |
| w4a8-16-Relu2 | FC2 | 70 → 68 | 1410 → 1401 | 10 → 9 |
| w4a4-16-Relu2 | FC1 | 168 → 168 | 1937 → 1930 | 29 → 28 |
| w4a4-16-Relu2 | FC2 | 83 → 82 | 1349 → 1340 | 10 → 9 |

`qualification-summary.json` preserves every resource and binary comparison; `alpha-load-removal.json` traces each affected PTX argument and expert-indexed address. This is bounded exact/native qualification, not performance evidence, sanitizer coverage, a full-suite result, or a claim that every possible one-channel specialization is binary-identical. The subsequent authorized screen has completed; see `RESULTS.md` for all cells, resource changes and limitations. The candidate is rejected after the complete screen and independent root raw replay.

## Performance screen complete

The authorized 56-cell CAAC screen uses the same 28 supported swap model/topology/dtype arms at 32 and 4096 tokens, with frozen choices/routes, strict CUPTI, 100 samples, 10 warmups, cold-L2 graph replay and activation quantization included for NVFP4. Config `9e1e4a3a` uses GPUs 0/2 on `fi-gather-pipeline-recovery-1030`; launch PID 12008. All 12 execution/observer helper bytes match the independently reviewed readiness harness, including passive shared-memory and residency recording. The recovered release-library hashes, exact/native gate and source inventories are bound by preflight. All 56 cells completed and passed raw replay; GPUs 0/2 are released. The remaining 308-point run was not started. No W4 timing is included.
