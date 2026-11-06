# FlashInfer CUB automatic top-k dispatch for short inputs

Follow-up to the completed SGLang W4A16 MegaMoE integration and GLM-5.2 serving
comparison in https://github.com/sgl-project/sglang/pull/39210.
The SGLang benchmark was published first and retains FI083 with an explicit
native radix override; it does not measure this later fix.

Published upstream draft: https://github.com/flashinfer-ai/flashinfer/pull/5185.
Verified open/draft at commit `62ff0a1751a537af89e5e2353ea1ca72954ba165`.
`PR_BODY.md` includes exact setup and commands plus all three complete raw
pytest logs; `artifacts/published-pr.json` and `pr-body-validation.json` retain
the publication check (58,188 characters / 58,209 bytes).

## Scope

- Independent FlashInfer clone: `flashinfer/`.
- Base: `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`.
- Branch: `fix/cub-topk-short-input-auto`.
- Automatic CUB dispatch currently accepts physical width 64 with k=2048,
  then its workspace query rejects `0 < top_k <= d`.
- Pass k through the shared eligibility gate so automatic selection retains
  the native padded short-row behavior. Keep explicit forced-CUB validation,
  eligible CUB dispatch and logical short-row handling unchanged.
- No C++ kernel, input-padding, workspace-size, or public API signature change.

## Validation

Fresh c2 devbox `ziangli/fi-cub-topk-short-0913`, explicitly requested with
`nvcr.io/nvidia/pytorch:26.05-py3`, the newest monthly PyTorch image with CUDA
13.2 according to the live NVIDIA release matrix checked before allocation.
The node allocated eight B300 GPUs; focused tests used GPU0 only on
`hu-pdx-10`. Image Torch was preserved and native top-k JIT was built from the
clean base source with CUDA 13.2.78 / SM103a.

`CUB_TOPK_FIX_PLAN.md` preserves the initial read-only audit and focused test
plan. `setup/` holds setup scripts, logs and source/image evidence.

Validated commit: `62ff0a1751a537af89e5e2353ea1ca72954ba165`.

- Baseline native setup smoke: 24 valid-input API/mode combinations passed;
  all 13 required exports verified.
- Parent Python dispatch plus new tests: 6 expected failures, each with
  `cub_topk requires 0 < top_k <= d, got top_k=2048, d=64`.
- Fixed dispatch: 21 regression tests passed (4.20 s pytest time).
- Existing related controls: 122 tests passed (4.42 s pytest time).
- No skipped tests or unexpected errors in these three phases. The full
  top-k suite was not run; scoped pre-commit checks passed.
- The native library stayed identical throughout all phases:
  `06b44eb1709cbe1a25706d267b29b1dc783b5bdfe21db65c0ff1780cafa1af21`.
  Final source was clean and there were no GPU compute processes.

`scripts/validate_fix.py` preserves the parent/patch procedure and assertions.
`artifacts/remote-final/` contains all 35 hash-verified remote evidence files,
including full test stdout, JUnit XML, per-phase source hashes, setup/build
proofs and the tested native binary. The 15,077,901-byte archive is
`artifacts/final-evidence.tar.gz`, SHA256
`a522bc957ff36d3f32bf1a369625599d2c2071aed0bf29cbd6f9fe845a057a99`.
`artifacts/local-final-verification.json` records verification. The separate
upstream PR will remain draft.

The task-owned C2 devbox was deleted after artifact retrieval and verification;
`setup/delete-devbox.log` records cleanup. No GPU resource remains allocated
for this follow-up.
