# FC1 first16 numerical coverage on the e359 checkpoint

Local source and saved-evidence review, 2026-09-09. The existing five-job UInt16/h subset is a useful starting point, but FC1 also needs the retained M128 layout families and long-K/raw-ring cases. The recommendation below uses existing numerical definitions, tolerances and geometry observation. It adds no decoder probe, host framework, public knob or GPU run in this review.

## Exact change and evidence boundary

Source proposal `../w4a16_fc1_first16_predecode_20ae` has handoff `ef94e29841f26a9afbf21c5b4f7b158c7b037a00f5ea2a14e9687c795364b2c0`. Both source files in the frozen native control/candidate packages were checked byte for byte against its base/proposed files. Native package `../w4a16_fc1_first16_native_e359` has handoff `9680bfad30cb546d83038e5a5c9055dc82f4d4aecaba6514104ac9998605a712` and capture-plan SHA `9ed2092ca966ed28b90e704900e4bf48f3e643298c0f5facb367f98ddae87a60`.

The shared transform changes b473→eb7a and private Mega changes 2d53→a1e1; utility357 is unchanged. The private edit enables the existing compile-time predecode flag for FC1. FC1 still requests fragment128; FC2 still requests32. The shared helper accepts 32/64/128, copies only the first packed32 chunk before decoded-stage acquire, decodes its first16 values, then finishes the remaining first-fragment loads/decodes after acquire. No TMEM store moves before acquire. Raw advance/probe, store fence, raw release and decoded publication remain in their original order.

The source proof resolves the defaultFalse path to its original AST at 32/64/128 and preserves the FC2 true/32 specialization. This proves source structure, not DSL layout execution. The native reviewers confirm that the two actual M256/N128/C2 and M256/N64/C2 cohorts both instantiate FC1 fragment128; N64 is not evidence for fragment64. Their compile-only scheduling/resource findings are separate from GPU numerical validation. Neither this note nor the native gate claims candidate numerical success.

## What the existing focused tests cover

- `tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16` is exactly 14 cases: two in-place scale-update cases, six exact row/K scale-mapping cases and six routed-tile boundary cases. They execute the shared split transformer with its defaultFalse flag. They check that the generalized method still compiles and that loaded shared/decoder aliases point to the candidate, but do not exercise the new true FC1 branch. Mapping uses packed0x22 and positive normal E4M3 scales with exact equality; routed accuracy retains its original 97% band. No tolerance change is proposed.
- `test_w4a16_mega_reference_schedule` has two return-mode cases per EP size. Each creates four layers: ordinary H256/I256 numerics; H288/I448 with257 tokens; exact sparse scale/routing; and exact graph replay. It already covers balanced/skewed/single-token/empty-source/all-empty/refill sequences in a reused workspace, K tails, padded feature/token tiles, three stable graph replays and changed-input replay. This is meaningful phase/workspace reuse, not a missing test.
- That reference subset has at most two FC1 K256 tiles and previously forces only M256/C2. It does not provide a long FC1 raw-ring wrap, the M128/N64/C1 or M128/N64/C2 layout family, or a mostly padded H64/I64 feature tile.
- Retained `test_w4a16_mega_geometry` already supplies the needed cases: H64/I64/M257 for heavy padding, H1024/I512/M257 for four FC1 and two FC2 K256 tiles across multiple work tiles/phases, and H9472/I64/M257 for37 FC1 K tiles and repeated raw-ring wrapping. The latter alone scales fixture FC1 global weights by1/sqrt(H), after decoded-weight MMA. No kernel arithmetic is changed by that fixture.

Historical first16 EP2 observations show raw-stage counts5/5/4 for those three cases at M256/N128/C2, 5/5/5 at M256/N64/C2, and5/5/4 at both M128 families. Decoded stages are2 for N128 and3 for N64. These saved values explain why the cases are useful; the new candidate must record its own actual geometry/resources/stages. Historical results do not attest the candidate.

## Minimal recommended seven-job set

| Job | Geometry / EP | Existing selectors | Expected call rank-tests / compiled objects |
| --- | --- | --- | ---: |
| 1 | Split, EP1 | Entire W4A16 class,14 cases | 14 / no Mega objects |
| 2 | M256/N128/C2, EP1 | Both reference return modes | 2 /8 |
| 3 | M256/N64/C2, EP1 | Both reference return modes | 2 /8 |
| 4 | M256/N128/C2, EP2 | Both reference modes + the three geometry cases | 10 /22 |
| 5 | M256/N64/C2, EP2 | Same five cases | 10 /22 |
| 6 | M128/N64/C1, EP2 | Same five cases | 10 /22 |
| 7 | M128/N64/C2, EP2 | Same five cases | 10 /22 |

Totals are14 split call tests (42 setup/call/teardown reports) and44 Mega call rank-tests /104 actual compiled-object observations. A reference case creates four layers; a geometry case creates one. These are expected counts derived from the unchanged test definitions, not results. The existing four M256 reference jobs are retained; only their EP2 selectors expand, and two M128 EP2 jobs are added.

Use this exact split selector:

```text
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16
```

Use the exact two EP1 selectors for jobs2–3:

```text
tests/moe_ep/test_cutedsl_w4a16_mega.py::test_w4a16_mega_reference_schedule[ep1-epi_warps]
tests/moe_ep/test_cutedsl_w4a16_mega.py::test_w4a16_mega_reference_schedule[ep1-reuse_dispatch_warps]
```

Use the exact five EP2 selectors for jobs4–7:

```text
tests/moe_ep/test_cutedsl_w4a16_mega.py::test_w4a16_mega_reference_schedule[ep2-epi_warps]
tests/moe_ep/test_cutedsl_w4a16_mega.py::test_w4a16_mega_reference_schedule[ep2-reuse_dispatch_warps]
tests/moe_ep/test_cutedsl_w4a16_mega.py::test_w4a16_mega_geometry[ep2-h64_i64_m257]
tests/moe_ep/test_cutedsl_w4a16_mega.py::test_w4a16_mega_geometry[ep2-h1024_i512_m257]
tests/moe_ep/test_cutedsl_w4a16_mega.py::test_w4a16_mega_geometry[ep2-h9472_i64_m257]
```

Pass selector strings as separate argv values (quote brackets in a shell). Retain `-p geometry_c1_flag8_test_plugin640`, `--w4a16-test-tile m256n128|m256n64|m128n64`, `--w4a16-test-cluster 2|1`, and `--w4a16-geometry-record-dir OUTPUT/observed`. Only M128 permits C1. Keep `-m 'not gpu_2'` for EP1 and `-m gpu_2` for EP2. Retain the same selected Python and distributed launch at `--master-addr=127.0.0.1 --master-port=29587 --nproc_per_node=2`, existing source/native/predecessor guards, fresh candidate DSL/driver outputs and unchanged original oracles. Default geometry cases exercise injected flag8; explicit reference cases retain flag4 and both return modes.

## Existing runner origins and narrow admission changes

Reuse `../cuda132_recovery_0909a/scale_operand_u16/{run_validation640.py,geometry_c1_flag8_test_plugin640.py,reference_subset.py,split_provenance.py,resource_gate640.py}`. The original runner currently rejects M128 and declares only five scalar jobs; the candidate must admit only the new exact seven-job list. For EP1 reference-only output, the existing exact two-case subset validator fits unchanged. For mixed EP2 output, reuse the original geometry validator with `expected_tests=5`, require the exact five node IDs above, and retain the existing per-layer config/resource checks and original raw PRELAUNCH reconciliation. The reference validator's four-layer/both-return checks can be applied to only the reference records; do not feed mixed rows into its strict two-case parser or weaken its node-ID assertion. Keep one layer per geometry case and exact setup/call/teardown success. Source pin changes must reach actual nested shared/MRO ownership and split loaded aliases, not merely manifest labels.

No new host125, tuner/lifecycle/sampler rerun, complete16-tactic cohort, standalone resource-only job or unrelated dense tests are needed for this internal transform change. Existing graph/empty/refill coverage remains inside the reference cases. The H192/I320 case adds little beyond the retained H288/I448 tails plus H64 padding and is omitted from this focused set. M128 EP1 is not separately covered by this minimal matrix; its layouts are exercised at EP2 while M256 retains both EP sizes.

## Remaining boundary

The actual fragment is `min(coalesced leading extent, requested cap)` in shared `_setup_transform_partitions`; neither hidden size, N tile nor a routed-tile test ID proves that extent. The existing observer records geometry, stage depths and actual resource/MRO identity but not the true per-thread fragment extent. Thus even this set must not be described as explicit true-fragment32/64/128 numerical coverage without an actual specialization observation. The two current native cohorts prove128; true/32 remains the FC2 specialization with source-equivalent behavior; no actual true/64 native or numerical specialization has been established. A direct exhaustive16/32/64/128 decoder test would be a different scope and is not proposed here. Existing numerical oracles plus source/native checks are sufficient for the declared public-layout experiment, not an exhaustive bitwise proof for unreachable or unobserved specializations.

No production or frozen file was edited, and this review ran no GPU tests, native imports or remote command. Performance owns the runtime adaptation and all execution; the source-only package and compile-only native quality do not substitute for the new-source numerical results.

Source test hashes: public Mega `868d4d934621cabcdb04d0ba08bb154835237cb7829c1c201b2d072bae255011`; split `e3c912620f0e7e7e46bb1243d9668ddb46a3743ac8e0ca3643db038dc6f66fa9`. Reviewed runner `e7addf79b3614b4c22f3eb1c4c9f07923ae78ef737c9f51c1c132c235df6926a`, geometry plugin `9a645a181f683321d56df13e0c12b5156191693bfd05fee07c56ad2318a780b3`, reference subset `33455dd802c83e184dd564aef926ca8925e8814bac60c9d5e31c0a4a62cd6a34`, split observer `3c8a417d6c8470e537a979cfe13b937d667358b05c50cd89e85db03c8c2fc1a4`.
