# Deterministic-RL native W4A4 benchmark

All four completed runs passed validation. Run order: before-r1, after-r1, after-r2, before-r2; each invocation used fresh AUTO selection.

- Before: `03f82fddadaebed69879b4e7d28f3df38c4e28d2`; after: `e07d67af9339c8ace3791bcea1b6c6614206e5d4`.
- Runtime: `nvcr.io/nvidia/pytorch:26.05-py3`; NVIDIA B300 SXM6 AC; PyTorch `2.12.0a0+5aff3928d8.nv26.05`; CUDA `13.2`; CuTe DSL `4.8.1`; CUPTI `13.4.0`.
- CUPTI packages: `{"cupti-python": "13.4.0", "nvidia-cuda-cupti": "13.4.58"}`.
- Workload: H7168, I2048, 256 experts, 32 local experts, topK8, group8/top-group4, routing scale 2.5, EP8/TP1 simulation, seed 42 and bias scale 0.01.
- Recipe: per-token activation, 4over6, E4M3 max 256, MSE, packed error arithmetic enabled, quantization fast math disabled; FC2 scale 1/1536; deterministic finalize; async memset disabled.
- Timer: native cold-L2 CUDA-graph CUPTI; 10 warmups and 100 samples per row. Saved tactic caches were never loaded.

## All 52 native medians

Milliseconds; values below retain the JSON float representation. T1/T2 are reported and excluded from all aggregates.

| Tokens | before-r1 | after-r1 | after-r2 | before-r2 |
| --- | --- | --- | --- | --- |
| 1 | 0.032096 | 0.032064 | 0.032032 | 0.031936 |
| 2 | 0.0431365 | 0.042976 | 0.043040499999999995 | 0.043009 |
| 4 | 0.061921 | 0.0622565 | 0.062336 | 0.0617765 |
| 8 | 0.077569 | 0.079713 | 0.079681 | 0.077873 |
| 16 | 0.087041 | 0.089985 | 0.089889 | 0.086849 |
| 32 | 0.123233 | 0.1249455 | 0.125057 | 0.12312100000000001 |
| 64 | 0.157378 | 0.15945749999999997 | 0.15940900000000002 | 0.15725 |
| 128 | 0.160994 | 0.1628335 | 0.1630255 | 0.1612015 |
| 256 | 0.1720175 | 0.172194 | 0.172162 | 0.171426 |
| 512 | 0.17656100000000002 | 0.175233 | 0.1752015 | 0.176994 |
| 4096 | 0.261154 | 0.22744199999999998 | 0.2274095 | 0.261154 |
| 8192 | 0.3735075 | 0.3025785 | 0.302355 | 0.373508 |
| 16384 | 0.6217 | 0.488996 | 0.4881 | 0.62183 |

## Per-row comparison

Speedup is before/after; values above 1 favor after. Combined speedup is sqrt(R1 × R2). Before/after columns are geometric means of the two process medians, in microseconds.

| Tokens | Group | Before us | After us | R1 speedup | R2 speedup | Combined speedup | Latency reduction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | excluded-small | 32.015900 | 32.047996 | 1.000998x | 0.997003x | 0.998999x | -0.100% |
| 2 | excluded-small | 43.072703 | 43.008238 | 1.003735x | 0.999268x | 1.001499x | 0.150% |
| 4 | decode | 61.848708 | 62.296237 | 0.994611x | 0.991024x | 0.992816x | -0.724% |
| 8 | decode | 77.720851 | 79.696998 | 0.973104x | 0.977310x | 0.975204x | -2.543% |
| 16 | decode | 86.944947 | 89.936987 | 0.967283x | 0.966181x | 0.966732x | -3.441% |
| 32 | decode | 123.176987 | 125.001238 | 0.986294x | 0.984519x | 0.985406x | -1.481% |
| 64 | decode | 157.313987 | 159.433248 | 0.986959x | 0.986456x | 0.986708x | -1.347% |
| 128 | decode | 161.097717 | 162.929472 | 0.988703x | 0.988812x | 0.988757x | -1.137% |
| 256 | decode | 171.721495 | 172.177999 | 0.998975x | 0.995725x | 0.997349x | -0.266% |
| 512 | decode | 176.777367 | 175.217249 | 1.007578x | 1.010231x | 1.008904x | 0.883% |
| 4096 | prefill | 261.154000 | 227.425749 | 1.148222x | 1.148387x | 1.148304x | 12.915% |
| 8192 | prefill | 373.507750 | 302.466729 | 1.234415x | 1.235329x | 1.234872x | 19.020% |
| 16384 | prefill | 621.764997 | 488.547795 | 1.271381x | 1.273981x | 1.272680x | 21.426% |

## Unweighted geometric aggregates

| Group | Rows | R1 speedup | R2 speedup | Combined speedup | Latency reduction | Improved combined | Improved R1/R2 | Improved both |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| overall | 11 | 1.045668x | 1.045636x | 1.045652x | 4.366% | 4/11 | 4/4 | 4/11 |
| decode | 8 | 0.987862x | 0.987458x | 0.987660x | -1.249% | 1/8 | 1/1 | 1/8 |
| prefill | 3 | 1.216898x | 1.218086x | 1.217492x | 17.864% | 3/3 | 3/3 | 3/3 |

Overall includes 11 rows: decode T4–512 and prefill T4096/T8192/T16384. Each row has equal weight.

## Full selected tactics

Tactics are the complete recorded repr strings. AUTO columns record selections during prewarm; execution columns record the selection used outside tuning, including graph capture.

| Tokens | Process | AUTO selection | Execution selection |
| --- | --- | --- | --- |
| 1 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 1 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 1 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 1 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 2 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 4 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 4 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 4 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 4 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 16 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 32 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 32 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 32 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 32 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 64 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 64 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 64 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 64 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 128 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 128 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 128 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 128 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 256 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 256 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 256 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 256 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 512 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 512 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 512 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 512 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 4096 | before-r1 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 4096 | after-r1 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 4096 | after-r2 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 4096 | before-r2 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 8192 | before-r1 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 8192 | after-r1 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 8192 | after-r2 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 8192 | before-r2 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 16384 | before-r1 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 16384 | after-r1 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 16384 | after-r2 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |
| 16384 | before-r2 | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` | `(256, ((256, 256), (2, 1), False), ((256, 256), (2, 1), False))` |

## Tactic differences

| Tokens | Before→after R1 | Before→after R2 | Before repeats | After repeats |
| --- | --- | --- | --- | --- |
| 1 | same | changed | changed | same |
| 2 | changed | same | same | changed |
| 4 | same | same | changed | changed |
| 8 | same | same | same | same |
| 16 | changed | same | changed | same |
| 32 | changed | same | same | changed |
| 64 | changed | changed | changed | changed |
| 128 | same | changed | changed | same |
| 256 | changed | changed | same | same |
| 512 | changed | same | changed | same |
| 4096 | same | same | same | same |
| 8192 | same | same | same | same |
| 16384 | same | same | same | same |

## Evidence validation

- Runner SHA256: `f39f104974167b8f92096a95bbabf55eb53a71b09b88720a258c183504f0dec8`.
- Pristine native harness SHA256: `9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371`.
- Adapted native harness SHA256: `906f531eded00dcbef733e42ada0f7480b14ca99e924b8a994d2aa5af5a8310f`.
- All 52 medians match 100 positive finite samples per row; all native medians and unit conversions agree; every row records measured AUTO and execution selections without fallback.
- Runtime, recipe, environment, workload, imported checkout path and routing histograms match. The source difference is exactly six implementation files plus tests/moe/utils.py; other recorded source hashes match.

| Process | Input JSON SHA256 | Local evidence verification |
| --- | --- | --- |
| before-r1 | a446432cf9b7aa3e1dad7e95a8fd522588b2b925e82e21e31883d190ab956123 | complete |
| after-r1 | d13cc786d11657f78388243e40b64a7fa34d9c5862de77007266df9d0d898671 | complete |
| after-r2 | 770a41cb2b5d9cadcee13a63fed749cbbe53d4b4a01b0eb8666eca77484f1fa6 | complete |
| before-r2 | 03fd308140fd8d18c9522e8a9d75bfcd08b00dc863a23965e3ab74d31fee0543 | complete |

| Source | Before SHA256 | After SHA256 | Changed |
| --- | --- | --- | --- |
| benchmarks/bench_moe_deepseek.py | 9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371 | 9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371 | False |
| flashinfer/autotuner/autotuner.py | 0db42ad90d1a3fec6f81509a2c520c1892cea0a433f5dbd7f43468a2a10243ca | 0db42ad90d1a3fec6f81509a2c520c1892cea0a433f5dbd7f43468a2a10243ca | False |
| flashinfer/cute_dsl/fp4_common.py | 6cda2e2fa955ca608844209e5792d5a2136f6a2e6e0a8d3fb7cc285ebc01531d | 3a82766dfc00ee9ec749728f3ef25cb854b37c7b0cbebc9ff721574a77b78bab | True |
| flashinfer/fp4_quantization.py | fb394c543cfd112ec6ceccfd8c808058f7b10ab88d9a8adda0a9cbd067c25f97 | fb394c543cfd112ec6ceccfd8c808058f7b10ab88d9a8adda0a9cbd067c25f97 | False |
| flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py | d1931bb6eaada693e6f4b43c1e682179424a1e478170624cacef28834f768cdb | 5618e95b448cc4aa80a6d5d5661f696134bdddba390b9c97cc7244b00f794b1a | True |
| flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py | 79cdcb441ce569986394bbd536126dbed03015ad72694972a237bf89da07bb45 | 79cdcb441ce569986394bbd536126dbed03015ad72694972a237bf89da07bb45 | False |
| flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py | 4266a8ec5b941558aafaf767aa3dbdc0d3a4c4e28edd8cf339007b4c45b91635 | f4a1297341525fda06f63a4fe990e9e6bf0bdae422e43ba504062b8a21fcd8f1 | True |
| flashinfer/fused_moe/cute_dsl/fused_moe.py | db8602ce17902b085ec5589e13abe842910119038628a354d230145b9c5e48d4 | 3a253fbf49e9d385b9b1777ef1248950dd8e1a952aae0b7b8d25484306760f77 | True |
| flashinfer/fused_moe/cute_dsl/tuner.py | d12a73b51ca5e239a6a3ae04ad2b8f68baad0d1c650e1997e47fd5f2b48c6fde | 9a17e6bd843e7b356f034f49162917aff8dbe53a269a12babef222860c860928 | True |
| flashinfer/quantization/kernels/nvfp4_quantize.py | 6fcef37fd6e41cbeea7987b458fb6eedfad387918b4521ae74891f9b9b948e7a | 2b626b7421169b2abe4a56ba395b906009e03daab9ea9cb68934613e73536473 | True |
| flashinfer/quantization/nvfp4_quantization_utils.py | d52442fc6aa04b3e2dd5ebad3bbd2d8820ce437c8de2b6a7ad0e8e19960a15d6 | d52442fc6aa04b3e2dd5ebad3bbd2d8820ce437c8de2b6a7ad0e8e19960a15d6 | False |
| flashinfer/testing/utils.py | bf532ebc0b82d3551a09bea6bc96017b838bcb52d461f9a5d19573ac9766ac34 | bf532ebc0b82d3551a09bea6bc96017b838bcb52d461f9a5d19573ac9766ac34 | False |
| tests/moe/utils.py | e67f360546998ef49dd7f2872564c27fb17166667fe52b621bc1983ea37e2b9f | 3b410a7b2370891a5b7e5dd369d82a9c4294d3dcead4509be7accfde47e62df5 | True |

Environment:

```json
{
  "CUDA_HOME": "/usr/local/cuda",
  "CUDA_VISIBLE_DEVICES": "0",
  "CUTE_DSL_CACHE_DIR": "/root/.cache/flashinfer/cute_dsl",
  "CUTLASS_DSL_VERSION": "4.4.2",
  "FLASHINFER_AUTOTUNER_LOAD_FROM_FILE": "0",
  "FLASHINFER_CUDA_ARCH_LIST": "10.3a",
  "FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH": "1",
  "FLASHINFER_DIST_AWARE_AUTOTUNE": "0",
  "FLASHINFER_NVFP4_4OVER6": "0",
  "TORCH_CUDA_ARCH_LIST": "7.5 8.0 8.6 9.0 10.0 12.0+PTX",
  "TRTLLM_ENABLE_PDL": "1"
}
```

Process commands:

```json
{
  "before-r1": [
    "/workspace/pr4824/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824/bench_moe_deepseek.native.py",
    "--expected-head",
    "03f82fddadaebed69879b4e7d28f3df38c4e28d2",
    "--label",
    "before-r1",
    "--output",
    "/workspace/pr4824/results/pr7196-deterministic-rl/before-r1.json"
  ],
  "after-r1": [
    "/workspace/pr4824/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824/bench_moe_deepseek.native.py",
    "--expected-head",
    "e07d67af9339c8ace3791bcea1b6c6614206e5d4",
    "--label",
    "after-r1",
    "--output",
    "/workspace/pr4824/results/pr7196-deterministic-rl/after-r1.json"
  ],
  "after-r2": [
    "/workspace/pr4824/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824/bench_moe_deepseek.native.py",
    "--expected-head",
    "e07d67af9339c8ace3791bcea1b6c6614206e5d4",
    "--label",
    "after-r2",
    "--output",
    "/workspace/pr4824/results/pr7196-deterministic-rl/after-r2.json"
  ],
  "before-r2": [
    "/workspace/pr4824/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824/bench_moe_deepseek.native.py",
    "--expected-head",
    "03f82fddadaebed69879b4e7d28f3df38c4e28d2",
    "--label",
    "before-r2",
    "--output",
    "/workspace/pr4824/results/pr7196-deterministic-rl/before-r2.json"
  ]
}
```

## Limits

- Two process repeats describe consistency; no confidence interval or statistical-significance claim.
- AUTO tunes independently per process; tactic changes are part of this native API comparison, not a fixed-tactic kernel comparison.
- Single-GPU EP8/TP1 simulation, with no distributed communication or fused atomic finalization.
- Initial activation quantization is outside timing; routing, MoE, intermediate quantization and deterministic unpermute are inside.
- Explicit recipe and FC2 scale 1/1536 adapt the native W4A4 harness; unused CUTLASS packs retain native preparation.
