# Interface refactor and separate test/documentation cleanup — 2026-09-14

Public draft: https://github.com/flashinfer-ai/flashinfer/pull/5019

## Commits

- `b83cbedbcb0198eda9ebe7658f4827c3488e6490`: common global-weight-scale capability validation, W4A16 capture/lifecycle guards, shared partial-knob normalization, independent unchanged default profile, environment-selected staging fallback.
- `2c451c733e8b917431e0d97150ab7ede85da26ee`: separate test/documentation audit. The four reviewed test files expand to 82 cases, down from 87; test LOC increases by three while covering the interface fixes. Numerical references and tolerances are unchanged.
- `7f1a093119f12b1f5b79d50bf6d0c951069224e5`: documentation-only follow-up removes the standalone W4A16 architecture walkthrough. Preserve only global-scale and combine precision exceptions in existing sections, the backend registration row, and a shared BF16 input-copy clarification. Net 79 lines removed.

Implementation, test and documentation commit hooks passed. See `source-checks.json`, `test-cleanup-source.json`, `TEST_CLEANUP_AUDIT.md` and `GLOBAL_SCALE_REVIEW.md` for source/audit details. The preceding unresolved-findings snapshot is `../interface-audit-20260914/`.

## Fresh GPU validation

C2 devbox `fi-w4a16-interface-0914`, node `hu-pdx-15`, 8 B300 allocated; only GPU 0 used. Image `nvcr.io/nvidia/pytorch:26.05-py3`; driver 590.48.01; nvcc 13.2.78; Python 3.12.3; PyTorch `2.12.0a0+5aff3928d8.nv26.05`; CuTe DSL 4.7.1; TVM-FFI 0.1.13.post3; pytest 9.1.1; nvshmem4py-cu13 0.3.1; nccl4py 0.5.0.

The live [NGC catalog](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch) and NVIDIA release notes were checked before allocation: [26.05](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html) provides CUDA 13.2.1; subsequent 26.06–26.08 releases provide CUDA 13.3 or later. The explicit 26.05 image was selected for the requested CUDA 13.2 testing. Managed `/usr/local/bin/h` ran from an existing HAI checkout, with `--bare` and no size argument. C2 rejected the initial 1-GPU allocation; the required 8-GPU allocation succeeded.

| Source | Selection | Result |
|---|---|---|
| `2c451c73` | Config, weight pack, mega layer validation, BF16 config | 88 passed, 1 skipped in 4.79s |
| `2c451c73` | Cached/explicit knobs and pre-staging graph rejection | 7 passed in 8.32s |
| `2c451c73` | W4A16 eager/graph replay and interleaving | 1 passed in 13.48s |
| `b83cbedb` | BF16 staging and selected fallback | 5 passed, 11 deselected in 6.32s |

Raw commands and results: `test-final.sh`, `final-tests.log`, `test-interface-b83.sh`, `b83-interface-tests.log`, `final-environment.log`. Staging code/tests are unchanged after b83; implementation and tests are unchanged after 2c. No GPU tests were rerun for the final documentation-only commit.

The one skip is optional DeepGEMM. An initial CUDA-hidden run had 87 passes, one skip and one failure in the unchanged distributed-readiness test because its workspace path queries the current CUDA device first. The full selection passes with CUDA visible. Existing marker/deprecation warnings and expected empty CUDA graphs from rejection tests remain. No unrelated tests were modified to conceal that result.

No full numerical, multi-rank, benchmark, nsys or ncu rerun was performed for this interface/test/doc work. All compute kernels, tactics, benchmark code and default tuning values remain unchanged. Historical performance evidence is not relabeled as measured at this head. The complete PR Final performance section is byte-identical to `pr-before.json`; its hash is recorded in `publication-check.json`.

The independent remote checkout is `/workspace/flashinfer-w4a16-megamoe-interface/flashinfer`, tested at 2c451c73. The devbox was left available for subsequent work; availability may change. No claim is made that the final documentation-only commit was copied to that remote checkout.

Publication body: `PR_BODY.md`. Live final readback: `pr-after.json`.
