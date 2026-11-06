# Selected AUTO preparation-only diagnostic

The frozen actual regular-TMA source was measured on C1 GPU4 at16K tokens using each completed AUTO A1 screen's selected tactic. No full-chain timing, original baseline rerun, gridsweep, or source change was performed.

| Mode | Actual selected tactic | Grid16 preparation median | Active rows |
|---|---|---:|---:|
| MXFP8 | N256, FC1/FC2 M256,2CTA |49.312 µs|19,712|
| Mixed W4A8 | N128, FC1 M512 NB2 / FC2 M256,2CTA |47.088 µs|18,176|

Each measurement uses10warmups and100cold-L2 CUDA-graph CUPTI samples, all retained in its rawJSON. The actual prepare function obtains the current CUDA stream inside capture. An independent byte reference verifies payload and canonical SF output, padding zeros, and whole unused-capacity canaries. Final full-MoE output bytes before and after the diagnostic match; those native calls capture inputs and verify correctness, and are not timed full-chain results. Routing histogram summaries match the corresponding primary A1 rows.

This is the scale of preparation work, not a causal subtraction from GPU1 primary full-chain timing. Different kernel cache state, dependencies, and overlap can affect the amount exposed in a whole pipeline. The unchanged source SHA is125d0f15910debc75ca1a128c6c59ad83db84558ef66fe338d362371955d4392. Full helper/command/source metadata and raw outputs are archived here with sha256.json.
