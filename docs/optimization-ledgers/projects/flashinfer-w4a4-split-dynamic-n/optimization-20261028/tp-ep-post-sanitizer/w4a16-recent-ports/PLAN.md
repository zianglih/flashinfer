# W4A16 independent port screens

Prepare-only until each source passes its exact/codegen gate and root authorizes its launch. No new tuning, external baselines, or production source edits.

- Common control: `fd72759b15b8d417d6c791c0382f90d14262a8e4` (W4A16 kernel unchanged from retained9e). Tail and packed-FC2 candidates are independent, with separate source manifests, native CuTe compilation caches, managed-cache copies, and results.
- Each candidate:32 cells, four models × EP/TP × tokens4/64/4096/16384. V3/K3/N3U use EP8 or TP8; V41F uses EP4 or TP4. Fixed saved83df W4A16 tactics and routing identities, no retuning.
- One job per model/topology, four native subprocesses in C-A-A-C order. Existing observer `--w4a16-only` uses the public benchmark's existing backend selector; it never overrides tactics or kernel behavior.
- Native `benchmarks/bench_moe_deepseek.py`, functional public API, swapAB, unfused finalize,10 warmups,100 strict CUPTI samples, cold L2, CUDA graph timing. Keep the NV-family `--include-activation-quant` flag: W4A16 still consumes BF16 directly, so input quantization is not timed for this arm.
- Verify every source/helper before/after, exact command/environment, GPU UUID, unchanged managed caches, saved winner identity, route identity, zero profiling, finite raw samples and their exact medians. Both boxes use the same persistent filesystem; every native subprocess has its own compiler CWD. Persistent C++ cache links are reused.
- Per-cell speedup uses geometric mean(C1,C2)/geometric mean(A1,A2)−1. Preserve all raw samples and report EP/TP decode/prefill geomeans, per-cell variation, and largest slowdowns. No published full-table replacement from this diagnostic.
