# One election per MMA stage — 2026-10-26

Independent source: `../../flashinfer-mma-election-20261026`, parent
`0def601d6603df828ea39679b41ccbce64f7f09e`. One core function changes: the
existing `elect_one()` scope moves outside the compile-time native-MMA loop.
There are no new flags or tactic choices. The entire caller, scale copies,
pipeline waits/commits, TMA loops, epilogue and arithmetic stay unchanged.
The 227-file manifest and patch remain local and unstaged.

CPU AST comparison removes only the election scope from each function and
confirms the entire module then matches. The operands/descriptors used by the
MMA helper are warp uniform; one elected lane can issue the same ordered native
instructions as repeated elections. No warp collective is moved under election.
GPU public profile replay succeeds, but exact numerical comparisons and
sanitizers have not been run for this source.

## Why inspect generated code first

Current control PTX contains repeated `elect.sync` around each MMA. Its actual
NV32 FC2 SASS already folds them into one straight-line UTCOMMA region at
`0x5c90–0x5da0`, without ELECT or branches between MMAs. Therefore source-level
election count is not evidence of executed issue overhead.

Four current saved-tactic public kernels were captured with PTX/CUBIN retention
on the exclusive c3 B300 GPU7. The same existing profiling helper and exact
current-control caches are used; source and cache immutability are verified.
Native compilation-cache sources and headers are identical and shared through
verified persistent cache links; CuTe artifacts remain source private.

| Kernel | PTX elections control → candidate | SASS elections | Registers | Static instruction words |
| --- | ---: | ---: | ---: | ---: |
| NV32 FC1 N32/M128 | 61 → 54 | 8 → 8 | 78 → 78 | 2976 → 2976 |
| NV32 FC2 N32/M128 | 79 → 72 | 11 → 11 | 92 → 92 | 3584 → 3584 |
| MX32 FC1 N16/M128 | 59 → 59 | 10 → 10 | 78 → 80 | 3120 → 3408 |
| MX32 FC2 N16/M128 | 53 → 53 | 9 → 9 | 90 → 90 | 2624 → 2848 |

Instruction words count both 64-bit halves of every encoded 128-bit instruction,
including trailing NOP padding. It is a static binary count, not executed work.
All four kernels have zero local memory and unchanged SMEM/TMEM, operand and
accumulator stage counts, and one active CTA per SM. Instruction words differ
in all four; NV is primarily scheduling/register-transfer movement, while MX
NVVM now emits two mainloop iterations (16 rather than 8 static native MMAs).
This is a code-generation change, not a demonstrated reduction in elections.

`codegen-comparison.json` binds exact word hashes, counts and resources. The
control artifacts come from the current parent campaign
`../../codegen-epilogue-prefetch-20261026`, not a historical code version.

## Bounded timing

`run_fixed.py` runs source C–A–A–C for V41 at 32,128,4096 tokens, both benchmark
families, using the unmodified public benchmark and native 10-warmup/100-repeat
cold-L2 CUDA-graph CUPTI timer. All geometry, K8/K8 and scheduler fields are held
fixed; route bytes, source pins, cache hashes and all 100 timing samples are
verified. NV includes input quantization and unchanged W4A16 as a drift control.
Fused finalize remains disabled. This diagnostic is not a native AUTO retention
campaign, and the historical tactic files supply geometry only, never timings.

Rejected after completed fixed ABBA. W4A4 speedups at 32/128/4096 tokens are
0.9992/0.9996/1.0021; MXFP8 is 0.9964/0.9988/0.9988; MXFP4x8 is
0.9947/1.0036/1.0004. This is neutral/noise rather than a useful shared policy.
The unchanged W4A16 prefill drift-control ratio is 0.9768, larger than the tiny
apparent affected improvements. No expanded AUTO campaign or further correctness
suite is justified for a rejected candidate. Full paired medians are in
`results.md`, with individual repeat values in `summary.json`.

All eight fixed-table processes completed; route bytes, source and cache pins,
and 100-sample native timer checks passed. GPU7 is idle. Canonical source and
public PR are untouched. The separate candidate remains unstaged for parent
review/cleanup; it is not a retained optimization.

## Checked prior history

The native MMA K-tail predication experiment did execute after its initial
control-only harness failure: 24 exact cases passed, but V41 NV was 0.995366x
and V3 0.999355x, so it was rejected. The old experiment README still says
pending; the later `V41_GAP_OPTIMIZATION_2026-10-25.md` and
`evidence/mma-k-tail-r2` are the final authority. This candidate does not repeat
that predication. No prior single-election attempt was found in the ledger.
