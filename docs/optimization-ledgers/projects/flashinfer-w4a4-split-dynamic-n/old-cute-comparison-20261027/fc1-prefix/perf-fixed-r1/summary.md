# Deferred FC1 prefix — rejected

Completed4 of12 planned CAAC cells; the next cell is partial and excluded. No AUTO.1600 samples form complete brackets;300 partial samples are preserved separately. Sources matched their frozen hashes after stopping.

| Model | Backend | Tokens | C1/C2 ms | A1/A2 ms | Change (+faster) |
|---|---|---:|---:|---:|---:|
|kimi-k3|CuteDSL PER-TOKEN|8192|0.644291 / 0.644035|0.646418 / 0.647667|-0.445%|
|kimi-k3|CuteDSL W4A4|8192|0.497123 / 0.497506|0.497555 / 0.496642|+0.043%|
|nemo3-ultra|CuteDSL PER-TOKEN|4096|0.317442 / 0.316305|0.325570 / 0.324722|-2.544%|
|nemo3-ultra|CuteDSL PER-TOKEN|8192|0.559539 / 0.560771|0.564179 / 0.564738|-0.763%|

NV includes input quantization;10 warmups/100 cold-L2 CUPTI CUDAgraph samples per leg, C-A-A-C with identical frozen native winners. Both sources remain unfused. Changes compare geometric means of the two source medians.

The Nemo4096 loss is stable across adjacent comparisons, whereas K3 standard is neutral. These results do not justify142 added net lines or higher register use. Nemo16384 had completed C1/A1/A2 when stopped; no complete bracket or retention ratio is claimed. V3,V41 and timing guards were not reached.

Numerical/resource gate:48 exact replays per source on the main matrix, plus6 per source for CLC. Candidate36 total compiled artifacts contain no stack/local spill or LDL/STL. All18 paired FC2 and six inactive/one-slab FC1 executable sections are identical. Active hardware release remains1–3 SASS sites after the final protected TMEM access. No sanitizer was run.

Local and remote rejected source checkouts are removed only after source verification; helpers,evidence,compiled caches,manifests,and shared data are preserved. No composition or source retention.
