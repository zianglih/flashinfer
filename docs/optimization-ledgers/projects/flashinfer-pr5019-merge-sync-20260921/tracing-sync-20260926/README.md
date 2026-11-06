# Remaining owned W4A16 tracing sync

Local commit `b1eab683651680e1434321b3e0adf499be79447a` follows the existing
FlashInfer port `74ba96d551640938edde68d628b36ba404a7f331`. Donor:
HashInfer `cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7`. The parent has pushed this commit. The selected C2 tests and targeted native
IKET smoke are complete; current-head CI status is recorded below. This
external documentation/audit handoff does not perform GitHub operations.

Exactly two owned W4A16 files change (30 insertions, 15 deletions):

| File under `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/` | SHA-256 |
|---|---|
| `epilogue.py` | `c0deb410b5e32a397400078b7a64be93056dd87ad0ec5711a9c2371e92410219` |
| `megamoe_kernel.py` | `8b39904f6d9ff8dd51037a7ff1a750281ae5bddf50f0440ec714014e57d961af` |

The sync separates each K tile's weight/activation producer-slot wait from TMA
issue/commit, labels the surrounding whole-tile load ranges, traces the existing
epilogue store-warp rendezvous with the previous tile's phase/expert payload,
clarifies FC1 compute/store and FC2 acquire/convert/store names, records the FC2
intermediate wait only when its ready peek misses, restricts return draining to
dispatch warps, and marks each actual BF16 combine worker invocation. Per-K
payloads use `state.count`; whole-work payloads retain `(phase << 16) | expert`.
TMA issue ranges do not claim asynchronous completion.

Protected transport changes are deliberately excluded: the upstream dispatch
helpers retain their existing marker names and representative-warp guards. This
revision does not synchronize HashInfer's expanded per-warp transport markers.
There are no upstream scripts, tests, docs, workload/default-contract changes,
TMEM width/probe changes, or copied helper implementations. Existing FI namespace
imports, `_MegaMixedInput` trace overrides, constructor arguments, shared no-op
hooks and scheduler markers are preserved.

Completed CPU checks:

- `source-audit.json`: marker-stripped computational AST equality against74ba
  for both files; marker calls, payloads and enclosing control flow match the
  committed donor; Python syntax passes and constant marker labels fit32 chars.
- All319 tracked files under `flashinfer/moe_ep/kernel_src/` remain byte-identical,
  as do the shared W4A16 helper and FC1/FC2 scheduler.
- `precommit.log`: every applicable scoped pre-commit hook passes, including
  mypy, Ruff lint and Ruff format; `git diff --check` passes.

```bash
cd /Users/ziangli/playground/projects/flashinfer-pr5019-merge-sync-20260921/flashinfer
python3 ../tracing-sync-20260926/audit_owned_marker_sync.py
pre-commit run --files \
  flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py \
  flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py
```

Existing GPU selectors executed by the parent in the prepared C2 environment,
with isolated caches and the new source checkout (exact commands, including
four repeated shared split cases, are in `test-c2.sh`):

```bash
export PYTHONPATH="$PWD" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTEST_ADDOPTS=''
export OMP_NUM_THREADS=1 MEGA_USE_NCU=0
unset CUTE_DSL_COMPILER_OPT MEGA_NO_DIST
CUDA_VISIBLE_DEVICES=0 python -m pytest -q -s --maxfail=1 --confcutdir=tests/moe_ep \
  tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py::test_nvfp4_w4a16_fp32_scales_and_routing

CUDA_VISIBLE_DEVICES=0,1,2,3 python -m torch.distributed.run \
  --nnodes=1 --nproc-per-node=4 --master-addr=127.0.0.1 --master-port=29626 \
  -m pytest -q -s --maxfail=1 --confcutdir=tests/moe_ep \
  tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_w4a16_epilogue_contract \
  'tests/moe_ep/test_mega_cuda_graph_multirank.py::test_nvfp4_mega_two_rank_graph_replay_lockstep[w4a16-reuse_dispatch_warps-manual-False-runtime]' \
  'tests/moe_ep/test_mega_cuda_graph_multirank.py::test_nvfp4_mega_two_rank_graph_replay_lockstep[w4a16-None-auto-False-config]'

CUDA_VISIBLE_DEVICES=0,1 python -m torch.distributed.run \
  --nnodes=1 --nproc-per-node=2 --master-addr=127.0.0.1 --master-port=29626 \
  -m pytest -q -s --maxfail=1 --confcutdir=tests/moe_ep \
  'tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-tail-epi_warps]' \
  'tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-n64-wrap-epi_warps]' \
  'tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-n128-wrap-reuse_dispatch_warps]'
```

The existing standalone split tests were unchanged and the shared helper is
byte-preserved; the parent repeated all four selected split cases successfully. Native IKET validation must
recognize the revised labels and payloads above while retaining upstream's
unchanged protected transport markers. Ordinary GPU codegen identity, GPU
numerics and a new native trace are not implied by the CPU AST result.


## Completed C2 validation

Tested `b1eab683651680e1434321b3e0adf499be79447a` on C2/infra devbox
`fi-w4a16-align256-r2-0926`, node `hu-pdx-43`, eight B300 GPUs, image
`nvcr.io/nvidia/pytorch:26.05-py3`, digest
`sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`.
Container PyTorch/CUDA 13.2 is preserved; the venv supplies CuTe DSL 4.8.0.

- `test-audit.json`: **18 logical cases / 42 rank-case executions passed**,
  eight JUnit files, zero failures/errors/skips. Source head and tracked status
  were unchanged before/after. `PR-body.md` includes all raw summaries and
  exact public commands.
- `remote-validation/validation/iket-smoke/audit.json`: **targeted native smoke
  passes all four ranks**, finite exact bits for 32,768 BF16 elements/rank;
  one target launch/rank per tracker or collection pass. Refined loader,
  readiness, epilogue, drain/combine and all 16 transform-warp subsection checks
  pass. Profiler and auditor success receipts are collected.
- Runtime Python/oracle digest:
  `bfa2bd31a0072898a6ebe9424e4ab57d2db3b93d1304b7bbcdd6eacb355fba92`.
  CPU plan digest `aa70bf38a881a4b9cb9eadf2df9320f6508039b5c6fbc52a2931354cc303763c`
  differs only by generated `flashinfer/_build_meta.py`; no existing file hash
  changed.
- The unchanged protected Pull marker stack still drops one of eight outer
  dispatch ranges per rank. Protected transport completeness is explicitly
  outside this smoke's pass, as are SASS scanner completeness, timestamp units
  and performance.
- Verified local archive SHA-256:
  `6af9ee678b9e20e34e9e965f07291cb5dae40f22864a964f4bb3d63c9100c097`.
  All 13 consumed input hashes were rechecked after extraction; the frozen
  auditor's record/structural checks were rerun locally on complete artifacts.
  No GPU work was launched by this documentation/audit subtask.
- `published-final.json`: pre-commit, Public API/documentation and Build Docs pass.
  GPU CI is skipped pending authorization,
  with its summary marked failed; the actual gate is retained in
  `ci-gpu-gate.log`. No upstream GPU-CI pass is claimed.

`PR-body.md` is published and exact body/head/state readback is verified in
`published-final.json`; `completion.json` records the final source and body hash.
The PR remains OPEN and non-draft, as before. No PR was merged or devbox released.
