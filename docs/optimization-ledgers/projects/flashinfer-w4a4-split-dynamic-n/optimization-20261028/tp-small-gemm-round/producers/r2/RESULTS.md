# One-CTA rank folding R2

Retainable as a general instruction cleanup. A physical cluster of one CTA has rank zero; the two-CTA expression is unchanged. No scheduling, storage, barriers, tactics, or model policy changed.

- Base: `1054743780dda2919c1424124c1e3258248b8c19`. Candidate kernel: `7932107248fa69ae0e843896d5931430d987be2ad4571fd15f77b1505238a5aa`. Source changes remain unstaged in `flashinfer-tp-producer-review`.
- Exact/codegen: 112 storage-bit comparisons, 56 GEMM pairs and 10 unchanged combines. All 24 two-CTA streams/resources identical; 32 one-CTA streams remove 10–42 static non-NOP instructions. Registers −12..+2; no local/stack spills, unchanged uniform spill/fill counts. Hardware-rank reads elsewhere in SDK code can increase; static totals are not a blanket dynamic instruction claim.
- Matched C-A-A-C: 15 jobs, 144 cells, 57,600 raw CUPTI samples. Four models, EP/TP, tokens 4/64/4096/16384; 10 warmups, 100 cold-L2 samples per phase. Frozen 83df winners/routes, no autotune. TP V41 MX and K3 MXFP8 omitted as unsupported. 32 W4A16 cells are unchanged sanity controls.

| Subset | Cells | Geomean | Worst | Best |
|---|---:|---:|---:|---:|
| All blockscaled | 112 | +0.052% | -2.809% | +2.742% |
| Affected one-CTA | 53 | +0.342% | -0.313% | +2.742% |
| Affected decode | 40 | +0.208% | -0.313% | +1.036% |
| Affected prefill | 13 | +0.753% | -0.206% | +2.742% |
| Unchanged two-CTA | 59 | -0.208% | -2.809% | +0.391% |
| Unchanged W4A16 | 32 | +0.083% | -2.307% | +4.423% |

Positive means candidate faster: `sqrt(C1*C2)/sqrt(A1*A2)-1`, using each phase's standard 100-sample median. First/last quartiles remain diagnostics only.

The strongest affected cell is N3U EP W4A4 T4096 (+2.742%; control spread 0.060%, candidate spread 0.303%; first/last-quartile +3.036/+2.790%). Worst affected cell is K3 TP per-token T4 (−0.313%). The large −2.81% N3U EP MXFP4x8 T16384 and −2.52% V3 EP MXFP8 T16384 cells select unchanged two-CTA code and show phase variation; they cannot establish a causal rank-folding regression.

Raw artifact audit checked source hashes/native links, observer and helper identity, cache immutability, route identity, selected tactics, no tuner calls/admission, CUPTI-only 100 samples and exact reported medians. All 2,047 archive members verified. See `perf-evidence/perf-audit.json`, `perf-evidence/perf-cells.csv`, `perf-evidence-verification.json`, and source-bound `RETENTION.json`. No sanitizer or external-baseline rerun. No publication-table replacement from this diagnostic.
