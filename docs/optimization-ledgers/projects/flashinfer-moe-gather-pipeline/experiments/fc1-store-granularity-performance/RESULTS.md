# FC1 store granularity result

The full affected26-cell N3U per-token EP8/TP8 screen is complete. Control is
retained `49c91adf`; candidate is the same source inventory plus swap kernel
`faae8834`. All10,400 raw samples and all26 rows are retained. Tokens1/2 are
excluded only from the22-cell retention aggregate. The four phases use the
same frozen choices/routes and native strict CUPTI cold-L2 CUDA-graph timing.

| Group | Cells | Geomean speedup | Negative cells |
|---|---:|---:|---:|
| band/all | 22 | +0.085% | 10 |
| band/decode | 10 | +0.024% | 5 |
| band/middle | 6 | +0.075% | 2 |
| band/prefill | 6 | +0.197% | 3 |
| model_topology/nemo3-ultra/ep | 11 | +0.179% | 4 |
| model_topology/nemo3-ultra/tp | 11 | -0.009% | 6 |

The aggregate is broadly neutral. EP8K/16K recover +0.700%/+0.692% with tight
repeats and FC1 extensions reduced3.960/6.368µs. EP4K instead regresses−0.229%
with an additional0.720µs FC1 extension. TP overall is−0.009%. The apparent
EP8-token +0.545% has0.966% control repeat spread and is not a dependable gain.
No clock anomalies occurred: all416 quartiles report2032MHz and zero reasons.
All30 paired native configurations have unchanged resources andLOCAL0 across
120 loaded function records. All10 negative retention rows remain visible.

Final source qualification passed16 calls and20 native pairs. Seventeen pairs
are byte-identical to retained49; per-token BF16FC1 restores the prejoin cubin
with non-NOP count3309→3355 and unchanged168registers. Two FP32 fused cases also
restore prejoin binaries; two-CTA registers125→122 is outside this unfused
performance scope. Quantized4/8-bit, gatedFC1, ordinaryFC2 and finalize remain
native-identical for the representative captured cases.

The implementation adds six net source lines and a compile-time grouping loop.
The parent rejects it under the no-neutral-added-complexity rule:
two EP large-token recoveries do not establish a broad benefit, andEP4K loses.
No retuning, selected-shape rescue, source commit or publication update follows.
Independent raw/component/retention replay passed and supports the rejection. Production stays49c.

## All four phase medians

| Model | EP/TP | Mode | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | C spread | A spread |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 1 | 25.440 | 25.472 | 25.456 | 25.409 | -0.156% | 0.122% | 0.061% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 2 | 31.216 | 31.152 | 31.168 | 31.200 | +0.155% | 0.053% | 0.051% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 4 | 39.536 | 39.520 | 39.393 | 39.489 | +0.141% | 0.120% | 0.322% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 8 | 51.345 | 51.377 | 51.249 | 51.841 | +0.545% | 0.966% | 0.249% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 16 | 87.441 | 87.649 | 87.665 | 87.617 | -0.146% | 0.202% | 0.018% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 32 | 110.385 | 110.544 | 110.353 | 110.497 | -0.007% | 0.101% | 0.174% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 64 | 137.361 | 137.073 | 137.249 | 137.057 | +0.035% | 0.222% | 0.128% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 128 | 143.569 | 143.681 | 143.649 | 143.713 | -0.017% | 0.101% | 0.022% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 256 | 149.697 | 149.585 | 149.618 | 149.826 | +0.107% | 0.086% | 0.022% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 512 | 157.250 | 157.089 | 156.865 | 157.169 | +0.148% | 0.052% | 0.143% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 4096 | 328.034 | 328.899 | 328.899 | 328.259 | -0.229% | 0.068% | 0.000% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 8192 | 569.188 | 564.820 | 565.076 | 568.613 | +0.700% | 0.101% | 0.045% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 16384 | 951.847 | 945.111 | 944.774 | 951.112 | +0.692% | 0.077% | 0.036% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 1 | 28.513 | 28.576 | 28.561 | 28.577 | -0.083% | 0.224% | 0.054% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 2 | 33.953 | 34.016 | 33.984 | 34.032 | -0.023% | 0.234% | 0.094% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 4 | 45.168 | 45.200 | 45.025 | 45.152 | +0.106% | 0.035% | 0.390% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 8 | 63.777 | 63.697 | 63.889 | 63.713 | -0.075% | 0.100% | 0.301% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 16 | 88.193 | 88.289 | 88.032 | 88.289 | +0.091% | 0.109% | 0.291% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 32 | 123.344 | 123.505 | 123.553 | 123.441 | -0.110% | 0.079% | 0.039% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 64 | 146.113 | 147.137 | 146.401 | 146.433 | -0.338% | 0.219% | 0.502% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 128 | 153.906 | 153.825 | 154.018 | 153.794 | -0.047% | 0.073% | 0.125% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 256 | 162.642 | 162.386 | 162.401 | 162.834 | +0.212% | 0.118% | 0.010% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 512 | 180.322 | 180.322 | 180.305 | 180.466 | +0.044% | 0.080% | 0.009% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 4096 | 553.956 | 554.516 | 554.630 | 554.246 | -0.085% | 0.052% | 0.021% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 8192 | 979.880 | 978.552 | 978.825 | 979.882 | +0.122% | 0.000% | 0.028% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 16384 | 1801.712 | 1803.391 | 1800.435 | 1801.632 | -0.013% | 0.004% | 0.164% |

## Evidence

- Raw: `evidence/fc1-store-granularity-screen/1793373874703112000/data`.
- Derived: sibling `report/`, including all phase/component/clock/resource data.
- `execution-status.json` binds final source, patch, configuration, qualification,
  raw fetch and result hashes. Both full13245-file source postflights passed.
- GPUs0/1 are idle/released; persistent native compilation caches remain intact.
- Exact/codegen receipts remain under `experiments/fc1-store-granularity/qualification`.

The final independent receipts are `audits/fc1-store-granularity-data-peer.json`,
`components-peer.json` and `retention-peer.json` with the same filename prefix;
`execution-status.json` pins their hashes.
