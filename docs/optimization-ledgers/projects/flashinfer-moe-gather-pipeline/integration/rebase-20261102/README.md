# PR7290 archive, squash and rebase

User requested archiving the existing PR in the zianglih fork before squashing,
rebasing on current upstream, auditing new upstream behavior, and testing on C3.
The later instruction requests implementing ClampedRelu2 in swap-AB as a
follow-up instead of rejecting the new upstream activation.

- Archive: https://github.com/zianglih/flashinfer/pull/10. Fixed head
  `a620ce7790b32f7f0ae524a811417d2c6cee1152`, fixed base
  `002529e17b22567a071091053c6c4dc2a55e050e`; all 61 prior commits and PR body.
- Squash: `bd804285557589284ed120e8887370affdfca14a`, tree-identical to a620.
- Rebased single implementation commit:
  `b17f941056c36ccca799a7fd84d4cd3aa65a0b15`, direct parent
  `e29bf6d5207a2021ebc0e27509dc8c7c48a01c60` (668 newer upstream commits).
- Follow-ups: `ac1d507f97a17cd5a0dd22e399d04d2e697089a3` adds runtime
  ClampedRelu2 support and exact coverage; `95a998233637b7cb471bcc8ee439497be841276d`
  exercises non-power-of-two limits.
- Activation-state cleanup: `a3b184949a3108a16a927b6f5082540c4cc14fe3`
  groups internal activation arguments; `017d91be18bb5c7ae9426e95eebb192a9168d339`
  removes repeated clamp helper arguments; `2b4732791a3ce48bc3ae6c030a283fab73854e0e`
  uses explicit class-method calls so CuTe does not carry the local epilogue
  context through the runtime tile loop. The intermediate 017 compile failure
  and its successful replacement are preserved in validation logs.

Conflicts were confined to the core CuTe wrapper, tuner and MXFP8 test suite.
Both upstream legacy ClampedRelu2 support and the new swap implementation were
preserved. Rank-invariant persisted tuning keys from #6139 remain in both
blockscaled and W4A16 runners. Shared kernel/pipeline/dequantizer changes were
not rewritten. The follow-up leaves W4A16 and Rubin's upstream activation
support boundaries unchanged.

The runtime clamp remains a one-element FP32 tensor, with no new public API
argument beyond upstream's contract. Epilogue threads read it after the PDL
wait and outside the persistent tile loop. Existing tests cover functional and
wrapper execution, exact unfused outputs, runtime updates and CUDA graph replay.
The trace reference now recognizes nongated ClampedRelu2 and forwards the limit.
The runtime limit and reciprocal live on a compilation-local epilogue context,
matching the activation state lifetime without extra per-helper plumbing.

A final upstream fetch found two subsequent CAKE-only commits through
`a9de989e6`. They touch no PR paths; `git merge-tree --write-tree HEAD origin/main`
completed without conflicts. The tested rebase base remains `e29bf6d52`.

## Validation

Changed-file pre-commit passes, including mypy and Ruff. See `precommit-final.log`,
`precommit-nonpower-limits.log`, `precommit-argument-order.log`,
`precommit-epilogue-state.log`, and `precommit-epilogue-binding.log`.
`git diff --check` passes.

C3 runtime and test evidence lives in `testing/`. Final `2b4732791` passes
98 executions across 94 unique cases, including the four-call same-process
ClampedRelu2 → Relu2 → SiTU → ClampedRelu2 sequence. All 34,759 source files
match the committed source manifest after validation. The broader preceding
`95a998233` qualification passed 224 executions across 220 unique cases.
The final run recompiles and rechecks every activation/epilogue path affected
by the argument-lifetime cleanup. Both epochs have zero failures, errors or
skips. Earlier setup and intermediate 017 compilation failures remain logged.

Runtime: C3, 8×B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.78,
Torch `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL 4.8.0. Native compilation
and CuTe caches remain on Weka persistent storage.

No performance rerun or sanitizer run was performed for this rebase.
Existing performance results retain their measured a620 revision and must not
be presented as new measurements of the rebased source.

Independent source review: `audit/upstream-semantic-audit.md`,
`audit/test-conflict-audit.md`, `audit/final-followup-review.json`.
