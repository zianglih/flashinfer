# Small-N independent weight producer

Experimental, unretained, and unstaged. Base `98fd3566b5f945c100f48cddacf25deb2432cbc2`; actual local source copy `../../flashinfer-producer-roles-review`. Only the blockscaled SM100 core changes. Production, preparation, APIs, and MegaMoE remain untouched. [manifest.json](manifest.json) pins source and patch hashes.

## Mechanism and prior boundary

At small N, the existing four producer warps collectively copy all 128 physical SF rows, including zero-fill. Warp0 also issues A/SFA and B TMA after waiting for the SF ring. The experiment moves weight A/SFA into a new warp9 with an independently advancing pipeline state. Existing warps0–3 retain B/SFB work, epi warps4–7 and MMA warp8 keep their roles. CTA size is320 instead of288, gated by `cta_group_size == 1 && !tma_sfb && overlap_epilogue`; other geometries retain their organization.

A/SFA uses `a_barriers`; B payload gets its own TMA ring using `relay_barriers`, which are inactive in group1. The active 128-participant SF cp.async ring remains untouched. This introduces no additional shared operand stage, TMEM column, barrier storage, allocation, cache-policy change, or alignment requirement. Each TMA ring expects one elected producer arrival. For native NVFP4 K512/N16: A/SFA expects36,864B, B8,192B, and the existing cp.async pipeline owns4,096B SFB. MMA waits A, B, and SF before the original S2T/MMA sequence, then releases each only after MMA. Each producer drains its own cloned state; whole-CTA retrieval/teardown barriers follow320 threads while the128-thread TMEM deallocation protocol remains unchanged.

This is distinct from two rejected experiments:

- [Prior independent rings](../regular_tma_pipeline_experiment/README.md) only enabled prepared FC1 N128/N256 with TMA SFB. Small-N was unchanged numerical control; no small-N performance experiment occurred. Large-N results were neutral or slower.
- [Prior dedicated weight warp](../dedicated_weight_tma_experiment/README.md) used442 Gather4 N128/NB2 and a shared TMA completion ring. Results did not establish repeatable whole-chain gains. This experiment tests regular B TMA plus independent weight advancement on decode.

The tradeoff is an extra warp and an extra completion release per stage. Existing decode profiles show mostly near-single-pass cold weight traffic; increased producer issue overlap cannot be assumed to improve bandwidth or final latency. Static source validation is not performance evidence.

## Bounded screen

Assigned GPU4 on replacement C1 `fi-w4a4-narrow-1025`, nodeB200-92, UUID `GPU-9b1e25f5-48e6-f126-6d93-160b7ea7dd32`. Image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.78, CuTeDSL4.7.1, CUPTI13.4.0. Parent environment receipt: [environment.json](../../evidence/narrow-pipeline-environment/environment.json). All remote shells source `scripts/recovery442/env_candidate.sh`; native epoch remains candidate442, CuTe cache is private to this experiment.

Plan: timeout-bounded native T32 exact smoke, then fixedN16 T32/T128 same-input ABA/BAB full chain and FC1/FC2 phase diagnostics,10warmups/100cold-L2 CUDA-graph/CUPTI samples per arm. Actual native benchmark inputs, unchanged regular preparation and unfused finalization. Explicit output initialization checks full phase bytes/SF before and after timing; full chain checks final bytes and input hashes. FC1 phase includes preparation; isolated phases are not additive. No original primary/TRT campaign rerun and no sanitizer before the performance gate.

`check_source.py` is CPU-only: source/Git identities,20role selections,36transaction-accounting cases,128unique SF-row owners, and byte-identical storage/SF-copy/S2T-MMA/epilogue/teardown regions. [cpu-checks.json](cpu-checks.json) is the initial structural receipt. GPU results will be recorded separately; no result is implied by this initial document.
