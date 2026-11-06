# Preserved442 primary AUTO prefill tactics

CPU-only extraction from each actual-token key in the saved candidate A1/A2 AUTO caches. No GPU work or benchmark rerun. These are full-sweep native AUTO selections, not fixed-tactic minima.

```text
N256 = [256, [[256, 256], [2, 1], false], [[256, 256], [2, 1], false]]
NB2  = [128, [[512, 128], [2, 1], false], [[256, 128], [2, 1], false]]
NB2-1CTA-FC2 = [128, [[512, 128], [2, 1], false], [[128, 128], [1, 1], false]]
```

Tuple format: `[route_N, [FC1_MN, cluster, fused], [FC2_MN, cluster, fused]]`. All use unfused finalization. FC1 M512 reuses B/SFB across two M256 instructions.

| Mode | Tokens | A1 | A2 |
|---|---:|---|---|
| nvfp4 | 4096 | N256 | N256 |
| nvfp4 | 8192 | NB2 | NB2 |
| nvfp4 | 16384 | NB2 | NB2 |
| mxfp8 | 4096 | N256 | N256 |
| mxfp8 | 8192 | NB2 | NB2 |
| mxfp8 | 16384 | N256 | NB2 |
| mxfp4 | 4096 | N256 | N256 |
| mxfp4 | 8192 | NB2 | NB2-1CTA-FC2 |
| mxfp4 | 16384 | NB2 | NB2 |

`mxfp4` names the mixed E4M3-activation/FP4-weight benchmark, not homogeneous MXFP4.

Implications: N128 NB2 is directly relevant to NV8K/16K and mixed8K/16K. N256 matters for all4K rows and was also the MXFP8 A1 winner at16K. MXFP8 changed to N128 in A2; mixed8K changed only FC2 to oneCTA. Assess both geometries before claiming an AUTO improvement. GPU5 fixed-tactic absolute times are not paired with primaryGPU0/1 absolute times.

## Exact source files

- A1 nvfp4 T4096: `evidence/combined-screen-442d2aa5/raw/results/nvfp4-candidate-screen-442d2aa5.t4096.autotune.json`
- A1 nvfp4 T8192: `evidence/combined-screen-442d2aa5/raw/results/nvfp4-candidate-screen-442d2aa5.t8192.autotune.json`
- A1 nvfp4 T16384: `evidence/combined-screen-442d2aa5/raw/results/nvfp4-candidate-screen-442d2aa5.t16384.autotune.json`
- A1 mxfp8 T4096: `evidence/combined-screen-442d2aa5/raw/results/mxfp8-unfused-candidate-screen-442d2aa5.t4096.autotune.json`
- A1 mxfp8 T8192: `evidence/combined-screen-442d2aa5/raw/results/mxfp8-unfused-candidate-screen-442d2aa5.t8192.autotune.json`
- A1 mxfp8 T16384: `evidence/combined-screen-442d2aa5/raw/results/mxfp8-unfused-candidate-screen-442d2aa5.t16384.autotune.json`
- A1 mxfp4 T4096: `evidence/combined-screen-442d2aa5/raw/results/mxfp4-unfused-candidate-screen-442d2aa5.t4096.autotune.json`
- A1 mxfp4 T8192: `evidence/combined-screen-442d2aa5/raw/results/mxfp4-unfused-candidate-screen-442d2aa5.t8192.autotune.json`
- A1 mxfp4 T16384: `evidence/combined-screen-442d2aa5/raw/results/mxfp4-unfused-candidate-screen-442d2aa5.t16384.autotune.json`
- A2 nvfp4 T4096: `evidence/final-campaign-442-recovery/raw/results/final-442-recovery/A2-nvfp4.t4096.autotune.json`
- A2 nvfp4 T8192: `evidence/final-campaign-442-recovery/raw/results/final-442-recovery/A2-nvfp4.t8192.autotune.json`
- A2 nvfp4 T16384: `evidence/final-campaign-442-recovery/raw/results/final-442-recovery/A2-nvfp4.t16384.autotune.json`
- A2 mxfp8 T4096: `evidence/final-campaign-442-recovery/raw/results/final-442-recovery/A2-mxfp8.t4096.autotune.json`
- A2 mxfp8 T8192: `evidence/final-campaign-442-recovery/raw/results/final-442-recovery/A2-mxfp8.t8192.autotune.json`
- A2 mxfp8 T16384: `evidence/final-campaign-442-recovery/raw/results/final-442-recovery/A2-mxfp8.t16384.autotune.json`
- A2 mxfp4 T4096: `evidence/final-campaign-442-recovery/raw/results/final-442-recovery/A2-mxfp4.t4096.autotune.json`
- A2 mxfp4 T8192: `evidence/final-campaign-442-recovery/raw/results/final-442-recovery/A2-mxfp4.t8192.autotune.json`
- A2 mxfp4 T16384: `evidence/final-campaign-442-recovery/raw/results/final-442-recovery/A2-mxfp4.t16384.autotune.json`

`auto-prefill-tactics-442.json` contains each exact cache key, tactic, path, and file SHA256.
