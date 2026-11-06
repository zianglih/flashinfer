# Old and retained CuTe DSL comparison

All208 model/format/token cells completed:182 paired cells and26 current-only K3 MX cells;78,000 primary timing samples. OldK3 MX rejects SiTU and remains N/A.

Excluding tokens1/2, the paired-cell geometric speedup is1.1616x (+16.16%): decode4–512 +20.00%, prefill4096/8192/16384 +6.51%.

- Old source: `002529e17b22567a071091053c6c4dc2a55e050e`; retained source: `0b7fe90151340d4fca6a5ec41a91019dde743819`. Only benchmark overlays differ from these sources.
- Both arms use the public functional API, source-native weight packing, seed42 and matched routes. NVFP4 includes input quantization; MX uses prequantized input. No W4A16, CUTLASS or TRTLLM backend timing. Shared native routing remains inside the public benchmark.
- Both NV formats are unfused. Old MX uses its native fused finalizer because old unfused MX is unsupported; current MX is unfused. These paths differ in rounding/reduction order and launch structure. Their speedup is a native-path comparison, not an algebraically identical finalizer comparison.
- C3 B300, one GPU per model/family, CUDA13.2 in `nvcr.io/nvidia/pytorch:26.05-py3`; persistent native C++ artifacts were reused after source/header identity checks.
- Primary timing is old/current/current/old on the same GPU,100 cold-L2 CUPTI CUDA-graph samples per pass after10 warmups. Each arm latency is the geometric mean of its two pass medians. Current-only K3 MX uses two current passes. No AUTO timing enters speedups.
- Old supported groups and current Nemo use fresh source-specific native AUTO. Existing retained winners for the three original models were reused after the96-case API equivalence proof and GPU weight-payload proof. The explicit operation-name mapping preserves all other keys and winner payload; originals remain intact.

| Model |D|I|Experts|Top-k|EP|Activation|Routing|
|---|---:|---:|---:|---:|---:|---|---|
|v3|7168|2048|256|8|8|swiglu|deepseek_v3|
|v41-flash|5120|2304|384|6|4|swiglu|sqrtsoftplus|
|kimi-k3|3584|3072|896|16|8|situ|sigmoid|
|nemo3-ultra|2048|5120|512|22|8|relu2|sigmoid|

Nemo times the latent routed expert workload; it excludes surrounding latent projections.

Complete signed speedup tables: `speedups.md`. All old/current raw pass medians and derived ratios: `raw-median-speedups.csv`. All78,000 primary samples: `raw-samples.csv`. Public stdout, native caches, per-token snapshots, source receipts, cache equivalence proofs and route hashes are under `evidence/`.

| Model | All retained cells | Decode4–512 | Prefill |
|---|---:|---:|---:|
|v3|+12.79%|+16.99%|+2.31%|
|v41-flash|+15.98%|+19.43%|+7.25%|
|kimi-k3|+17.51%|+19.69%|+11.87%|
|nemo3-ultra|+19.13%|+23.83%|+7.43%|

The one NsightSystems diagnostic pair for V3 standardNVFP4 T16384 is in `profiles/v3-nvfp4-t16384/`. It used the frozen native winners with no AUTO. The trace locates the critical path increase in the added prepare and FC2 tail; durations must account for PDL wait overlap. Raw `.nsys-rep`, SQLite and per-iteration timelines are preserved.

No numerical equivalence claim is made between old and current kernels. Compatibility smoke failures were benchmark interface/parser mismatches before timed GPU work; the final functional API/benchmark-only parser correction resolved them without changing either source kernel. Original failed receipts are preserved.
