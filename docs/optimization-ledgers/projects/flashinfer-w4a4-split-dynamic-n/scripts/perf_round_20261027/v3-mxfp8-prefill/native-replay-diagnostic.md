# V3 MXFP8 8192: bounded native replay diagnostic

Retained source `f7182d5c`; no kernel, benchmark-default, sampler, tactic, or original-cache change. A fresh private one-bucket native AUTO run used the public `cuda_graph_profile_replays=10`: 10 repeats × 10 cold-L2 CUDA-event samples per tactic, 320 admitted tactics. The final public closure still used 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples.

| Native order | Route N | FC1/FC2 M | FC1/FC2 K steps | Shared CLC | Native median (us) |
| --- | --- | --- | --- | --- | --- |
| 248 | 128 | 256 / 256 | 4 / 4 | off | 529.744 |
| 312 | 256 | 256 / 256 | 4 / 4 | off | 531.104 |
| 224 | 128 | 128 / 256 | 4 / 4 | off | 551.232 |
| 240 | 128 | 256 / 128 | 4 / 4 | off | 552.928 |
| 250 | 128 | 256 / 256 | 4 / 8 | off | 552.928 |

The selected tactic remained N128, only 0.257% ahead of N256 in this native profile. Its separate actual-public-route latency was **482.628 us**. The prior same-source CAAC pair favored N256 by 1.08610× on actual routes and 1.01780× after substituting synthetic expert IDs. Neither pair replaces a published row.

## Routing identity and geometry boundary

The native observer asserted `[8192,7168]` activation shape on every one of 320 profile calls. With the explicit `(8192,)` bucket set, the source derives min/opt 8192 and upper bound infinity. That upper bound is cache coverage; allocation and profiling use opt 8192. The private cache also records 8192-row dynamic inputs.

The retained runner constructs `CuteDslMoEInputsHelper(256,8,32,0)` with default seed 515. Its approx-max formula gives `ceil(8192 + sqrt(8192*ln(8))) = 8323`: first three experts have 261 assignments, remaining 29 have 260. The helper samples CPU permutations under `torch.random.fork_rng(devices=[])` and `torch.manual_seed(515)`, then restores ambient CPU RNG state. The deterministic permutations do not depend on the benchmark CUDA RNG context.

The earlier synthetic pair **observed** that histogram and expert-ID SHA `6ceed231361c61fc20b103f974ac48198c1485308948a9b17c3436308446b2fe` in all four arms. The native diagnostic did **not** capture its synthesized expert-ID hash, histogram, or helper instance state. Identical source plus this deterministic hook predicts the same routing, but does not establish observed byte identity. We therefore do not attribute the different ranking solely to timer noise or sample count.

For the source-predicted balanced histogram, N128 has 96 live padded route tiles / 12,288 padded rows; N256 has 64 / 16,384. Both execute 8,704 dynamic MMA rows after per-expert 16-row rounding. The allocation upper bounds allow arbitrary 8192×8 assignments across 32 local experts: N128 543 tiles / 69,504 rows; N256 287 / 73,472. These maximum capacities differ from live route padding and from the approx-max local load. FC1/FC2 compiled geometry from both prior synthetic arms exactly matches the corresponding native compilation records, including stages, SMEM, accumulator overlap and TMEM columns.

The earlier synthetic pair replaced only expert IDs, retaining public activations, activation scales and routing weights. Native AUTO reinitializes all dynamic inputs: activations, scales and routing weights have separate seed-515 initializers, then the hook replaces IDs. Thus even proven ID equality would not prove identical complete profile inputs or timer closures.

## Cost and conclusion

The diagnostic took 190.22 s end to end; summed `_profile_single_kernel` calls took 173.32 s. There were 114 core `cute.compile` API calls, with compile/cache-load time not isolated. The previous published 8K AUTO context took 12.15 s after earlier in-process shapes; this is not a controlled 10-versus-100-sample cost comparison. The increase from 10 to 100 samples is 10×, not 100×.

The two leading tactics were profiled about 54.5 s apart with compilation interleaved. One-hertz clock/temperature telemetry is not synchronized to kernel samples and cannot assign the exact clock to either median. The longer diagnostic did not change the winner. **No benchmark default override, sampler change or further AUTO rerun is justified by this run.**
