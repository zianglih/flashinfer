# Complete FC1 integer-carried-store evidence

The full affected104-cell N3U EP8/TP8 matrix is complete. It preserves the original32 rows exactly and adds72 disjoint rows. All41,600 untrimmed CUPTI samples, all39 raw negative rows and all clock anomalies remain; tokens1/2 are excluded only from the88-cell retention aggregate.

Control: retained`bf072d26b163e71458e7e4dfb12e615b19bd2c9a`. Candidate: final swap source`482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`. Both campaigns use the same immutable source inventories, four-phase C-A-A-C,100samples/phase,10warmups,coldL2,CUDAgraphs and strict nativeCUPTI. Original choices/routes/cache entries are frozen; no tuning, compiler-policy change or sanitizer. Per-cell speedup is`sqrt(C1median*C2median/(A1median*A2median))-1`.

| Group | Retention cells | Geomean speedup | Negative cells |
|---|---:|---:|---:|
| all | 88 | +0.643% | 32 |
| quantized-payload | 66 | +0.863% | 23 |
| band/decode | 40 | +0.054% | 15 |
| band/middle | 24 | -0.022% | 14 |
| band/prefill | 24 | +2.309% | 3 |
| mode/CuteDSL W4A4 | 22 | +1.065% | 6 |
| mode/CuteDSL MXFP4x8 | 22 | +0.738% | 9 |
| mode/CuteDSL MXFP8 | 22 | +0.786% | 8 |
| mode/CuteDSL PER-TOKEN | 22 | -0.013% | 9 |
| Quantized prefill | 18 | +3.144% | 0 |

Decode means4–64tokens; middle means128–512; prefill means4096/8192/16384. Decode/middle are effectively neutral. Every quantized prefill cell improves, from+0.390% to+5.965%; the W4A4 large-token gains have tight repeats. Several MX16K repeats remain noisy, so their individual magnitude should not be overinterpreted.

Per-token is an unchanged-store-width comparator, not an identical binary. Its overall result is neutral. Preserve the EP8192−0.787% andEP16384−0.544% losses explicitly, plus all small decode/middle negatives; no dtype-specific rescue or claim of uniform improvement. The EP8192 FC1 extension grows4.688µs; the EP16384 FC1 extension grows5.440µs. Other component durations overlap throughPDL and must not be summed as independent timings.

All155 paired guarded native compilation configurations retain identical resources andLOCAL0 across620loaded-function records. Of1,664clock quartiles,17 show non2032MHz/nonzero reasons and none are missing. No measurements were excluded for clocks or repeats.

## Full matrix

| Topology | Mode | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 512 | 4096 | 8192 | 16384 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EP8 | CuteDSL MXFP4x8 | +0.154% | -0.241% | +0.000% | +0.456% | -0.049% | +0.168% | -0.163% | -0.062% | -0.006% | +0.058% | +3.614% | +3.492% | +3.660% |
| EP8 | CuteDSL MXFP8 | -0.100% | -0.415% | +0.151% | +0.250% | +0.132% | +0.005% | -0.075% | -0.061% | -0.079% | -0.023% | +1.585% | +2.587% | +1.973% |
| EP8 | CuteDSL PER-TOKEN | +0.126% | +0.080% | +0.080% | -0.280% | +0.146% | +0.051% | -0.023% | -0.066% | -0.080% | +0.152% | +0.397% | -0.787% | -0.544% |
| EP8 | CuteDSL W4A4 | +0.116% | -0.061% | +0.115% | -0.322% | -0.143% | -0.148% | -0.025% | +0.047% | -0.411% | -0.165% | +3.664% | +4.730% | +5.965% |
| TP8 | CuteDSL MXFP4x8 | -0.072% | +0.057% | +0.240% | +0.214% | -0.156% | -0.108% | +0.164% | -0.157% | -0.111% | -0.048% | +3.377% | +0.390% | +1.468% |
| TP8 | CuteDSL MXFP8 | -0.030% | +0.138% | +0.090% | +0.009% | -0.122% | +0.053% | -0.026% | -0.094% | -0.190% | +0.043% | +2.353% | +4.244% | +4.716% |
| TP8 | CuteDSL PER-TOKEN | -0.140% | +0.140% | +0.287% | +0.013% | -0.045% | +0.304% | -0.098% | +0.146% | +0.034% | +0.022% | +0.009% | +0.006% | -0.012% |
| TP8 | CuteDSL W4A4 | +0.337% | +0.389% | +0.119% | +0.066% | +0.126% | +0.444% | +0.268% | +0.211% | +0.310% | +0.005% | +2.303% | +2.281% | +4.358% |

## Qualification, scope and provenance

- `combined104/table.md` contains all104 rows with four raw phase medians and repeat spreads; `cells.csv` and`summary.json` bind both source configs and both immutable input reports.
- Initial data:`evidence/fc1-integer-store-screen/1793370953565557000/data`; extension:`evidence/fc1-integer-store-remaining/1793371744150407000/data`. Native report replay verifies every sample span, route, tactic, cache, source and resource receipt. Original32 row dictionaries are unchanged.
- Final source qualification selected16exact calls/20native pairs withLOCAL0. The failed metadata-only orchestration receipt is preserved, and the separate fused leaf supplies complete source postflight. The unrelated fused two-CTA signature grows122→125registers; the benchmark remains unfused and all measured resources are unchanged.
- `scope-reuse-final.json` binds eight additional gated exact calls and12byte-identical native pairs against the actualbf072performance sources: FP8 SwiGLU andFP4/FP8/BF16SiTU. Together with priorFP4SwiGLU equality and source specialization proof, this supports reusing260gated swap cells and104untouched W4cells. It does not claim individually recompiling all364reused cells.
- Historicald2aaaqualification andfailedcdb2generic-recastLOCAL272 evidence remain separate. Only final482b was timed. The original source manifest's13,245qualified files match cleanbf072; native third-party assets are separately pinned by symlink and releaseNinja receipts.
- GPUs0–3 are idle/released. No source commit, push or PR publication was performed by this experiment. Full retention remains the parent's decision after the combined independent audit.
