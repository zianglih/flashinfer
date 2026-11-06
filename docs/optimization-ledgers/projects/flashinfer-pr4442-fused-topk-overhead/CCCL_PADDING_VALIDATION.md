# CCCL Batched Top-K padding validation

These helpers validate the opt-in fixed-width tail padding extension without adding benchmark-only files to CCCL.

## B200 performance comparison

`cccl_batched_topk_padding_bench.cu` uses the FlashInfer/GLM-5 shape and semantics:

- 16 rows, width 202752, `k=2048`
- fp32 scores and row-local int32 source indices
- device-resident `full`, `mixed`, and `short` lengths
- `gpu_to_gpu` determinism plus `prefer_smaller_index` (FlashInfer `SMALL` tie-break)
- discarded score output, matching the fused page/ragged transform APIs
- cold L2, with the cache flush synchronized before each timed interval, 20 warmups, and 100 CUDA-event samples

For each length pattern it measures the default unpadded call, then brackets the fused padded call with the default call plus a separate tail-fill kernel (`A1 / B / A2`). It also verifies that default output tails remain untouched and both padding implementations write exactly `-1`.

Run inside the CUDA 13.2 B200 devbox:

```bash
./run_cccl_batched_topk_padding_bench.sh \
  /hai-workspace/cccl \
  /hai-workspace/cccl-padding-results/perf
```

The current source uses the existing `MaxPairs(..., env)` overload with the opt-in `DeviceBatchedTopK::OutputPadding(key, value)` environment property. If the property factory is renamed during API review, only `invoke_padded` in the harness needs to change.

## Default-path SASS identity

`cccl_batched_topk_default_sass.cu` instantiates only the existing, unpadded call. The comparison helper archives the baseline header trees from `origin/main` without switching or modifying the candidate checkout, compiles both for `sm_100`, normalizes `cuobjdump --dump-sass`, and requires an empty diff:

```bash
./compare_cccl_batched_topk_default_sass.sh \
  /hai-workspace/cccl \
  origin/main \
  /hai-workspace/cccl-padding-results/sass
```

The retained artifacts are the two cubins, normalized SASS dumps, hashes, and `sass.diff`. An empty diff demonstrates that the default specialization compiles the opt-in padding machinery out; it does not substitute for runtime correctness tests of the padded specialization.
