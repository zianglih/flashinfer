# Retained: capacity-derived stages plus exact routing counts

The formatted guard candidate is retained in kernel/helper commit `1a33d30c9` and final production/review HEAD `fca8462cbd9096059d0019a206aa760fb34ca8c4` (the latter removes unused table-printing arguments). All five retained source hashes match the focused49-test and paired-benchmark candidate exactly. The K-tail variant is rejected. All four experiment copies remain separate and unstaged; the historical r2 evidence below is preserved.

- Review source: [formatted guard source](../../flashinfer-stage-capacity-ghost-formatted-review/).
- Final candidate full patch: `aafc4ffd2d74e502bc6eb1f000837a04d9f0e044b4efbba483cd68bac70813d6` on HEAD `63d5fa0ea1c60e49242970e7721f0581e41c267a`, including the unchanged V3/V4.1 benchmark overlay.
- Production scope is five files: the three stage-policy files, `_inputs_helper.py`, and six parameterized count assertions in the existing `TestInputsHelperContract` class. No new test file. The benchmark overlay is already independently managed.
- Exact five-file source pins, patch, and pre-commit command/log binding: [source-handoff.json](../../evidence/stage-ghost-formatted-final-gate/source-handoff.json).
- Formatting: all scoped pre-commit hooks passed, including mypy, Ruff checks, and Ruff format. Only common-core formatting changed; ASTs for all six experiment files match the pre-format copy. The helper and test bytes did not change.
- Helper correction: skip experts requesting zero assignments before selecting tokens. Prior code created spurious expert assignments until token slots filled. The change preserves all positive-count profiles byte-for-byte; the existing approx-max-load contract and separate upstream prioritization issue remain intact. W4A16 uses a different initializer.
- CPU counts: twelve requested-count cases, twelve all-zero cases, and twelve determinism checks passed, including V3/V4.1 small-token profiles and nonzero local expert offsets. The complete nine-test helper class also passed remotely before benchmarking.
- Final focused GPU5 gate: **49 passed, 46 warnings in 9.67s**, zero failures/errors/skips: existing43 cases plus the six new count-conservation cases. Exact command, raw pytest output, JUnit count, and all83 source pins verified before/after are kept in [final gate evidence](../../evidence/stage-ghost-formatted-final-gate/). Broad tests/sanitizers remain deferred.

## Final retention evidence

The two paired model campaigns used native C1/A1/A2/C2 medians, identical routes, and the full token grid; tokens1/2 remain reported but excluded from retention aggregates. Ratios are direct control/candidate comparisons, not chained with historical whole-PR speedups.

| Workload | NVFP4 overall | MXFP8 overall | MXFP4×MXFP8 overall |
|---|---:|---:|---:|
| V3 EP8 | 1.003002× | 0.997231× | 1.018390× |
| V4.1 Flash EP4 | 1.010991× | 1.009835× | 1.031032× |

[Complete V3 paired evidence](../../evidence/pr7290-v3-stage-ghost-r1-a2/independent-paired.md); [complete V4.1 paired evidence](../../evidence/pr7290-v41-stage-ghost-r1-a2/independent-paired.md). Mixed-precision decode improves2.43%/3.54%; V4.1 NV T16 improves11.74%. This is not a universal per-cell gain: V3 MXFP8 decode is0.993091× and V3 mixed T16384 is0.970501×. Keep the complete tables and those boundaries visible.

Final six-file pre-commit on production passed every applicable hook without edits. Production/review are clean and identical at `fca8462cbd9096059d0019a206aa760fb34ca8c4`. [Final check receipt](../../evidence/stage-ghost-retained-final-check/receipt.json) binds all six file hashes, exact command, raw log, and the tested five-file handoff. The [source inventory](../../evidence/narrow-pipeline-source-inventory.json) records production/review and all four stage experiment copies.

Remaining boundaries: this focused numerical/compile gate ran on B200 SM100, not a broad dtype/shape or sanitizer matrix; the180-policy audit checks actual layouts/capacity, not180 numerical executions. The separate final four native comparison tables are being collected on the final commit; a stable all-shape decode win over TRT-LLM is not established. Per-token and fused-finalize performance are outside this paired campaign, and Rubin is unchanged.

## Rejected FC2 K-tail variant

[Separate review source](../../flashinfer-stage-capacity-ktail-review/) and [experiment notes](../../evidence/stage-ktail-r1/NOTES.md). The compile-time divisibility selector changed only nine V4.1 FP4×FP4 FC2 policies: K512 to K256 on narrow M128 tiles. All180 per-source actual shared layouts fit capacity; cache priorities, bulk TMA policy, all FC1, all MX, and all V3 geometry remained unchanged. Fixed actual-route C/A/A/C pairs nevertheless regressed: T8=0.9891×, T16=0.9909×, T512=0.9826×, while unchanged N128T64=1.0009×. Do not include the K selector or cache-condition edits in the retained source. GPUs5/7 were released after these measurements.

---

# SM100 stage-capacity experiment — frozen candidate r2

This is a local, unstaged optimization experiment, not a retained performance claim.

- Base: `63d5fa0ea1c60e49242970e7721f0581e41c267a`.
- Local source: `flashinfer-stage-capacity-review/`.
- Remote source: `/workspace/flashinfer-w4a4-split-dynamic-n/stage-capacity-r2`.
- Patch: `evidence/stage-capacity-r2/candidate.patch`.
- Patch SHA256: `8d737d533a6ca9ac7988fe9179b9580433528d7a32b55e22a2f98187e41b64e1`.
- Source pins, exact commands, environment, and timestamps: `evidence/stage-capacity-r2/validation.json`.
- Hardware: GPU 5 NVIDIA B200, UUID `GPU-a4c14cdc-d487-e8b3-9e76-1fdbbb5e1a21` on C1 devbox `fi-w4a4-narrow-1025`; image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe 4.7.1.

## Change

Replace FC1/FC2 wrapper-specific 3/4/5-stage lookup tables with compile-time storage sizing in the common SM100 kernel. The existing public MMA tactics, K4/K8 selection, producer organization, accumulator overlap, and Rubin path remain unchanged. The explicit `num_stages` input still supports controlled experiments; `None` requests automatic sizing. `requested_num_stages` remains immutable across recompilation, so reusing a kernel object with another static reduction size recomputes the policy correctly.

1. Build real one-stage A/B/SFA/SFB CuTe layouts, including paired channel tiles and mixed-FP4 weight unpacking, then sum their allocation bytes.
2. Reserve supported epilogue storage before maximizing operand depth. For eligible output-scatter paths, prefer the existing 64-token/two-stage bulk TMA slab, falling back to the existing 32-token/one-stage slab only when necessary. Other paths reserve 128 FP32 scratch elements.
3. Choose the largest depth satisfying `depth * operand_stage_bytes + aligned_metadata(depth) + epilogue_reserve <= SM100_capacity`. Metadata includes four operand barrier words per stage, two accumulator barrier words per accumulator stage, the TMEM handle, and both 128-byte alignment gaps.
4. Cap depth by `ceil(K / tileK)` only when `overlap_epilogue=False`: that producer performs its own epilogue before advancing the persistent scheduler. Dedicated epilogue warps allow cross-tile prefetch, so that path deliberately has no single-expert reduction-tile cap.
5. Build final operand layouts, select the supported bulk epilogue slab, then assert the real nested `SharedStorage.size_in_bytes()` fits. All policy computation occurs at compile time.

The SM100 capacity comes from the existing CUTLASS architecture helper: `utils.get_smem_capacity_in_bytes("sm_100")`. The actual queried value here is 232,448 bytes. Rubin already owns a separate architecture-derived stage policy and different operand/TMEM/epilogue layouts; this experiment does not reuse SM100 assumptions there.

## Actual-layout audit

The helper `scripts/stage_capacity_experiment/kernel_layout_audit.py` enumerates 6 dtype/scale contracts × 15 FC1/FC2 policies × 2 model shapes = 180 policies. It extracts the exact decorated `SharedStorage` definition from the candidate source and asks CuTe for `size_in_bytes()`, rather than relying only on a copied arithmetic estimate.

- V3: H7168/I2048. V4.1 Flash: H5120/I2304.
- 180/180 policies fit actual SMEM, all stages≥1, zero bulk TMA regressions.
- Automatic stage range: 3–7. Maximum actual storage: 230,272 bytes, leaving at least 2,176 bytes below 232,448 bytes capacity.
- 100/180 policies change operand depth. The model shapes produce the same policy choices here; their reduction lengths do not reach the non-overlap cap. The helper separately recompiles each object with K=tileK and back to the model K to verify cap behavior and requested-knob preservation.
- 12/180 policies upgrade output bulk storage from (32 tokens, 1 stage) to (64 tokens, 2 stages): FC2 M128/N256 for every dtype on both model shapes. Their operand depth changes 4→3 to reserve that larger working epilogue buffer. These are deliberate policy changes requiring timing evidence.

| Dtype / scale contract | FC1 changed /16 | FC2 changed /14 | New depth range |
|---|---:|---:|---:|
| fp4_sf16_e4 | 6 | 4 | 3–6 |
| fp4_sf16_e8 | 6 | 4 | 3–6 |
| fp4_sf32_e8 | 12 | 8 | 3–7 |
| e4_sf32_e8 | 12 | 8 | 3–7 |
| e5_sf32_e8 | 12 | 8 | 3–7 |
| e4_fp4_sf32_e8 | 12 | 8 | 3–7 |

Across all 180 policies, transitions are 4→4: 44, 4→6: 12, 3→4: 24, 5→5: 36, 4→3: 12, 5→6: 12, 4→5: 32, 5→7: 8. Full per-policy dimensions and actual allocations are preserved in `evidence/stage-capacity-r2/layout-audit.json`.

## Focused GPU compile/numerical gate

The same established 41 cleanup nodes plus the two existing W4A4 `test_swiglu_limit_accuracy` cases (limits 0.05 and 0.1) passed:

```text
43 passed, 46 warnings in 11.39s
```

Exact command and raw output are in `evidence/stage-capacity-r2/validation.json` and `pytest.log`. This checks existing tail, padding, per-token, clamp, determinism, PDL-forwarding, and implementation-admissibility coverage. The 180-policy pass is a real-layout compilation audit, not 180 full numerical kernel tests. Broad correctness/sanitizer coverage remains deferred per the requested iteration workflow.

The failed first attempt is retained under `evidence/stage-capacity-r1/`: its storage audit passed, but the new actual-size guard lacked `cutlass.const_expr` inside `@cute.jit`, so preprocessing rejected 12 kernel tests (31 non-kernel cases passed). The only kernel change between r1 and r2 wraps that guard in `cutlass.const_expr`. No r1 results count as passing correctness evidence.

## Retention boundary and future tactics

No performance retention decision has been made. Run the same frozen V3/V4.1 benchmark harness against control and this candidate before adopting it. This experiment expands buffer depth only; it adds no autotune choices. K4/K8, physical N allocation, CTA grouping, accumulator-window ownership, and the supported bulk/TMEM slabs remain direct existing geometry choices. Exploring those as explicit tactics is possible later, but combining them now would confound the capacity-policy comparison.

## Frozen source SHA256

```json
{
  "flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py": "9b75063e19b70890f6bbec5ba97998de8147896a7f46832f20693d6bef928a58",
  "flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py": "8e5181ec51a77be8ebfb2f02ca76b47463b982558ce96a8e7fd02faa4aed5ab6",
  "flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_grouped_gemm_finalize_fusion.py": "2dd1a9ef4a00b418a4cf151ee01f8e3a6c8c76c5946e2559a4be76076f9ca238"
}
```
