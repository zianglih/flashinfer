# Independent retention recommendation: reject R1 unsigned prepare indexing

Do not retain R1. Keep retained33b7 and its published tables. Do not add a model/dtype exception or substitute confirmation values into the original full matrix.

The full468-cell matrix was independently verified from4,208 fresh+retained artifact hashes and187,200 raw samples. Excluding tokens1/2, all formats are−0.1023% geometric-mean speedup (scaled−0.1061%, shared W4A16−0.0888%). Those saved-control results have a25.5–34.1minute gap and do not alone establish causation.

The fresh same-device CAAC confirmation independently passes522 hashes,14cells and5,600 raw CUPTI samples with unchanged sources, route identities, frozen winning tactics and managed-cache contents. It confirms meaningful K3 TP prefill costs:

| Cell | Saved-AA comparison | Fresh CAAC | C1 / A1 / A2 / C2 (µs) |
|---|---:|---:|---|
| kimi-k3 EP CuteDSL W4A4 T8 | -1.461% | -0.719% | 81.825 / 82.433 / 82.305 / 81.729 |
| kimi-k3 TP CuteDSL W4A4 T16384 | -2.287% | -2.468% | 1537.320 / 1581.001 / 1579.081 / 1544.777 |
| kimi-k3 TP CuteDSL PER-TOKEN T16384 | -1.890% | -1.713% | 2152.300 / 2189.100 / 2190.028 / 2151.804 |
| v41-flash EP CuteDSL W4A16 T8192 | -3.666% | -2.386% | 750.164 / 775.460 / 733.380 / 722.372 |

For K3 TP16K W4A4 and per-token, both candidate phase medians exceed both controls, and first25/last25/last50 diagnostic ratios are all negative. The W4A4 stratum losses are−2.68/−2.53/−2.33%; per-token−1.67/−1.83/−1.75%. Standard100-sample medians remain the primary result. K3 EP8 W4A4 also retains a smaller−0.719% cost; TP MXFP4x8 T8/T16 retains−0.447/−0.820%.

W4A16 is affected by the shared prepare change. Its V41F EP8192 full-matrix−3.666% becomes−2.386% in confirmation, but candidate/control phase ranges overlap, and first25 is+0.059% while late strata are negative. This is not clean independent evidence for a stable W4A16 regression; it is also not an unchanged negative control. K3 W4A16 confirmation is roughly−0.23…−0.27%.

Correctness qualification passed, and unsigned arithmetic is semantically valid for the guarded nonnegative indices. That does not guarantee better compiled execution. V3 scaled prepare removes23 static SASS sites, while K3 scaled automatic unrolling grows85→301 sites and30→32registers; BF16 removes14 sites with+2registers. Static sites are not dynamic instruction counts, and this audit does not infer the measured causal mechanism from them. The isolated earlier V3 TP MX4x8 gain does not justify the confirmed broader costs. Rejecting the shared change globally keeps the policy simple.

Original full/analysis/cells.csv remains byte-identical (SHA1fbf9cdf5ab10a1bf117d28804703a8f5f0515630f1095b9da4cd487e0643246). No source, published result, GPU job or external baseline was changed by this audit.

Replayable checks: `audit.py`, `audit_confirmation.py`; receipts `full-audit.json`, `confirmation-audit.json`; full14-cell comparison `confirmation-cells.csv`.
