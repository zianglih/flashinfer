# SF row-index algebra: isolated candidate

Candidate kernel `5004ca3d`, base `659777aa`. The one expression rewrites `q*p+r` as `row+q*(p-n)`; padding and layout are unchanged. The padding term vanishes naturally at tile N128/N256. No dtype/model branch, new tactic, memory operation, or synchronization change.

Scoped pre-commit passed. CPU identity: 5,263,360 signed row/tile checks. Exact source-paired gate: 32 replay comparisons, 16 GEMM pairs, 4 combine pairs, static/CLC and PDL off/on, N64 SF16 SiTU and N256 SF32 Relu2. N256 FC1 removes 106–107 static non-NOP instructions and 0–2 registers; N64 removes one instruction. FC2 and combine instructions/resources are unchanged; no local/stack or new uniform spill/fill sites.

CAAC uses retained 83df frozen winners/routes through the public functional benchmark, cold L2, 10 warmups, 100 strict CUPTI samples per phase. All 15 jobs completed: 72 cells and 28,800 samples. No AUTO or external baseline rerun. The primary statistic is the geometric mean of two 100-sample medians per arm; positive percentages mean candidate faster. Original output/sample logs remain under `perf-evidence/`.

- Blockscaled 56-cell GM: +0.154%; decode −0.011%; prefill +0.320%.
- Affected FC1 40-cell GM: +0.215%; decode −0.008%; prefill +0.439%.
- Unchanged per-token sanity: +0.002%; unchanged W4A16 sanity: −0.264%. These sources predate the separately retained W4 rank change.
- Largest affected negative: V3 EP MXFP4x8 prefill −2.067%, with phase spreads 1.04/1.50% and first25/last50 −0.239/−2.207%. N3U TP MXFP8 −1.444% approaches zero in both first25 and last50 strata. V3 EP W4A4 decode −0.526% is more stable. N3U TP W4A4 prefill +0.994% has both phase spreads below 0.09%.
- Large positive medians (+3.44%, +4.07%) change sign in later strata; do not attribute those to the source. The unchanged N3U EP W4A16 −4.99% likewise shows substantial measurement variation. Strata do not replace standard medians.

Retention is pending a bounded same-GPU confirmation of the specified negative/positive cells. No result is replaced by the repeat. The later shared-parameter candidate is separate and not included here.

| Topology/model | Mode | Tokens | FC1 N | SF | Candidate delta |
|---|---|---:|---:|---:|---:|
| EP v3 | W4A4 | 4 | 32 | 16 | -0.526% |
| EP v3 | PER-TOKEN | 4 | 16 | — | +0.237% |
| EP v3 | W4A16 | 4 | — | — | +0.062% |
| EP v3 | W4A4 | 16384 | 256 | 16 | +0.248% |
| EP v3 | PER-TOKEN | 16384 | 128 | — | +0.062% |
| EP v3 | W4A16 | 16384 | — | — | -0.583% |
| EP v3 | MXFP8 | 4 | 32 | 32 | +0.081% |
| EP v3 | MXFP4x8 | 4 | 16 | 32 | +0.135% |
| EP v3 | MXFP8 | 16384 | 256 | 32 | +1.693% |
| EP v3 | MXFP4x8 | 16384 | 128 | 32 | -2.067% |
| EP v41-flash | W4A4 | 4 | 16 | 16 | -0.000% |
| EP v41-flash | PER-TOKEN | 4 | 16 | — | +0.185% |
| EP v41-flash | W4A16 | 4 | — | — | -0.020% |
| EP v41-flash | W4A4 | 16384 | 256 | 16 | +0.152% |
| EP v41-flash | PER-TOKEN | 16384 | 128 | — | -0.045% |
| EP v41-flash | W4A16 | 16384 | — | — | +0.880% |
| EP v41-flash | MXFP8 | 4 | 16 | 32 | +0.096% |
| EP v41-flash | MXFP4x8 | 4 | 16 | 32 | +0.071% |
| EP v41-flash | MXFP8 | 16384 | 128 | 32 | +0.793% |
| EP v41-flash | MXFP4x8 | 16384 | 128 | 32 | +0.241% |
| EP kimi-k3 | W4A4 | 4 | 16 | 16 | -0.078% |
| EP kimi-k3 | PER-TOKEN | 4 | 16 | — | -0.070% |
| EP kimi-k3 | W4A16 | 4 | — | — | +0.085% |
| EP kimi-k3 | W4A4 | 16384 | 128 | 16 | +0.337% |
| EP kimi-k3 | PER-TOKEN | 16384 | 128 | — | +0.059% |
| EP kimi-k3 | W4A16 | 16384 | — | — | -0.120% |
| EP kimi-k3 | MXFP4x8 | 4 | 16 | 32 | +0.016% |
| EP kimi-k3 | MXFP4x8 | 16384 | 128 | 32 | +3.445% |
| EP nemo3-ultra | W4A4 | 4 | 16 | 16 | +0.113% |
| EP nemo3-ultra | PER-TOKEN | 4 | 16 | — | -0.379% |
| EP nemo3-ultra | W4A16 | 4 | — | — | +0.152% |
| EP nemo3-ultra | W4A4 | 16384 | 128 | 16 | +0.885% |
| EP nemo3-ultra | PER-TOKEN | 16384 | 128 | — | +0.037% |
| EP nemo3-ultra | W4A16 | 16384 | — | — | -4.986% |
| EP nemo3-ultra | MXFP8 | 4 | 16 | 32 | -0.050% |
| EP nemo3-ultra | MXFP4x8 | 4 | 16 | 32 | -0.204% |
| EP nemo3-ultra | MXFP8 | 16384 | 256 | 32 | +4.070% |
| EP nemo3-ultra | MXFP4x8 | 16384 | 256 | 32 | +0.241% |
| TP v3 | W4A4 | 4 | 32 | 16 | +0.042% |
| TP v3 | PER-TOKEN | 4 | 16 | — | +0.038% |
| TP v3 | W4A16 | 4 | — | — | +0.002% |
| TP v3 | W4A4 | 16384 | 256 | 16 | +0.026% |
| TP v3 | PER-TOKEN | 16384 | 256 | — | +0.022% |
| TP v3 | W4A16 | 16384 | — | — | -0.702% |
| TP v3 | MXFP8 | 4 | 16 | 32 | +0.154% |
| TP v3 | MXFP4x8 | 4 | 16 | 32 | -0.022% |
| TP v3 | MXFP8 | 16384 | 256 | 32 | -0.189% |
| TP v3 | MXFP4x8 | 16384 | 256 | 32 | -0.223% |
| TP v41-flash | W4A4 | 4 | 16 | 16 | +0.022% |
| TP v41-flash | PER-TOKEN | 4 | 16 | — | -0.098% |
| TP v41-flash | W4A16 | 4 | — | — | -0.151% |
| TP v41-flash | W4A4 | 16384 | 256 | 16 | +0.159% |
| TP v41-flash | PER-TOKEN | 16384 | 256 | — | +0.011% |
| TP v41-flash | W4A16 | 16384 | — | — | -0.043% |
| TP kimi-k3 | W4A4 | 4 | 16 | 16 | +0.019% |
| TP kimi-k3 | PER-TOKEN | 4 | 16 | — | -0.122% |
| TP kimi-k3 | W4A16 | 4 | — | — | +0.127% |
| TP kimi-k3 | W4A4 | 16384 | 128 | 16 | -0.015% |
| TP kimi-k3 | PER-TOKEN | 16384 | 128 | — | +0.044% |
| TP kimi-k3 | W4A16 | 16384 | — | — | +0.293% |
| TP kimi-k3 | MXFP4x8 | 4 | 16 | 32 | -0.298% |
| TP kimi-k3 | MXFP4x8 | 16384 | 128 | 32 | +0.133% |
| TP nemo3-ultra | W4A4 | 4 | 16 | 16 | -0.064% |
| TP nemo3-ultra | PER-TOKEN | 4 | 16 | — | +0.057% |
| TP nemo3-ultra | W4A16 | 4 | — | — | +0.101% |
| TP nemo3-ultra | W4A4 | 16384 | 256 | 16 | +0.994% |
| TP nemo3-ultra | PER-TOKEN | 16384 | 256 | — | +0.002% |
| TP nemo3-ultra | W4A16 | 16384 | — | — | +0.812% |
| TP nemo3-ultra | MXFP8 | 4 | 16 | 32 | +0.362% |
| TP nemo3-ultra | MXFP4x8 | 4 | 16 | 32 | -0.022% |
| TP nemo3-ultra | MXFP8 | 16384 | 256 | 32 | -1.444% |
| TP nemo3-ultra | MXFP4x8 | 16384 | 256 | 32 | -0.524% |

Raw source/sample bindings and transfer manifests: `evidence-verification.json`, `perf-evidence-verification.json`, `perf-evidence/perf-audit.json`. No sanitizer was run.
