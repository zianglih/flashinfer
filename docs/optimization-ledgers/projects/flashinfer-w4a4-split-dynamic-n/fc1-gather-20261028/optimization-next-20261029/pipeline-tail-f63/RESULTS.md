# Operand-only terminal-drain result

Retained in `3b8c1c9e3b94`, based on f63e9485. The measured source and patch remain frozen in this ledger; W4-only formatting is AST equivalent. The current patch changes only operand all-slot tails. Accumulator leader-only last-slot tails are unchanged.

Existing exact tests: **8 passed per arm**, 16 total. One/two-CTA swap MXFP8, MXFP4x8 and NVFP4 K tails; W4A16 old/new layouts and route-boundary tails. Full source guards and prelaunch executable register guards passed. **14 compiled kernels per arm**; all register/stack/local resources unchanged and zero local load/store sites. The end-to-end screen below is complete.

| Kernel | CTA group / cluster | Stages | Non-NOP SASS removed | Registers | Wait sites |
|---|---:|---|---:|---:|---:|
| 00 Float8E4M3FN swap FC1 | 1 | 5 | 11 | 168 | 13 |
| 01 Float8E4M3FN swap FC2 | 1 | 5 | 11 | 82 | 11 |
| 02 Float8E4M3FN swap FC1 | 2 | 9 | 23 | 168 | 23 |
| 03 Float8E4M3FN swap FC2 | 2 | 7 | 17 | 100 | 14 |
| 04 Float4E2M1FN swap FC1 | 1 | 9 | 23 | 168 | 17 |
| 05 Float4E2M1FN swap FC1 | 1 | 3 | 5 | 168 | 11 |
| 06 W4A16 FC1 | (2, 1) | 4/2/2 | 16 | 96 | 38 |
| 07 W4A16 FC2 | (2, 1) | 4/2/2 | 18 | 128 | 42 |
| 08 W4A16 FC1 | (2, 1) | 4/2/2 | 16 | 96 | 38 |
| 09 W4A16 FC2 | (2, 1) | 4/2/2 | 18 | 128 | 42 |
| 10 W4A16 FC1 | (1, 1) | 7/3/2 | 38 | 96 | 44 |
| 11 W4A16 FC2 | (1, 1) | 7/3/2 | 39 | 128 | 48 |
| 12 W4A16 FC1 | (2, 1) | 4/2/2 | 16 | 96 | 38 |
| 13 W4A16 FC2 | (2, 1) | 4/2/2 | 18 | 128 | 42 |

Every PTX mbarrier wait/arrival, TMA issue and MMA issue site count matches between paired kernels. SASS reductions come from repeated dynamic-index increment/select and shared-barrier address calculations; the expected phase is computed directly for a compile-time physical slot. NOP count differences are excluded above.

All-stage capacity, inter-work-tile prefetch, PDL, CLC, metadata, steady-state loops and store drains remain unchanged. The CPU proof checks the exact (slot, phase) multiset for 4160 states. Bound-method identity is recorded in `evidence/method-audit-v2.json`: only TmaAsync, TmaUmma, and AsyncUmma operand subclasses inherit the all-slot SDK implementation.

The first exploratory R0 incorrectly included accumulator overrides. It was stopped, restored, and excluded. Its raw source/log/capture evidence is retained in `evidence/r0-stopped/`; the complete passing R1 is at `evidence/{candidate,control}/`.

This optimization affects terminal draining once per CTA; instruction sanity is the motivation, and the completed screen below is performance neutral.

## Fixed-winner end-to-end screen

Twenty source-paired C-A-A-C cells,100 strict CUPTI samples per phase, native winners unchanged, input quantizer included where applicable; f63 control and operand-only candidate. Four models,EP/TP,decode32/prefill4096,allfive dtype modes represented.

Aggregate **+0.0045%**: neutral. Decode **+0.016%**, prefill **-0.007%**. Excluding the high-repeat-spread K3 TP W4A16 prefill cell: **+0.022%**. All sampled clocks2032MHz, reason0. No speedup claim; retain for instruction sanity. All source,route,tactic,runtime register guards passed.

| Workload | Tokens | Dtype | Control μs | Candidate μs | Change | Repeat spread C/A |
|---|---:|---|---:|---:|---:|---:|
| ep-v3-w4a4 | 32 | CuteDSL W4A4 | 99.713 | 99.713 | +0.000% | 0.06% / 0.06% |
| ep-v3-w4a4 | 4096 | CuteDSL W4A4 | 199.257 | 199.249 | +0.004% | 0.27% / 0.02% |
| tp-v3-mxfp | 32 | CuteDSL MXFP8 | 168.865 | 168.273 | +0.352% | 0.06% / 0.21% |
| tp-v3-mxfp | 4096 | CuteDSL MXFP8 | 456.410 | 456.578 | -0.037% | 0.01% / 0.04% |
| ep-v41-flash-mxfp | 32 | CuteDSL MXFP4x8 | 119.833 | 119.673 | +0.134% | 0.04% / 0.04% |
| ep-v41-flash-mxfp | 4096 | CuteDSL MXFP4x8 | 349.051 | 349.036 | +0.004% | 0.22% / 0.14% |
| tp-v41-flash-per-token | 32 | CuteDSL PER-TOKEN | 146.177 | 146.153 | +0.016% | 0.11% / 0.10% |
| tp-v41-flash-per-token | 4096 | CuteDSL PER-TOKEN | 536.596 | 536.701 | -0.019% | 0.02% / 0.03% |
| ep-kimi-k3-mxfp | 32 | CuteDSL MXFP4x8 | 167.456 | 167.441 | +0.009% | 0.11% / 0.02% |
| ep-kimi-k3-mxfp | 4096 | CuteDSL MXFP4x8 | 391.705 | 391.169 | +0.137% | 0.13% / 0.39% |
| tp-kimi-k3-w4a4 | 32 | CuteDSL W4A4 | 168.049 | 168.417 | -0.219% | 0.09% / 0.02% |
| tp-kimi-k3-w4a4 | 4096 | CuteDSL W4A4 | 550.788 | 549.460 | +0.242% | 0.05% / 0.16% |
| ep-nemo3-ultra-per-token | 32 | CuteDSL PER-TOKEN | 110.249 | 110.225 | +0.022% | 0.25% / 0.15% |
| ep-nemo3-ultra-per-token | 4096 | CuteDSL PER-TOKEN | 325.698 | 325.962 | -0.081% | 0.08% / 0.13% |
| tp-nemo3-ultra-mxfp | 32 | CuteDSL MXFP8 | 180.361 | 180.392 | -0.018% | 0.12% / 0.03% |
| tp-nemo3-ultra-mxfp | 4096 | CuteDSL MXFP8 | 441.506 | 441.454 | +0.012% | 0.18% / 0.07% |
| ep-v3-w4a16 | 32 | CuteDSL W4A16 | 107.705 | 107.648 | +0.053% | 0.01% / 0.06% |
| ep-v3-w4a16 | 4096 | CuteDSL W4A16 | 285.130 | 285.160 | -0.011% | 0.24% / 0.05% |
| tp-kimi-k3-w4a16 | 32 | CuteDSL W4A16 | 190.617 | 190.977 | -0.189% | 0.16% / 0.00% |
| tp-kimi-k3-w4a16 | 4096 | CuteDSL W4A16 | 718.892 | 721.191 | -0.319% | 5.26% / 4.80% |

The K3 TP W4A16 4096-token comparison is inconclusive: control/candidate repeat spreads5.26%/4.80%; its nominal−0.319% is smaller than that variability. Every other repeat spread is≤0.39%. Positive change means control/candidate−1. Raw timings,activities,telemetry and source proofs are in perf-evidence/.
