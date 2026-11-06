# GLM5 EP8 shared-helper R2 comparison

Retained `82254e20` versus the helper-only R2 candidate. All other production files are identical. Eight B300 GPUs, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2; native distributed W4A16 MegaMoE with frozen tactics/routes. GLM5 uses hidden 6144, intermediate 2048, 256 experts, top-8 SwiGLU, EP8. No source or optimization was committed by this benchmark.

The native benchmark measured 100 strict-CUPTI CUDA-Graph/cold-L2 samples per token in serialized C1/A1/A2/C2 phases, with three warmups. Each sample is the per-iteration maximum across eight ranks. Latencies below are the median of the pooled 200 samples per arm; positive percentages mean R2 is faster. Tokens 1/2 are measured but excluded from geometric means. No AUTO, event fallback, or sanitizer.

| Tokens | Control µs | R2 µs | R2 speedup | C1 µs | A1 µs | A2 µs | C2 µs |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 70.049 | 70.481 | -0.61% | 68.881 | 70.944 | 70.097 | 71.601 |
| 2 | 89.648 | 99.601 | -9.99% | 77.680 | 88.368 | 104.145 | 94.192 |
| 4 | 96.288 | 90.113 | +6.85% | 91.584 | 85.377 | 94.400 | 101.985 |
| 8 | 113.296 | 123.329 | -8.13% | 110.673 | 126.481 | 116.497 | 116.977 |
| 16 | 129.185 | 128.273 | +0.71% | 129.601 | 127.713 | 129.089 | 128.577 |
| 32 | 145.522 | 150.017 | -3.00% | 143.793 | 152.977 | 140.000 | 147.714 |
| 64 | 165.297 | 168.289 | -1.78% | 162.610 | 167.745 | 169.361 | 168.001 |
| 128 | 184.145 | 168.913 | +9.02% | 171.874 | 167.009 | 172.114 | 192.145 |
| 256 | 175.154 | 176.449 | -0.73% | 175.154 | 172.385 | 180.145 | 175.170 |
| 512 | 172.338 | 175.361 | -1.72% | 177.985 | 175.618 | 175.201 | 167.696 |
| 4096 | 406.228 | 407.076 | -0.21% | 400.947 | 407.781 | 406.498 | 410.339 |
| 8192 | 676.645 | 671.381 | +0.78% | 677.415 | 668.903 | 672.485 | 676.645 |
| 16384 | 1264.779 | 1269.804 | -0.40% | 1262.463 | 1262.841 | 1275.081 | 1265.099 |

Geometric means excluding tokens 1/2: **+0.032% overall**, +0.022% decode (4–512), +0.059% prefill (4096–16384).

Maximum repeated-phase spread across retention tokens: control 11.79%, candidate 10.57%. Including excluded tokens 1/2, these are 21.26% and 17.85%. Preserve individual negative cells and repeat variability when interpreting these small effects.

All 52 native timing records/5,200 samples, 416 frozen choices, and 416 routing fingerprints passed. All 1,664 native resource records use 96 registers, 640 threads, and zero local memory. The four persistent C++ build files remain identical and all Ninja pre/post checks report no work. Full 13,245-file source manifests passed before and after.

All 96 available same-arm repeated PTX/cubin pairs are byte-identical. The eight early C1 captures at tokens 1/2 are explicitly missing due to an absent artifact directory; their timing and resource records are complete, and C2 captured those configurations. No failed-attempt timing is used.

The actual native 4-token and 16384-token kernels each have four staging ABI specializations. All eight control/candidate pairs remove six `SHF.R.U32.HI` instructions and two NOP padding slots, with every other full opcode count and resource count unchanged. This is representative native codegen qualification, not an all-specialization instruction-count guarantee.

Raw phase logs and all samples: `evidence/logs/`. Source and runtime receipts: `evidence/{source-control,source-candidate,runtime,complete}.json`. Full source/helper hashes and frozen choices are adjacent. Artifact comparison: `evidence/codegen-comparison-{4,16384}/summary.json`. Failure history and validation boundary: `README.md`.
