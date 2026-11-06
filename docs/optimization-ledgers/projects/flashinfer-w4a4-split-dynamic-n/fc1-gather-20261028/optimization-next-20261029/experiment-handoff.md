# Experiment workspace handoff

Use a frozen source manifest and one active review checkout per variant. Keep measured snapshots immutable while later sources evolve.

For the current C3 runtime, a Git clone alone is insufficient: `flashinfer/data` is an ignored link to the prepared native source/submodule tree. Copy the existing runtime data link and exclude it from Git status. The native C++ workspace remains the shared persistent cache; do not clear it to fix a missing source link.

Copy every path named in `observer_hashes`, including JSON register policy files. Verify each hash. Copying only Python helpers omits required guard configuration. Rebind both `config.output` and `config.observer` to the new experiment root, preserving the timing observer itself. Keep all source, route, tactic, physical-GPU and strict-CUPTI guards active.

A pytest selector may expand into many parameterized cases. Derive a new expected case count from the previous expanded count plus individually named new cases, not the number of selectors. Always inspect the collected count before interpreting a gate failure as a kernel failure.

Use separate attempt output paths. A driver may create its output directory before a guard rejects the run, so an empty directory is not a completed or partial measurement. Remove only verified empty directories or choose a new output directory; preserve receipts and logs with actual results. Do not overwrite completed benchmark evidence.

The W4 single-arrival experiment encountered these setup omissions; all were rejected before timing. Its unchanged source then passed33 existing exact cases. None of those setup failures are kernel correctness results.
