# Final owned R2 versus historical original AUTO controls

Two historical original002 AUTO controls pooled (200 samples) versus one final-owned AUTO run (100 samples); not ABBA.

3 warmups;100 untrimmed cold-L2 CUDA-graph CUPTI per-iteration rank-MAX samples per run.

| Source / run | Samples | Median µs | MAD µs |
|---|---:|---:|---:|
| A1 | 100 | 332.2750 | 1.5685 |
| A2 | 100 | 339.0910 | 1.5520 |
| final | 100 | 324.9150 | 1.4235 |
| Original pooled | 200 | 335.8745 | 3.5680 |

Pooled original / final ratio: **1.033730×**. Historical A2−A1 drift: **6.8160µs**.

All three runs select AUTO N64/G512/epi and pass the independent BF16-bit reference on every EP4 rank. Inputs, routes, weights and output hashes match; source closure, final successful-driver receipt and capacity-keyed knob caches pass. Each raw sample, per-run quarter median, fingerprint and exact tactic is preserved in the companion JSON.

Before:002ef145 / sourcec366a5e7d7c7aa82034f339a959a058945948381157618bee9139d9005f77eff. After:55cd345d / sourcea7001bd59e04b03b372ba4315b3cad8cdcfd7e2db40a96006a5a987c08939e29.

- Historical control timing is not contemporaneous with final timing; no causal drift correction is claimed.
- Both historical controls are pooled; neither is selected because its timing is favorable.
- Before has200 samples and after100; all startup outliers remain included.
- This uniform H6144 target is separate from the native H7168 decode matrix.
- Fixed-control333.171us evidence is a different selection protocol and is not used.
