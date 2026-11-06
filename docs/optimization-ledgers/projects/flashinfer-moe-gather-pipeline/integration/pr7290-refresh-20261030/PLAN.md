# PR7290 retained integration refresh

Merged source `a620ce7790b32f7f0ae524a811417d2c6cee1152` is tree-identical to retained fork `8bc69ee40cb383a88eadb4fd5ffd7bd0ff2694a4`. Full13,245-file snapshot differs from c1ac only by the requested W4 helper restoration.

Run seven existing exact/native smokes, then31 frozen jobs /468 cells /two candidate passes /93,600 strict CUPTI samples on8 GPUs.100 samples and10 warmups, coldL2 CUDA graphs, NVFP4 input quant included; tokens1/2 preserved raw, excluded from retention. Historical TRT/legacy/pre-PR denominators remain unchanged. No optimization, retuning, source policies, sanitizer or new repo tests.

All12 performance helpers match the completed current046 cumulative campaign. Candidate-only private cached_ops/CuTe roots share only four release C++ modules plus canonical generated/cubin inputs. Actual merged bytes, normal native loads/no-op, source pre/post, frozen route/cache choices, loaded resources and clocks are checked.
