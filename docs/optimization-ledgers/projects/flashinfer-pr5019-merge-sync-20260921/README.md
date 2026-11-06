# FlashInfer PR #5019 merge and HashInfer sync

[Private deployment-integration status section omitted from this kernel archive.]

## Current archive and rebase (2026-09-26)

[PR5019](https://github.com/flashinfer-ai/flashinfer/pull/5019) is OPEN/non-draft, now one commit `7ca3eb567a2400df70579d55e9bc717ea1784b0c` atop upstream `d97b1801`, with conflicts resolved and GitHub reporting MERGEABLE. [Third archive](https://github.com/zianglih/flashinfer/pull/6) freezes the prior six commits at `acbc0b1f` plus the original PR body. Both earlier archives are retained.

Owned W4A16 production source remains byte-identical. Shared tests preserve upstream SiTU and existing W4A16 coverage; the NCU profile now honors precomputed routing. Source/AST/dependency checks, scoped pre-commit and the mocked host routing-stage check passed. Replies address stale bot findings and the intentional cache boundary. [Runbook](archive-squash-20260926/README.md) and [completion receipt](archive-squash-20260926/completion.json) record exact refs and reply links.

No fresh GPU run is claimed: the previously retained C2 pod was absent when checked. This task did not release a devbox. Earlier GPU results remain pinned to their tested revisions. Neither PR was merged; HashInfer was not modified. The records below are historical.

## Current tracing follow-up (2026-09-26)

[PR5019](https://github.com/flashinfer-ai/flashinfer/pull/5019) is published at `b1eab683651680e1434321b3e0adf499be79447a`. The remaining owned kernel/epilogue marker changes are synced; all 319 protected source files, scripts and tests are unchanged by this follow-up. Eighteen existing cases / 42 rank reports and the targeted four-rank native IKET smoke pass on C2. Pre-commit, API/documentation and docs-build checks pass; upstream GPU CI awaits maintainer authorization. Protected transport trace completeness is outside the smoke qualification. See [scope and validation](tracing-sync-20260926/README.md), [published PR body](tracing-sync-20260926/PR-body.md), and [completion receipt](tracing-sync-20260926/completion.json).

Keep C2/infra devbox `fi-w4a16-align256-r2-0926` on `hu-pdx-43` for iteration. The prior `fi-w4a16-trace-0925` devbox is gone; its completed evidence remains historical. Neither PR was merged. HashInfer's separate 4096-global tracing run is tracked in `../hashinfer-w4a16-device-trace/optimization/trace4096-20260926`.

The earlier four-file port `74ba96d` and its 15-case / 36-rank validation remain in [the September25 record](tracing-sync-20260925/README.md). The merge/sync records below are also historical.

## Request

Resolve upstream PR #5019 conflicts with a merge commit and open a separate HashInfer sync PR. [Private integration rationale omitted.]

## Upstream result

- PR: https://github.com/flashinfer-ai/flashinfer/pull/5019
- Branch: `zianglih/flashinfer:feat/w4a16-megamoe`.
- Prior head: `ad0a5e5e78e57070ec7c582efe733cb55cd8839f`.
- Merged main: `c62cf664117a34ccfc746df5076efab546ea9736`.
- Two-parent merge: `67fcdc6b161027a1d142244ab7b5f820171468a0`.
- Three conflicted test modules preserve W4A16 tests and upstream W4A4 MiniMax coverage. Shared imports follow the `kernel_src/sm100/cutedsl_megamoe` relocation. The inherited split constructor receives `m_cluster_aligned=False`; MegaMoE does not execute the split epilogue controlled by that flag.
- GitHub reports `MERGEABLE` after push; branch protection/CI remains separate from conflict resolution.

## Local validation

- Scoped upstream pre-commit: passed (`upstream-precommit.log`). Initial formatting run changed four files, then the complete PR scope passed.
- `python3 validate_upstream_merge.py`: passed (`upstream-source-validation.log`). All 32 PR Python files parse. Twelve W4A16 implementation modules are AST-identical after import/constructor normalization; three inherited decoder/transform methods are unchanged. Existing test functions are retained; no obsolete shared-module references remain under the MoE package/test trees.
- Independent static integration review: `upstream-review.md`.
- Local macOS validation did not run GPU tests. A direct upstream package import there stops at unavailable `tvm_ffi`. Fresh C2 GPU results for the exact merge commit are recorded below; historical benchmarks/sanitizer results remain labeled with their original commits.

## Durable artifacts

`flashinfer/` and `hashinfer/` are independent project-local clones. PR-body drafts, source-audit helpers, and local validation logs remain at this project root. No HAI deployment/submodule update is part of this effort.

## HashInfer result

- Draft PR: [private repository link omitted]
- Branch: `sync/flashinfer-pr5019-merge-20260921`.
- Commit: `71d29cbedda05b8342a39d0a4148161673f0e19a`.
- Source pin: upstream merge `67fcdc6b161027a1d142244ab7b5f820171468a0`.
- Verified OPEN, draft, unmerged, no auto-merge request, MERGEABLE.
- HashInfer main remains `9e97350298a7a4107f5090a8b89d42282bedddb8`; no HAI pin/deployment updates.
- Final checks: all pre-commit hooks, 39 host tests, 95 namespace-only AST comparisons, 130 internal import edges, four selected shared transform methods, two shim helpers, and wheel packaging/import checks passed. Independent review additionally checked 181 internal imports and 36 lazy exports.
- Fresh GPU compilation/numerical/distributed tests passed on C2 as recorded below. Sanitizers and performance were not rerun.
[Private account-operation receipt omitted.]

## C2 validation (2026-09-21)

This section records the initial focused run. A subsequent full HashInfer EP4/EP8 finite-bit numerical matrix is running in `exhaustive-validation/`; see that directory's README and live progress records. The dedicated numerical suite was omitted from the initial run, and its partial progress must not be treated as a full pass.

Both exact commits above passed the focused suite on `fi5019-merge-tests-0921`, C2 / infra, node `hu-pdx-150`: 8× NVIDIA B300 SXM6 AC, driver 590.48.01, image `nvcr.io/nvidia/pytorch:26.05-py3`, PyTorch `2.12.0a0+5aff3928d8.nv26.05` / CUDA 13.2, CuTe DSL 4.7.1, NVSHMEM 3.6.5. The image's PyTorch was preserved in a system-site-packages venv. FlashInfer used GPUs 0/1 and HashInfer used GPUs 2/3; each package's stages ran sequentially.

| Package | Config/cache | EP1 | EP2 logical cases | Total logical cases | Rank reports |
|---|---:|---:|---:|---:|---:|
| FlashInfer | 24 | 66 | 33 | 123 | 156 |
| HashInfer | 21 | 33 | 19 | 73 | 92 |
| Total | 45 | 99 | 52 | 196 | 248 |

All selected cases passed with zero failures, errors or skips. EP2 executes each logical case on two cooperating ranks. FlashInfer config/cache includes three GPU workspace cases; HashInfer's group is host-only. Two MXFP8 graph parameters were explicitly deselected in the FlashInfer EP1 stage. All HashInfer optional layout/package parity parameters executed against the pinned FlashInfer source.

- All eight JUnit reports, worker exits, launcher exits, source pins, case identities and counts were independently verified. Source trees stayed clean and node/boot/GPU identity remained unchanged; no GPU process remained after completion.
- No assertion/tolerance changed. FlashInfer deterministic W4A16 uses bit-exact assertions; its atomic reduction uses the existing term-band oracle. HashInfer's general torch-reference cases retain existing term-band tolerances, while targeted precision, graph and package-parity fixtures use exact equality.
- No full-repository suite, EP4/EP8 rerun, sanitizer rerun, performance benchmark, or RL bring-up run was performed. Warnings are retained in raw logs.
- Both PR bodies now include self-contained setup, test commands, full pytest output, exact commits and limits. HashInfer PR #11 remains draft, open, unmerged, with no auto-merge request. Its main branch remains `9e97350298a7a4107f5090a8b89d42282bedddb8`.
- The task devbox was released after archiving results and confirming idle GPUs. Its absence from C2 / infra was verified.

Evidence: `gpu-validation/collected/results/verification-summary.txt`, `environment.json`, `postrun.json`, and each stage's raw logs / JUnit / exit files. Runbooks and pinned dependencies remain in `gpu-validation/`; the exact published bodies remain at this project root. Original archive: `gpu-validation/c2-results.tar.gz` (95,664 bytes), SHA256 `fd8865a91f9ded32111bd84bd1a7df5be7b0c3e018f710df0ac17b6e632a4818`.

Offline verification:

```bash
python3 gpu-validation/verify_results.py gpu-validation/collected/results \
  --run-id c2-20260921 --require-supervisor
```

## Fixed F4 versus F8 experiment (2026-09-24)

Completed a W4A16 Mega-only comparison at clean `19e8aebb`, with native autotuning of the other eight tactics under fixed F4/F8, EP4 and EP8, and two 100-sample cold-L2 CUPTI sweeps per arm in ABBA order. F8 increased decode latency by 0.74%/1.24% and regressed all measured prefill rows. Keep F4; no production source change was made. All 624 untimed winner-output checks passed with exact cross-run hashes. Both devboxes were released.

See [decision and complete table](flag-batch-20260924/DECISION.md), [full timings and selected tactics](flag-batch-20260924/final-performance.md), and [reproduction instructions](flag-batch-20260924/README.md).
