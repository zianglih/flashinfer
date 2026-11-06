# Prepared AUTO52 mixed static scheduling experiment

`auto52-mixed-static.patch` is **unapplied** against candidate3r with the current AUTO34 catalog. Apply only if the PC reports identify work-ID claim or mixed fallback handoff costs worth isolating. This patch changes only the candidate generator and its existing host catalog assertions. It selects the already supported `load_balance_mode="static"`; it does not change scheduling algorithms, kernel code, geometry, arithmetic, capability filtering, or cache handling.

| Session | Preserved uniform prefix | Preserved atomic mixed | Appended static mixed | Product total | Mixed-only benchmark total | IKR choices in product |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Default | 16 | 18 | 18 | 52 | 36 | 0 |
| IKR opt-in | 24 | 27 | 27 | 78 | 54 | 26 |

Every existing entry and its order remain exact. The appended suffix copies all current mixed choices in order, changing only `load_balance_mode`. That retains M256, N32/N64/N128, groups512/1024/256, both deterministic return modes, and dispatch-only IKR choices when the session opted in. Uniform candidates remain atomic. Filtering the opt-in catalog to deterministic choices reproduces the complete default catalog in order. No uniform4 candidates are introduced.

## Source basis and limits

The maintained [W4A16 scheduler](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py) already initializes static work IDs from `blockIdx.z` (line426) and advances by the logical persistent cluster count (lines654–667). Its static storage omits the atomic cluster-broadcast channel (lines328–350), and mixed registration is conditional on atomic mode (lines582–607). Both modes still use common tile mapping and scheduler publication (lines1120–1147).

This is the existing SM100 GenPhase pattern: [NonClcMixedCgaSchedulerWorker](../flashinfer/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/blackwell_genphase_sources/kernel_src/schedulers/non_clc_mixed_cga.py) assigns fallback channel halves from preferred-grid coordinates for `grid_stride` (lines208–222), seeds the work ID from `blockIdx.z`, and uses the logical preferred cluster count as stride (lines261–265). Its [work-ID helper](../flashinfer/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/blackwell_genphase_sources/kernel_src/schedulers/work_id_claim.py) performs integer ID advancement at lines295–300. This is grouped scheduling; the separate GenPhase `phase_interleave` policy requires atomic mode ([shim validation](../flashinfer/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/shim/block_scaled.py), lines309–312).

`force_static_sched=True` is a separate W4A16 2Dx3D record requirement ([kernel constructor](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py), lines169–172). It does not mean that the current AUTO choices use static work IDs: their `load_balance_mode` is atomic.

Static mode avoids atomic work claims and fallback-group handoff but sacrifices dynamic work redistribution. It does not remove common expert/tile mapping, FC readiness, scheduler publication, TMA, transform or MMA dependency waits. A PC sample at a consumer wait is not by itself evidence that work-ID claiming caused it. Uniform2 already occupies all148 SMs on this B300, so launch packing alone cannot establish a benefit. No performance improvement is claimed.

## Conditional measurement policy

All performance measurements remain native AUTO sweeps. The pristine baseline stays uniform AUTO16. If selected, the optimized project policy wrapper should expose mixed-only AUTO36 (18 atomic plus18 static); do not include the uniform product prefix in the optimized arm. Candidate3r mixed-only AUTO18 versus the same kernel with mixed-only AUTO36 isolates this candidate expansion, while the baseline remains the external control. Keep the same workload, routes, timing/cache policy and raw sample/winner receipts. This is a candidate-catalog experiment, not a fixed-tactic performance comparison.

The appended entries add compilation and tuning work. Keep the iteration grid bounded by the parent run plan, and retain this patch only if measurements support it. Full numerical and sanitizer qualification remains deferred until retained gains, as requested. The newly exposed IKR combinations need the separate [qualification plan](MIXED_IKR_QUALIFICATION_PLAN.md) before an unrestricted final PR claim.

## Validation and application

The [validation receipt](auto52-static-validation.json) records AST parsing, Ruff lint/format, exact forward/reverse application in a project-local temporary tree, and execution of the actual proposed catalog-contract function for both IKR settings using AST-isolated production candidate/validator functions. Prefix equality was separately checked against the live generator. Only the two intended function ASTs changed. This imports neither FlashInfer nor Torch; it is not a full package pytest run. Live source bytes, including the candidate3r kernel, remained unchanged. No GPU run, remote operation, or sync occurred.

Patch SHA256: `51b5bd28ae22154753f8c0f1fca0931d326ccf6f300770ac539c872ab78c42c9`.

Current kernel SHA256: `664a74fde4f0d60957a2ddb07839c95f393d477f7ee84d5ce4415bb56bf4d939`.

| File | Base SHA256 | Proposed SHA256 |
| --- | --- | --- |
| `autotune.py` | `feea41a6bd666ff0b92c77cdd507645354d82589f577e32ba6677a8fe5ed168e` | `3b14d47a8f7b45e0a022fe5d36915492da5093a1be8f008e350ffcd34534d6a6` |
| `test_w4a16_mixed_cluster_config.py` | `822fc7dc03e15f88f52c7a3371c08186358206f306fe40ba9002184e7a5dfc41` | `054b4e2110d4dcb77bebd309c118edfd10153f08f632c779576a2539d41acdc6` |

After the parent selects this experiment and releases the active checkout:

```bash
cd /Users/ziangli/playground/projects/flashinfer-w4a16-mixed-clusters/flashinfer
git apply --check ../experiments/auto52-mixed-static.patch
git apply ../experiments/auto52-mixed-static.patch
```

The raw-weight lookahead patch does not overlap these files. If either catalog file changes first, recheck its base hash and regenerate or revalidate the patch; do not silently discard changed context.

## Selected bounded follow-up after the full13 capture

The coordinating agent selected one final trial at **GLM5 EP8 T64/T128/T4096**, comparing a fresh pristine-main **AUTO16/all** arm with **mixed-only AUTO36**. The PC-based application condition at the start of this note was **not met**: the profiles did not establish work-ID claiming or fallback handoff as the dominant cost. Preserve that original preparation condition as history. This later decision authorizes a bounded test of an established scheduling mode because its source demonstrably removes those operations, not because the profiles proved a performance cause. Earlier T128 improvement did not repeat in the ongoing full-grid capture, and the isolated T64 improvement remains provisional. Neither observation establishes a retained mixed-cluster gain.

Wait for the complete candidate3r full13 capture, frozen source/measurement receipts, and the coordinating agent's explicit idle/lock handoff before applying or syncing anything. The committed full13 implementation remains `3d047d3f8e7923118ffea8b8d36151504ab1fa3d`; the static experiment must receive its own source manifest and commit/diff identity. Do not relabel its results as unchanged candidate3r or combine its samples with the full13 capture. This note records a decision and release plan, not an application or launch.

The selected policy adds only existing static-mode copies: default product **52**, optimized **36 = 18 atomic + 18 static**. IKR remains disabled for this screen. Its preserved opt-in catalog would be product78/mixed54 and still needs the separate qualification plan. Tile shapes, groups, return modes, arithmetic, runtime, native AUTO scoring, inputs, seeds, timer, three explicit warmups, and 100 untrimmed cold-L2 rank-MAX CUPTI samples remain unchanged. Use the same native driver and project policy wrapper, fresh serialized EP8 process groups, `FLASHINFER_MOE_EP_KNOB_CACHE=0`, and `separate-flashinfer-workspace-v1` for both arms: distinct FlashInfer workspaces with shared CuTe DSL/CUDA/Triton cache roots. Freeze helper hashes again. The fresh AUTO16 control determines whether this expanded policy is useful; an AUTO36 atomic winner does not support the static-mode hypothesis. An AUTO18-versus-AUTO36 repeat would be needed for a contemporaneous causal comparison of the candidate expansion itself, and is not an additional run authorized by this note.

Doubling the candidate count from18 to36 adds AUTO compilation and tuning work outside the measured forward. Static assignment also gives up dynamic redistribution when expert work or CTA progress is uneven. This is the final bounded scheduler-mode trial, not a reason to add further axes. Broader numerical and sanitizer qualification stays deferred until retained gains; native AUTO compilation and liveness are the iteration gate.

### Exact removed operations and retained correctness boundaries

- Static storage omits the work-ID broadcast channel ([scheduler](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py), lines328–350); work-ID state construction, fallback registration and atomic claims are atomic-mode-only (lines493–538,582–607,1134–1146). Static kernel initialization waits for dispatch metadata before decoding (kernel lines1381–1385,1423–1433). Local work-counter/registration/token storage is atomic-only (kernel lines1993–2015). Independent token-return scheduling and completion counters remain; static does not remove every atomic or synchronization operation.
- The supported launch grid is `(4,1,Z)`. Static uses `blockIdx.z + q*Z` and retains global `blockIdx.x % 4` channel coordinates (scheduler lines373–395,426,654–667). Two fallback clusters at x0/1 and x2/3 therefore execute disjoint halves of the same logical tile without pairing by registration order, even when their physical GPC placement differs. Runtime cluster-local dimensions still select the active TMA/pipeline geometry (kernel lines1273–1281). This assumes the existing preferred4/fallback2 launch contract; it does not establish other cluster shapes or heterogeneous EP partitions.
- Both modes retain the same monotonic FC1/FC2 tile decoder (scheduler lines943–1089), readiness peeks ([extension](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/custom_ext.py), lines239–295), and FC2 wait for the CTA-count threshold (kernel lines1282–1284,1553–1565). Padded channel CTAs continue participating; the existing [epilogue](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py) clips output channels at lines248–261 and suppresses out-of-bound FC1 completion contributions at lines406–429. No new static-specific defect was found in this read-only review. This source check is not a proof of all runtime synchronization cases.
- Historical [unit-v1 output](../evidence/remote/unit-v1/run.log), lines30/42, exercised static scheduler records with actual33 preferred4 plus8 fallback2 clusters, including partial channels and empty/ragged counts. Its25-pass total includes host and scheduler cases; it is not current full-kernel numerical, graph, or sanitizer qualification. Retained static winners still require existing reference tests for both return modes, tails, empty/refill experts, and graph replay, with the established synchronized first-use/runtime-owner safeguard.

### Pending source release and host validation

The following steps are for the coordinating agent after the idle handoff. They have **not** been run against an applied live static candidate. Before application, verify the base hashes in the table above and record a clean source status. After application, verify the two proposed hashes, the unchanged kernel hash, and exactly the two expected changed paths. Preserve the full13 source receipt separately.

```bash
cd /Users/ziangli/playground/projects/flashinfer-w4a16-mixed-clusters/flashinfer
git status --porcelain=v1
shasum -a 256 ../experiments/auto52-mixed-static.patch \
  flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py \
  tests/moe_ep/test_w4a16_mixed_cluster_config.py \
  flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py
git apply --check ../experiments/auto52-mixed-static.patch
git apply ../experiments/auto52-mixed-static.patch
git diff --name-only
git diff --check
python3 -c 'import ast,pathlib; [ast.parse(pathlib.Path(p).read_text()) for p in ("flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py", "tests/moe_ep/test_w4a16_mixed_cluster_config.py")]'
ruff check flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py \
  tests/moe_ep/test_w4a16_mixed_cluster_config.py
ruff format --check flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py \
  tests/moe_ep/test_w4a16_mixed_cluster_config.py
```

Run the existing package-level host checks in the pinned runtime, under the normal coordinated test lock, and preserve full output/exit status and source-before/after receipts:

```bash
python3 -m pytest -q tests/moe_ep/test_w4a16_mixed_cluster_config.py \
  tests/moe_ep/test_mega_workspace_knobs.py
```

The prior134-pass result belongs to candidate3r, not the proposed catalog. The prepared AST-isolated contract check is recorded above and must not be presented as this package-level pytest run. The final manifest must include the applied source diff/commit, all source/helper hashes, policy receipts showing available52/selected36 on candidate and16/16 on baseline, plus every rank's winner including `load_balance_mode`.

Release-note scope: **Experimental AUTO catalog extension exposing the existing static mixed4+2 scheduler alongside atomic choices. Kernel and arithmetic source are unchanged; capability filtering and IKR permission remain intact. No speedup or full-kernel static qualification is established by preparation or host checks.**

## Released experiment freeze

After the full13 pair completed with both capture audits/exit statuses passing, Rubin reported the idle/lock handoff at23:14:47UTC. Root then applied the exact prepared patch, passed scoped pre-commit on its two files and `git diff --check`, and committed the experiment as **`f14e4bae9379703fd5693d8ee993faae23e130d5`**, direct parent candidate3r, on `experiment/w4a16-mixed-static-auto36`. The [freeze receipt](../evidence/candidate4s-commit-freeze.json) records a clean checkout, the exact patch hash, source hashes and local transfer-bundle hash. Independent local read-only checks confirmed that commit/parent, clean status, both proposed catalog/test hashes and the unchanged kernel hash. The preparation/application instructions above are retained as history; do not apply the patch a second time.

Root authorized Rubin to sync this frozen experiment and run the selected three-point pair. This update does not claim that sync, host pytest, AUTO compilation or GPU measurements have completed. Preserve their eventual receipts separately from the completed candidate3r full13 capture and the historical134-pass host result.
