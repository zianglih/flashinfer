# Per-token NVFP4 256-bit loads

Independent unstaged source `flashinfer-quant-load-20261026`, based on0def. The two per-token row-load sites now reuse the existing `ld_global_v8_u32` helper, replacing two128-bit loads. FP16 and BF16 arithmetic, reductions, quantization and layouts are unchanged. A32-byte-alignment copy preserves storage-offset input compatibility; row stride is already32-byte aligned because K is a multiple of16. Fake/input-row alignment promises match. No dtype/model/shape threshold or alternate kernel is added.

Fixed native-tactic CAAC screens include initial quantization and both MoE GEMMs, at32/128/4096/8192 tokens. Native public timing:10warmups/100cold-L2 CUDA-graph CUPTI samples. Cache misses are fatal, actual tactics are recorded unchanged, source/routing/quantization configuration and all100 samples are checked. Geomeans: V3 1.002169x, V41 1.001039x, K3 1.002254x. Full precision: `quant-load-comparison.json`. These small positive diagnostics do not yet constitute full-grid retention.

Twelve existing exact CUDA-vs-CuTe per-token wide-row selectors pass, covering FP16/BF16,128x4/8x4/linear SF layouts, K1536 register-resident and K69632 two-pass paths,17rows. Command and source-bound log are in persistent `quant-load/existing-wide-tests.json`; no upstream tests were added. Scoped pre-commit and diff checks pass.

A separate route-count candidate addresses much larger unnecessary work; this source remains independent so its benefit can be measured separately.
