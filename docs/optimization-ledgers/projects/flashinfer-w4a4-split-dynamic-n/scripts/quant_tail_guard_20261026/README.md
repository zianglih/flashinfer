# Guard inactive per-token quantizer tails before conversion

Independent candidate `../../flashinfer-quant-tail-guard-20261026` is based on `dd266b91` plus the parent's composed FC2 AUTO / row-limits source (including strict integer validation). Only the existing pass-2 `sf_col_idx < num_sf_blocks_per_row` guard moves around quantization as well as stores. Pass-1 clamped loads, amax reduction, row scales, active-lane arithmetic order, and SF padding remain unchanged. No new shape/dtype policy, CTA-width rule or upstream tests.

Control source is captured in `control-source.json`; candidate full patch is `source.patch`, SHA256 `f8ba9aeec6cd3f10925ca67712d7743468772145bcb71f70bef54de2386189ee`. The isolated change is `candidate-vs-control.patch`. Both codegen runs use fresh source-private CuTe caches and source-verified persistent C++ artifacts on c3 B300 GPU0. The environment remains NGC `26.05-py3`, runtime CUDA13.2 / bundled NVVM13.3. `tools/inspect_quantizer.py` appends only keep-PTX/CUBIN options, invokes the public quantizer, captures CUDA function resources, and performs no performance timing.

Control PTX and SASS establish that the compiler does **not** skip inactive pass-2 work. For BF16 K2304 with128threads and4over6, every thread executes the second16-element block's conversion, reconstruction and error selection. Only then does SASS `0x3e90 ISETP.GT.U32 ... 0xf` / `0x3ed0 @P0 BRA` mask its stores. E2M1 conversion and reconstruction occur earlier around0x2fa0–0x3e60. The control uses63registers, no local/spill memory and8residentCTAs/SM. This is static codegen evidence, not a speedup claim.

Four bounded cases compare BF16/FP16 K2304 with4over6, BF16 K2304 standard quantization, and BF16 K2048 with4over6 (fully covered threads). All use8193rows, live prefix and group limits, SF128x4, PDL, and the no-fast-math activation contract. Generated artifacts and exact source/resource receipts are collected in `results/quant-tail-guard/`.


The candidate moves the tail predicate in BF16 K2304 SASS to `0x2840 ISETP` / `0x2870 @P0 BRA 0x3f70`, before the second block conversion and error selection. Register counts / local bytes / resident CTAs per SM remain unchanged for all four cases: BF16 K2304 4over6 63/0/8; FP16 K2304 4over6 63/0/8; BF16 K2304 standard52/0/9; BF16 K2048 4over6 64/0/8. All four output byte hashes match. The fully covered K2048 case has byte-identical PTX **and SASS**: the extra guard vanishes entirely. These codegen results justified a bounded full-chain timing screen.

CAAC timing is against the exact frozen B+C control on GPU0, V41 then V3 then K3, tokens32/128/4096/8192. It uses the public per-token backend, includes initial quantization, disables fused finalize, and preserves the saved native AUTO tactics with10warmups/100cold-L2 CUDA-graph CUPTI samples. A read-only observer records the quantizer specialization names and Python getter counts per token; these are construction/capture observations, not physical GPU launch counts.

MX isolation: the candidate changes only the register-resident method of `NVFP4QuantizePerTokenKernel`. The benchmark MX selectors explicitly use `per_token=False` (`bench_moe_deepseek.py:1613–1614`), prepare activations with `mxfp8_quantize`, and the wrapper rejects an MX input paired with a per-token scale (`fused_moe.py:463–464`). The inter-FC NVFP4 per-token quantizer is called only under `if use_per_token_activation`, which is derived from a non-None per-token scale (`fused_moe.py:482,781`). All other implementation bytes are identical to B+C. The later full MX evidence can therefore remain tied to B+C if the tail guard is retained; only the NV family needs refreshing.


`source-isolation.json` records the exact provenance: B+C control is `dd266b91fdf61dae2de45ee9192d36c81c56be23` plus patch `2b0bd7eaa43af0fbfe6935d3d06f52550c3e916da437172945afbb2b4a4178d1`; guard candidate is the same commit plus patch `f8ba9aeec6cd3f10925ca67712d7743468772145bcb71f70bef54de2386189ee`. The isolated one-file patch is SHA256 `f3d43faae31db1c8aedbaae28b7269eae08abca6230ff935556e87edf31e89e4`. Quantizer file hashes are `ae5c6479a596215fb2536f5fcdaf5df3c7a3f94bb7d9c2e21297c40c089c62c8` → `6fd1839db0ad338c2281b47357ae72ebc7b72cbf759fc3ac74ea1ae69914e643`. After replacing the one method body with `pass`, the entire module AST is identical, including all imports, constants and other definitions. `codegen-summary.json` validates both codegen receipts, the shared observer hash, every output hash and artifact/resource comparison. The collection manifest pins all raw PTX/SASS/CUBIN files.


Launch bookkeeping: the first timing observer attempt failed before importing Torch or launching kernels because a local `import importlib` shadowed its earlier module access. That helper-only error was corrected, and the failed launch is preserved under `results/quant-tail-guard/failed-observer-r0/`. All timed arms belong to the fresh campaign launched afterward; source kernels were never changed during this correction. Static Ruff, formatting, Python compile and Git whitespace checks passed for the candidate.


## Completed fixed-tactic CAAC screen

All three models completed on GPU0 in control / candidate / candidate / control order. The control is the exact frozen B+C source; speedup is `sqrt(C0*C3/(A1*A2))`. `validate.py` checks48medians against4,800individual samples, the exact source/helper/cache receipts, unchanged GEMM tactics/configuration, route identities/histograms, recipe and quantizer specialization/count parity. There are exactly two per-token specializations per row, one initial and one inter-FC; their getter counts are identical across all four arms.

| Tokens | V3 | V41-Flash | Kimi K3 |
| ---: | ---: | ---: | ---: |
| 32 | 0.99909× | 1.00156× | 1.00074× |
| 128 | 0.99978× | 1.00441× | 0.99959× |
| 4096 | 0.99631× | 1.03143× | 1.01639× |
| 8192 | 1.01026× | 1.03470× | 1.01992× |

Recommend retaining the guard: V41/K3 prefill improves1.64–3.47%, V3 T8192 improves1.03%, and the small V3 T4096 regression is0.37% (~0.9µs). Decode is essentially neutral, with V41 T128 improving0.44%. The V3 intermediate K2048 specialization remains unchanged, so its gain/loss comes from the initial quantizer and full-chain interaction. No performance number here is a new TRTLLM comparison; the parent's refreshed full NV family sweep must measure both per-token backends because they share the initial quantizer. The four direct codegen output hashes remain exact; no new upstream tests were added.

Validated summary: `results/quant-tail-guard/validated-summary.json`. Raw CAAC data: `results/quant-tail-guard/fixed-*/`; source and artifact manifest: `results/manifest.json`. The source remains frozen, unstaged and uncommitted for parent composition. GPU0 was checked free after all pairs completed.
