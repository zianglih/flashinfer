# TRTLLM BF16 autotuning audit

Source: `a3fce87d5beec29775e9bc3917df99ba6bc4db9c`. B300 GPU1, same retained C2 CUDA 13.2 environment. Root profiling was paused during this isolated control.

## Outcome

- The benchmark invokes BF16 autotuning and uses its retained choices during measurement. All 10 observed benchmark API calls outside the tuning context hit the process cache and selected a nonfallback tactic.
- The first prewarm profiled 2,852 native candidates over 21 token buckets with zero candidate failures. Each requested sweep token count is itself a native tuning bucket.
- At 32 tokens the tuned and native heuristic controls are equal within run noise. At 4096 tokens tuning improves the median by 15.15% in speedup terms (0.6104075/0.530087=1.1515x); turning tuning off cannot explain the W4A16 advantage.
- This verifies tuning activation/cache reuse, not global tactic optimality. The native tuner profiles synthetic routing inputs. Its 21 buckets use uniform random routing logits, whereas the benchmark uses standard normal logits. It does not explicitly race fallback(-1) under the v1 autotune context. Actual-input candidate controls can test this remaining caveat.

## Reproduction

```bash
cd /workspace/flashinfer-moe-bf16-benchmark/flashinfer
CUDA_VISIBLE_DEVICES=1 FLASHINFER_DISABLE_VERSION_CHECK=1 MAX_JOBS=8 \
python3 ../audit_bf16_autotuning.py \
  --repo /workspace/flashinfer-moe-bf16-benchmark/flashinfer \
  --output /workspace/flashinfer-moe-bf16-benchmark/artifacts/bf16-autotune-audit.json \
  --num-tokens 32,4096 --ep 8 --tp 1 --backends trtllm-bf16 \
  --include-activation-quant --use-per-token-activation --warmup 10 --iters 100
```

The project-local wrapper records autotuner state and public API choices without modifying the tracked benchmark/kernel code. It repeats each selected/default control using the exact same input closure and `_measure_or_profile` graph+CUPTI cold-L2 path. Each value is a median of 100 iterations. The 3 control pairs alternate selected/default; weight preparation and tuning remain outside timing. Instrumentation executes while enqueueing/capturing, not during device graph replays.

## Raw control results

| Tokens | Repetition | Tuned tactic | Tuned latency (ms) | Default tactic | Default latency (ms) |
| --- | --- | --- | --- | --- | --- |
| 32 | 1 | `[8, 92]` | 0.2869315 | `-1` | 0.2871400 |
| 32 | 2 | `[8, 92]` | 0.2871560 | `-1` | 0.2870915 |
| 32 | 3 | `[8, 92]` | 0.2870440 | `-1` | 0.2870440 |
| 4096 | 1 | `[128, 0]` | 0.5289665 | `-1` | 0.6091280 |
| 4096 | 2 | `[128, 0]` | 0.5300870 | `-1` | 0.6104075 |
| 4096 | 3 | `[128, 0]` | 0.5315110 | `-1` | 0.6116720 |

| Tokens | Native candidates | Tuned median (ms) | Default median (ms) | Default / tuned |
| --- | --- | --- | --- | --- |
| 32 | 352 | 0.2870440 | 0.2870915 | 1.0002x |
| 4096 | 8 | 0.5300870 | 0.6104075 | 1.1515x |

Native profile count per token bucket:

```json
{
  "measured_api_calls": 10,
  "measurement_cache_lookups": 10,
  "all_measurement_calls_cache_hit_nonfallback": true,
  "native_profile_count": 2852,
  "native_failed_profiles": 0,
  "native_bucket_counts": {
    "1": 352,
    "2": 352,
    "4": 352,
    "8": 352,
    "16": 352,
    "32": 352,
    "64": 356,
    "128": 216,
    "256": 72,
    "512": 8,
    "768": 8,
    "1024": 8,
    "1280": 8,
    "1536": 8,
    "1792": 8,
    "2048": 8,
    "2560": 8,
    "3072": 8,
    "3584": 8,
    "4096": 8,
    "8192": 8
  }
}
```

## Source trace (a3fce87d, kernel files unchanged by benchmark-only commits)

- `benchmarks/bench_moe_deepseek.py:961-977`: one public call in `autotune(True)`, then sync; measurement after context exits.
- `flashinfer/fused_moe/core.py:2785-2791`: BF16 tuning explicitly enables CUDA graphs and cold-L2 input scheduling.
- `flashinfer/fused_moe/core.py:2816-2823`: `choose_one` is invoked for `flashinfer::trtllm_bf16_moe`.
- `flashinfer/fused_moe/core.py:2825-2864`: selected native tactic pair is forwarded; only `-1` maps to native `[-1,-1]` fallback.
- `flashinfer/autotuner/autotuner.py:1007-1028`: leaving autotune resets mode, retains winner cache.
- `flashinfer/autotuner/autotuner.py:2130-2148` and `1880-1898`: outside tuning, cache lookup returns chosen tactic; fallback/misses would have been visible to the instrumentation.
- `flashinfer/autotuner/autotuner.py:2215-2224,2274-2293`: v1 enumerated candidates, v2-only explicit default-racing behavior.
- `flashinfer/fused_moe/core.py:1927-1932` versus benchmark `create_inputs`: synthetic uniform routing logits versus benchmark normal routing logits.
- `flashinfer/fused_moe/core.py:1984-1994` and `flashinfer/fused_moe/utils.py:195-244`:21hybrid token buckets through 8192, including all 13 performance sweep tokens.

## Evidence files

- `artifacts/bf16-autotune-audit.json`: full 2,852 candidate timings and every captured cache/selection record.
- `artifacts/bf16-autotune-audit.log`: normal CSV result and full raw controls.
- `audit_bf16_autotuning.py`: exact diagnostic wrapper.
- A first diagnostic attempt hit a helper-only TVM Array JSON serialization error after native tuning and measurement succeeded. Corrected the serializer and repeated the run; preserved remote `bf16-autotune-audit-initial-serialization-failure.log`.

## Performance interpretation boundary

The same BF16 Tensor Core datatype does not make equal memory traffic: these 32 local expert weights occupy 2,818,572,288bytes in pure BF16, versus 792,723,456bytes for packed FP4 weights plus 1-byte-per16-weight scales (3.56x smaller, excluding tiny global scales). Depending on routed experts and reuse, a bandwidth-limited W4A16 kernel can win despite dequantization. This is a mechanism hypothesis until kernel profiles/counters show where time is spent.
