# Small routing tile epilogue overlap

Frozen control: `d9074cb6e9e934d387e358a069e90ddf084f5ef7`. c1 B200 GPU0, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1. This is a task-local phase diagnostic, not native AUTO retention evidence. No original baseline campaign was rerun.

## Result and retained policy

- Extend dedicated epilogue warps to one-CTA routing N16/32/64 for FC2 and nonmixed FC1. Preserve all previous larger-N behavior.
- Keep mixed FP4-weight/FP8-activation FC1 inline at every N: at four active experts, overlap regressed about 0.7us (3%) while the 32-expert gain was under 1%.
- Reject small two-CTA tactics: M256 with physical N>=64 was exact, but slower in sparse phase timing. No new tactic geometry is proposed.
- Production delta is the `overlap_epilogue` policy in `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`. Focused pre-commit and `git diff --check` passed. SHA256: `581395ff44b3598ff3d0d497b12e4f5326e0ee5d83f525d2bf79e501b317dd0d`. Left unstaged and uncommitted for parent.

## Exact probes

- Small2: 162 paired cases across NVFP4, FP4/E8M0/SF16, MXFP4, MXFP8 E4M3, MXFP8 E5M2, and mixed MXFP4 x MXFP8.
- Overlap1: 216 paired cases across the same six formats. Raw Float32 FC2, quantized FC1 (output and SF bytes), and per-token BF16 FC1 match the frozen kernel byte for byte.
- N16/32/64 with valid1/4/16 and partial31/63; M384 channel tail; K64 for SF16 and K128 for SF32. Separate sentinels surround output and SF views; invalid output rows remain untouched. Per-token source rows are gathered in reverse, with repeated source indices.
- Additional K1536 pass: all 90 paired cases passed across all six formats, N16/64, valid1/16/63, and all three epilogues. This exercises K-pipeline wrap and repeated accumulator stages. Total overlap1 exact coverage: 306 paired cases.
- Focused paired checks only; full tests and sanitizer remain deferred.

## Timing methodology

Same GPU, same frozen d907 dependencies, same generated inputs per pair. 3 warmups, 21 cold-L2 CUDA graph CUPTI repetitions, median microseconds. Separate reverse-order confirmation. Constant nonzero packed data/scales; one routing tile per expert, 1/4/16 live routes per expert. FC1 dimensions: channels4096, K7168; FC2: channels7168, K2048, BF16 output. Expert counts32 and4. Logical routing padding is tactic N; source/route/output allocations differ with N, so cross-N comparisons are phase diagnostics. The within-N paired comparisons use identical allocations.

Run from remote candidate with `CUDA_VISIBLE_DEVICES=0 PYTHONPATH=.`:

```sh
../.venv/bin/python ../transfer/decode-geometry-experiment/run_probe.py --action exact --modes nvfp4,fp4_e8_sf16,mxfp4,mxfp8,mxfp8_e5,w4a8 --tiles 16,32,64 --valid 1,4,16,31,63 --variants baseline1,overlap1
../.venv/bin/python ../transfer/decode-geometry-experiment/run_probe.py --action exact --modes nvfp4,fp4_e8_sf16,mxfp4,mxfp8,mxfp8_e5,w4a8 --tiles 16,64 --valid 1,16,63 --variants baseline1,overlap1 --reduction 1536
../.venv/bin/python ../transfer/decode-geometry-experiment/run_probe.py --action perf --modes nvfp4,mxfp8,w4a8 --tiles 16,32,64 --valid 1,4,16 --phases fc1,fc2 --variants baseline1,small2,overlap1,overlap2
../.venv/bin/python ../transfer/decode-geometry-experiment/run_probe.py --action perf --modes nvfp4,mxfp8,w4a8 --tiles 128 --valid 1,4,16 --phases fc1,fc2 --variants baseline1,baseline2
../.venv/bin/python ../transfer/decode-geometry-experiment/run_probe.py --action perf --modes nvfp4,mxfp8,w4a8 --tiles 16 --valid 1,4,16 --phases fc1,fc2 --variants overlap1,baseline1
../.venv/bin/python ../transfer/decode-geometry-experiment/run_probe.py --action perf --modes nvfp4,mxfp8,w4a8 --tiles 16 --valid 1,4,16 --phases fc1,fc2 --variants overlap1,baseline1 --experts 4
```

## Complete phase timings

Variant suffix1=one CTA,2=two CTA. `small2` retains inline epilogues for small N; `overlap` always separates epilogue warps. Production keeps mixed FC1 inline, so its overlap timings are rejected evidence.

| Run | Mode | Phase | Experts | N | Live/expert | Variant | Median us |
|---|---|---|---:|---:|---:|---|---:|
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 1 | baseline1 | 103.263 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 1 | small2 | 105.440 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 1 | overlap1 | 99.840 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 1 | overlap2 | 100.447 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 4 | baseline1 | 103.359 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 4 | small2 | 105.248 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 4 | overlap1 | 99.904 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 4 | overlap2 | 100.319 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 16 | baseline1 | 103.519 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 16 | small2 | 105.792 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 16 | overlap1 | 99.872 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 16 | 16 | overlap2 | 100.768 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 1 | baseline1 | 103.008 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 1 | small2 | 105.536 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 1 | overlap1 | 99.551 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 1 | overlap2 | 100.352 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 4 | baseline1 | 103.488 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 4 | small2 | 105.695 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 4 | overlap1 | 99.679 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 4 | overlap2 | 100.544 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 16 | baseline1 | 103.551 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 16 | small2 | 106.176 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 16 | overlap1 | 100.032 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 32 | 16 | overlap2 | 100.768 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 1 | baseline1 | 103.712 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 1 | small2 | 105.183 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 1 | overlap1 | 100.095 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 1 | overlap2 | 100.576 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 4 | baseline1 | 103.935 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 4 | small2 | 105.376 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 4 | overlap1 | 100.831 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 4 | overlap2 | 100.448 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 16 | baseline1 | 104.448 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 16 | small2 | 105.792 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 16 | overlap1 | 100.352 |
| sparse-perf.log | nvfp4 | fc1 | 32 | 64 | 16 | overlap2 | 100.800 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 1 | baseline1 | 66.976 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 1 | small2 | 68.929 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 1 | overlap1 | 57.663 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 1 | overlap2 | 57.664 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 4 | baseline1 | 66.784 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 4 | small2 | 68.448 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 4 | overlap1 | 57.184 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 4 | overlap2 | 57.600 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 16 | baseline1 | 67.072 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 16 | small2 | 69.344 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 16 | overlap1 | 57.696 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 16 | 16 | overlap2 | 57.696 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 1 | baseline1 | 67.744 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 1 | small2 | 69.856 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 1 | overlap1 | 57.440 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 1 | overlap2 | 57.344 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 4 | baseline1 | 67.776 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 4 | small2 | 69.920 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 4 | overlap1 | 57.472 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 4 | overlap2 | 57.632 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 16 | baseline1 | 68.863 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 16 | small2 | 70.272 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 16 | overlap1 | 57.599 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 32 | 16 | overlap2 | 57.696 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 1 | baseline1 | 67.872 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 1 | small2 | 70.656 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 1 | overlap1 | 57.664 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 1 | overlap2 | 57.727 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 4 | baseline1 | 68.159 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 4 | small2 | 70.880 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 4 | overlap1 | 57.727 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 4 | overlap2 | 57.888 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 16 | baseline1 | 68.448 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 16 | small2 | 70.944 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 16 | overlap1 | 57.856 |
| sparse-perf.log | nvfp4 | fc2 | 32 | 64 | 16 | overlap2 | 57.984 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 1 | baseline1 | 170.207 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 1 | small2 | 174.399 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 1 | overlap1 | 168.959 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 1 | overlap2 | 170.848 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 4 | baseline1 | 170.590 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 4 | small2 | 174.816 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 4 | overlap1 | 169.343 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 4 | overlap2 | 171.424 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 16 | baseline1 | 171.456 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 16 | small2 | 175.585 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 16 | overlap1 | 170.432 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 16 | 16 | overlap2 | 172.703 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 1 | baseline1 | 170.431 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 1 | small2 | 174.623 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 1 | overlap1 | 168.640 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 1 | overlap2 | 171.263 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 4 | baseline1 | 170.751 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 4 | small2 | 175.104 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 4 | overlap1 | 169.151 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 4 | overlap2 | 171.455 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 16 | baseline1 | 171.328 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 16 | small2 | 175.808 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 16 | overlap1 | 170.271 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 32 | 16 | overlap2 | 172.703 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 1 | baseline1 | 171.040 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 1 | small2 | 174.336 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 1 | overlap1 | 169.344 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 1 | overlap2 | 171.167 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 4 | baseline1 | 171.488 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 4 | small2 | 174.815 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 4 | overlap1 | 170.143 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 4 | overlap2 | 171.585 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 16 | baseline1 | 172.480 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 16 | small2 | 175.775 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 16 | overlap1 | 170.624 |
| sparse-perf.log | mxfp8 | fc1 | 32 | 64 | 16 | overlap2 | 172.321 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 1 | baseline1 | 100.672 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 1 | small2 | 103.040 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 1 | overlap1 | 94.496 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 1 | overlap2 | 96.096 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 4 | baseline1 | 101.631 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 4 | small2 | 103.744 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 4 | overlap1 | 94.912 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 4 | overlap2 | 96.351 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 16 | baseline1 | 102.239 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 16 | small2 | 104.480 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 16 | overlap1 | 94.880 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 16 | 16 | overlap2 | 96.640 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 1 | baseline1 | 100.511 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 1 | small2 | 103.712 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 1 | overlap1 | 94.880 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 1 | overlap2 | 96.288 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 4 | baseline1 | 101.279 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 4 | small2 | 104.576 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 4 | overlap1 | 94.944 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 4 | overlap2 | 96.512 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 16 | baseline1 | 102.528 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 16 | small2 | 105.535 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 16 | overlap1 | 95.519 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 32 | 16 | overlap2 | 97.600 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 1 | baseline1 | 101.215 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 1 | small2 | 104.128 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 1 | overlap1 | 94.463 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 1 | overlap2 | 96.544 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 4 | baseline1 | 101.888 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 4 | small2 | 105.024 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 4 | overlap1 | 95.200 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 4 | overlap2 | 97.024 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 16 | baseline1 | 102.879 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 16 | small2 | 105.952 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 16 | overlap1 | 95.392 |
| sparse-perf.log | mxfp8 | fc2 | 32 | 64 | 16 | overlap2 | 97.471 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 1 | baseline1 | 120.511 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 1 | small2 | 127.104 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 1 | overlap1 | 119.520 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 1 | overlap2 | 125.055 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 4 | baseline1 | 120.896 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 4 | small2 | 127.488 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 4 | overlap1 | 120.095 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 4 | overlap2 | 125.280 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 16 | baseline1 | 121.344 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 16 | small2 | 128.031 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 16 | overlap1 | 120.416 |
| sparse-perf.log | w4a8 | fc1 | 32 | 16 | 16 | overlap2 | 125.856 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 1 | baseline1 | 120.383 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 1 | small2 | 127.263 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 1 | overlap1 | 119.615 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 1 | overlap2 | 125.247 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 4 | baseline1 | 120.800 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 4 | small2 | 127.583 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 4 | overlap1 | 119.968 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 4 | overlap2 | 125.344 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 16 | baseline1 | 121.248 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 16 | small2 | 128.192 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 16 | overlap1 | 120.704 |
| sparse-perf.log | w4a8 | fc1 | 32 | 32 | 16 | overlap2 | 126.111 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 1 | baseline1 | 124.000 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 1 | small2 | 127.168 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 1 | overlap1 | 122.624 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 1 | overlap2 | 124.928 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 4 | baseline1 | 124.544 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 4 | small2 | 127.489 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 4 | overlap1 | 122.592 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 4 | overlap2 | 125.088 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 16 | baseline1 | 124.160 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 16 | small2 | 128.064 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 16 | overlap1 | 122.463 |
| sparse-perf.log | w4a8 | fc1 | 32 | 64 | 16 | overlap2 | 125.760 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 1 | baseline1 | 77.824 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 1 | small2 | 82.656 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 1 | overlap1 | 67.072 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 1 | overlap2 | 71.232 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 4 | baseline1 | 78.175 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 4 | small2 | 83.232 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 4 | overlap1 | 67.232 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 4 | overlap2 | 71.328 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 16 | baseline1 | 78.784 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 16 | small2 | 83.488 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 16 | overlap1 | 68.031 |
| sparse-perf.log | w4a8 | fc2 | 32 | 16 | 16 | overlap2 | 71.616 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 1 | baseline1 | 76.927 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 1 | small2 | 82.368 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 1 | overlap1 | 66.848 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 1 | overlap2 | 71.104 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 4 | baseline1 | 78.464 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 4 | small2 | 82.784 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 4 | overlap1 | 66.912 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 4 | overlap2 | 71.359 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 16 | baseline1 | 78.527 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 16 | small2 | 83.615 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 16 | overlap1 | 67.232 |
| sparse-perf.log | w4a8 | fc2 | 32 | 32 | 16 | overlap2 | 71.615 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 1 | baseline1 | 76.415 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 1 | small2 | 83.232 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 1 | overlap1 | 67.263 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 1 | overlap2 | 71.104 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 4 | baseline1 | 76.992 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 4 | small2 | 83.392 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 4 | overlap1 | 67.616 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 4 | overlap2 | 71.296 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 16 | baseline1 | 77.152 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 16 | small2 | 84.191 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 16 | overlap1 | 68.224 |
| sparse-perf.log | w4a8 | fc2 | 32 | 64 | 16 | overlap2 | 71.744 |
| n128-perf.log | nvfp4 | fc1 | 32 | 128 | 1 | baseline1 | 112.128 |
| n128-perf.log | nvfp4 | fc1 | 32 | 128 | 1 | baseline2 | 101.376 |
| n128-perf.log | nvfp4 | fc1 | 32 | 128 | 4 | baseline1 | 112.351 |
| n128-perf.log | nvfp4 | fc1 | 32 | 128 | 4 | baseline2 | 101.792 |
| n128-perf.log | nvfp4 | fc1 | 32 | 128 | 16 | baseline1 | 112.351 |
| n128-perf.log | nvfp4 | fc1 | 32 | 128 | 16 | baseline2 | 101.439 |
| n128-perf.log | nvfp4 | fc2 | 32 | 128 | 1 | baseline1 | 59.520 |
| n128-perf.log | nvfp4 | fc2 | 32 | 128 | 1 | baseline2 | 58.239 |
| n128-perf.log | nvfp4 | fc2 | 32 | 128 | 4 | baseline1 | 59.329 |
| n128-perf.log | nvfp4 | fc2 | 32 | 128 | 4 | baseline2 | 58.687 |
| n128-perf.log | nvfp4 | fc2 | 32 | 128 | 16 | baseline1 | 59.584 |
| n128-perf.log | nvfp4 | fc2 | 32 | 128 | 16 | baseline2 | 58.848 |
| n128-perf.log | mxfp8 | fc1 | 32 | 128 | 1 | baseline1 | 192.351 |
| n128-perf.log | mxfp8 | fc1 | 32 | 128 | 1 | baseline2 | 172.511 |
| n128-perf.log | mxfp8 | fc1 | 32 | 128 | 4 | baseline1 | 192.256 |
| n128-perf.log | mxfp8 | fc1 | 32 | 128 | 4 | baseline2 | 172.576 |
| n128-perf.log | mxfp8 | fc1 | 32 | 128 | 16 | baseline1 | 191.136 |
| n128-perf.log | mxfp8 | fc1 | 32 | 128 | 16 | baseline2 | 173.503 |
| n128-perf.log | mxfp8 | fc2 | 32 | 128 | 1 | baseline1 | 97.887 |
| n128-perf.log | mxfp8 | fc2 | 32 | 128 | 1 | baseline2 | 95.520 |
| n128-perf.log | mxfp8 | fc2 | 32 | 128 | 4 | baseline1 | 98.080 |
| n128-perf.log | mxfp8 | fc2 | 32 | 128 | 4 | baseline2 | 95.904 |
| n128-perf.log | mxfp8 | fc2 | 32 | 128 | 16 | baseline1 | 99.168 |
| n128-perf.log | mxfp8 | fc2 | 32 | 128 | 16 | baseline2 | 96.767 |
| n128-perf.log | w4a8 | fc1 | 32 | 128 | 1 | baseline1 | 159.199 |
| n128-perf.log | w4a8 | fc1 | 32 | 128 | 1 | baseline2 | 131.135 |
| n128-perf.log | w4a8 | fc1 | 32 | 128 | 4 | baseline1 | 159.519 |
| n128-perf.log | w4a8 | fc1 | 32 | 128 | 4 | baseline2 | 131.232 |
| n128-perf.log | w4a8 | fc1 | 32 | 128 | 16 | baseline1 | 157.984 |
| n128-perf.log | w4a8 | fc1 | 32 | 128 | 16 | baseline2 | 131.391 |
| n128-perf.log | w4a8 | fc2 | 32 | 128 | 1 | baseline1 | 77.472 |
| n128-perf.log | w4a8 | fc2 | 32 | 128 | 1 | baseline2 | 71.424 |
| n128-perf.log | w4a8 | fc2 | 32 | 128 | 4 | baseline1 | 78.048 |
| n128-perf.log | w4a8 | fc2 | 32 | 128 | 4 | baseline2 | 71.936 |
| n128-perf.log | w4a8 | fc2 | 32 | 128 | 16 | baseline1 | 78.560 |
| n128-perf.log | w4a8 | fc2 | 32 | 128 | 16 | baseline2 | 72.255 |
| decode-reverse-perf.log | nvfp4 | fc1 | 32 | 16 | 1 | overlap1 | 99.711 |
| decode-reverse-perf.log | nvfp4 | fc1 | 32 | 16 | 1 | baseline1 | 103.264 |
| decode-reverse-perf.log | nvfp4 | fc1 | 32 | 16 | 4 | overlap1 | 99.712 |
| decode-reverse-perf.log | nvfp4 | fc1 | 32 | 16 | 4 | baseline1 | 103.392 |
| decode-reverse-perf.log | nvfp4 | fc1 | 32 | 16 | 16 | overlap1 | 99.808 |
| decode-reverse-perf.log | nvfp4 | fc1 | 32 | 16 | 16 | baseline1 | 103.840 |
| decode-reverse-perf.log | nvfp4 | fc2 | 32 | 16 | 1 | overlap1 | 58.048 |
| decode-reverse-perf.log | nvfp4 | fc2 | 32 | 16 | 1 | baseline1 | 66.944 |
| decode-reverse-perf.log | nvfp4 | fc2 | 32 | 16 | 4 | overlap1 | 57.856 |
| decode-reverse-perf.log | nvfp4 | fc2 | 32 | 16 | 4 | baseline1 | 66.880 |
| decode-reverse-perf.log | nvfp4 | fc2 | 32 | 16 | 16 | overlap1 | 58.240 |
| decode-reverse-perf.log | nvfp4 | fc2 | 32 | 16 | 16 | baseline1 | 67.552 |
| decode-reverse-perf.log | mxfp8 | fc1 | 32 | 16 | 1 | overlap1 | 169.184 |
| decode-reverse-perf.log | mxfp8 | fc1 | 32 | 16 | 1 | baseline1 | 169.919 |
| decode-reverse-perf.log | mxfp8 | fc1 | 32 | 16 | 4 | overlap1 | 169.375 |
| decode-reverse-perf.log | mxfp8 | fc1 | 32 | 16 | 4 | baseline1 | 170.431 |
| decode-reverse-perf.log | mxfp8 | fc1 | 32 | 16 | 16 | overlap1 | 170.464 |
| decode-reverse-perf.log | mxfp8 | fc1 | 32 | 16 | 16 | baseline1 | 171.039 |
| decode-reverse-perf.log | mxfp8 | fc2 | 32 | 16 | 1 | overlap1 | 94.336 |
| decode-reverse-perf.log | mxfp8 | fc2 | 32 | 16 | 1 | baseline1 | 100.640 |
| decode-reverse-perf.log | mxfp8 | fc2 | 32 | 16 | 4 | overlap1 | 94.304 |
| decode-reverse-perf.log | mxfp8 | fc2 | 32 | 16 | 4 | baseline1 | 101.120 |
| decode-reverse-perf.log | mxfp8 | fc2 | 32 | 16 | 16 | overlap1 | 95.072 |
| decode-reverse-perf.log | mxfp8 | fc2 | 32 | 16 | 16 | baseline1 | 103.168 |
| decode-reverse-perf.log | w4a8 | fc1 | 32 | 16 | 1 | overlap1 | 119.872 |
| decode-reverse-perf.log | w4a8 | fc1 | 32 | 16 | 1 | baseline1 | 120.384 |
| decode-reverse-perf.log | w4a8 | fc1 | 32 | 16 | 4 | overlap1 | 119.935 |
| decode-reverse-perf.log | w4a8 | fc1 | 32 | 16 | 4 | baseline1 | 120.864 |
| decode-reverse-perf.log | w4a8 | fc1 | 32 | 16 | 16 | overlap1 | 120.832 |
| decode-reverse-perf.log | w4a8 | fc1 | 32 | 16 | 16 | baseline1 | 121.280 |
| decode-reverse-perf.log | w4a8 | fc2 | 32 | 16 | 1 | overlap1 | 66.624 |
| decode-reverse-perf.log | w4a8 | fc2 | 32 | 16 | 1 | baseline1 | 77.824 |
| decode-reverse-perf.log | w4a8 | fc2 | 32 | 16 | 4 | overlap1 | 67.040 |
| decode-reverse-perf.log | w4a8 | fc2 | 32 | 16 | 4 | baseline1 | 78.240 |
| decode-reverse-perf.log | w4a8 | fc2 | 32 | 16 | 16 | overlap1 | 67.392 |
| decode-reverse-perf.log | w4a8 | fc2 | 32 | 16 | 16 | baseline1 | 79.104 |
| decode-four-expert-perf.log | nvfp4 | fc1 | 4 | 16 | 1 | overlap1 | 20.096 |
| decode-four-expert-perf.log | nvfp4 | fc1 | 4 | 16 | 1 | baseline1 | 20.320 |
| decode-four-expert-perf.log | nvfp4 | fc1 | 4 | 16 | 4 | overlap1 | 20.064 |
| decode-four-expert-perf.log | nvfp4 | fc1 | 4 | 16 | 4 | baseline1 | 20.032 |
| decode-four-expert-perf.log | nvfp4 | fc1 | 4 | 16 | 16 | overlap1 | 19.904 |
| decode-four-expert-perf.log | nvfp4 | fc1 | 4 | 16 | 16 | baseline1 | 19.968 |
| decode-four-expert-perf.log | nvfp4 | fc2 | 4 | 16 | 1 | overlap1 | 12.512 |
| decode-four-expert-perf.log | nvfp4 | fc2 | 4 | 16 | 1 | baseline1 | 14.176 |
| decode-four-expert-perf.log | nvfp4 | fc2 | 4 | 16 | 4 | overlap1 | 12.480 |
| decode-four-expert-perf.log | nvfp4 | fc2 | 4 | 16 | 4 | baseline1 | 14.081 |
| decode-four-expert-perf.log | nvfp4 | fc2 | 4 | 16 | 16 | overlap1 | 12.608 |
| decode-four-expert-perf.log | nvfp4 | fc2 | 4 | 16 | 16 | baseline1 | 14.143 |
| decode-four-expert-perf.log | mxfp8 | fc1 | 4 | 16 | 1 | overlap1 | 32.768 |
| decode-four-expert-perf.log | mxfp8 | fc1 | 4 | 16 | 1 | baseline1 | 32.672 |
| decode-four-expert-perf.log | mxfp8 | fc1 | 4 | 16 | 4 | overlap1 | 32.736 |
| decode-four-expert-perf.log | mxfp8 | fc1 | 4 | 16 | 4 | baseline1 | 32.544 |
| decode-four-expert-perf.log | mxfp8 | fc1 | 4 | 16 | 16 | overlap1 | 32.736 |
| decode-four-expert-perf.log | mxfp8 | fc1 | 4 | 16 | 16 | baseline1 | 32.480 |
| decode-four-expert-perf.log | mxfp8 | fc2 | 4 | 16 | 1 | overlap1 | 18.943 |
| decode-four-expert-perf.log | mxfp8 | fc2 | 4 | 16 | 1 | baseline1 | 20.768 |
| decode-four-expert-perf.log | mxfp8 | fc2 | 4 | 16 | 4 | overlap1 | 18.784 |
| decode-four-expert-perf.log | mxfp8 | fc2 | 4 | 16 | 4 | baseline1 | 20.800 |
| decode-four-expert-perf.log | mxfp8 | fc2 | 4 | 16 | 16 | overlap1 | 19.136 |
| decode-four-expert-perf.log | mxfp8 | fc2 | 4 | 16 | 16 | baseline1 | 20.896 |
| decode-four-expert-perf.log | w4a8 | fc1 | 4 | 16 | 1 | overlap1 | 25.056 |
| decode-four-expert-perf.log | w4a8 | fc1 | 4 | 16 | 1 | baseline1 | 24.287 |
| decode-four-expert-perf.log | w4a8 | fc1 | 4 | 16 | 4 | overlap1 | 24.928 |
| decode-four-expert-perf.log | w4a8 | fc1 | 4 | 16 | 4 | baseline1 | 24.224 |
| decode-four-expert-perf.log | w4a8 | fc1 | 4 | 16 | 16 | overlap1 | 24.896 |
| decode-four-expert-perf.log | w4a8 | fc1 | 4 | 16 | 16 | baseline1 | 24.288 |
| decode-four-expert-perf.log | w4a8 | fc2 | 4 | 16 | 1 | overlap1 | 14.560 |
| decode-four-expert-perf.log | w4a8 | fc2 | 4 | 16 | 1 | baseline1 | 15.680 |
| decode-four-expert-perf.log | w4a8 | fc2 | 4 | 16 | 4 | overlap1 | 14.496 |
| decode-four-expert-perf.log | w4a8 | fc2 | 4 | 16 | 4 | baseline1 | 15.808 |
| decode-four-expert-perf.log | w4a8 | fc2 | 4 | 16 | 16 | overlap1 | 14.688 |
| decode-four-expert-perf.log | w4a8 | fc2 | 4 | 16 | 16 | baseline1 | 15.712 |
