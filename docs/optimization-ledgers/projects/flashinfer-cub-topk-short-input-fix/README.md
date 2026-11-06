# FlashInfer oversized CUB Top-K fix

Implements the follow-up to the source audit in `../flashinfer-cub-topk-gap-audit/README.md`.
The user requested a draft upstream PR with performance-conscious implementation. Earlier benchmarks were explicitly waived and the original driver was stopped. The user subsequently requested fresh before/after benchmarks and a separate results comment; see `BENCHMARK_PLAN.md`. Final correctness and paired performance validation are complete; see the current status below.

Upstream PR: https://github.com/flashinfer-ai/flashinfer/pull/5187

## Current status

- PR #5187 is ready for review at `d49e8ce71c0148d122da74cd3a0005b77b39c8d5`; commit, push, title/body, and clean source tree verified in `artifacts/review-validation/pr-final.json` and `commit-attestation.json`.
- Final scope is the fused page-table and ragged APIs. Normalize selection K only in their shared variable-length wrapper, preserve requested-K output strides, and reuse the original tail kernel/helper. Plain CUB entry/workspace/bound dispatch and plain Python docstring match the upstream base; existing other-backend plain behavior is not standardized by this PR.
- Fused padding docstrings are backend-neutral. Explicit CUB call counts are asserted only for forced CUB; automatic dispatch tests assert outputs. The added plain oversized-K rejection test was removed at the user's request.
- **Fresh validation: 89 passed, zero failures/errors/skips**, on B300 SM10.3 using `nvcr.io/nvidia/pytorch:26.05-py3`. Includes60 fused physical,20 fused graph,5 workspace,3 nonpositive-length,1 existing torch compatibility case. Fresh native build took892.986s; final pytest7.876s. Source/binary/XML and27retrieved artifacts were independently hash-verified; see `root-verification.json`.
- Native binary SHA256: `23332a275e6def9df0b35dfdc6dbe9b0260df24bf9daa5b422a62618b083d2d8`.
- Scoped pre-commit (including clang-format, mypy, Ruff) passed. No new benchmarks were run; historical performance remains attributed to30b1b2e6 below. The PR body now describes only the final scope and current validation, preserving its template.
- Task-owned `cub-topk-review-validation` devbox deleted and absence verified in `artifacts/review-validation/cleanup/`. All local artifacts and superseded scope snapshots remain preserved. No review replies or additional comments were posted.

## Prior validation and benchmark history (30b1b2e6)

- PR #5187 is ready for review at `30b1b2e6d12792951309b607b9e009d791aed7b8`; public status/head/body re-read and verified in `published-pr-ready.json`. The source repository is clean.
- Restored the static-width conditional plain tail launch and simplified tests (41 fewer test lines versus `a0d9bb64`, preserving 90 physical-width, 26 graph-replay, and 6 workspace cases plus 3 adjacent controls).
- Final-head native rebuild and correctness: **125 passed, zero failures/errors/skips**. Exact source/binary hashes and XML verified in `artifacts/test-cleanup/`.
- Broad before/after: three alternating pairs, 4,728 records, **304 comparable CUB cases (+0.006% geometric change)** and 354 native controls (−0.027%). Zero cases meet the predefined >=5% and >=0.25 µs regression screen. The largest broad CUB increase is +3.939%; individual round variation remains preserved.
- Targeted longer-batch follow-up: 24 existing small-row workloads, all APIs/ties, three alternating pairs, 288 successful records. CUB −0.075% geometric change; largest increase +0.038%. This selected rerun does not replace the broad dataset or cover every broad increase.
- Results comment: https://github.com/flashinfer-ai/flashinfer/pull/5187#issuecomment-5656144758
- Complete raw evidence/reproduction: https://gist.github.com/zianglih/2b35e2c545804091d209370676a61085. All 64 public files were downloaded and SHA256-verified; the filename-only follow-up also passed verification. See `published-performance-gist-verification.json`.
- Task-owned `cub-topk-test-cleanup` devbox deleted and absence verified; cleanup evidence in `artifacts/test-cleanup/cleanup/`. All local scripts, binaries, raw artifacts, and earlier validation history remain retained.
- Optional fused-tail SASS audit found identical complete dumps except source paths/function name, including the read-only length load; evidence in `artifacts/sass-tail-audit/`.
- Scope: one B300, CUDA-event graph replay with reused inputs. No eager host-overhead, cold-L2/CUPTI, end-to-end SGLang, full-suite, or other-architecture performance claim.

## Workspace and sources

- Independent FlashInfer clone: `flashinfer/`, branch `agent/cub-topk-padded-short-inputs`.
- Upstream base: `93e9eef092c11bc93a6f432a16404054e85d19c5`.
- CCCL pin unchanged: `16bd510c9b712e82b0ab6cbb630d8e29ba1f7116`.
- #5185 remains an independent draft guard-only PR; this implementation targets upstream main directly.
- `hai/` is an independent checkout used only as cwd for managed `/usr/local/bin/h`. The user explicitly approved this cwd exception after the managed CLI rejected bare devbox creation outside HAI. No checkout-owned CLI is used.

## Implementation

- CUB always handles selection. Only its K argument is normalized to `min(K,physical_width)` to fit FlashInfer's selected compile-time bounds; all output row strides remain original K.
- CUB reads logical lengths on device and clamps selection each replay. Transform suffix filling remains in the existing tail kernel, also reading lengths on device.
- Generalize that same tail kernel to support plain Top-K's int64 indices and zero-valued score padding with a constant physical length iterator. Plain tail filling is conditional on successful CUB selection and K>physical width. The user restored this condition after clarifying that K/width are static during capture/replay; normal-width calls avoid an extra launch.
- The rejected separate select-all kernel/header has been removed. Its old commit `09e941c` is retained only in the local backup branch `backup/select-all-draft-09e941`.
- Python backend eligibility/benefit policies remain unchanged. The earlier K>2048 exception was removed as a separate policy issue outside this wrapper fix. Oversized calls work when routed to CUB, including explicit CUB selection.
- No CCCL edits. Existing valid logical-length/window/metadata bounds still apply.

## Validation environment

Selected immediately after checking NVIDIA's live NGC catalog and 26.06/26.07/26.08 release notes:
`nvcr.io/nvidia/pytorch:26.05-py3`, newest available PyTorch release using CUDA13.2 (later releases use13.3/13.4).

- Managed HAI devbox `cub-topk-short-fix`, c2/ziangli, bare, size unspecified, 8B300 node; tests and benchmarks use GPU0 only.
- `environment.json` records the observed environment, compiler, versions, and GPU details.
- Image Torch preserved; native top-k built from source, no flashinfer-cubin or flashinfer-jit-cache installed.
- Image CuTe DSL4.4.2, cuTile1.3.0, cuDNN frontend1.23.0 remain installed. Those are below unrelated current package requirements; this effort validates native top-k only.

`setup_remote.sh` reproduces the source/environment setup and base build. Local logs retain the managed-CLI checkout constraint, failed update authentication, initial stdin transport correction, and successful setup.

## Retained performance helpers (not part of PR validation)

- `bench_short_topk.py`: public-API CUDA graph event timing, all GPU launches included, warm L2, exact tie-aware selected-set validation before timing. Raw per-replay samples go to JSON; CSV contains median/p10/p90 and every case status.
- `cub_topk_adapter.cu`: alternative correctness repair that keeps CUB selection with min(K,d) and separate suffix filling. This is an experiment artifact, not part of the upstream patch.
- `make_adapter_variant.py`: regenerates the adapter control from the pinned upstream base.
- `transfer/`: exact source/helper snapshots sent to the validation devbox.

## Initial publication and validation history

- Historical published head of draft #5187: `a0d9bb64d7b5ee219364a990147ef25819a6cba8`. The graph replay follow-up passed26 cases on this head; the earlier236-case run remains attributed to `6dfb65bfd92469864a70c4bcfec4aa651e8e1c05`. The early-return readability change, user docstring cleanup, and expanded capture-state coverage are included.
- Scoped pre-commit checks passed (`precommit-wrapper.log`).
- Parent regression: six expected failures at the old `0 < top_k <= d` assertion.
- Final wrapper GPU correctness completed via `run_correctness.sh`:114 focused cases and122 existing controls passed, zero failures/errors/skips. The first phase includes JIT compilation. No benchmarks run by that script. The superseded select-all build was stopped without claiming a result.
- Graph coverage captures fixed physical (width,K) pairs below/above K, then changes only GPU-resident scores and metadata across replay, including logical lengths crossing K.
- The original `transfer/run_phases.sh` includes superseded benchmark phases. Its process tree was terminated during the adapter build when the user waived benchmarks. The upstream-only quick sample had already completed; it is not evidence for patch performance and is excluded from the PR.
- `PR_BODY.md` is the durable upstream body draft; `published-pr.json` records its verified state.


`SGLANG_GRAPH_CONTRACT.md` preserves a bounded trace from an older SGLang reference checkout. It separates fixed physical capacity from replay-updated device lengths and is not evidence of current live SGLang validation.

Final source/binary/test evidence: `artifacts/final-validation-summary.json`, `artifacts/final-validation-metadata.json`, and complete pytest logs/XML. All final source hashes were verified against `6dfb65bfd92469864a70c4bcfec4aa651e8e1c05`; Python executable AST is unchanged from upstream.

Task-owned B300 devbox deleted after all24 remote artifacts were retrieved and verified; cleanup output is retained in `devbox-delete.log`. Final public body and head were re-read and verified in `published-pr.json`.


## Graph replay coverage follow-up

- Revision `a0d9bb64d7b5ee219364a990147ef25819a6cba8` makes all three API branches explicit and expands graph tests from18 to26 cases (FP32/BF16).
- Fixed batch4, capacities8192/32768, K2048: each fused API independently captures all-short and all-long device lengths, then replays the capture state, the opposite side of K, and the original state without recapture. Mixed exact-K/empty/negative-length and metadata updates remain covered.
- Physical65/K4096 stays a separate fixed-capacity regression. Direct plain Top-K has no logical-length input; its graph cases update scores at fixed physical shape.
- At pinned SGLang failure revision202eef4cf5dd9398f4955bdb059c1d106bb55a2f, graph page tables retain context-capacity columns (`dsa_backend.py:1225-1296,1331-1338,1372-1380`), the indexer derives logits capacity from those columns (`dsa_indexer.py:776-793`), and replay updates existing device metadata (`dsa_backend.py:1579-1636`). This is source evidence; no new SGLang serving run is claimed.
- Local pre-commit, Python compilation, and whitespace checks pass (`precommit-graph-replay.log`). Focused GPU correctness passed26 cases on exact a0d9bb64 (zero failures/errors/skips), including a fresh native JIT build. Complete logs/XML, environment, source/binary hashes, and verified summary are in `artifacts/graph-replay-followup/`. The prior236-case results remain attributed to6dfb65bf.

Graph replay follow-up devbox `cub-topk-graph-replay` deleted after verified artifact retrieval (`artifacts/graph-replay-followup/delete.log`). No benchmarks or broader tests were run in this follow-up.


## Test simplification follow-up

- Test-only cleanup head `85bd38dd8fd308f2bb8fbcc38135964eac7da54a` changes only `tests/utils/test_topk.py` relative to `a0d9bb64`, removing 41 net lines (81 insertions, 122 deletions).
- Preserve 90 physical-width, 26 graph-replay, and 6 workspace cases. Use separate physical parameter axes, one shared graph reference, exact raw-to-page mapping, and one mixed boundary state after crossing K in both capture directions.
- Retain a simple strided physical input and fixed nonzero fused graph window to exercise both CUB iterator paths. Remove the complex dynamic-start/shared-page-row setup. Include the 3 adjacent nonpositive-length controls in the 125-case GPU selection.
- Local scoped pre-commit, Python compilation, and whitespace checks pass. The later final kernel head passed the same 125-case selection under `artifacts/test-cleanup/`; earlier 236-case and 26-case results remain attributed to their original revisions.
- Benchmark follow-up now requested: see `BENCHMARK_PLAN.md`. Reuse the task-owned GPU after correctness; publish performance evidence in a PR comment, then retrieve artifacts and delete the devbox.

## Conditional plain tail and performance follow-up

- Current head `30b1b2e6d12792951309b607b9e009d791aed7b8` restores `status == cudaSuccess && top_k > max_len` around the plain tail launch. Both values are fixed for a captured graph. All normal-width APIs retain the parent launch count.
- Test-only head `85bd38dd` passed 125 cases in 3.64s with the unchanged earlier binary; retain this as historical evidence. The later final kernel head completed a fresh native rebuild and the 125-case validation.
- Paired benchmark target is parent `93e9eef0` versus current `30b1b2e6`, 788 records per arm, three alternating pairs. Mark PR ready after completed validation, as requested.

Final conditional-tail correctness verified at `30b1b2e6`: 125 passed, zero failures/errors/skips, in 835.30s including native CUB rebuild. Source/binary identity and retrieved checksums verified again by the root agent (`artifacts/test-cleanup/root-verification.json`). Smoke pair, three broad alternating pairs, and three longer-batch targeted pairs completed successfully.
