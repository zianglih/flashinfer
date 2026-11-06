# Saved T4096 per-token audit

One native AUTO screen per source, not a paired retention result. Saved receipts have no per-phase durations or register/occupancy measurements. Geometry identity does not establish identical generated code or overlap.

| Model | Arm | Copy us | PDL us | Change | Same tactic |
|---|---|---:|---:|---:|---|
| v3 | CuteDSL W4A16 | 319.650 | 320.178 | +0.17% | True |
| v3 | CuteDSL W4A4 | 195.809 | 194.609 | -0.61% | True |
| v3 | CuteDSL PER-TOKEN | 253.713 | 274.769 | +8.30% | True |
| v41-flash | CuteDSL W4A16 | 567.301 | 611.239 | +7.75% | True |
| v41-flash | CuteDSL W4A4 | 345.059 | 343.906 | -0.33% | True |
| v41-flash | CuteDSL PER-TOKEN | 414.756 | 431.076 | +3.93% | False |
| kimi-k3 | CuteDSL W4A16 | 621.221 | 672.101 | +8.19% | True |
| kimi-k3 | CuteDSL W4A4 | 387.187 | 383.299 | -1.00% | True |
| kimi-k3 | CuteDSL PER-TOKEN | 542.628 | 581.860 | +7.23% | True |

All compared route identities, recipes, GPU UUIDs, imported runtime versions and timing settings match. Actual imports are CuTe4.7.1 and Torch CUDA13.2. V41 per-token FC2 changes from M128/oneCTA to M256/twoCTA at N128; V3 and K3 per-token geometry is unchanged. Unchanged W4A16 source and geometry show substantial V41/K3 drift, so V3 is the cleanest initial diagnostic.

If the quantizer screen does not resolve the loss, trace V3 with saved identical per-token choices first using the public profiler path, preserving graph PDL. Capture compiler-bound PTX/cubins and Nsight node resources; isolated NCU only afterward because it serializes the chain.
