# Small-N independent weight producer

Experimental and unstaged. The first two extra-warp variants are **closed, unretained**. The zero-extra-warp follow-up is also **neutral and unretained as a standalone change**; its frozen source is available for the separately owned SF-publication composition. Base `98fd3566b5f945c100f48cddacf25deb2432cbc2`; initial actual local source copy `../../flashinfer-producer-roles-review`. Only the blockscaled SM100 core changes. Production, preparation, APIs, and MegaMoE remain untouched. [manifest.json](manifest.json) pins source and patch hashes.

## Mechanism and prior boundary

At small N, the existing four producer warps collectively copy all 128 physical SF rows, including zero-fill. Warp0 also issues A/SFA and B TMA after waiting for the SF ring. The experiment moves weight A/SFA into a new warp9 with an independently advancing pipeline state. Existing warps0–3 retain B/SFB work, epi warps4–7 and MMA warp8 keep their roles. CTA size is320 instead of288, gated by `cta_group_size == 1 && !tma_sfb && overlap_epilogue`; other geometries retain their organization.

A/SFA uses `a_barriers`; B payload gets its own TMA ring using `relay_barriers`, which are inactive in group1. The active 128-participant SF cp.async ring remains untouched. This introduces no additional shared operand stage, TMEM column, barrier storage, allocation, cache-policy change, or alignment requirement. Each TMA ring expects one elected producer arrival. For native NVFP4 K512/N16: A/SFA expects36,864B, B8,192B, and the existing cp.async pipeline owns4,096B SFB. MMA waits A, B, and SF before the original S2T/MMA sequence, then releases each only after MMA. Each producer drains its own cloned state; whole-CTA retrieval/teardown barriers follow320 threads while the128-thread TMEM deallocation protocol remains unchanged.

This is distinct from two rejected experiments:

- [Prior independent rings](../regular_tma_pipeline_experiment/README.md) only enabled prepared FC1 N128/N256 with TMA SFB. Small-N was unchanged numerical control; no small-N performance experiment occurred. Large-N results were neutral or slower.
- [Prior dedicated weight warp](../dedicated_weight_tma_experiment/README.md) used442 Gather4 N128/NB2 and a shared TMA completion ring. Results did not establish repeatable whole-chain gains. This experiment tests regular B TMA plus independent weight advancement on decode.

The tradeoff is an extra warp and an extra completion release per stage. Existing decode profiles show mostly near-single-pass cold weight traffic; increased producer issue overlap cannot be assumed to improve bandwidth or final latency. Static source validation is not performance evidence.

## Bounded screen

Assigned GPU4 on replacement C1 `fi-w4a4-narrow-1025`, nodeB200-92, UUID `GPU-9b1e25f5-48e6-f126-6d93-160b7ea7dd32`. Image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.78, CuTeDSL4.7.1, CUPTI13.4.0. Parent environment receipt: [environment.json](../../evidence/narrow-pipeline-environment/environment.json). All remote shells source `scripts/recovery442/env_candidate.sh`; native epoch remains candidate442, CuTe cache is private to this experiment.

Completed for both variants: timeout-bounded native T32 exact smoke, then fixedN16 T32/T128 same-input ABA/BAB full chain and FC1/FC2 phase diagnostics,10warmups/100cold-L2 CUDA-graph/CUPTI samples per arm. Actual native benchmark inputs, unchanged regular preparation and unfused finalization. Explicit output initialization checks full phase bytes/SF before and after timing; full chain checks final bytes and input hashes. Full-chain sort reruns normally and may change within-expert permutation; isolated phases retain their captured metadata. FC1 phase includes preparation; isolated phases are not additive. No original primary/TRT campaign rerun or sanitizer.

`check_source.py` is CPU-only: source/Git identities,20role selections,36transaction-accounting cases,128unique SF-row owners, and byte-identical storage/SF-copy/S2T-MMA/epilogue/teardown regions. [cpu-checks.json](cpu-checks.json) is the initial structural receipt.

## Completed extra-warp variants

The initial independent A/B rings regressed; the refinement retained distinct full barriers but shared their empty barrier because both operand payloads have the same post-MMA lifetime. Both producers independently wait that phase, and only A's consumer release publishes it once. SF cp.async ownership/publication stayed separate and unchanged. Refinement source lives in `../../flashinfer-producer-roles-shared-empty-review`, pinned by [shared_empty/manifest.json](shared_empty/manifest.json). Its fresh source/patch epoch preserves the initial clone and all evidence.

|Variant|Full-chain T32 control/candidate|Full-chain T128 control/candidate|FC1 T32/T128|FC2 T32/T128|
|---|---:|---:|---|---|
|Separate empty barriers|0.981853×|0.983633×|0.994320× /0.993333×|0.972831× /0.970852×|
|Shared empty barrier|0.982274×|0.980920×|0.996700× /0.992335×|0.973263× /0.970760×|

[RESULTS.md](RESULTS.md) contains **every arm median**, and [summary.json](summary.json) pins the receipts. All6 successful processes passed final-output and initialized FC1/FC2 byte checks;12 paired phase checks and72 arms/7,200 samples verify. Candidate gates also include other dtypes/per-token/N32/N64 geometries that were not exercised; no broader correctness claim or retention is made.

|Resource|Control|Both extra-warp variants|
|---|---:|---:|
|CTA threads|288|320|
|FC1 registers/thread|64|74|
|FC2 registers/thread|90|86|
|Reported static shared bytes|1024|1024|
|Stack/local bytes|0/0|0/0|

Operand dynamic storage and TMEM allocations remain source-identical; no new occupancy profiling was performed. In all captured binaries, shared-empty removes one static UTCBAR site (4→3) while8UTCOMMA sites remain. It does not recover performance. This rejects the extra notification as the sole explanation; it does not establish extra warp count or register pressure as the cause. The subsequently assigned zero-extra-warp experiment is a separate hypothesis.

The first smoke helper rejected the control's documented untracked `flashinfer/data` link before Torch/CUDA import. `history/r1-data-guard` and its failed receipt preserve that attempt. The corrected helper permits only that project-owned symlink and checks its target; no kernel repair was required. No failed GPU execution occurred.

Immutable raw archives, including source/helpers, command/environment receipts, samples, PTX/CUBIN/SASS and resource dumps:

- [Initial](../../evidence/producer-roles-98fd-initial/raw.tar.gz):2,033,761B, SHA256 `da86af1989cf39712d1135b29d080dc0a6cdd581503df951714212d351ce22b4`.
- [Shared-empty](../../evidence/producer-roles-98fd-shared-empty/raw.tar.gz):2,068,263B, SHA256 `a7debc5f2fc2c1166fdfe165aaefd93791a7c82cc937cbf4e7ff497104bd97b2`.

`python3 scripts/producer_roles_experiment/summarize.py` regenerates the CPU-verified summary/full median table. Both archives' final GPU process queries were empty. GPU4 was released after these screens and separately reassigned for the follow-up.

## Three existing TMA issuer warps

The follow-up keeps288threads and assigns existing producer warps0/1/2 to A/SFA/B TMA. All128 producer threads retain their original SFB cp.async work. Each issuer independently waits the shared empty phase, then uses the installed DSL4.7.1 public `arrive_and_expect_tx` helper to announce its own transaction bytes before issuing its transfer. The full barrier expects3 elected arrivals. This prevents early phase completion before a later issuer announces, without a producer synchronization. The existing MMA wait and post-MMA empty release remain singular; one warp0 empty-only tail drains the joint ring. No operand stages, TMEM allocation, SF publication, math, or public API changes. [PIPELINE_AUDIT.md](distributed_tma/PIPELINE_AUDIT.md) and [receipt.json](distributed_tma/receipt.json) preserve the installed API excerpts, source hashes, and independent tail review.

Actual source: `../../flashinfer-producer-distributed-tma-review`; core SHA256 `e2c7089c2fe266a7ec12bd303e7b5602c9e0bfb97bd5d9af9a5724c7a69dcbf6`. The [manifest](distributed_tma/manifest.json) records its pre-execution CPU snapshot; its `gpu_execution:false` field describes that creation step. The completed GPU receipts are in [summary.json](distributed_tma/summary.json).

|Tokens|Full-chain control/candidate|FC1 including preparation|FC2|
|---|---:|---:|---:|
|32|0.996535×|0.999440×|1.000896×|
|128|0.999591×|0.996163×|1.000670×|

[All arm medians](distributed_tma/RESULTS.md):3 successful processes,6 paired phase byte checks,36 timed arms and3,600 retained samples. Same native NVFP4 per-tensor fixedN16 methodology and limitations as above. All pre/post final-output, initialized phase-output/SF bytes, source and input hashes passed. No new failed GPU execution, primary campaign, sanitizer, or wider dtype/per-token/N32/N64 coverage. Neither the neutral full-chain result nor these isolated nonadditive phases demonstrate a standalone speed improvement.

[Codegen receipt](distributed_tma/codegen-summary.json) verifies all12 binaries:288threads, FC1 64registers/thread, FC2 90registers/thread, static shared1024B, and zero local/stack bytes for both arms. Operand dynamic storage is unchanged in source. PTX confirms full-barrier initialization with3 arrivals and `mbarrier.arrive.expect_tx` before each issuing warp's TMA. Static instruction-site counts are not executed instruction counts. The parent's separate NCU comparison of the earlier shared-empty variant found higher executed instruction work with unchanged traffic; a lower per-issue MIO ratio alone is not causal evidence because its denominator also changed.

Immutable [raw archive](../../evidence/producer-roles-98fd-distributed-tma/raw.tar.gz):2,015,360B, SHA256 `e5f84029b5da63c8e290bd8a435902e2321dae4713da1c9600955bfd5bf918cb`. It includes actual sources, commands/environment, all samples, PTX/CUBIN/SASS and resources. `python3 scripts/producer_roles_experiment/summarize_distributed_tma.py` regenerates the verified result table. The final query confirms GPU4 has no active process. All three source copies remain unstaged and production is unchanged.

For the separately owned SF-publication composition, split the current full barrier into A+B payload readiness with2 arrivals and SFA readiness with1. Each issuer still announces before its own transfer. Keep SF-source lifetime and drain independent from payload when publication releases SF early; the current joint-tail proof applies only to operands whose final release remains shared. This is a design handoff, not measured evidence for that composition.
