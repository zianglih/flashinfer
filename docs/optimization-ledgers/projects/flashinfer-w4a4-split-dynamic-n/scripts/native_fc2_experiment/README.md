# Native-route FC2 bulk-scatter experiment

The selected FC2 variant is integrated locally for the final combined screen. It is **not full-MoE retention evidence**. It removes the FP32 TMEM transpose for large unfused BF16/FP16 FC2 tiles and stages output inside the existing fused kernel before scattering contiguous 128-channel rows with `cp.async.bulk`. It adds no kernel or activation-preparation pass.

## Frozen inputs and scope

- Control kernel/utils: production `d9074cb6e9e934d387e358a069e90ddf084f5ef7`, copied into `fc2_trial/baseline_{core,utils}.py`.
- Remote host/API snapshot: `94be9a712a46ab34b902605c4a34d26a4c570692`; its small-N overlap update does not affect these N128/N256 diagnostics.
- Hardware: C1 B200, GPU2, one GPU; image `nvcr.io/nvidia/pytorch:26.05-py3`; CUDA13.2, CuTe DSL4.7.1. Native input creation and routing from `benchmarks/bench_moe_deepseek.py`; MXFP8/mixed preparation from the frozen local `bench_cute_dsl_mxfp8.py` campaign helper.
- Native workload: T16384, top-k8, hidden7168, intermediate2048, 256 global/32 local experts. All final pairs have16280 local routes; N128 creates142 live route tiles, N256 creates77. The expanded BF16 output has shape `[131072,7168]`.
- Fixed tactics; no AUTO search or broad token sweep. Only isolated FC2 is timed:10 warmups,100 samples, cold-L2 CUDA graph/CUPTI median. Each variant receives the exact same captured native FC2 tensors in its process. Both execution orders are recorded for N256.
- No production tests added. No sanitizer claim. Parent owns commit/deployment/full-MoE benchmarking.

## Selected design and contract

`Ld32x32b.x32` or `.x64` reads one channel per lane and one token per register from each warp's own32-row TMEM group. Scaling and BF16/FP16 conversion happen before scalar contiguous-channel shared stores. All four epilogue warps issue bulk row copies after the async-proxy fence and128-thread barrier. The output row remains `token_mapping[permuted_row]`.

The kernel computes available shared memory from actual A/B/SFA/SFB layout byte counts and exact mbarrier/alignment overhead. If32KiB fits it uses two64-token output stages; otherwise8KiB gives one32-token stage. Operand stage count is unchanged. N<128, fused atomic combine, FP32/FP8 outputs, generated output scales, and insufficient-memory configurations retain the existing direct epilogue. This is an explicit shared capability/geometry choice, not an NVFP4-only dispatch.

Per-token scales use permuted FC2 route indices. The combined expert/per-token scale is rounded through `final_scale_dtype` before multiplying the FP32 accumulator, matching the existing metadata contract. Per-tensor scaling uses the same rounded expert alpha in all channel lanes. Inactive channel CTAs are guarded before the bulk helper, so M384 with two-CTA tiles does not issue a zero-byte copy. Shared stages are not reused until each issuer's bulk read completes and the epilogue barrier synchronizes the warp group. Dedicated scratch never aliases live operand buffers.

## Exact checks

- `native-fc2-selected-contract02.log`:50 existing output/metadata cases. N16/32/64/128/256, partial routes, per-token on/off; BF16, FP16, FP32, E4M3, E5M2 outputs; FP32/BF16/FP16 metadata. The small/direct cases remain byte-exact.
- `native-fc2-selected-formats01.log`:24 format cases across NVFP4, FP4/E8M0/SF16, MXFP4/SF32, homogeneous MXFP8 E4M3/E5M2 and mixed W4A8. N128 oneCTA/N256 twoCTA, live129/257 rows, repeated persistent tiles, top-k8 scattered output, per-token on/off, BF16/FP16 metadata.
- `native-fc2-selected-tail-formats.log`:24 final-snapshot M384 cases over that same matrix, including the inactive second CTA in the final channel tile. Both unused output rows and a trailing128-element sentinel remain unchanged.
- Every timed native call below also compares the entire output byte tensor to the frozen control.
- Production utils AST is identical to the final tested selected snapshot after restoring its production-relative import. `manifest.json` records hashes, including the combined production core hash; production changes are limited to the epilogue and its shared-storage sizing, alongside the independently owned FC1 load-order update.

## Complete selected native FC2 medians

All values are microseconds; speedup is control/selected. Full100-sample arrays, route histograms, and geometry are retained in `../../logs/native-fc2-selected*.json`. `results.json` is the compact machine-readable table.

| Mode | M/N; CTA group | Order | Control | Selected | Speedup |
|---|---|---|---:|---:|---:|
| NVFP4 |128/256;1|control then selected|211.968|193.888|1.093×|
| NVFP4 |128/256;1|selected then control|217.456|193.808|1.122×|
| NVFP4 |128/128;1|control then selected|212.400|182.480|1.164×|
| NVFP4 |256/256;2|control then selected|213.0245|181.840|1.171×|
| MXFP8 E4M3 |128/256;1|control then selected|277.952|280.064|0.992×|
| MXFP8 E4M3 |128/256;1|selected then control|278.672|280.1275|0.995×|
| MXFP8 E4M3 |128/128;1|control then selected|296.224|288.432|1.027×|
| Mixed W4A8 |128/256;1|control then selected|263.456|265.824|0.991×|
| Mixed W4A8 |128/256;1|selected then control|260.272|266.208|0.978×|
| Mixed W4A8 |128/128;1|control then selected|279.6645|269.696|1.037×|

NVFP4 has the material phase gain. The other modes have small geometry-dependent tradeoffs: N128 improves, while N256 is neutral/slightly slower. These diagnostics do not establish a universal gain or recovery versus upstream a65's full-MoE baseline.

## Profiler evidence and discarded buffer sizes

The first bulk32 prototype, before the packed uniform-alpha cleanup, was profiled on the same native N256 workload. Its full-output byte comparison passed. The selected variant preserves the same mainloop geometry and8KiB allocation in that case.

| Metric | Frozen control | Bulk32 prototype |
|---|---:|---:|
| NCU kernel duration µs |230.048|201.088|
| Registers/thread |112|91|
| Dynamic shared bytes |222080|229760|
| TMEM active % peak |39.61|33.82|
| Tensor active % peak |25.47|29.35|
| LSU shared throughput % peak |28.14|21.77|
| Local load/store sectors |0/0|0/0|
| LDTM warp instructions |1411200|117600|
| STTM warp instructions |705600|0|

Raw reports: `logs/native-fc2-{control,bulk32}-ncu-{raw,source}.csv` at the project root. The initial larger64-token buffers forced the one-CTA N256 operand pipeline from four to three stages and regressed to208.75/206.78µs versus205.57µs control. They remain archived but were not integrated. The selected fit policy preserves operand depth and uses the larger double buffer only where it fits.

## Reproduction

From the frozen remote host checkout, with these task-local snapshots synced:

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n/candidate
CUDA_VISIBLE_DEVICES=2 PYTHONPATH=. ../.venv/bin/python \
  ../scripts/native_fc2_experiment/probe_native.py \
  --repo . --expected-head 94be9a712a46ab34b902605c4a34d26a4c570692 \
  --output ../logs/native-fc2-new.json --variants baseline,selected \
  --tactic '[256,[[256,256],[2,1],false],[[128,256],[1,1],false]]'
CUDA_VISIBLE_DEVICES=2 PYTHONPATH=. ../.venv/bin/python \
  ../scripts/native_fc2_experiment/run_paired.py \
  --script probe_fc2_tail_formats.py --variant selected
```

Use `probe_native_modes.py --mode mxfp8` or `--mode w4a8` for the two extra modes and a valid fixed tactic. For N128 use a route bucket128 and matching FC1/FC2 N128. These scripts reject an unexpected or dirty production checkout; the actual tested kernels come from the immutable experiment modules.
