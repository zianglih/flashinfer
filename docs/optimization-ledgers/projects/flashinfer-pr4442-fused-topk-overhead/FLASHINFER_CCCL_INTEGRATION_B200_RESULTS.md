# FlashInfer reference integration with CCCL output padding

This validates the pushed FlashInfer reference consumer at
[`zianglih/flashinfer@01af1b18`](https://github.com/zianglih/flashinfer/commit/01af1b185c58e180e55835b6288d8f380ff61968),
which pins CCCL to
[`zianglih/cccl@ce2f49be`](https://github.com/zianglih/cccl/commit/ce2f49be55570021c46ff1af0abef8321c0dd5a3).
It is reference code for the CCCL proposal, not a FlashInfer integration target.

## Environment

- Image: `nvcr.io/nvidia/pytorch:26.05-py3`
- GPU: NVIDIA B200 183 GB (one GPU used)
- Driver: 580.126.09
- CUDA / `nvcc`: 13.2 / 13.2.78
- PyTorch: `2.12.0a0+5aff3928d8.nv26.05`
- FlashInfer local-tail reference: `f1af5865`
- FlashInfer CCCL-fused reference: `01af1b185c58e180e55835b6288d8f380ff61968`
- CCCL candidate: `ce2f49be55570021c46ff1af0abef8321c0dd5a3`

## Correctness

Both commands used a fresh SM100 JIT cache compiled from the extended-CCCL
FlashInfer source.

```bash
python3 -m pytest -q tests/utils/test_topk.py \
  -k '(top_k_tie_break_modes and cub) or cub_transform_nonpositive_lengths'
# 6 passed, 1546 deselected

python3 -m pytest -q tests/utils/test_topk.py \
  -k 'top_k_transform_with_row_starts or top_k_page_table_transform_compact_pages_cuda_graph_replay or top_k_tie_break_modes or cub_transform_nonpositive_lengths or cub_transform_workspace_paths'
# 146 passed, 1406 deselected
```

This covers wide and compact page tables, optional raw indices, ragged output,
row starts, workspace paths, smaller/larger-index ties, and CUDA graph replay
after mutating full rows to short, zero, and negative lengths.

## Performance method

- FP32 scores, 16 rows, width 202752, `k=2048`
- `tie_break=SMALL`, forced CUB, `dsa_graph_safe=True`
- page-table uses the current SGLang-compatible wide `page_size=1` layout
- cold L2, CUPTI activity timing, 20 dry runs, 100 measured runs, median
- three same-GPU adjacent local-tail A1 / CCCL-fused B / local-tail A2 sweeps
- `full`: all lengths 202752
- `mixed`: cycle `[202752, 131072, 65536, 32768, 16384, 8192, 4096, 2048]`
- `short`: cycle `[2047, 0, 2048, 1]`

Each table cell below is the reported median in microseconds.

| Sweep | Mode | API | Lengths | Local tail A1 | CCCL fused B | Local tail A2 |
|---:|---|---|---|---:|---:|---:|
| 1 | graph-safe eager | page-table | full | 41.2955 | 40.7040 | 41.2480 |
| 1 | graph-safe eager | page-table | mixed | 34.8480 | 34.2400 | 34.8800 |
| 1 | graph-safe eager | page-table | short | 4.6720 | 2.6880 | 4.6720 |
| 1 | graph-safe eager | ragged | full | 27.9360 | 26.5280 | 27.9680 |
| 1 | graph-safe eager | ragged | mixed | 23.0400 | 21.6640 | 23.0565 |
| 1 | graph-safe eager | ragged | short | 4.3845 | 2.2400 | 4.3200 |
| 1 | graph replay | page-table | mixed | 34.7040 | 34.2400 | 34.6560 |
| 1 | graph replay | ragged | mixed | 22.8480 | 21.7280 | 22.8800 |
| 2 | graph-safe eager | page-table | full | 41.2320 | 40.7040 | 41.3445 |
| 2 | graph-safe eager | page-table | mixed | 34.8800 | 34.2400 | 34.8480 |
| 2 | graph-safe eager | page-table | short | 4.6410 | 2.6880 | 4.7050 |
| 2 | graph-safe eager | ragged | full | 27.9680 | 26.4960 | 28.0000 |
| 2 | graph-safe eager | ragged | mixed | 23.0400 | 21.6640 | 23.0400 |
| 2 | graph-safe eager | ragged | short | 4.3200 | 2.2400 | 4.5450 |
| 2 | graph replay | page-table | mixed | 34.5765 | 34.2560 | 34.6885 |
| 2 | graph replay | ragged | mixed | 22.8800 | 21.7280 | 22.8480 |
| 3 | graph-safe eager | page-table | full | 41.3440 | 40.7205 | 41.2480 |
| 3 | graph-safe eager | page-table | mixed | 34.8800 | 34.1760 | 34.9440 |
| 3 | graph-safe eager | page-table | short | 4.6725 | 2.6880 | 4.6400 |
| 3 | graph-safe eager | ragged | full | 27.9360 | 26.5280 | 27.9360 |
| 3 | graph-safe eager | ragged | mixed | 23.0720 | 21.6960 | 23.0400 |
| 3 | graph-safe eager | ragged | short | 4.4160 | 2.2400 | 4.4960 |
| 3 | graph replay | page-table | mixed | 34.5920 | 34.3040 | 34.6720 |
| 3 | graph replay | ragged | mixed | 22.8805 | 21.7280 | 22.8800 |

For each sweep, the paired local-tail reference is `(A1 + A2) / 2`. The table
reports the median paired result across the three sweeps.

| Mode | API | Lengths | Local-tail median (us) | CCCL-fused median (us) | Latency reduction | Speedup |
|---|---|---|---:|---:|---:|---:|
| graph-safe eager | page-table | full | 41.2882 | 40.7040 | 1.394% | 1.014x |
| graph-safe eager | page-table | mixed | 34.8640 | 34.2400 | 1.790% | 1.018x |
| graph-safe eager | page-table | short | 4.6720 | 2.6880 | 42.466% | 1.738x |
| graph-safe eager | ragged | full | 27.9520 | 26.5280 | 5.094% | 1.054x |
| graph-safe eager | ragged | mixed | 23.0482 | 21.6640 | 5.972% | 1.064x |
| graph-safe eager | ragged | short | 4.4325 | 2.2400 | 49.464% | 1.979x |
| graph replay | page-table | mixed | 34.6325 | 34.2560 | 1.087% | 1.011x |
| graph replay | ragged | mixed | 22.8640 | 21.7280 | 4.969% | 1.052x |

The production-shaped full/mixed gains come from removing the second kernel
launch. The short-row stress case also benefits from having the already-running
Top-K CTAs write the suffix rather than launching a separate 256-thread block
per row.

## Limitations

- Operator-only results from one B200/SM100 system; no end-to-end SGLang throughput claim.
- Current SGLang page-table calls use the wide `page_size=1` representation; compact pages were correctness-tested but not included in this timing matrix.
- The reference branch depends on the unmerged CCCL candidate commit and is intentionally not proposed as the current FlashInfer integration target.
