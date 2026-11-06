# Independent FC2 CLC autotuning

Frozen independent source: `../../flashinfer-fc2-auto-20261026`, HEAD
`0def601d6603df828ea39679b41ccbce64f7f09e`. All changes are unstaged.
This composes the retained row-grid/live-row quantizer and shared-empty patch
from `flashinfer-retained-policy-20261026` with the internal scheduler extension.
It does not mutate the running retained-policy source.

- Full patch SHA256: `2d1a8e5dc7e548a023d15fa58f80f586f5e2c561519ed5a6cbd4bd6ab1eaa0d0`.
- Sixth-field-only patch SHA256: `88a1e76fa5d307036fcd4ddf80778a17ce52731bc36ba76e645b1b2d3c4b7790`.
- `source.json` pins 228 source/test files; `static-checks.json` records public
  signature, Rubin/W4A16, independent Git directory, and unstaged-state checks.
- Local incremental patch: `sixth-field-only.patch`; complete composition:
  `candidate.patch`; prior composition: `composed-base.patch`.

## Contract

Blackwell internal tactics become
`(route_tile, gemm1, gemm2, k_steps_pair, fc1_use_clc, fc2_use_clc)`.
Both scheduler fields are strict booleans. Existing three/four/five-field tactics
remain accepted with exactly their previous FC1 behavior and static FC2.
The appended field preserves existing prefix validation and JSON cache loading.
Existing cached selections remain usable; fresh AUTO tuning is required to
explore the newly available FC2 choice.

The private runner passes `gemm2_use_clc_scheduler` through the core to the
private finalize implementation's `use_clc_scheduler`. Public signatures,
Rubin execution, W4A16, startup PDL weight prefetch, cache priorities, scheduler
eligibility, and shared-memory admission are unchanged. There are no new
model/dtype/shape policy branches.

The raw enumeration grows from 360 to 720. At most 30 new FC2 geometry/depth
signatures exist per fixed dtype/output/per-token/PDL signature; FC1 codegen is
unchanged. Actual V3/V41/K3 resource admission leaves 320 old and 640 new tactics,
with 28 unique admitted FC2 geometry/depth signatures. Existing effective-CLC
eligibility can map additional requests back to the existing static binary.
Profiling combinations double even though distinct FC2 kernels grow much less.

## Validation

- Ruff lint, Ruff formatting, AST parse, and `git diff --check` pass.
- Existing `TestTacticEnumeration` is extended in place for sixth-field JSON
  roundtrips, strict bool validation, independent scheduler combinations, legacy
  defaults, and Rubin rejection. No new test file is added.
- All 115 unique selected existing tactic/cache/blocklist tests pass: initial
  GPU-hidden run had 110 passes and five stream-capture-discovery failures; those
  same five also fail on unchanged 0def with hidden GPUs and pass normally on
  GPU7 (`5 passed in 0.85s`). The CPU-only selector excluding the six integration
  tests reports `109 passed, 6 deselected`; the sixth integration test passed in
  the initial run. No production/test change was made for this environment issue.
- CPU admission uses the actual `can_implement` resource planner and benchmark
  `MODEL_CONFIGS`: V3/V41/K3 × NVFP4/per-token/MXFP4x8/MXFP8 × T32/128/4096,
  36 cases per source. Every old admission equals the new FC2-static projection;
  FC2 static/dynamic admission sets are identical. Rubin and W4A16 tactic lists
  are identical. See `cpu-validation/comparison.json` and full per-source JSON.
- Source-paired GPU chain gates are owned by the port agent; no broad GPU timing
  or performance claim is made by this implementation receipt.

CPU selector command (GPU hidden):

```sh
python -m pytest -q \
  tests/moe/test_cute_dsl_fused_moe.py::TestTacticEnumeration \
  tests/autotuner/test_autotuner_configs.py \
  tests/autotuner/test_tactics_blocklist.py -k 'not TestAutotunerIntegration'
```

The five initially failing integration selectors pass with GPU7 visible;
`gpu7-five.stdout` records the result. All raw stdout and stderr are retained
in `cpu-validation/`. `check_admission.py` is a task-local
CPU-only helper; its only monkeypatch chooses Blackwell enumeration without GPU
device discovery and leaves the actual resource planner unchanged.

## Remote handoff

Devbox `fi-moe-nvfp4-port-1026`, c3/infra, image
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, B300.

Remote root:
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026`.

- Repo: `<root>/fc2-auto/flashinfer`.
- Source manifest: `<root>/fc2-auto/source.json`.
- Persistent private workspace:
  `<root>/fc2-auto/cache/94533f7a43ef677671f5e3556c7a04ad199ae666e418abee7221bfdda2c10874`.
- Python: `<root>/control-0def601d/.venv/bin/python` (preserve venv symlink path).
- Env: `FLASHINFER_CUDA_ARCH_LIST=10.3a`, `OMP_NUM_THREADS=1`, `MAX_JOBS=8`,
  `TRTLLM_ENABLE_PDL=1`, `FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1`, candidate
  `PYTHONPATH` and source-private `FLASHINFER_WORKSPACE_BASE`.

`deploy.py` stages a new independent clone and reuses the verified persistent
native compilation cache through `prepare_workspace_cache.py`. Do not rerun it
over the existing frozen directory. Gate helpers are separate under
`<root>/fc2-auto/gate-tools`; they do not change source pins.
