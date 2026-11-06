Recommend retaining exact R5 for the final full-grid run. All twelve affected model/format geometric means exceed 1.0; the largest observed affected loss is 0.59% (K3 MXFP4x8 T32). This is a single five-token screen of the combined change, not a repeated non-regression or isolated-mechanism claim.

| Model | W4A4 | Per-token | MXFP8 | MXFP4x8 |
|---|---:|---:|---:|---:|
| v3 | 1.002613x | 1.010589x | 1.001773x | 1.006333x |
| v41-flash | 1.009166x | 1.010934x | 1.005301x | 1.007417x |
| kimi-k3 | 1.007087x | 1.005464x | 1.001117x | 1.008268x |

Ratios are clean dea2 latency / R5 latency, over tokens 4,32,128,512,4096. NV includes initial activation quantization; MX excludes it. Same model, GPU UUID, exact routing IDs/weights/histogram, input recipe, runtime and native 10-warmup/100-iteration cold-L2 CUDA-graph CUPTI timing are checked. Fused finalize is disabled.

The report verifies 75 raw comparisons, all six completed source-before/after receipts, 112 input hashes, and exact saved outer-five-field tactic versus the last actual private-core host call for all 60 affected points. It separately checks that the 15 unchanged W4A16 calls bypass this core. Requested CLC is recorded; effective CLC is established by the separate 72-replay gate, not inferred from the host boolean.

V4.1/K3 mixed T4096 improve 3.11%/3.48%. The previously observed static-only mid-decode losses are recovered by AUTO choosing CLC in many of those rows. W4A16 has unchanged implementation but V4.1/K3 T4096 varies +5.57%/-5.16%, so small cross-sweep differences remain subject to drift and tactic variation. Reused TRT numbers in comparison.json are explicitly provisional cross-sweep comparisons; final public tables must measure TRT on the retained source campaign.

| Model | R5 NV wall (s) | R5 MX wall (s) | R5 total / R3 total |
|---|---:|---:|---:|
| v3 | 366.787 | 384.797 | 1.852x |
| v41-flash | 397.667 | 355.935 | 1.642x |
| kimi-k3 | 389.345 | 463.521 | 1.798x |

These are process wall times including AUTO setup/compilation and profiling, not an isolated tuner benchmark. The raw candidate count doubles 180→360 (resource-admitted 160→320); the per-configuration specialization upper bound grows from 28 FC1+28 FC2 to 56 FC1+28 FC2. No actual unique compiled-kernel count was instrumented.

Canonical source: evidence/generality-scheduler-cache-r5/source.json; full patch af2426e28bd67ac537adf7d31f979bd40aa22584fb600d5df849ee4677d12037. Comparison SHA256: c579e8d2ba4bb7e9d314314513f2f73586e1830b1c8780f06698ebc98c4742d2.

Exact-source validation: 68 existing tests and 72 changing-input/route scheduler replays passed. Public signatures and benchmark source are unchanged. Manual legacy tactics remain accepted; the v4 cache namespace ensures native AUTO searches the expanded internal K/scheduler space.
