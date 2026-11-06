# Whole-PR scope audit

Audited local HEAD `fa2a89203` plus the current ownership-refactor working tree
against `91bda04c66f7cb851e1ab3b78b9fecea644b9844`. This is both the local
merge-base and the live PR 5019 base reported by root. The initial diff had
43 files; after root's validator cleanup, 36 remain. `diff-files.txt` and
`diff-numstat.txt` record the full reviewed surface. Read-only audit; no primary
source changes, native compilation or GPU execution by this reviewer.

## Result

The unrelated cross-backend global-scale enforcement was the only production
runtime scope expansion found. Root has now removed it. The surviving shared
weight fields/layout helpers and autotune extraction directly serve W4A16 and
should remain. Further cleanup candidates are stale W4A16 documentation and
optional generic benchmark/profiler controls; they are listed separately below
so a scope reduction does not accidentally disable advertised MegaMoE modes.

## Removed by root; verified against base

The following files now have no diff against the PR base:

- `flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_bf16_bf16_cutedsl/weights.py`
- `flashinfer/moe_ep/backends/mega/kernel/sm100/fp8_fp4_bf16_deepgemm/weights.py`
- `flashinfer/moe_ep/backends/mega/kernel/sm100/mxfp8_mxfp8_bf16_cutedsl/weights.py`
- `flashinfer/moe_ep/backends/mega/kernel/sm120/mxfp8_mxfp8_bf16_cutedsl/weights.py`
- `flashinfer/moe_ep/modes/{mega_layer,split_layer}.py`
- `flashinfer/moe_ep/core/kernel/base.py`

The NVFP4 preprocessor retains only its shared byte-layout helper delta; its
validator call/import is gone. `validate_global_scale_support` and the W4A16
`supports_global_weight_scales` flag are gone. The two rejection-only test
families and the embedded rejection assertion in the W4A4/W4A16 shared-layout
test are also gone; existing-backend policy is no longer enforced by this PR.

## Additional actionable cleanup

Line numbers below refer to the current source; function/option names are the
stable hunk anchors.

| Priority | File / hunk | Action and reason |
| --- | --- | --- |
| Fix stale docs | `docs/design_docs/moe_ep_architecture.md:32`, W4A16 backend row | Include the existing `knobs="auto"` and cache behavior, or point at the common tuning section. The row currently lists only None/dictionaries. |
| Fix stale docs | Same file, W4A16 section at lines 72–87 | Correct or shorten the fixed M256/N128 description, fixed two-stage activation claim, and explicit statement that W4A16 has no cache/online tuner. Current code accepts the curated M128/M256 and N64/N128 geometries, tries three activation stages before two, uses the common capacity-keyed cache, and provides the eight-candidate graph-event tuner. These are stale feature descriptions rather than unrelated code. |
| Optional scope reduction | `benchmarks/bench_cute_dsl_moe_distributed.py:1988–2014`, `--nsys-cuda-trace`, `--nsys-capture-range-end`, `--ncu-metrics`; command construction at `_run_nsys_profiles:428` and `_run_ncu_profiles:565` | These generic profiler tuning controls are not required to add the W4A16 backend, shared-weight comparison, or default profiling modes. If minimizing upstream scope, keep them in the durable project profiling wrappers and retain benchmark defaults (`cuda`, `stop`, full metric set). Do not discard the existing saved reports/scripts. |
| Optional scope reduction | Same file, `_profile_torchrun_arguments:389–402` and its use in `_run_nsys_profiles` | Replaces the existing generic Nsight Systems `torchrun --standalone` launch with a free localhost port to work around container-hostname resolution. Useful environment hardening, but unrelated to precision support; it can be separated or restricted to the newly added coordinated MegaMoE NCU launcher. Keeping it is a deliberate benchmark scope choice, not a runtime necessity. |
| Optional scope reduction | Same file, `main`, new `--iters/--warmup` checks near 2068 and global-token positivity check at 2091–2092 | These newly reject arguments for all pre-existing split EP/TP variants. They are general CLI validation, not W4A16 functionality. For the narrowest change, retain old behavior for existing variants and validate positive capacity at the new MegaMoE branch. This audit does not claim zero-token split execution was validated. |

The larger new coordinated NCU implementation (`_run_ncu_profiles`,
`_ncu_application_replay_rendezvous`, associated CLI/help) is optional to the
backend itself, but it is directly related to safely profiling this mandatory
collective kernel. If removing that advertised feature wholesale, remove its
flags/help and explicitly prevent isolated-rank MegaMoE kernel replay. Removing
only its coordination, fresh-store epochs, or nonempty-rank constraint while
leaving the mode selectable would be incorrect. The same applies to required
CUPTI availability checks when retaining a no-fallback CUPTI timer.

## Shared changes to keep

| Surface | Dependency and scope assessment |
| --- | --- |
| `flashinfer/moe_ep/weights.py` optional `w13_global_scale` / `w2_global_scale` fields | Required to carry per-expert FP32 weight alphas into W4A16 without folding them into BF16 weights. Keyword-only defaults preserve old four-argument constructors. Corresponding unquantized `None` fields/constructor handling and dataclass tests preserve the shared pack contract; they are not cross-backend enforcement. |
| `.../sm100/nvfp4_nvfp4_bf16_cutedsl/weights.py::_interleave_gate_up_16` | The only surviving other-precision implementation delta. The W4A16 preprocessor imports this same layout helper. It performs one contiguous byte-preserving interleave and retains independent storage, including singleton/strided cases and byte-backed FP4/FP8 inputs. This aligns the intentionally shared NVFP4 weight layout. W4A4/W4A16 byte/storage-equality tests exercise that direct reuse. No other W4A4 compute/pipeline changes remain. |
| `shim/autotune.py:148–346`, shared sweep extraction | Direct dependency of W4A16 graph-event timing without duplicating collective candidate selection/cache callbacks. Existing NVFP4/MXFP8/BF16 wrappers still use the original synchronized wall-clock sampler, barriers, median scoring, rank-MAX winner selection, and score-and-continue behavior. The new fatal graph-error path applies to the W4A16 sampler. No existing dtype tactic/default changed. |
| `shim/tuner.py` | Adds only the fixed W4A16 profile and its dtype branch. Existing precision profiles remain unchanged. |
| `flashinfer/moe_ep/__init__.py` and drop/shim exports | Adds W4A16 config/preprocessing/frontend/tuning names only. No broad universal bridge or W4A4 core re-export remains from the abandoned standalone-package proposal. |
| `.pre-commit-config.yaml`, `pyproject.toml`, kernel-source README/VENDOR/SKILL | Necessary scoped ownership documentation and lint/type inclusion for the user-directed new `src/moe_nvfp4_w4a16` precision. Original vendor package exclusions and bytes remain intact; no generic new lint policy is introduced. |
| `benchmarks/...` shared weights, MegaMoE EP path, variants/mode filtering, refcheck, CUDA-graph/CUPTI timing | Directly supports the same-input/same-weight W4A16 comparison and full-forward measurement. Defaults retain the existing W4A4/W4A16 variants, event timing and EP/TP modes. The runtime/driver launch correlation union is needed to include CuTe-launched MegaMoE kernels in the advertised Nsight Systems breakdown. |
| Remaining five W4A16 test files | Cover the new backend/staging/numeric contract, global-alpha transport, byte-layout sharing, cache/tuning and scheduler/constructor behavior. The `test_other_dtype_cache_does_not_replace_w4a16_default` case validates W4A16 cache-key isolation; it does not impose a new policy on the other dtype. No unrelated existing test suite remains modified. |

All remaining owned kernel, scheduler, epilogue, workspace and CLC files are
inside the requested W4A16 precision package. The full diff adds no other
precision core, no changes to existing vendor source packages, no unrelated
configuration/backend aliases, and no new shared capability framework after
root's cleanup.
