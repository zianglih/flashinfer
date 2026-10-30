# Paired W4A16 SiTU refresh evidence

Retained source: `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`.
The fresh experiment measured retained `49c91adf` plus the frozen `5e61d045`
W4 kernel. The committed kernel has exactly those qualified bytes. Earlier
records retain their original measured revisions and environments.

- **Reason for retention:** the private paired helper removes duplicated
  scalar arithmetic and 13 net source lines, with no new state, policy,
  interface, tactic, or oracle. It preserves the Python-beta reciprocal,
  separate RN multiply/subtract, and scalar FTZ EX2/RCP. Qualification covers
  12 exact calls and 18 native pairs; 14 unaffected pairs are byte-identical.
  Actual EP16/32 winning FC1 images remove 24/48 non-NOP instructions at the
  same 96 registers and zero local memory. Their FC2/finalizer images are
  byte-identical. Local epilogue instruction scheduling does change.
- **Primary paired result:** all 26 K3 EP8/TP8 W4A16 cells, C/A/A/C with 10,400
  untrimmed CUPTI samples. Tokens 1/2 remain in raw data but are excluded from
  retention. The 22 retention cells have +0.275% GM; decode 4–64 is −0.047%,
  middle 128–512 is −0.011%, and prefill is +1.103%. All nine negative retention
  rows remain, including EP16/32 at −0.720%/−0.452%. Prefill repeat spread and
  clock variation prevent claiming a dependable prefill speedup.
- **Separate diagnostic:** a six-cell A/C/C/A repeat uses the same source,
  routes, choices and timing contract. EP16/32 become +0.007%/+0.097%, while
  EP128 is −0.101%; the repeated prefills still have variation. All 2,400 raw
  samples remain separate. No repeat replaces any primary table row, and
  the smaller token list prevents attributing the difference uniquely to
  phase order. See `paired-situ-acca/` and `source/campaign-comparison.json`.
- **Full matrix:** 26 fresh plus 442 exactly reused candidate rows, 468 total.
  Reuse is all 364 unchanged swap rows and 78 non-SiTU W4 rows selecting
  unchanged compile-time graphs. Representative unchanged native identities
  support this boundary; not all 442 signatures were recompiled. Previous
  W4-tail and integer-store results remain unchanged.
- **Historical comparisons:** original TRTLLM, non-swap CuTe and pre-PR W4
  baselines are unchanged. The retained baseline is the historical measured
  `326c4a79` data, production-equivalent to `82254e20`. Full 468-cell plots are
  not a fresh paired comparison. The 396 displayed cells omit tokens 1/2 and
  preserve 165 negative historical rows; historical GM is +0.278% (swap
  +0.245%, W4 +0.395%).
- **Timing/resource evidence:** 93,600 selected candidate samples (5,200 fresh
  plus 88,400 reused), 1,156 loaded native function records with zero local
  memory. Primary paired evidence has 120 loaded functions and 416 telemetry
  quartiles, with 37 exceptions and one missing observation; separate ACCA
  has 48 functions and 96 quartiles, four exceptions and none missing. The
  mixed candidate view has 3,744 quartiles, 89 exceptions and one missing
  observation. No sample filtering, new tuning, sanitizer, or distributed
  timing is implied by this refresh.

## Environment and measurement contract

Fresh 26-cell and separate diagnostic measurements use two independent B300
GPUs on an eight-B300 node, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.78,
CUDA driver 595.91.07, CuTe DSL 4.8.0, CUPTI Python 13.2.0 / runtime 13.2.86,
and PyTorch package `2.12.0a0+5aff3928d8.nv26.5.50603568`. Recovery receipts
pin the actual native routing/moe-utils libraries and release-cache checks;
those ELF bytes are not asserted identical to earlier runtime cohorts.

The native public benchmark is `benchmarks/bench_moe_deepseek.py`, model
`kimi-k3`, topology `--ep 8 --tp 1` or `--ep 1 --tp 8`, `--quant-family nvfp4`,
`--functional-api --backends cutedsl --swap-ab --no-fused-finalize --include-activation-quant`,
`--warmup 10 --iters 100 --no-autotune --output-format both`, and tokens
`1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. The saved observer selects W4A16
only, loads frozen choices, requires the original cache hit and route identity,
records any deterministic default resolution against native resources, and
rejects AUTO/event fallback. Exact argv, observer code, choices, launch and
source receipts accompany each raw phase. CUDA Graph replay uses strict
CUPTI timing and cold L2. Each arm's latency is the geometric mean of its two
100-sample phase medians; paired speedup is `100 × (control/candidate − 1)`.

## Contents

- `report/`, `external/`, `plots/`: full rows, unchanged historical fields,
  provenance, native resources, clocks, full EP/TP plots and paired 26-cell plot.
- `stdout/`: 142 original logs, eight fresh CAAC logs plus 134 inherited logs.
- `completed-tables/`: 15 printed tables across 16 groups, emitted from 26 fresh
  and 442 reused final-pass CuTe records plus 390 historical TRTLLM records.
  All 51 original final-pass stdout suffixes reproduce byte-for-byte before
  joining families. These final-pass tables differ from two-pass heatmaps.
  Missing/unsupported entries stay N/A. Older BF16 records report CUDA Graphs
  and CUPTI but predate strict per-record timing guards.
- `evidence/`: both immutable primary and diagnostic fetch manifests and raw
  records, all phases, telemetry, frozen choices, source/cache/resource guards.
- `source/`, `audits/`, `experiments/`, `runtime/`: exact source integration,
  reuse and qualification boundaries, native evidence, rounding/source audits,
  separate diagnostic comparison, and the recovery runtime receipts.
- `previous-integer-publication/`: every member of the previously sealed
  integer-store archive, verified unchanged. This refresh is built directly
  as XZ without embedding a nested archive.

The original GLM5 comparison is unchanged; no new MegaMoE timing is implied.
No exceptional-NaN payload device test was added. The earlier capture path
and metadata failures remain recorded as harness failures, not passing gates.
Prior publication directories are untouched. Body drafts and publisher logs
are excluded from the archive.
