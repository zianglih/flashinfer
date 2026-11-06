# Retained-head validation preparation

Prepared only; no GPU jobs are launched by this directory. Copy these five
runtime files together into the frozen refresh root's `validation-tools/`:
`run.py`, `run_existing_tests.py`, `selection.json`, `probe.py`, and
`preparation.json`. The parent assigns an idle GPU to each process.

```bash
python3 <refresh-root>/validation-tools/run.py --root <refresh-root> --kind exact --gpu <gpu>
python3 <refresh-root>/validation-tools/run.py --root <refresh-root> --kind api --gpu <gpu>
python3 <refresh-root>/validation-tools/run.py --root <refresh-root> --kind memcheck --gpu <gpu>
python3 <refresh-root>/validation-tools/run.py --root <refresh-root> --kind synccheck --gpu <gpu>
python3 <refresh-root>/validation-tools/run.py --root <refresh-root> --kind racecheck --gpu <gpu>
```

The root must contain the newly retained clean Git snapshot's `source.json` and
`runtime.json`. Every source hash is checked before and after execution. The
actual retained reference and actual-plan fixture file hashes are explicit in
each receipt; no frozen experimental reference bytes are substituted. Existing
persistent native compilation cache links must resolve correctly. Tests use
private output/dump/Triton paths while retaining the existing compilation cache.

- `exact`: unchanged selectors from
  `report/publication/existing-test-commands.md`, expected **33 passed**.
- `api`: unchanged selected wrapper eager/graph, unified API, legacy W4A8 and
  autotuner policy/scope cases, expected **62 passed**, plus the existing Linux
  CI compilation-cache unittest command. No new repository tests.
- Each sanitizer tool: the prior qualified focused **96-replay, 48-compile**
  H512/I384 partial-K probe. Six configs cover NVFP4 per-tensor/per-token,
  MXFP4x8/MXFP8, narrow/wide N, one/two CTA, M512, static/CLC, PDL off/on and
  balanced/skewed/empty/reactivated routes. Source/dump/tool/options/raw clean
  summary are bound in `validation/<kind>/receipt.json`.

The sanitizer uses the retained repository's `_sanitizer_options` unchanged,
with the known Compute Sanitizer2026.3 executable. Memcheck retains
`--check-tensor-ops no` and requests ptxas `-g-tmem-access-check`; codegen artifacts
remain available for post-run assembled-guard inspection. Guarded memcheck
register/spill usage must not be reported as production usage. The focused
probe compares storage bits within the same source across schedule/PDL variants;
the separate pytest group supplies the actual numerical oracle. This does not
repeat or relabel the earlier broad150-case d1767 sanitizer campaign.

Outputs are new directories only; failures preserve logs and partial receipts.
The wrapper is intentionally a single-job runner, not a new queue/deployment
framework. Launch detached processes using the existing parent orchestration,
then inspect their completion receipts. Do not run five jobs on one GPU.
