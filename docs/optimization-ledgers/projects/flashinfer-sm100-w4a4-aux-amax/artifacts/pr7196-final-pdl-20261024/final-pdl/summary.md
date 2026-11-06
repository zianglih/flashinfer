# Deterministic-RL native W4A4 benchmark

All four completed runs passed validation. Run order: before-r1, after-r1, after-r2, before-r2; each invocation used fresh AUTO selection.

- Before: `e734816171909b755ed1a9a510b7178d23bdf692`; after: `1db8a7507bbca6f2d705ee1365f3108ba03fa128`.
- Runtime: `nvcr.io/nvidia/pytorch:26.05-py3`; NVIDIA B300 SXM6 AC; PyTorch `2.12.0a0+5aff3928d8.nv26.05`; CUDA `13.2`; CuTe DSL `4.8.1`; CUPTI `13.4.0`.
- CUPTI packages: `{"cupti-python": "13.4.0", "nvidia-cuda-cupti": "13.4.58"}`.
- Workload: H7168, I2048, 256 experts, 32 local experts, topK8, group8/top-group4, routing scale 2.5, EP8/TP1 simulation, seed 42 and bias scale 0.01.
- Recipe: per-token activation, 4over6, E4M3 max 256, MSE, packed error arithmetic enabled, quantization fast math disabled; FC2 scale 1/1536; deterministic finalize; async memset disabled.
- Timer: native cold-L2 CUDA-graph CUPTI; 10 warmups and 100 samples per row. Saved tactic caches were never loaded.

## All 52 native medians

Milliseconds; values below retain the JSON float representation. T1/T2 are reported and excluded from all aggregates.

| Tokens | before-r1 | after-r1 | after-r2 | before-r2 |
| --- | --- | --- | --- | --- |
| 1 | 0.031777 | 0.031968 | 0.0319685 | 0.031968 |
| 2 | 0.0431365 | 0.0430085 | 0.042993 | 0.043104500000000004 |
| 4 | 0.0616805 | 0.061553 | 0.061792 | 0.061921 |
| 8 | 0.0778885 | 0.077889 | 0.0777925 | 0.077969 |
| 16 | 0.086945 | 0.086913 | 0.0868645 | 0.086849 |
| 32 | 0.123233 | 0.122961 | 0.123185 | 0.1228815 |
| 64 | 0.15737800000000002 | 0.1572015 | 0.1573295 | 0.1569935 |
| 128 | 0.1610255 | 0.16093 | 0.1608175 | 0.160802 |
| 256 | 0.171282 | 0.171506 | 0.171506 | 0.172162 |
| 512 | 0.177026 | 0.175266 | 0.175202 | 0.17661 |
| 4096 | 0.261139 | 0.22673900000000002 | 0.226819 | 0.26105849999999997 |
| 8192 | 0.37402 | 0.30272350000000003 | 0.30288349999999997 | 0.373444 |
| 16384 | 0.622438 | 0.4886775 | 0.4891095 | 0.622151 |

## Per-row comparison

Speedup is before/after; values above 1 favor after. Combined speedup is sqrt(R1 × R2). Before/after columns are geometric means of the two process medians, in microseconds.

| Tokens | Group | Before us | After us | R1 speedup | R2 speedup | Combined speedup | Latency reduction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | excluded-small | 31.872357 | 31.968250 | 0.994025x | 0.999984x | 0.997000x | -0.301% |
| 2 | excluded-small | 43.120497 | 43.000749 | 1.002976x | 1.002593x | 1.002785x | 0.278% |
| 4 | decode | 61.800633 | 61.672384 | 1.002071x | 1.002088x | 1.002080x | 0.208% |
| 8 | decode | 77.928740 | 77.840735 | 0.999994x | 1.002269x | 1.001131x | 0.113% |
| 16 | decode | 86.896987 | 86.888747 | 1.000368x | 0.999822x | 1.000095x | 0.009% |
| 32 | decode | 123.057124 | 123.072949 | 1.002212x | 0.997536x | 0.999871x | -0.013% |
| 64 | decode | 157.185632 | 157.265487 | 1.001123x | 0.997864x | 0.999492x | -0.051% |
| 128 | decode | 160.913711 | 160.873740 | 1.000593x | 0.999904x | 1.000248x | 0.025% |
| 256 | decode | 171.721436 | 171.506000 | 0.998694x | 1.003825x | 1.001256x | 0.125% |
| 512 | decode | 176.817878 | 175.233997 | 1.010042x | 1.008036x | 1.009039x | 0.896% |
| 4096 | prefill | 261.098747 | 226.778996 | 1.151716x | 1.150955x | 1.151336x | 13.144% |
| 8192 | prefill | 373.731889 | 302.803489 | 1.235517x | 1.232963x | 1.234239x | 18.978% |
| 16384 | prefill | 622.294483 | 488.893452 | 1.273719x | 1.272008x | 1.272863x | 21.437% |

## Unweighted geometric aggregates

| Group | Rows | R1 speedup | R2 speedup | Combined speedup | Latency reduction | Improved combined | Improved R1/R2 | Improved both |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| overall | 11 | 1.056995x | 1.056243x | 1.056619x | 5.358% | 9/11 | 9/7 | 5/11 |
| decode | 8 | 1.001882x | 1.001413x | 1.001647x | 0.164% | 6/8 | 6/4 | 2/8 |
| prefill | 3 | 1.219240x | 1.217585x | 1.218412x | 17.926% | 3/3 | 3/3 | 3/3 |

Overall includes 11 rows: decode T4–512 and prefill T4096/T8192/T16384. Each row has equal weight.

## Full selected tactics

Tactics are the complete recorded repr strings. AUTO columns record selections during prewarm; execution columns record the selection used outside tuning, including graph capture.

| Tokens | Process | AUTO selection | Execution selection |
| --- | --- | --- | --- |
| 1 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 1 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 1 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 1 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 2 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 2 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 4 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 4 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 4 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 4 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 8 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 8 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 16 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 32 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 32 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 32 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 32 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 64 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 64 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 64 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 64 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 128 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 128 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 128 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 128 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 256 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 256 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 256 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 256 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 512 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 512 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 512 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 512 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
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
| 1 | changed | same | changed | same |
| 2 | changed | same | changed | same |
| 4 | same | changed | same | changed |
| 8 | same | changed | same | changed |
| 16 | same | same | same | same |
| 32 | changed | changed | changed | changed |
| 64 | same | changed | changed | same |
| 128 | changed | same | changed | same |
| 256 | same | same | same | same |
| 512 | same | same | same | same |
| 4096 | same | same | same | same |
| 8192 | same | same | same | same |
| 16384 | same | same | same | same |

## Evidence validation

- Runner SHA256: `f39f104974167b8f92096a95bbabf55eb53a71b09b88720a258c183504f0dec8`.
- Pristine native harness SHA256: `9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371`.
- Adapted native harness SHA256: `906f531eded00dcbef733e42ada0f7480b14ca99e924b8a994d2aa5af5a8310f`.
- All 52 medians match 100 positive finite samples per row; all native medians and unit conversions agree; every row records measured AUTO and execution selections without fallback.
- Runtime, recipe, environment, workload, imported checkout path and routing histograms match. Changed recorded source hashes match the explicit expected delta: `flashinfer/cute_dsl/fp4_common.py`, `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py`, `flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py`, `flashinfer/fused_moe/cute_dsl/fused_moe.py`, `flashinfer/quantization/kernels/nvfp4_quantize.py`, `tests/moe/utils.py`. Other recorded source hashes match.

| Process | Input JSON SHA256 | Local evidence verification |
| --- | --- | --- |
| before-r1 | d90e987107dfb42b4c879807b1d7c8e36ee189c4dc387678f929db089be07186 | complete |
| after-r1 | e1ba859239632b54773f158d0bedecb43339377990ea80fdce376f2b4d631aba | complete |
| after-r2 | c992c0f7e56ae4cdfdc8c8ab6b5b73d177fce201645cc914aef1c73baacc1364 | complete |
| before-r2 | 59f09d8e9b9b54890574329c39d837e181502e1f66819fca78b17faf0243ab7c | complete |

| Source | Before SHA256 | After SHA256 | Changed |
| --- | --- | --- | --- |
| benchmarks/bench_moe_deepseek.py | 9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371 | 9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371 | False |
| flashinfer/autotuner/autotuner.py | 0db42ad90d1a3fec6f81509a2c520c1892cea0a433f5dbd7f43468a2a10243ca | 0db42ad90d1a3fec6f81509a2c520c1892cea0a433f5dbd7f43468a2a10243ca | False |
| flashinfer/cute_dsl/fp4_common.py | 6cda2e2fa955ca608844209e5792d5a2136f6a2e6e0a8d3fb7cc285ebc01531d | 3a82766dfc00ee9ec749728f3ef25cb854b37c7b0cbebc9ff721574a77b78bab | True |
| flashinfer/fp4_quantization.py | fb394c543cfd112ec6ceccfd8c808058f7b10ab88d9a8adda0a9cbd067c25f97 | fb394c543cfd112ec6ceccfd8c808058f7b10ab88d9a8adda0a9cbd067c25f97 | False |
| flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py | d1931bb6eaada693e6f4b43c1e682179424a1e478170624cacef28834f768cdb | 5618e95b448cc4aa80a6d5d5661f696134bdddba390b9c97cc7244b00f794b1a | True |
| flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py | 79cdcb441ce569986394bbd536126dbed03015ad72694972a237bf89da07bb45 | 79cdcb441ce569986394bbd536126dbed03015ad72694972a237bf89da07bb45 | False |
| flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py | 4266a8ec5b941558aafaf767aa3dbdc0d3a4c4e28edd8cf339007b4c45b91635 | 00a9a3317d0c3c25a5291a3c186ba634bdbb6b433a4b93b2090f5cecf1bcaaed | True |
| flashinfer/fused_moe/cute_dsl/fused_moe.py | db8602ce17902b085ec5589e13abe842910119038628a354d230145b9c5e48d4 | e79c9b23e04d0f3218a3540b560edd9155a9c80be141452c80c02080d060814b | True |
| flashinfer/fused_moe/cute_dsl/tuner.py | d12a73b51ca5e239a6a3ae04ad2b8f68baad0d1c650e1997e47fd5f2b48c6fde | d12a73b51ca5e239a6a3ae04ad2b8f68baad0d1c650e1997e47fd5f2b48c6fde | False |
| flashinfer/quantization/kernels/nvfp4_quantize.py | 6fcef37fd6e41cbeea7987b458fb6eedfad387918b4521ae74891f9b9b948e7a | 2c93a85cd4b0ca0675cc0c023cc29d8bcf9adce22793d6680819d66eee52e685 | True |
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
    "/workspace/pr4824-final-pdl/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824-final-pdl/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824-final-pdl/bench_moe_deepseek.native.py",
    "--expected-head",
    "e734816171909b755ed1a9a510b7178d23bdf692",
    "--label",
    "before-r1",
    "--image",
    "nvcr.io/nvidia/pytorch:26.05-py3",
    "--tokens",
    "1",
    "2",
    "4",
    "8",
    "16",
    "32",
    "64",
    "128",
    "256",
    "512",
    "4096",
    "8192",
    "16384",
    "--output",
    "/workspace/pr4824-final-pdl/results/final-pdl/before-r1.json"
  ],
  "after-r1": [
    "/workspace/pr4824-final-pdl/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824-final-pdl/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824-final-pdl/bench_moe_deepseek.native.py",
    "--expected-head",
    "1db8a7507bbca6f2d705ee1365f3108ba03fa128",
    "--label",
    "after-r1",
    "--image",
    "nvcr.io/nvidia/pytorch:26.05-py3",
    "--tokens",
    "1",
    "2",
    "4",
    "8",
    "16",
    "32",
    "64",
    "128",
    "256",
    "512",
    "4096",
    "8192",
    "16384",
    "--output",
    "/workspace/pr4824-final-pdl/results/final-pdl/after-r1.json"
  ],
  "after-r2": [
    "/workspace/pr4824-final-pdl/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824-final-pdl/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824-final-pdl/bench_moe_deepseek.native.py",
    "--expected-head",
    "1db8a7507bbca6f2d705ee1365f3108ba03fa128",
    "--label",
    "after-r2",
    "--image",
    "nvcr.io/nvidia/pytorch:26.05-py3",
    "--tokens",
    "1",
    "2",
    "4",
    "8",
    "16",
    "32",
    "64",
    "128",
    "256",
    "512",
    "4096",
    "8192",
    "16384",
    "--output",
    "/workspace/pr4824-final-pdl/results/final-pdl/after-r2.json"
  ],
  "before-r2": [
    "/workspace/pr4824-final-pdl/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824-final-pdl/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824-final-pdl/bench_moe_deepseek.native.py",
    "--expected-head",
    "e734816171909b755ed1a9a510b7178d23bdf692",
    "--label",
    "before-r2",
    "--image",
    "nvcr.io/nvidia/pytorch:26.05-py3",
    "--tokens",
    "1",
    "2",
    "4",
    "8",
    "16",
    "32",
    "64",
    "128",
    "256",
    "512",
    "4096",
    "8192",
    "16384",
    "--output",
    "/workspace/pr4824-final-pdl/results/final-pdl/before-r2.json"
  ]
}
```

## Limits

- Two process repeats describe consistency; no confidence interval or statistical-significance claim.
- AUTO tunes independently per process; tactic changes are part of this native API comparison, not a fixed-tactic kernel comparison.
- Single-GPU EP8/TP1 simulation, with no distributed communication or fused atomic finalization.
- Initial activation quantization is outside timing; routing, MoE, intermediate quantization and deterministic unpermute are inside.
- Explicit recipe and FC2 scale 1/1536 adapt the native W4A4 harness; unused CUTLASS packs retain native preparation.
