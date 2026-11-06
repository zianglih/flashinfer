**Paired CUB before/after results**

3 alternating paired rounds, `93e9eef092c1` → `30b1b2e6d127`.
Times below are medians across cases of each case’s median across round medians. Changes are geometric means of paired after/before round ratios, with equal case weight. They are not ratios of the displayed aggregate times. SMALL and LARGE are kept separate.
Paired Δµs is the median of within-round after-minus-before differences; it need not equal the difference of separately summarized before/after times.
Complete public-API GPU work is timed by CUDA events over graph replay, with warm L2; every selection, translation, padding, and plain native index-conversion launch is included. Host dispatch, allocation, and compilation are outside this metric. PR4442’s historical cold-L2 CUPTI measurements use a different metric.

**Normal physical width, random inputs (`d >= k`)**

Native changes provide an independent timing control; their case counts exclude unsupported `k > 2048`. Plain is screened under the same regression rule as the fused APIs.

| Dtype | API | CUB cases S/L | SMALL: before → after µs (change) | LARGE: before → after µs (change) | Native change S / L [cases] |
|---|---|---:|---|---|---|
| fp32 | Page | 23/23 | 13.153 → 13.095 (+0.30%) | 13.306 → 13.274 (+0.22%) | +0.22% [21] / +0.01% [21] |
| fp32 | Page + raw | 23/23 | 13.511 → 13.457 (+0.22%) | 13.407 → 13.376 (+0.42%) | -0.05% [21] / -0.06% [21] |
| fp32 | Ragged | 21/21 | 12.628 → 12.559 (-0.06%) | 12.501 → 12.470 (-0.26%) | -0.15% [19] / -0.15% [19] |
| fp32 | Plain | 21/21 | 11.432 → 11.370 (-0.21%) | 11.236 → 11.217 (-0.22%) | -0.22% [19] / -0.23% [19] |
| fp16 | Page | 2/2 | 33.821 → 33.840 (+0.41%) | 33.891 → 33.960 (+0.50%) | +0.00% [2] / -0.13% [2] |
| fp16 | Page + raw | 2/2 | 34.467 → 34.450 (+0.31%) | 34.619 → 34.464 (+0.19%) | -0.05% [2] / -0.25% [2] |
| fp16 | Ragged | 2/2 | 28.476 → 28.501 (+0.58%) | 28.174 → 28.180 (+0.51%) | +0.00% [2] / -0.12% [2] |
| fp16 | Plain | 2/2 | 27.101 → 27.087 (-0.12%) | 26.729 → 26.695 (-0.17%) | +0.15% [2] / -0.06% [2] |
| bf16 | Page | 2/2 | 34.978 → 34.947 (+0.09%) | 35.766 → 35.751 (-0.04%) | +0.09% [2] / -0.11% [2] |
| bf16 | Page + raw | 2/2 | 35.710 → 35.718 (+0.01%) | 36.431 → 36.402 (-0.11%) | +0.17% [2] / -0.16% [2] |
| bf16 | Ragged | 2/2 | 29.298 → 29.354 (+0.03%) | 29.572 → 29.593 (-0.00%) | +0.18% [2] / -0.06% [2] |
| bf16 | Plain | 2/2 | 27.721 → 27.708 (-0.06%) | 27.968 → 27.965 (-0.06%) | +0.26% [2] / -0.09% [2] |

**Newly supported physical-short inputs (`d < k`)**

Parent CUB rejects these inputs, so no numeric before/after CUB ratio exists. This table compares final CUB against final native on identical supported inputs. Paired rows use `k=2048`; native `k=4096/8193` is n/a and counted separately. Larger-k CUB timings remain in `broad-excluded.csv` and the raw round JSON.

| Dtype | API | Paired cases S/L | SMALL: native → CUB µs (speedup) | LARGE: native → CUB µs (speedup) | Native n/a S/L |
|---|---|---:|---|---|---:|
| fp32 | Page | 8/8 | 4.069 → 2.922 (1.36×) | 4.068 → 2.922 (1.36×) | 2/2 |
| fp32 | Page + raw | 8/8 | 4.982 → 3.046 (1.64×) | 4.969 → 3.065 (1.62×) | 2/2 |
| fp32 | Ragged | 7/7 | 3.393 → 2.820 (1.21×) | 3.393 → 2.819 (1.22×) | 2/2 |
| fp32 | Plain | 6/6 | 4.550 → 2.814 (1.51×) | 4.570 → 2.828 (1.50×) | 2/2 |
| fp16 | Page | 1/1 | 4.090 → 2.882 (1.41×) | 4.111 → 2.891 (1.42×) | 0/0 |
| fp16 | Page + raw | 1/1 | 5.010 → 3.004 (1.66×) | 4.991 → 3.025 (1.65×) | 0/0 |
| fp16 | Ragged | 1/1 | 3.329 → 2.840 (1.16×) | 3.313 → 2.834 (1.16×) | 0/0 |
| fp16 | Plain | 1/1 | 4.581 → 2.759 (1.67×) | 4.581 → 2.758 (1.66×) | 0/0 |
| bf16 | Page | 1/1 | 4.110 → 2.942 (1.41×) | 4.112 → 2.932 (1.41×) | 0/0 |
| bf16 | Page + raw | 1/1 | 5.009 → 3.045 (1.65×) | 5.010 → 3.046 (1.64×) | 0/0 |
| bf16 | Ragged | 1/1 | 3.332 → 2.881 (1.16×) | 3.332 → 2.882 (1.16×) | 0/0 |
| bf16 | Plain | 1/1 | 4.602 → 2.747 (1.67×) | 4.602 → 2.756 (1.67×) | 0/0 |

<details>
<summary>Logical-length and tied-boundary controls</summary>

**Logical-short, random inputs (`d >= k`, every row’s logical length <= k)**

This cohort retains the normal physical width and includes empty rows, nonzero score windows, and explicit zero page-table starts. Its before/after ratios remain separate from physical-short support.

| Dtype | API | CUB cases S/L | SMALL: before → after µs (change) | LARGE: before → after µs (change) | Native change S / L [cases] |
|---|---|---:|---|---|---|
| fp32 | Page | 9/9 | 3.291 → 3.290 (-0.21%) | 2.901 → 2.901 (-0.38%) | -0.45% [9] / -0.04% [9] |
| fp32 | Page + raw | 9/9 | 3.506 → 3.497 (-0.13%) | 3.477 → 3.476 (-0.17%) | -0.30% [9] / -0.08% [9] |
| fp32 | Ragged | 9/9 | 2.902 → 2.902 (-0.89%) | 2.901 → 2.902 (-0.92%) | +0.36% [9] / -0.49% [9] |
| fp16 | Page | 1/1 | 3.639 → 3.659 (+0.15%) | 3.597 → 3.598 (+0.18%) | -0.08% [1] / -0.00% [1] |
| fp16 | Page + raw | 1/1 | 3.885 → 3.882 (-0.21%) | 3.834 → 3.843 (-0.09%) | +0.17% [1] / +0.04% [1] |
| fp16 | Ragged | 1/1 | 2.921 → 2.923 (+0.04%) | 2.923 → 2.922 (+0.02%) | -0.04% [1] / +0.03% [1] |
| bf16 | Page | 1/1 | 3.556 → 3.578 (+0.20%) | 3.638 → 3.680 (+0.73%) | -0.05% [1] / +0.10% [1] |
| bf16 | Page + raw | 1/1 | 3.783 → 3.791 (-0.01%) | 3.823 → 3.885 (+1.26%) | +0.00% [1] / -0.13% [1] |
| bf16 | Ragged | 1/1 | 2.881 → 2.922 (+0.71%) | 2.881 → 2.922 (+0.69%) | +0.92% [1] / +0.68% [1] |

**Mixed logical lengths, random inputs**

| Dtype | API | CUB cases S/L | SMALL: before → after µs (change) | LARGE: before → after µs (change) | Native change S / L [cases] |
|---|---|---:|---|---|---|
| fp32 | Page | 1/1 | 19.275 → 19.480 (+0.64%) | 19.398 → 19.480 (+0.49%) | -0.19% [1] / -0.13% [1] |
| fp32 | Page + raw | 1/1 | 20.076 → 20.232 (+0.49%) | 19.827 → 19.970 (+0.51%) | -0.18% [1] / -0.20% [1] |
| fp32 | Ragged | 1/1 | 18.005 → 18.212 (+0.78%) | 17.802 → 17.966 (+0.61%) | -0.11% [1] / -0.12% [1] |

**Deliberately tied boundary (`pivot_tie`)**

| Dtype | API | CUB cases S/L | SMALL: before → after µs (change) | LARGE: before → after µs (change) | Native change S / L [cases] |
|---|---|---:|---|---|---|
| fp32 | Page | 3/3 | 21.487 → 21.383 (+0.58%) | 19.746 → 19.583 (+0.11%) | +0.38% [2] / -0.11% [2] |
| fp32 | Page + raw | 3/3 | 23.106 → 22.935 (+0.07%) | 19.909 → 19.746 (+0.45%) | -0.13% [2] / +0.42% [2] |
| fp32 | Ragged | 3/3 | 20.546 → 20.381 (+0.07%) | 18.641 → 18.497 (+0.02%) | -0.10% [2] / -0.11% [2] |
| fp32 | Plain | 3/3 | 21.139 → 21.160 (-0.04%) | 17.688 → 17.710 (-0.01%) | -0.13% [2] / -0.13% [2] |

</details>

**Regression screen and worst measured CUB cases**

Screen: paired geometric-mean increase >=5% **and** median paired increase >=0.25 µs. 0/304 comparable CUB cases and 0/354 native controls meet it. A screen hit requires investigation; being below it does not mean zero change. The table includes the largest changes even below the screen.

| Case | Before → after µs | Change | Paired Δµs | Screen | Native change |
|---|---|---:|---:|---|---:|
| `page_raw-fp32-random-normal-b1-d2048-k2048-Lfull-w0-p64-large` | 3.326 → 3.595 | +3.94% | +0.000 | below | +2.47% |
| `page_raw-fp32-random-logical_short-b1-d4096-k2048-Lshort-w0-p64-large` | 2.902 → 2.902 | +2.26% | +0.000 | below | -0.03% |
| `page-fp32-random-normal-b1-d16384-k2048-Lfull-w0-p1-small` | 11.470 → 11.800 | +2.16% | +0.368 | below | -0.12% |
| `page_raw-fp32-random-normal-b1-d16384-k2048-Lfull-w0-p1-large` | 11.574 → 11.901 | +2.15% | +0.362 | below | +0.00% |
| `page_raw-fp32-random-normal-b1-d16384-k256-Lfull-w0-p64-large` | 10.376 → 10.603 | +2.12% | +0.228 | below | +1.48% |

`broad-paired.csv` retains every comparable case, all round medians, paired ratios, and screen results; `broad-excluded.csv` records every unsupported comparison. The final `flagged.csv` files are empty and omitted from the gist; each `analysis.json` records zero hits, and each round’s JSON retains all timing samples. These tables do not replace the raw evidence.

**Longer-batch follow-up for small-case variation**

One page-plus-raw case temporarily crossed the screen after two broad pairs; the complete three-pair sweep has no hits. We retained that full sweep and separately reran all four API forms and both tie modes at batch 1, FP32 random inputs, `(d,k) = (2048,2048), (4096,2048), (16384,256)`. These are 24 existing workload IDs, not 24 additional unique workloads.

Three more alternating pairs used **500 calls per graph and 100 samples**, with seeds `20260923 + round`. All 24 CUB cases and 24 native controls stayed below the screen. The largest CUB increase was **+0.038%**; CUB's geometric-mean change was **−0.075%**. The increase did not reproduce in these selected cases with longer timing batches. This follow-up does not rerun every broad case with an increase, including logical-short d=4096 and page-size-1 d=16384/k=2048. Original results remain included above and in the raw files.

| CUB case | Before → after µs | Paired change |
|---|---|---:|
| `page-fp32-random-normal-b1-d16384-k256-Lfull-w0-p64-small` | 10.279296 → 10.265024 | -0.055% |
| `page_raw-fp32-random-normal-b1-d16384-k256-Lfull-w0-p64-large` | 10.549440 → 10.535296 | -0.074% |
| `page_raw-fp32-random-normal-b1-d2048-k2048-Lfull-w0-p64-large` | 3.609664 → 3.609536 | -0.039% |
| `page_raw-fp32-random-normal-b1-d2048-k2048-Lfull-w0-p64-small` | 3.654400 → 3.654368 | -0.051% |
