# Deterministic-RL native W4A4 benchmark

All four completed runs passed validation. Run order: before-r1, after-r1, after-r2, before-r2; each invocation used fresh AUTO selection.

- Before: `03f82fddadaebed69879b4e7d28f3df38c4e28d2`; after: `e40fad018174232e26d97a69c66dd60e1ddfb59b`.
- Runtime: `nvcr.io/nvidia/pytorch:26.05-py3`; NVIDIA B300 SXM6 AC; PyTorch `2.12.0a0+5aff3928d8.nv26.05`; CUDA `13.2`; CuTe DSL `4.8.1`; CUPTI `13.4.0`.
- CUPTI packages: `{"cupti-python": "13.4.0", "nvidia-cuda-cupti": "13.4.58"}`.
- Workload: H7168, I2048, 256 experts, 32 local experts, topK8, group8/top-group4, routing scale 2.5, EP8/TP1 simulation, seed 42 and bias scale 0.01.
- Recipe: per-token activation, 4over6, E4M3 max 256, MSE, packed error arithmetic enabled, quantization fast math disabled; FC2 scale 1/1536; deterministic finalize; async memset disabled.
- Timer: native cold-L2 CUDA-graph CUPTI; 10 warmups and 100 samples per row. Saved tactic caches were never loaded.

## All 52 native medians

Milliseconds; values below retain the JSON float representation. T1/T2 are reported and excluded from all aggregates.

| Tokens | before-r1 | after-r1 | after-r2 | before-r2 |
| --- | --- | --- | --- | --- |
| 1 | 0.0320005 | 0.0319045 | 0.031968 | 0.031872 |
| 2 | 0.042976 | 0.0429285 | 0.0430405 | 0.0429925 |
| 4 | 0.061825 | 0.0617925 | 0.061729 | 0.0618085 |
| 8 | 0.077921 | 0.078016 | 0.0778565 | 0.0779045 |
| 16 | 0.086945 | 0.0868965 | 0.087057 | 0.086961 |
| 32 | 0.123137 | 0.1229775 | 0.123105 | 0.1231375 |
| 64 | 0.15726600000000002 | 0.157282 | 0.1572015 | 0.1572825 |
| 128 | 0.1611535 | 0.161058 | 0.16118549999999998 | 0.160993 |
| 256 | 0.171569 | 0.1716655 | 0.171473 | 0.17156949999999999 |
| 512 | 0.1770415 | 0.1755055 | 0.1752335 | 0.17704199999999998 |
| 4096 | 0.2613305 | 0.226946 | 0.227026 | 0.2615225 |
| 8192 | 0.373715 | 0.302531 | 0.30269100000000004 | 0.373651 |
| 16384 | 0.621766 | 0.4885485 | 0.4882125 | 0.6219414999999999 |

## Per-row comparison

Speedup is before/after; values above 1 favor after. Combined speedup is sqrt(R1 × R2). Before/after columns are geometric means of the two process medians, in microseconds.

| Tokens | Group | Before us | After us | R1 speedup | R2 speedup | Combined speedup | Latency reduction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | excluded-small | 31.936185 | 31.936234 | 1.003009x | 0.996997x | 0.999998x | -0.000% |
| 2 | excluded-small | 42.984249 | 42.984464 | 1.001106x | 0.998885x | 0.999995x | -0.000% |
| 4 | decode | 61.816749 | 61.760742 | 1.000526x | 1.001288x | 1.000907x | 0.091% |
| 8 | decode | 77.912750 | 77.936209 | 0.998782x | 1.000617x | 0.999699x | -0.030% |
| 16 | decode | 86.953000 | 86.976713 | 1.000558x | 0.998897x | 0.999727x | -0.027% |
| 32 | decode | 123.137250 | 123.041233 | 1.001297x | 1.000264x | 1.000780x | 0.078% |
| 64 | decode | 157.274250 | 157.241745 | 0.999898x | 1.000515x | 1.000207x | 0.021% |
| 128 | decode | 161.073230 | 161.121737 | 1.000593x | 0.998806x | 0.999699x | -0.030% |
| 256 | decode | 171.569250 | 171.569223 | 0.999438x | 1.000563x | 1.000000x | 0.000% |
| 512 | decode | 177.041750 | 175.369447 | 1.008752x | 1.010321x | 1.009536x | 0.945% |
| 4096 | prefill | 261.426482 | 226.985996 | 1.151510x | 1.151950x | 1.151730x | 13.174% |
| 8192 | prefill | 373.682999 | 302.610989 | 1.235295x | 1.234430x | 1.234863x | 19.019% |
| 16384 | prefill | 621.853744 | 488.380471 | 1.272680x | 1.273916x | 1.273298x | 21.464% |

## Unweighted geometric aggregates

| Group | Rows | R1 speedup | R2 speedup | Combined speedup | Latency reduction | Improved combined | Improved R1/R2 | Improved both |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| overall | 11 | 1.056379x | 1.056577x | 1.056478x | 5.346% | 8/11 | 8/9 | 6/11 |
| decode | 8 | 1.001226x | 1.001403x | 1.001315x | 0.131% | 5/8 | 5/6 | 3/8 |
| prefill | 3 | 1.218763x | 1.219028x | 1.218895x | 17.958% | 3/3 | 3/3 | 3/3 |

Overall includes 11 rows: decode T4–512 and prefill T4096/T8192/T16384. Each row has equal weight.

## Full selected tactics

Tactics are the complete recorded repr strings. AUTO columns record selections during prewarm; execution columns record the selection used outside tuning, including graph capture.

| Tokens | Process | AUTO selection | Execution selection |
| --- | --- | --- | --- |
| 1 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 1 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 1 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 1 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 4 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 4 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 4 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 4 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 8 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 16 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 32 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 32 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 32 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 32 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 64 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 64 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 64 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 64 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 128 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 128 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 128 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 128 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 256 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 256 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
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
| 1 | changed | changed | changed | changed |
| 2 | same | same | same | same |
| 4 | changed | changed | changed | changed |
| 8 | changed | changed | changed | changed |
| 16 | same | changed | changed | same |
| 32 | changed | same | changed | same |
| 64 | changed | changed | same | same |
| 128 | same | same | same | same |
| 256 | same | same | changed | changed |
| 512 | same | same | same | same |
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
| before-r1 | 3a535b15be16fe6cce69ed74553a812640002e6305db4d8ffb61eea1e1c26bfa | complete |
| after-r1 | 0eb59b813925b2a620fb6cc96b71cfb4709f89542e5d78afb0cc5628f1acebb2 | complete |
| after-r2 | 90d654c8ebce710923cdbd4af41bdfe6c99948184cc69849de413ab8a81f7891 | complete |
| before-r2 | 1fcae73b3b4eb57170eeb112b14dbfc8755c3affcd65e88f7800ab301084db6b | complete |

| Source | Before SHA256 | After SHA256 | Changed |
| --- | --- | --- | --- |
| benchmarks/bench_moe_deepseek.py | 9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371 | 9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371 | False |
| flashinfer/autotuner/autotuner.py | 0db42ad90d1a3fec6f81509a2c520c1892cea0a433f5dbd7f43468a2a10243ca | 0db42ad90d1a3fec6f81509a2c520c1892cea0a433f5dbd7f43468a2a10243ca | False |
| flashinfer/cute_dsl/fp4_common.py | 6cda2e2fa955ca608844209e5792d5a2136f6a2e6e0a8d3fb7cc285ebc01531d | 3a82766dfc00ee9ec749728f3ef25cb854b37c7b0cbebc9ff721574a77b78bab | True |
| flashinfer/fp4_quantization.py | fb394c543cfd112ec6ceccfd8c808058f7b10ab88d9a8adda0a9cbd067c25f97 | fb394c543cfd112ec6ceccfd8c808058f7b10ab88d9a8adda0a9cbd067c25f97 | False |
| flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py | d1931bb6eaada693e6f4b43c1e682179424a1e478170624cacef28834f768cdb | 5618e95b448cc4aa80a6d5d5661f696134bdddba390b9c97cc7244b00f794b1a | True |
| flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py | 79cdcb441ce569986394bbd536126dbed03015ad72694972a237bf89da07bb45 | 79cdcb441ce569986394bbd536126dbed03015ad72694972a237bf89da07bb45 | False |
| flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py | 4266a8ec5b941558aafaf767aa3dbdc0d3a4c4e28edd8cf339007b4c45b91635 | f4a1297341525fda06f63a4fe990e9e6bf0bdae422e43ba504062b8a21fcd8f1 | True |
| flashinfer/fused_moe/cute_dsl/fused_moe.py | db8602ce17902b085ec5589e13abe842910119038628a354d230145b9c5e48d4 | e79c9b23e04d0f3218a3540b560edd9155a9c80be141452c80c02080d060814b | True |
| flashinfer/fused_moe/cute_dsl/tuner.py | d12a73b51ca5e239a6a3ae04ad2b8f68baad0d1c650e1997e47fd5f2b48c6fde | cef43204402ae65ab609ff3d3510e38ea56467d41013145331318f0bbdadf0a0 | True |
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
    "/workspace/pr4824/results/pr7196-deterministic-rl-final/before-r1.json"
  ],
  "after-r1": [
    "/workspace/pr4824/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824/bench_moe_deepseek.native.py",
    "--expected-head",
    "e40fad018174232e26d97a69c66dd60e1ddfb59b",
    "--label",
    "after-r1",
    "--output",
    "/workspace/pr4824/results/pr7196-deterministic-rl-final/after-r1.json"
  ],
  "after-r2": [
    "/workspace/pr4824/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824/bench_moe_deepseek.native.py",
    "--expected-head",
    "e40fad018174232e26d97a69c66dd60e1ddfb59b",
    "--label",
    "after-r2",
    "--output",
    "/workspace/pr4824/results/pr7196-deterministic-rl-final/after-r2.json"
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
    "/workspace/pr4824/results/pr7196-deterministic-rl-final/before-r2.json"
  ]
}
```

## Limits

- Two process repeats describe consistency; no confidence interval or statistical-significance claim.
- AUTO tunes independently per process; tactic changes are part of this native API comparison, not a fixed-tactic kernel comparison.
- Single-GPU EP8/TP1 simulation, with no distributed communication or fused atomic finalization.
- Initial activation quantization is outside timing; routing, MoE, intermediate quantization and deterministic unpermute are inside.
- Explicit recipe and FC2 scale 1/1536 adapt the native W4A4 harness; unused CUTLASS packs retain native preparation.
