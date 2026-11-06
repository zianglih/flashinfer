# K3 routing-policy and pipeline audit

This is diagnostic work on retained `1b0f1f69`, not a production tuning-policy change.

## Tuner policy

- The functional and wrapper APIs pass real inputs to `AutoTuner.choose_one`, but the native tuner synthesizes dynamic tensors for every profile bucket and then calls `CuteDslMoEInputsHelper.inputs_pre_hook`. Even a bucket equal to the caller's token count receives synthetic routes. See `cute_dsl/tuner.py:569–673`, `autotuner/autotuner.py:2838–2854,4236–4256`.
- The helper deliberately models approximate maximum rank load, then divides that load almost equally among local experts. The extra rank quota is `ceil(mean + sqrt(mean * log(ep)))`; this is a faithful TRTLLM policy, not an accidental random initializer (`cute_dsl/_inputs_helper.py:89–115`).
- Shape profiles and synthesis-invariant runner configuration determine the cache key. Routing values are absent. An actual-route default would bind a shared shape key to one warmup distribution. The earlier exact-shape prototype was rejected: zero-local EP warmup selected a winner 12.237% slower on the real N3U per-token workload. Preserve that result in `optimization-20261027/actual-routing/holdout/RESULTS.md`; do not repeat or disguise this policy.
- Hopper already uses seeded uniform global top-k (`cute_dsl/sm90_tuner.py:275–298`), explicitly to avoid balanced-count tile-padding artifacts. This establishes a repository precedent for deterministic variance, but directly adopting it here would discard the maximum-rank contract. It also gives only unskewed count variance, while K3 actual counts have persistent expert popularity skew.

A clean future diagnostic distribution can preserve the helper's local rank quota and each token's number of local slots, then refill those slots with seeded unique uniform local expert choices. This introduces natural count variance without actual-input binding, model constants, dtype/tile branches, or new cache keys. It still does not model persistent popularity skew; treating an arbitrary extra skew parameter as universal would be unjustified. Any retained policy would need broad EP/TP, decode/prefill and warmup holdouts, and a deliberate decision about maximum-rank profiling. No such source change is part of this experiment.

## Established causal evidence

The prior `k3-route-scope` probe held payload, scales, weights, output buffers and fixed N128/N256 tactics constant. Changing only expert IDs reverses the K3 EP8 W4A4 T8192 ranking: N256 is +3.053% on balanced routes and −6.931% on actual routes using cold-L2 graph CUPTI. Full actual chain is −6.723%. Event timing gives the same reversal. This rules out the graph/eager policy or missing input quantizer as necessary explanations for that EP case; it does not prove the TP case.

Actual local counts are 64–252 (16,464 assignments), versus 147–148 (16,569 assignments) in the helper. This creates 185 versus224 N128 routed tiles, while both have112 N256 tiles. Tile-count arithmetic motivates inspection but does not prove a particular kernel bottleneck.

## Kernel distinctions at identical M256 / two CTA / K4

`blackwell/moe_swap_ab_kernel.py`:

- Dynamic MMA uses the live token width rounded to16 for a two-CTA group (`:241–269`). The N256 tactic does not blindly issue N256 math on every expert. However activation/SFB allocations and transport geometry remain tactic-sized.
- N128:128 accumulator columns plus32 scale columns fit two full accumulator stages. N256:256 accumulator columns plus48 scale columns fit one full stage (`:1694–1708,1748–1757`). Its overlap uses alternating windows with a protected64-column interval (`:2407–2433`), released by the epilogue after the first two32-column slabs (`:984–1096`). This is a different overlap mechanism, not simply "no overlap".
- N256's activation and SFB storage is larger, reducing shared-memory operand-ring capacity. Stage counts and scratch/TMEM ownership are recorded from actual compiled objects in the experiment, rather than guessed from formulas (`:1760–1799,1989–2045`).
- The CLC grid is admitted only when allocated work exceeds concurrent capacity and no explicit SM budget limits it (`moe_swap_ab.py:164–178`). The actual compiled mode is recorded, not inferred solely from the tactic flag.
- CLC metadata ring depth is currently one (`moe_swap_ab.py:245`). The scheduler acquires that metadata slot before issuing the next CLC cancellation (`kernel.py:2881–2893`). A future small experiment could move cancellation issue before metadata acquire to hide response latency behind consumer backpressure, while preserving ordered publication, one outstanding response, per-CTA metadata state and the two-CTA release quorum. No evidence currently shows this limits the K3 case, and the present diagnostic changes no scheduler code.

## Controlled experiment

On GPU7, use latest retained source and explicit fixed combinations N128/static, N256/static, N128/CLC, N256/CLC. Keep both GEMMs M256/two-CTA/K4. Measure actual and production-balanced routes and the complete actual benchmark chain. For each scope, use symmetric A-B-C-D-D-C-B-A order,100 strict CUPTI samples/phase,10 warmups, cold L2 and the same captured graph for each configuration.

Preserve per-kernel CUPTI activities by copying the existing timer's collected activity arrays only at its final return, after measurement and aggregation. This adds no device work and leaves its launch/flush/timing sequence unchanged. No native search, production policy, cache key, tactic axis, source file, or original evidence is modified. The source-equivalent remote tree is c0c0 plus the measured120-register patch; all513 source files match clean retained1b0 locally.
