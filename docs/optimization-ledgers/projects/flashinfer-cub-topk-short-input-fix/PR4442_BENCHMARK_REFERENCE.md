# FlashInfer top-k: CUB `DeviceBatchedTopK` backend benchmarks (B200, post tail-fill rerun)

Environment: NVIDIA B200 (SM100, 183 GB), driver 595.58.03, CUDA runtime 13.2 (nvcc 13.0.88),
PyTorch 2.9.0a0+nv25.10, `cupti-python` 13.3.1 (all timings are CUPTI hardware timings; cold L2;
dry runs + 100 measured iterations, median). FlashInfer branch `cub-device-batched-topk` @
`5868b905`, CCCL submodule at main (contains the merged `cub::DeviceBatchedTopK`). The JIT cache
was cleared before the runs, so every kernel was built from these sources.

**Why this rerun.** The CUB transform wrappers previously issued their `-1` tail padding as
Python `fill_()` calls before selection, which billed a device-idle host gap to every eager
call. That padding now runs as a C++ post-selection tail kernel launched back-to-back with
`DeviceBatchedTopK`, which roughly halves eager CUB transform times (and adds one small node to
graphs). All numbers from before that change are superseded by this data set.

**What is measured.** CUB is integrated as a dispatcher backend of the three public top-k APIs —
`top_k`, `top_k_page_table_transform`, `top_k_ragged_transform` — selectable via
`FLASHINFER_TOPK_ALGO=cub`. The `CUB` columns run the *same public API call on the same tensors*
forced to the CUB backend: for the transforms that includes the fused page-table / ragged-offset
translation (inside CUB's output iterators) and the `-1` tail padding; for plain `top_k` it
includes writing int64 indices in-kernel. The `FlashInfer` / `FlashInfer(tie-*)` columns pin the
native radix backend (`FLASHINFER_TOPK_ALGO=default`). `CUBvsFI` and `CUBvsFI(tie-s/l)` are
native-time / CUB-time, so >= 1.0x means CUB wins; gm = geometric mean.

Three run sets, three dtypes each (fp32/fp16/bf16):

- **Eager** (`--op all --tie-break`): plain calls, per-call host dispatch included.
- **CUDA graphs** (`--cuda-graph --tie-break`): each call captured once, replays timed;
  FlashInfer calls pass `dsa_graph_safe=True` (matching SGLang's graphed usage; native =
  FilteredTopK, VEC_SIZE=1). The Clusters column is skipped (that backend declines
  `dsa_graph_safe`).
- **Clusters comparison** (`--op all`, no tie, no graphs — the only regime the SM100 clusters
  backend serves): its `CUBvsClusters` column is clusters-time / CUB-time, >= 1.0x means CUB
  wins.

Grid: batch {1, 16, 32, 64, 128, 256} x seq_len {256 ... 524288, powers of two incl. 32768} x
k {256, 512, 1024, 2048, 4096}, plus two large-batch stress rows (top_k) and a varlen section
with realistic per-row length distributions. Full raw outputs, one file per run with
collapsible per-section tables:
[eager fp32](#file-z_raw_eager_fp32-md) | [eager fp16](#file-z_raw_eager_fp16-md) | [eager bf16](#file-z_raw_eager_bf16-md) | [graph fp32](#file-z_raw_graph_fp32-md) | [graph fp16](#file-z_raw_graph_fp16-md) | [graph bf16](#file-z_raw_graph_bf16-md) | [clusters fp32](#file-z_raw_clusters_fp32-md) | [clusters fp16](#file-z_raw_clusters_fp16-md) | [clusters bf16](#file-z_raw_clusters_bf16-md)

## Eager results (CUB wins / cells, gm CUBvsFI; no-tie / tie-small)

| Section | fp32 | fp16 | bf16 |
|---|---|---|---|
| top_k | 248/302 (1.56) / 204/254 (1.53) | 264/302 (1.55) / 220/254 (1.68) | 270/302 (1.58) / 229/254 (1.81) |
| dsa_topk | 3/4 (1.89) / 3/4 (2.61) | 4/4 (2.32) / 4/4 (2.85) | 4/4 (2.34) / 4/4 (2.78) |
| page_table | 73/300 (0.80) / 145/252 (1.05) | 71/300 (0.73) / 123/252 (1.07) | 79/300 (0.76) / 118/252 (1.13) |
| ragged | 112/300 (0.96) / 157/252 (1.12) | 125/300 (0.89) / 111/252 (1.23) | 129/300 (0.93) / 134/252 (1.33) |
| varlen | 16/48 (0.84) / 20/48 (0.92) | 20/48 (0.82) / 20/48 (0.95) | 21/48 (0.86) / 25/48 (1.11) |

- Plain `top_k` is unchanged by the tail-fill work (it never padded): CUB wins ~82–89% of
  cells; the loss region remains batch >= 128 at seq 16384–65536.
- Transforms moved dramatically vs the pre-tail-fill data (fp32 page gm 0.44 -> 0.80, ragged
  0.46 -> 0.97, with zero cells regressing): eager no-tie is near parity on average, and eager
  *tie-break* now favors CUB outright — small-d across batches plus large-d at small batch.
- Native tie-break still rejects k=4096 (`UNSUPPORTED`, 48 cells/section) where CUB runs fine.

## Clusters backend comparison (eager no-tie — the only regime clusters serves)

CUB wins / comparable cells, with gm(CUBvsClusters); < 1.0 means clusters is faster:

| Section | fp32 | fp16 | bf16 |
|---|---|---|---|
| top_k | 116/302 (gm 0.90) | 32/302 (gm 0.75) | 42/302 (gm 0.79) |
| dsa_topk | 1/4 (gm 0.88) | 1/4 (gm 0.81) | 1/4 (gm 0.82) |
| page_table | 8/300 (gm 0.61) | 0/300 (gm 0.49) | 2/300 (gm 0.52) |
| ragged | 44/300 (gm 0.73) | 5/300 (gm 0.61) | 14/300 (gm 0.65) |
| varlen | 5/42 (gm 0.73) | 0/42 (gm 0.55) | 2/42 (gm 0.60) |

- Clusters still wins the transforms overall, but the margin halved with CUB's eager
  improvement (page fp32 gm 0.34 -> 0.61, ragged 0.36 -> 0.73), and CUB now takes real cells:
  notably the expanded per-token varlen layouts (512–2048 rows at long d, 2.2–2.9x over
  clusters) and scattered single-row / fp32 mid-d cells.
- Plain top_k vs clusters is essentially unchanged: CUB keeps the fp32 8192 band, fp32
  small-batch mid-d, and single-row long-d; clusters wins the rest (86–89% of 16-bit cells).

## CUDA-graph results (what SGLang's graphed calls experience)

| Section | fp32 no-tie / tie-s | fp16 no-tie / tie-s | bf16 no-tie / tie-s |
|---|---|---|---|
| top_k | 246/254 (1.97) / 243 (1.92) | 238/254 (1.72) / 238 (1.91) | 238/254 (1.80) / 240 (2.00) |
| dsa_topk | 4/4 (3.20) / 4 (3.61) | 4/4 (3.19) / 4 (3.89) | 4/4 (3.63) / 4 (4.22) |
| page_table | 102/252 (1.14) / 191 (1.39) | 87/252 (0.94) / 139 (1.32) | 91/252 (0.99) / 141 (1.34) |
| ragged | 148/252 (1.37) / 223 (1.55) | 104/252 (1.14) / 177 (1.57) | 107/252 (1.21) / 181 (1.64) |
| varlen | 24/48 (1.19) / 29 (1.26) | 20/48 (1.00) / 29 (1.25) | 26/48 (1.27) / 30 (1.41) |

Nearly identical to the pre-tail-fill graph data — replay had already removed the fill gap —
but the extra tail-fill node costs ~2–5% (per-cell gm 0.95–0.98), which flips a set of
marginal cells back to native (e.g. page tie: 90 win->loss vs 12 loss->win cell flips).

## Graph vs eager, decomposed (per-cell gm of graph/eager on identical cells)

| Section | fp32 CUBvsFI-shift / CUB-time / FI-time | fp16 | bf16 |
|---|---|---|---|
| top_k | 1.30 / 1.00 / 1.30 | 1.12 / 1.00 / 1.12 | 1.15 / 1.00 / 1.15 |
| page_table | 1.45 / 0.97 / 1.41 | 1.28 / 0.98 / 1.25 | 1.31 / 0.98 / 1.28 |
| ragged | 1.48 / 0.95 / 1.41 | 1.31 / 0.95 / 1.25 | 1.33 / 0.96 / 1.27 |

CUB's time is now regime-invariant everywhere (gm 0.95–1.00 — its eager numbers are already
pure kernel time, so graph replay saves it nothing); the entire ratio shift under graphs is the
native side's graph-safe configuration slowing 1.12–1.41x. Before the tail-fill change, CUB's
transform time halved under replay; that asymmetry is gone.

## Notable findings

- **fp16 vs bf16 are not interchangeable at the margins**: CUB itself is dtype-invariant for
  16-bit keys, but the *native* radix tie-break path is ~30% slower for bf16 specifically while
  fp16 tie is free — so bf16 tie-break cells flip to CUB where fp16 ones do not. fp16 also lags
  fp32/bf16 on the graphed ragged transform at large batch.
- Some regions are k-dependent (the same batch/seq wins at k <= 512 and loses at k >= 1024, or
  vice versa), and uniform-length grid rows can disagree with varlen rows at the same
  (batch, max_len) — limits of any shape-only routing heuristic.
- All 9 runs were clean: exit 0, CUPTI active throughout, no crashes, no OOM; the only
  UNSUPPORTED entries are the known native tie-break k=4096 rejections.

## Routing

These results back the shape-based performance gates in `flashinfer/topk.py`
(`is_cub_topk_beneficial`, `is_cub_page_table_transform_beneficial`,
`is_cub_ragged_transform_beneficial`), each structured as: forced-algo override -> graphed
thresholds -> clusters-aware thresholds (when the SM100 clusters backend can serve the call) ->
radix-calibrated eager thresholds. Post tail-fill, CUB serves plain `top_k` broadly (minus the
large-batch cluster-tier pocket), the transforms route to CUB under graphed/`dsa_graph_safe`
conditions and — new in this data set — across much of the eager tie-break space and eager
large-d at small batch, while clusters keeps most eager no-tie transform traffic except the
expanded per-token wide-row layouts. Gates were validated cell-by-cell against all ~17k
measurements (worst surviving bad-allow ~0.8x, all k-split noise inside winning cells).
`FLASHINFER_TOPK_ALGO=cub` forces the CUB backend past the gates.
