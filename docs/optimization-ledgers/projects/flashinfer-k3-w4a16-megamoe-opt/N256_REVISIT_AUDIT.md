# Revisit decision: historical N256 / one-accumulator tactic

**Recommendation:** do not revive N256 merely because K3 T16384 has about 293
routes per expert. The old negative includes a workload with comparable or
greater weight-decode reuse. A bounded revisit becomes more defensible if the
current packed FC1 transpose materially improves **prefill**: that directly
changes the one-accumulator tradeoff. It would be a re-evaluation of a rejected
implementation, not a new tactic. No source edit or GPU work was performed.

## What was actually tried

The archived implementation is commit
`4db0979cff9adfe7553b5ab0fcb066a41a360616`, explicitly reverted by
`4733b060227ec8cba05c4facb2b1d65dde116225`. Its final form included both
N256/ACC1 and the refined half-width activation TMA. The original fixed-width
version is not the strongest rejected version.

| Aspect | Historical experiment | Current K3 study |
|---|---|---|
| Shape | DeepSeek D7168, E2048, N256, K8, EP8 | D3584, E3072, N896, K16, EP8 |
| Hardware | Eight B300; hu-pdx-15 | Eight B300; current replacement runtime |
| Software | CUDA 13.2, CuTe DSL 4.7.1; image 26.05-py3 | Current source/stack; historical code is not a compiled control |
| Activation | SwiGLU; FP32 alpha, optional clamp, sigmoid via EX2/RCP, two separate FP32 transposes per 64-token subtile | SiTU(4,25), retained native tanh; candidate packs two BF16 halves into one transpose |
| Final combine | Separate deterministic TopkReduce launch | Required deterministic combine fused into MegaMoE |
| Timing | 100 cold-L2 CUPTI graph samples; median rank-MAX span; hot graph scorer chooses tactic | Current native benchmark with precomputed K3 routing; reuse recorded BEFORE/intermediates |

Historical routing used the DeepSeek grouped router, random logits and fixed
small correction bias. K3 uses CPU sigmoid/bias top-k prepared before timing.
The old cold latency is not a substitute for a current measurement. Its
same-run N256-vs-N128 hot ranking still directly tests the resource tradeoff.

- Initial N256 had **zero wins in 13 points** from T1 through T4096.
- Final half-width version selected N256 only at T4096: hot score **444.0 us**
  versus **446.7 us** for the best old geometry (~0.60% lower). Cold latency
  **458.531 us** did not beat the retained baseline's **457.218 us**.
- A requested T8192 follow-up selected old N128: hot **730.4 us**, best N256
  **765.0 us**, so N256 was **4.74% slower**. There was no cold T8192 BEFORE.
- The user rejected the small sole winner and requested commit-and-revert.
  Variation in unchanged N64/N128 rows was explicitly not attributed to N256.

Source: prior project's `w4a16_optimization_experiments.md:8169–8362`,
`candidates/w4a16_n256_acc1/{README,EPILOGUE_DESIGN}.md`, and
`candidates/w4a16_n256_activation_width/README.md`. Workload verified in the
archived commit's `benchmarks/bench_moe_deepseek.py:55–67`; final-combine
separation in its `nvfp4_w4a16/frontend.py:381–415,564–579`.

## The resource cost was real

Historical native admission observed N256 **raw2 / activation2 / decoded2 /
ACC1**, 226688 bytes of dynamic shared memory, 640 threads, initial REG96,
and zero stack/local memory. N64/N128 instruction encodings and schedules were
unchanged controls. The refined N256 had 6744/6728 instructions for the two
return modes, 128 more than its original full-width implementation.

N256 uses columns 0–255 for its single accumulator and 256–511 for two decoded
K256 weight tiles. Its four 64-token epilogue subtiles reuse the accumulator
as transpose scratch. The next MMA work cannot acquire that same accumulator
until the final protected scratch reads finish. The original release stays at
the final static subtile/fallback; it does not release after an earlier valid
subtile. Thus losing ACC2 removes overlap across work tiles, not merely an
unused buffer. Current N128 has two accumulators, two decoded tiles, and the
fitter prefers three activation stages when they fit.

The final half-width loader uses a uniform per-work `valid_tokens<=128` choice,
outside the K loop, while preserving full N256 allocation/stride. It transfers
half the activation payload for those tails. For any expert count, this gives
the same aggregate nominal activation rows as full-width N128 tiles; it does
not restore the lost activation-buffer depth or accumulator overlap.

Current source pointers: `bf16_nvfp4/megamoe_kernel.py:83–109,408–431,1398–1444`
and `bf16_nvfp4/epilogue.py:533–572`. Historical scratch/release proof is in
`candidates/w4a16_n256_acc1/EPILOGUE_DESIGN.md`.

## K3 changes the balance, but not uniformly in N256's favor

The total mean routes per expert is `T*K/N`. To distinguish means from integer
tile counts, the table also gives `E[ceil(X/tile)]` under an **illustrative
unbiased routing model** `X~Binomial(T,K/N)`. These CPU calculations are not
measured histograms: fixed correction biases and grouped routing can change
the actual distribution.

| Shape / tokens | Mean routes / expert | Expected N128 tiles | Expected N256 tiles | Fewer weight-decode passes |
|---|---:|---:|---:|---:|
| Old DeepSeek / 4096 | 128.00 | 1.477 | 1.000 | 32.3% |
| Old DeepSeek / 8192 | 256.00 | 2.483 | 1.483 | 40.3% |
| K3 / 4096 | 73.14 | 1.000 | 1.000 | approximately 0% |
| K3 / 8192 | 146.29 | 1.933 | 1.000 | 48.3% |
| K3 / 16384 | 292.57 | 2.985 | 1.985 | 33.5% |

For an expert with 293 rows, N128 uses `[128,128,37]`, N256 `[256,37]`.
Both execute 304 dynamic MMA rows (`align16` per tail), and both refined
activation paths transfer 384 nominal rows. N256 saves one packed-weight load
and decode traversal, one work record per output-feature tile, and associated
pipeline setup. It does not reduce the useful activation arithmetic or the
number of valid 64-token epilogue subtiles. This mechanism was already present
in the old T8192 test; T16384 alone is not a stronger rationale.

K3 T8192 is the more distinct possible reuse point. Conversely, K3 changes
the two GEMMs as follows for M256/K256:

| Shape | FC1 output-feature tiles | FC1 K steps | FC2 output-feature tiles | FC2 K steps |
|---|---:|---:|---:|---:|
| Old DeepSeek | 16 | 28 | 28 | 8 |
| K3 | 24 | 14 | 14 | 12 |

K3's FC1 has half as many K steps per work tile, while its SiTU epilogue is
heavier than old SwiGLU. That makes the lost second accumulator more concerning
on FC1. FC2 has a longer reduction and may tolerate its epilogue better. This
is a source-level tradeoff, not a diagnosed bottleneck. W4A4 selecting N256
does not settle it: W4A4 does not reserve TMEM for decoded BF16 weights.

## What packed FC1 would change

The current packed candidate removes half the source-level FC1 scratch
transposes and their completion waits per 64-token subtile. It preserves the
FP32 alpha/SiTU arithmetic and final accumulator-release boundary. If that
shortens prefill epilogue service, it reduces the most direct ACC1 penalty and
is a concrete reason to revisit N256. It does not remove SiTU work, supply a
second accumulator, deepen the raw/B rings, or make a decode-only gain evidence
for this prefill tradeoff. Its benefit also applies to the N128 control.

If the packed result is flat in prefill, the old negative plus K3's shorter
FC1 reduction argues for deferring N256. If packed prefill improves materially,
one bounded re-evaluation can port the **final** historical N256 plus half-width
loader onto the current implementation. Keep N64/N128 untouched, preserve the
current fused combine, and add no simultaneous K128/raw-depth/scheduler axes.
Follow the current 13-point policy and existing BEFORE/intermediates rather
than repeating controls. This note does not request or prepare that run.

## Historical numerics do not qualify a current port

Old validation covered changing/empty/refill routing, long-K D7200/E2112,
partial counts 66/128/130/194, and full-plus-tail 258 routes `[256,2]`, with both
return modes and graph replay. The earlier 514-route case preceded the final
half-width loader. The final loader had 28 successful numerical rank-calls and
two graph cases per rank. These were ordinary SwiGLU paths; its historical
W4A16 oracle used `_assert_mega_oracle_term_band_close`, not today's exact SiTU
contract. A current port therefore needs the current existing zero-tolerance
checks, extended for N256 full/tail geometry, **only after a measured gain**.
