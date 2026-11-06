# Device live-row count for per-token quantization

Independent unstaged source: `flashinfer-route-count-20261026`, parent `0def601d6603df828ea39679b41ccbce64f7f09e`. The optimization gives the general per-token quantizer an optional int32 device live-prefix count. The MoE inter-FC call supplies `total_num_padded_tokens` already produced by routing; standalone initial quantization keeps its existing no-count specialization. No host readback, model/dtype/tile thresholds, new scheduling knobs, or upstream tests.

The count is loaded after the existing PDL dependency wait. Existing ancestor publication and launch signal remain before row work. Every row below the live count is quantized unchanged, including expert tile padding. SF slots from live count through the next128/8/1-row atom are zeroed. Storage beyond that atom is unspecified and never consumed by active FC2 tiles. Output allocation shapes and grid capacity remain unchanged in this minimal experiment; unused CTAs skip quantization and stores. A persistent/grid-cap alternative is deliberately deferred until this simpler change has evidence.

Motivation: clean0def V41 T8192 native tactic uses N256/twoCTAs/k_steps4. Its73,472-row intermediate allocation has about338.56MB of BF16 values. NCU measured338.61MB of reads,83.46M instructions and62.05 grid waves in the quantizer, proving it consumes essentially all capacity. The counter capture is isolated replay and is not native performance evidence. Original profiles are in `../per_token_single_transpose_20261026/results/ncu-v41-prefill-20261026`.

Task-local gate `probe.py` checks96 changing-count quantizer graph replays across BF16/FP16, all three SF layouts and PDL on/off. It verifies live output and scales exactly against full-capacity quantization, zero final-atom SF padding, and no stores beyond padding. Then80 public-wrapper graph replays compare count-on/off with identical source arithmetic across N16/32/128/256, one/twoCTAs, CLC/static, PDL on/off, SwiGLU/SiTU, changing input/routing and zero local routes. No benchmark methods are modified in timing runs. Validation and timing results will be recorded separately.

Validation completed:96 direct quantizer graph replays and80 public-chain replays all pass exactly. Existing gated/SiTU/wrapper/CUDA-graph selectors:5 passed,143 warnings in15.66s. Scoped pre-commit and source-byte verification passed. Source and patch hashes in source.json remain identical to the measured remote source.

Fixed native-tactic CAAC finished on c3 B300 GPU2 using10warmup/100cold-L2 CUDA-graph CUPTI samples, initial quantization included, no fused finalize. Exact route hashes and cache hits are verified. Speedups at tokens32/128/4096/8192:

|Model|32|128|4096|8192|
|---|---:|---:|---:|---:|
|V3|0.99745|1.00342|1.01403|1.01927|
|V41-Flash|1.00058|1.00109|1.02204|1.03538|
|Kimi K3|1.00200|1.00959|1.08371|1.07666|

This positive bounded screen supports progressing to full retention evidence. It is not a full-grid retention claim. Raw CAAC observations, timing vectors, source/cache receipts, test results and commands are in results/route-count; summary.json includes all four medians per point. The later bounded-grid traversal experiment is a separate source and uses this frozen count-only version as its control.
