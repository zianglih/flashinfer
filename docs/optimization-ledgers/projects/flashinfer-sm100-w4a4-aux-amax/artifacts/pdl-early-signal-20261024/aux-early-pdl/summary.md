# Deterministic-RL native W4A4 benchmark

All four completed runs passed validation. Run order: before-r1, after-r1, after-r2, before-r2; each invocation used fresh AUTO selection.

- Before: `3363d5d65d390f9a10e856981a241bb6c071568e`; after: `1db8a7507bbca6f2d705ee1365f3108ba03fa128`.
- Runtime: `nvcr.io/nvidia/pytorch:26.05-py3`; NVIDIA B300 SXM6 AC; PyTorch `2.12.0a0+5aff3928d8.nv26.05`; CUDA `13.2`; CuTe DSL `4.8.1`; CUPTI `13.4.0`.
- CUPTI packages: `{"cupti-python": "13.4.0", "nvidia-cuda-cupti": "13.4.58"}`.
- Workload: H7168, I2048, 256 experts, 32 local experts, topK8, group8/top-group4, routing scale 2.5, EP8/TP1 simulation, seed 42 and bias scale 0.01.
- Recipe: per-token activation, 4over6, E4M3 max 256, MSE, packed error arithmetic enabled, quantization fast math disabled; FC2 scale 1/1536; deterministic finalize; async memset disabled.
- Timer: native cold-L2 CUDA-graph CUPTI; 10 warmups and 100 samples per row. Saved tactic caches were never loaded.

## All 52 native medians

Milliseconds; values below retain the JSON float representation. T1/T2 are reported and excluded from all aggregates.

| Tokens | before-r1 | after-r1 | after-r2 | before-r2 |
| --- | --- | --- | --- | --- |
| 1 | 0.031808 | 0.031968 | 0.031856499999999996 | 0.031841 |
| 2 | 0.043104500000000004 | 0.043104 | 0.042992 | 0.048609 |
| 4 | 0.061616500000000005 | 0.061697 | 0.0616325 | 0.0616005 |
| 8 | 0.0778725 | 0.0779215 | 0.077681 | 0.0777285 |
| 16 | 0.0868645 | 0.0869125 | 0.086817 | 0.086849 |
| 32 | 0.1231855 | 0.122945 | 0.122977 | 0.12312100000000001 |
| 64 | 0.157361 | 0.157506 | 0.1572175 | 0.157249 |
| 128 | 0.161058 | 0.1610895 | 0.16093000000000002 | 0.16104200000000002 |
| 256 | 0.17156949999999999 | 0.17147400000000002 | 0.1716335 | 0.171394 |
| 512 | 0.175394 | 0.175282 | 0.1754095 | 0.1754745 |
| 4096 | 0.2271225 | 0.226851 | 0.22677 | 0.2269625 |
| 8192 | 0.302851 | 0.3026115 | 0.3026105 | 0.3027385 |
| 16384 | 0.489557 | 0.488709 | 0.48934849999999996 | 0.48886850000000004 |

## Per-row comparison

Speedup is before/after; values above 1 favor after. Combined speedup is sqrt(R1 × R2). Before/after columns are geometric means of the two process medians, in microseconds.

| Tokens | Group | Before us | After us | R1 speedup | R2 speedup | Combined speedup | Latency reduction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | excluded-small | 31.824496 | 31.912201 | 0.994995x | 0.999513x | 0.997252x | -0.276% |
| 2 | excluded-small | 45.774083 | 43.047964 | 1.000012x | 1.130652x | 1.063327x | 5.956% |
| 4 | decode | 61.608499 | 61.664742 | 0.998695x | 0.999481x | 0.999088x | -0.091% |
| 8 | decode | 77.800467 | 77.801157 | 0.999371x | 1.000611x | 0.999991x | -0.001% |
| 16 | decode | 86.856750 | 86.864737 | 0.999448x | 1.000369x | 0.999908x | -0.009% |
| 32 | decode | 123.153246 | 122.960999 | 1.001956x | 1.001171x | 1.001563x | 0.156% |
| 64 | decode | 157.304990 | 157.361684 | 0.999079x | 1.000200x | 0.999640x | -0.036% |
| 128 | decode | 161.050000 | 161.009730 | 0.999804x | 1.000696x | 1.000250x | 0.025% |
| 256 | decode | 171.481728 | 171.553731 | 1.000557x | 0.998605x | 0.999580x | -0.042% |
| 512 | decode | 175.434245 | 175.345738 | 1.000639x | 1.000371x | 1.000505x | 0.050% |
| 4096 | prefill | 227.042486 | 226.810496 | 1.001197x | 1.000849x | 1.001023x | 0.102% |
| 8192 | prefill | 302.794745 | 302.611000 | 1.000791x | 1.000423x | 1.000607x | 0.061% |
| 16384 | prefill | 489.212629 | 489.028645 | 1.001735x | 0.999019x | 1.000376x | 0.038% |

## Unweighted geometric aggregates

| Group | Rows | R1 speedup | R2 speedup | Combined speedup | Latency reduction | Improved combined | Improved R1/R2 | Improved both |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| overall | 11 | 1.000297x | 1.000163x | 1.000230x | 0.023% | 6/11 | 6/8 | 4/11 |
| decode | 8 | 0.999943x | 1.000188x | 1.000065x | 0.007% | 3/8 | 3/6 | 2/8 |
| prefill | 3 | 1.001241x | 1.000097x | 1.000669x | 0.067% | 3/3 | 3/2 | 2/3 |

Overall includes 11 rows: decode T4–512 and prefill T4096/T8192/T16384. Each row has equal weight.

## Full selected tactics

Tactics are the complete recorded repr strings. AUTO columns record selections during prewarm; execution columns record the selection used outside tuning, including graph capture.

| Tokens | Process | AUTO selection | Execution selection |
| --- | --- | --- | --- |
| 1 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 1 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 1 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 1 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 2 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 2 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 2 | before-r2 | `(128, ((128, 256), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 256), (1, 1), False), ((128, 128), (1, 1), False))` |
| 4 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 4 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 4 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 4 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 8 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 8 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 16 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 16 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 16 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 32 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 32 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 32 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 32 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 64 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 64 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 64 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 64 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 128 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 128 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 128 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 1), False))` |
| 128 | before-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 256 | before-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 256 | after-r1 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
| 256 | after-r2 | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` | `(128, ((128, 128), (1, 1), False), ((128, 128), (1, 2), False))` |
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
| 1 | changed | same | same | changed |
| 2 | same | changed | changed | changed |
| 4 | changed | same | same | changed |
| 8 | changed | same | same | changed |
| 16 | changed | same | same | changed |
| 32 | changed | same | same | changed |
| 64 | changed | same | changed | same |
| 128 | same | changed | same | changed |
| 256 | same | changed | changed | same |
| 512 | same | same | same | same |
| 4096 | same | same | same | same |
| 8192 | same | same | same | same |
| 16384 | same | same | same | same |

## Evidence validation

- Runner SHA256: `f39f104974167b8f92096a95bbabf55eb53a71b09b88720a258c183504f0dec8`.
- Pristine native harness SHA256: `9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371`.
- Adapted native harness SHA256: `906f531eded00dcbef733e42ada0f7480b14ca99e924b8a994d2aa5af5a8310f`.
- All 52 medians match 100 positive finite samples per row; all native medians and unit conversions agree; every row records measured AUTO and execution selections without fallback.
- Runtime, recipe, environment, workload, imported checkout path and routing histograms match. Changed recorded source hashes match the explicit expected delta: `flashinfer/quantization/kernels/nvfp4_quantize.py`. Other recorded source hashes match.

| Process | Input JSON SHA256 | Local evidence verification |
| --- | --- | --- |
| before-r1 | 676822d9e5b42d755f0080eed44a51eb058a674b57cfff3dacfe0fecb2bc27ef | complete |
| after-r1 | 4efb31141caa269c42f1355526f716d084aa5514f16625374c71eff5d423b795 | complete |
| after-r2 | d4feffab2362824bb16fe3243d0bd58a1d7185387ef7f53b56ff5a922e933bc0 | complete |
| before-r2 | 51db5366b009605b3e4462d14e73b14d1a7e254f9867fd78a258aeefb5c38d13 | complete |

| Source | Before SHA256 | After SHA256 | Changed |
| --- | --- | --- | --- |
| benchmarks/bench_moe_deepseek.py | 9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371 | 9561d42c798eecbdbc2e3edd31889c0475ff1a56dcd6be7b164ffa7068a86371 | False |
| flashinfer/autotuner/autotuner.py | 0db42ad90d1a3fec6f81509a2c520c1892cea0a433f5dbd7f43468a2a10243ca | 0db42ad90d1a3fec6f81509a2c520c1892cea0a433f5dbd7f43468a2a10243ca | False |
| flashinfer/cute_dsl/fp4_common.py | 3a82766dfc00ee9ec749728f3ef25cb854b37c7b0cbebc9ff721574a77b78bab | 3a82766dfc00ee9ec749728f3ef25cb854b37c7b0cbebc9ff721574a77b78bab | False |
| flashinfer/fp4_quantization.py | fb394c543cfd112ec6ceccfd8c808058f7b10ab88d9a8adda0a9cbd067c25f97 | fb394c543cfd112ec6ceccfd8c808058f7b10ab88d9a8adda0a9cbd067c25f97 | False |
| flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py | 5618e95b448cc4aa80a6d5d5661f696134bdddba390b9c97cc7244b00f794b1a | 5618e95b448cc4aa80a6d5d5661f696134bdddba390b9c97cc7244b00f794b1a | False |
| flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py | 79cdcb441ce569986394bbd536126dbed03015ad72694972a237bf89da07bb45 | 79cdcb441ce569986394bbd536126dbed03015ad72694972a237bf89da07bb45 | False |
| flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py | 00a9a3317d0c3c25a5291a3c186ba634bdbb6b433a4b93b2090f5cecf1bcaaed | 00a9a3317d0c3c25a5291a3c186ba634bdbb6b433a4b93b2090f5cecf1bcaaed | False |
| flashinfer/fused_moe/cute_dsl/fused_moe.py | e79c9b23e04d0f3218a3540b560edd9155a9c80be141452c80c02080d060814b | e79c9b23e04d0f3218a3540b560edd9155a9c80be141452c80c02080d060814b | False |
| flashinfer/fused_moe/cute_dsl/tuner.py | d12a73b51ca5e239a6a3ae04ad2b8f68baad0d1c650e1997e47fd5f2b48c6fde | d12a73b51ca5e239a6a3ae04ad2b8f68baad0d1c650e1997e47fd5f2b48c6fde | False |
| flashinfer/quantization/kernels/nvfp4_quantize.py | 2b626b7421169b2abe4a56ba395b906009e03daab9ea9cb68934613e73536473 | 2c93a85cd4b0ca0675cc0c023cc29d8bcf9adce22793d6680819d66eee52e685 | True |
| flashinfer/quantization/nvfp4_quantization_utils.py | d52442fc6aa04b3e2dd5ebad3bbd2d8820ce437c8de2b6a7ad0e8e19960a15d6 | d52442fc6aa04b3e2dd5ebad3bbd2d8820ce437c8de2b6a7ad0e8e19960a15d6 | False |
| flashinfer/testing/utils.py | bf532ebc0b82d3551a09bea6bc96017b838bcb52d461f9a5d19573ac9766ac34 | bf532ebc0b82d3551a09bea6bc96017b838bcb52d461f9a5d19573ac9766ac34 | False |
| tests/moe/utils.py | 3b410a7b2370891a5b7e5dd369d82a9c4294d3dcead4509be7accfde47e62df5 | 3b410a7b2370891a5b7e5dd369d82a9c4294d3dcead4509be7accfde47e62df5 | False |

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
    "/workspace/pr4824-pdl/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824-pdl/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824-pdl/bench_moe_deepseek.native.py",
    "--expected-head",
    "3363d5d65d390f9a10e856981a241bb6c071568e",
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
    "/workspace/pr4824-pdl/results/aux-early-pdl/before-r1.json"
  ],
  "after-r1": [
    "/workspace/pr4824-pdl/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824-pdl/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824-pdl/bench_moe_deepseek.native.py",
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
    "/workspace/pr4824-pdl/results/aux-early-pdl/after-r1.json"
  ],
  "after-r2": [
    "/workspace/pr4824-pdl/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824-pdl/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824-pdl/bench_moe_deepseek.native.py",
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
    "/workspace/pr4824-pdl/results/aux-early-pdl/after-r2.json"
  ],
  "before-r2": [
    "/workspace/pr4824-pdl/bench_pr7196_deterministic_rl.py",
    "--repo",
    "/workspace/pr4824-pdl/flashinfer",
    "--benchmark-source",
    "/workspace/pr4824-pdl/bench_moe_deepseek.native.py",
    "--expected-head",
    "3363d5d65d390f9a10e856981a241bb6c071568e",
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
    "/workspace/pr4824-pdl/results/aux-early-pdl/before-r2.json"
  ]
}
```

## Limits

- Two process repeats describe consistency; no confidence interval or statistical-significance claim.
- AUTO tunes independently per process; tactic changes are part of this native API comparison, not a fixed-tactic kernel comparison.
- Single-GPU EP8/TP1 simulation, with no distributed communication or fused atomic finalization.
- Initial activation quantization is outside timing; routing, MoE, intermediate quantization and deterministic unpermute are inside.
- Explicit recipe and FC2 scale 1/1536 adapt the native W4A4 harness; unused CUTLASS packs retain native preparation.
