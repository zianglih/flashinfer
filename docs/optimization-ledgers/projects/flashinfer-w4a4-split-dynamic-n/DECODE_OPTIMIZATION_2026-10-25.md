# NVFP4 decode optimization round

No candidate in this round produced a repeatable whole-MoE improvement worth
retaining. Production remains clean and pushed at
`98fd3566b5f945c100f48cddacf25deb2432cbc2`; upstream draft
[PR7290](https://github.com/flashinfer-ai/flashinfer/pull/7290) and its final
performance body were fetched and verified unchanged after the experiments.

The current retained CuTe/TRTLLM speed ratios are **0.992310 decode**, **1.170954
prefill**, and **1.038136 overall**. The stable decode-win target is not met.
These remain the completed native AUTO measurements; the fixed-tactic screens
below do not replace them. [Raw backend comparison and protocol](evidence/trtllm-nvfp4-reference-98fd/summary.md).

## TRTLLM and profiling evidence

The published, unmerged source is [PR2917](https://github.com/flashinfer-ai/flashinfer/pull/2917),
head `64ed071e23bf8d5d2d5af5c91577e5b8e036a1cf`. Its generated source is useful
architectural prior art. It is not byte-equivalent to the current measured
`8ee504560a86b6c72b8c941d3003e8fb1804b1b6/batched_gemm-fdba669-16ba8ed`
native artifacts. Three saved-cache decode traces identify six current cubins;
all six hashes match the original TRT benchmark archive. Their N8/N16 MMA and
narrow TMEM loads motivated the epilogue experiments.
[Source, cubin, launch and lane-layout audit](scripts/trtllm_gen_decode_audit/README.md).

Current98fd decode NCU shows70–84% DRAM throughput and weight reads within0.4%
of one payload-plus-SF pass over active experts. GEMMs dominate latency. The
original197504B SMEM limits residency to one CTA. Reducing SMEM alone does not
admit another CTA: a TMEM allocation permit retains the initial virtual-resource
reservation. Supported early permit release enabled measured1.88/1.93 active
CTAs per SM for FC1/FC2, but both tested pipeline configurations lost full-chain
performance. [Decode phase/NCU evidence](scripts/decode98fd_profile/README.md),
[permit semantics and source precedents](scripts/decode98fd_profile/TMEM_PERMIT_AUDIT.md).

## Candidate decisions

All ratios below are control/candidate, so greater than one favors the
candidate. Phase measurements are explicitly labeled and are not additive.

| Candidate | Workload and measured region | Result | Decision and evidence |
|---|---|---|---|
| Group-1 dynamic N rounded8 | T4/32/128/512, N16, whole chain | 1.000004/1.000954/1.002535/0.999228 | Neutral; [all full/phase medians](scripts/dynamic_n8_experiment/README.md) |
| Physical B16 plus five stages | T32/128, N16, whole chain | 0.991981/0.992374 | Rejected; does not isolate B16 alone. [Evidence](scripts/small_b_experiment/README.md) |
| K8/two stages, two resident CTAs, early permit | T32/128 × N16/32, whole chain | 1.56–3.49% slower | Rejected despite verified residency. [Evidence](scripts/small_n_occupancy_experiment/README.md) |
| K4/four stages, two resident CTAs, early permit | T32/N16, whole chain | 0.961570 | Rejected. [Evidence](scripts/small_n_k4_occupancy_experiment/README.md) |
| Narrow epilogue with FP32 shuffles | T32/128/N16, FC1 wrapper including prep | 1.000889/0.999877 | Neutral. [Evidence](scripts/narrow_epilogue_experiment/README.md) |
| Direct Ld16x256 plus packed output permutation | T32/N16, FC1 wrapper including prep | 0.997577 | Rejected. [Evidence](scripts/narrow_ld256_epilogue_experiment/README.md) |
| Contiguous destination ownership for scalar SF stores | T32/128/N16, preparation only | Approximately0.04–0.08us saved | Too small to retain; no full-chain claim. [Evidence](scripts/prep_linear_sf_experiment/summary.json) |
| Skip small-N canonical SF prep; gather original linear SF | T32/N16, whole chain | 0.997931 | Rejected. [Evidence](scripts/small_n_linear_sf_experiment/README.md) |

The eight screens preserve164 timed arms and16,400 individual samples. Each
timed arm uses ten warmups and100 cold-L2 CUDA-graph CUPTI samples, with adjacent
ABA/BAB or ABAB controls on the same assigned B200. Every candidate passed its
focused differential byte checks before timing; broader format and sanitizer
checks were deliberately not pursued for losing candidates. No original B1,
retained CuTe AUTO campaign, or TRT reference was rerun for these screens.

The linear-SF gather prototype additionally exposes an unretained alignment
boundary: preparation accepts4-byte SF views while its host pointer annotation
still assumes16. Current measurements used naturally aligned inputs. Any future
reuse must correct that annotation and validate offset4 source views. Its old
canonical-SF preparation probes also cannot blindly fill the now-aliased input.

All eight implementations remain unstaged in separate actual source copies for
review; raw archives preserve source snapshots, hashes, failed preflight/compile
attempts, outputs, samples and available PTX/SASS/NCU evidence. The PR body
continues to contain only retained results. There is no new retained commit.
