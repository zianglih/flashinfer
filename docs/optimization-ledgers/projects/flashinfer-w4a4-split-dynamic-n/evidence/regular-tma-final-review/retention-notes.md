# Retention reading

The prescribed paired calculation is verified; this note does not replace any AUTO-selected median. Tokens1/2 are excluded from every aggregate.

| Mode | Tokens | B2/B1 | Paired speedup | B1 tactic = B2 tactic |
|---|---:|---:|---:|---|
|nvfp4|4096|1.001921|1.025718|True|
|nvfp4|8192|1.004676|0.983506|True|
|nvfp4|16384|1.003656|0.979423|True|
|mxfp8|4096|0.974862|1.106929|False|
|mxfp8|8192|0.946268|1.067058|False|
|mxfp8|16384|1.113210|1.110298|False|
|mxfp4|4096|0.936321|1.123767|True|
|mxfp4|8192|0.972242|1.014539|False|
|mxfp4|16384|1.106247|1.042999|False|

NVFP4 remains slower at8192tokens (0.983506×) and16384tokens (0.979423×), with the same baseline AUTO tactics across B1/B2. Its prefill aggregate is0.995998×.

At16384tokens, MXFP8 and mixed W4A8 baseline B2 medians are11.3210% and10.6247% higher than B1, and their saved baseline AUTO tactics differ. The prescribed paired gains remain1.110298× and1.042999×, but these include baseline AUTO-selection drift and must not be described as isolated kernel gains. Full tactics and all four medians are preserved in summary.json and summary.md. Mixed4096 also has6.3679% baseline drift despite the same saved tactic, so tactic changes are not asserted as the sole cause of all timing variation.

Numerical and sanitizer validation is a separate task. This archive makes no initcheck claim. No additional benchmark execution was performed to select or replace any result.
