# Initial register redistribution tracing sync

FlashInfer local commit `acbc0b1f389d34dbeea6b33e64eebfdcc54a0119` adds exactly six marker statements to the owned W4A16 kernel on top of `b1eab683651680e1434321b3e0adf499be79447a`. The donor is HashInfer `accf82dae0b703cb0276839dd53d3b17eb21f936`.

The three ranges are `register_donate_96_to_80` on WG1, `register_acquire_96_to_144` on WG0, and `register_donate_96_to_64` on WG2. All participating warps execute their existing register instruction between flat, payload-free push/pop calls. Existing marker payloads, guards, barriers, register budgets and computation are unchanged. No protected transport, script, test, documentation or other source file is included in the upstream commit.

`source-audit.json` verifies exact source-byte recovery after removing the six statements, donor marker/guard/instruction parity, Python syntax, and all 319 protected files remaining byte-identical. `precommit.log` records every applicable scoped pre-commit hook passing; `git diff --check` also passed. These source checks do not establish GPU codegen identity.

## Retained C2 validation environment

- Devbox: `fi-w4a16-align256-r2-0926`, pod `devbox-fi-w4a16-align256-r2-0926-0`, namespace `infra`, node `hu-pdx-43`; eight B300 SXM6 AC GPUs. The box remains allocated.
- Image: `nvcr.io/nvidia/pytorch:26.05-py3`; image digest `sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`.
- Source: `/workspace/w4a16-marker-sync-20260926/flashinfer`, verified clean at the old base and fast-forwarded from `register-sync.bundle`.
- Runtime: `/workspace/hashinfer-alignment256-20260926/venv`; retained container PyTorch/CUDA13.2 and CuTe DSL4.8.0.
- Fresh outputs/caches: `/workspace/w4a16-register-sync-20260926`.

`test-c2.sh` reuses the previous serial selection without changing test code: four standalone split cases, four EP1 cases, seven EP4 cases and three EP2 cases, totaling 18 logical cases / 42 rank executions. Groups use GPU0, GPUs0–3 and GPUs0–1 serially. `pytest-rank.py` emits one JUnit report per rank. Only expected commit, source/output/cache paths change from the prior harness; `helper-adaptations.json` records the adaptations.

`run-smoke-c2.sh` runs only after the test launcher produces its success receipt. The copied fixed EP4 IKET smoke keeps H1024/I1024/E256/top8, 32 tokens/rank, M256/N64/K256, group512 and epilogue return, with exact finite BF16 reference checks. Its driver differs only in its pinned commit. Native full-grid execution is preserved and IKET selects cluster0 for recording. Native smoke remains targeted to owned W4A16 coverage; unchanged protected upstream transport coverage is not qualified.

Validation is in progress. Completed result receipts will be added separately; no current-head GPU pass, performance comparison or sanitizer result is asserted by this initial note.

## Completed validation

At `acbc0b1f`, all **18 logical cases / 42 rank executions** passed with zero failures, errors or skips. Raw logs and eight JUnit files are under `remote-tests/{split,ep1,ep4,ep2}`; `test-audit.json` independently verifies the exact cases and counts. Observed loaded NVSHMEM is 3.6.5, distinct from the installed 3.8.0 wheel.

The fixed native smoke passed on all four ranks: 32,768 finite BF16 output elements per rank match the independent reference exactly. Each rank contains 24 new register ranges (eight per label), on the expected WG0/1/2 tracks before their role work, with no payload and push/pop IDs bound to native metadata. All prior owned transform, loader, epilogue and combine checks remain enabled. `remote-tests/iket-smoke/register-audit.json` is the completed native result; `smoke-readback.json` records local revalidation of all four ranks and 17 copied input hashes.

Runtime package/oracle SHA-256: `38b8e1825e11f5066bbd6367d17889a7ca8cc693598c3977cf3fd4cd883c78cd`. The CPU plan digest differs only in generated `flashinfer/_build_meta.py`; all other package/oracle files match. The devbox is idle and remains allocated. No current-head sanitizer, full repository suite, protected transport/SASS completeness, timestamp-duration or new performance claim is made. `completion.json` binds the final receipts. Root handles GitHub publication; this subtask made no GitHub operations.

Publication verified: PR5019 remains OPEN/non-draft at `acbc0b1f389d34dbeea6b33e64eebfdcc54a0119`. Concise tracing and focused-validation bullets and current CI gate link refreshed; exact body readback passed. Existing performance tables, screenshots and checklist preserved. See `publication.json`. Hosted GPU CI remains authorization-gated; all current-head local C2 checks above passed.
