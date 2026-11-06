# PR5019 upstream merge and interface audit — 2026-09-17

Scope: merge upstream `f17b77260919a55b2d18b109370c149a74f34065`, including BF16×MXFP8 PR4604, into PR5019 with a merge commit. Keep audit corrections separately reviewable. HashInfer is unchanged and no reviewer response is posted.

## Merge

`a22dfb739e8ac2f46b08e60e039e213286a96d62` has parents `4d183b836bb8ceefea2fcd723f078b3a4935e6b6` and upstream `f17b77260919a55b2d18b109370c149a74f34065`. The only textual conflict was in `shim/tuner.py`: preserve upstream's split per-dtype default pickers and its IKR permission behavior while retaining the W4A16 profile/dispatch branch. No squash, rebase or history rewrite.

## Audit corrections

- Import the relocated Torch fallback from `sm100/common/bf16_staging.py`. Its staging function is AST-identical to the previous fallback.
- Reuse the new BF16 forward validator and ignore `quantize_input` in the W4A16 backend, as BF16/BF16×MXFP8 do. Continue rejecting pre-quantized activation fields, wrong routing dtypes/devices and unsupported shapes. The shared layer still requires explicit warmup tensors when `quantize_input=False`.
- Include the dtype backend in SM100 package aggregation and correct the default-knob supported-kind message/docstring.
- Extend the existing graph-test product to both W4A16 activation flag values; update the existing invalid-copy case and activation documentation.

## Reviewer integration concern

Read https://github.com/flashinfer-ai/flashinfer/pull/5019#issuecomment-5723458348. Compute is BF16 operand MMA with FP32 accumulation. E2M1×E4M3 weights are decoded directly into operand TMEM, and global alpha scales the FP32 accumulator. Core scheduler policy, mainloop and epilogues remain independently owned. Reused vendor primitives are the generic scheduler ABI, communication, synchronization, metadata, workspace and layout helpers; the new BF16×MXFP8 kernel also reuses NVFP4-named scheduler/epilogue primitives.

The new common BF16 config base exposes fast_math, activation_clamp and IKR options that W4A16 intentionally does not support, so its narrow config remains independent. Packed NVFP4 layout helper reuse is appropriate because the byte contract is shared; no refactoring of W4A4 weights or vendored source is needed here. Deterministic reduction and the four-tactic policy remain unchanged.

## Validation boundaries

- Full PR source audit covers config/registration, weight layout/global scales, staging, validation, workspace/tuning/capture lifecycle, dependency exports, core pipeline ownership, tests, benchmark and docs.
- Scoped pre-commit (including mypy and Ruff), 37 changed Python AST parses, and full PR whitespace checks pass.
- All ten maintained MegaMoE files, split decoder file and BF16 staging kernel are byte-identical to `4d183b83` before the subsequent mechanical naming commit; recorded in `source-checks.json`.
- Vendored `src/`, shared autotuner, W4A4 weights, build config, pre-commit config and VENDOR record match current upstream exactly.
- The existing AST-isolated benchmark host harness passes all five orchestration checks, with its existing mocked profiler calls/SQLite fixtures. It does not execute profilers or GPUs.
- Native pytest collection was attempted for validation, weights and knob cache: two collection errors and one skip due to missing `tvm_ffi`; no native cases executed. See `pytest-host.log`.
- No GPU numerical tests, sanitizer runs or performance sweeps were rerun. Historical tables keep their original measured source/environment.

## Separate published commits

- Merge: `a22dfb739e8ac2f46b08e60e039e213286a96d62`.
- Interface audit: `0701a11a` (7 files, +35/−30).
- Naming: `4bc27889` (mechanical rename of the maintained package/API/frontend/cache key to `bf16_nvfp4`; no legacy aliases for unreleased names). Public config and registered backend already used the correct order and are unchanged. Device class names and benchmark W4A16 precision labels remain intact.

The naming-only check verifies 17 files against explicit substitutions (including test-mode strings), and 9 device/workspace/staging/shared-decoder files remain byte-identical. All 37 changed Python files parse. Final scoped hooks pass. The seven core files moved with 100% Git similarity; frontend, autotune and exports only rename host identifiers/cache strings. `check_naming.py`, `rename-map.json`, and `naming-checks.json` preserve the mechanical mapping.

The focused CPU harness passes 412 checks before naming and 415 afterward. It executes extracted source definitions with real Torch2.8 CPU tensors, patches Tensor.is_cuda only for accepted-CUDA metadata validation, and does not import FlashInfer or stub its dependencies. It covers both activation flags, rejected input formats/dtypes/metadata, copied BF16/route buffers and tails, all 14 unchanged default profiles, 336 unchanged other-dtype profiles, and cache key/bucket/IKR filtering. See `check_api_host_renamed_results.json` for source hashes and exact limits. These are not GPU or full-package import tests.

Old `w4a16` cache records are intentionally a miss for `bf16_nvfp4`, so callers use the same default profile or tune under the new key. No HashInfer changes, source updates to shared checkouts, GPU reruns, or reviewer replies were made. PR body wording was refreshed for current API names/behavior and validation scope; its complete Final performance section is byte-identical to the pre-push body.

Published head `4bc278892b3ced0a8c81501f858de517931e2ae9` is clean locally, non-draft, and GitHub reports `MERGEABLE` (no conflicts). All 9 working-tree source hashes from the 415-check run match the committed files. Full readback and CI snapshot are in `publication-check.json`.

Current-head GPU workflow summary is red because CI was skipped pending authorization (verified `ci-summary.log`, run35297863094, job105454060073); setup/GPU matrix jobs did not run. No authorization-triggering comment was posted.
