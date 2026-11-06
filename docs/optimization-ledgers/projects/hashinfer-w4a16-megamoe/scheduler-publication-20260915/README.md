# Scheduler publication follow-up validation — prepared, not launched

Frozen HashInfer commit `224b0e3ae544c4697e6d21cdbbe59716796e18a6` mirrors native `a48e5706c2a7775b0b698aa8eccb4e124b02118c`. Source manifest SHA256: `44748b628ad8828d0176c527f229477acecfefb3fdb040167345c7194a04ce75`; source archive SHA256: `38c1a01fdd53adba2b030154d1e23e4bd22613784b0d740e8eda1d66af75544b`. All100 tracked files, including dotfiles, are frozen locally. `source-freeze.json` records `uploaded:false`.

Compared with frozen4ead, only `README.md` and owned `custom_ext.py` differ. Every test, tolerance, tactic/O-level loop, reference, workspace behavior and timing protocol is byte-identical. The runtime change elects one scheduler record writer, leaving all32 pipeline arrivals intact. Exact paired candidate/source rationale is in `../gpu-validation/owner6-source-audit/racecheck-owned-20260915/`.

## Prepared helpers

- This directory: full60 numerical run, unchanged `run.py`/`analyze.py`; strict zero audit and supervisor differ only in new commit/manifest/path/default output name. The reviewed process owner and its historical dependencies are reused unchanged.
- `../sanitizer-guarded-scheduler-20260915`: same four-case full-reference guarded memcheck batch per EP. Only common source pins/path change; rank/check/supervisor remain byte-identical.
- `../sanitizer-racecheck-scheduler-20260915`: same four-case full-reference racecheck batch per EP. Only common source pins/path and exact guarded-helper pins change. The prerequisite is **new same-EP guarded evidence on224b**, not a relabeled4ead pass.

`derivation.json`, per-directory `handoff-sha256.json`, and per-file `.diff` artifacts enumerate every transformation. Historical7ff ordinary memcheck/cached synccheck remain explicitly historical prerequisites; completed4ead numerical/guarded evidence is also historical. No current224b GPU pass is claimed.

## CPU checks

All four numerical suites passed: runner exact-coverage/exit/environment checks; analyzer full60/960-output/10080-comparison checks and missing/malformed cases; zero-audit exactness and exit gates; supervisor source/helper mutation rejection and plan-only behavior. Both sanitizer directories passed provenance and complete synthetic postcheck suites. Logs and JSON results are saved beside each helper. No CUDA imports, GPU queries or remote staging occurred during preparation.

## Commands after review, staging and exclusive GPU handoff

Use the existing `/workspace/hashinfer-w4a16-megamoe/.venv-hashinfer/bin/python`; preserve image dependencies and default runtime environment. These commands are documentation, not launch records:

```bash
python -B scheduler-publication-20260915/supervise-full.py --name full-224b0e3 --execute
python -B sanitizer-guarded-scheduler-20260915/supervise.py --name guarded-ep4 --ep 4 --execute
python -B sanitizer-guarded-scheduler-20260915/supervise.py --name guarded-ep8 --ep 8 --execute
python -B sanitizer-racecheck-scheduler-20260915/supervise.py --name racecheck-ep4 --ep 4 --execute
python -B sanitizer-racecheck-scheduler-20260915/supervise.py --name racecheck-ep8 --ep 8 --execute
```

Run sequentially under explicit ownership. The full60 watchdog remains10800s. Each sanitizer batch has random/skewed×1/16384 tokens, O2/O3/all four tactics and eager/graph, in one same-EP pytest process per rank; process-group timeout28800s, outer watchdog29400s, `--maxfail=0`, `--print-limit 0`. Healthy nonfatal reports do not stop the batch. Fatal CUDA/context failures or watchdog cleanup yield incomplete coverage.

Guarded memcheck retains compiler TMEM guardrails and `--check-tensor-ops no` because the documented legal two-CTA TMA control fails that tool checker; this is a coverage limitation, not full tensor-checker qualification. Racecheck retains shared-memory and bulk-copy checks with all severities, no filters/reference cache, no compiler TMEM guardrails. INFO or any unsupported/incomplete diagnostic still rejects a clean result; third-party NCCL reports must not be silently attributed to owned code or discarded. Neither tool proves arbitrary global-memory, TMEM or cross-process NVSHMEM race freedom.

Inspect new retained codegen for one scheduler copy writer and unchanged32 full-barrier arrivals before claiming the intended lowering. Keep all old4ead sources/results untouched. Artifact preparation alone supplies no performance or GPU-correctness result.
