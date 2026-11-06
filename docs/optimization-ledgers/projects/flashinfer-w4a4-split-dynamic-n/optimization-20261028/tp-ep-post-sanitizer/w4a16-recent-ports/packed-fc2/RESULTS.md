# Packed W4A16 FC2: source-paired screen

Audited **32 cells, 128 medians, 12,800 strict CUPTI samples** against `fd72759b15b8d417d6c791c0382f90d14262a8e4` using unchanged saved 83df winners/routes. Eight model/topology jobs each execute C1, A1, A2, C2; each pass uses 10 warmups and 100 samples. All source, managed-cache, winner, route, command, GPU UUID and raw-median checks pass.

The measured aggregate is effectively neutral: **+0.0233%** overall, **-0.0348% EP**, **+0.0815% TP**. The codegen gate's benefit is reduced static instruction duplication with unchanged registers and zero spills; the original code already used packed FP32 multiplies.

Speedup = geometric mean(C1,C2) / geometric mean(A1,A2) − 1; positive favors candidate.

| Model/topology | T4 | T64 | T4096 | T16384 |
|---|---:|---:|---:|---:|
| V3 EP | -0.048% | -0.034% | -0.073% | -0.888% |
| V41F EP | +0.041% | +0.019% | -1.331% | +1.927% |
| K3 EP | +0.027% | +0.158% | -0.995% | +0.129% |
| N3U EP | +0.058% | +0.084% | -0.620% | +1.031% |
| V3 TP | -0.399% | -0.011% | -0.346% | -0.246% |
| V41F TP | +0.094% | +0.079% | +2.015% | +1.927% |
| K3 TP | +0.205% | +0.153% | -0.267% | -0.705% |
| N3U TP | -0.199% | +0.098% | +0.334% | -1.376% |

EP decode/prefill geomeans: +0.0382% / -0.1079%. TP decode/prefill: +0.0025% / +0.1606%. All four pass medians and their observed variation are retained in `report/cells.csv`; raw samples remain in `perf-evidence/`.

Archive SHA256 `483901fef0be2f8fa49d2b3202c6a6bf09a0bc44ab24ee09c6563118533c0817`; 1,290 files hash-verified. Candidate kernel SHA `a8072d86763f4ebd48e516b39bf2a5f4904c87495ef9764d2babd2f0a3bc9bc2`. This is an independent packed-output screen, not a combined-candidate result or refreshed public benchmark column. No retuning or external baseline rerun.
