# cuDNN DSA Top-K tie-breaking

Upstream cuDNN selector contribution with a separate release-gated NVIDIA Megatron `dev` integration.

- Base: NVIDIA/cudnn-frontend develop `bc981788b0901a74accbdd93468eff12a0c764e1`.
- Branch: `dsa-topk-tie-break`.
- Scope: standalone `DSA.IndexerTopK` and `DSA.indexer_top_k_wrapper`, tie_break=0/1/2 (none/small/large), unsorted output.
- Preserve existing radix score ordering (+0 precedes -0); NaN policy remains unspecified. No score perturbation, new dependency, extra kernel or scratch allocation.
- Exact cutoff selection stays on GPU; only competing cutoff ties invoke a source-index ordered block scan, stopping after the quota is filled.
- Existing Cartesian tests and reference extended; no new test files.

## GPU validation environment

One bare C2 B300 node requested through managed `/usr/local/bin/h`, image `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA 13.2.1). Live NGC catalog and NVIDIA release notes inspected October 1: 26.05 is latest CUDA13.2 release, 26.06 uses13.3 and later releases13.4. Catalog: https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch ; notes: https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html .

First ziangli request queued with zero free GPU quota; only that pending task-owned fleet was removed and removal verified before submitting the replacement in infra/earth. No duplicate fleet held. Resource name `cudnn-dsa-topk-ties-1001`.

Managed h requires a HAI checkout as its working directory; operations use the earlier task-owned `/Users/ziangli/playground/projects/miles-dsa-backend-audit/hai-audit/hai`. It is not edited. All new source and artifacts are in this project, remote `/root/cudnn-dsa-topk-tie-break`.

`setup-gpu.sh` installs into a task-only system-site-packages venv; no global package modifications. Runtime import paths and exact package versions are saved in evidence.

### Setup corrections

Initial import verification caught the image's older FE1.23 module shadowing the editable source. Validation explicitly sets PYTHONPATH to the candidate Python tree and asserts module paths. A script-only `h sync` mirrors/deletes destination files, so syncing a subset to the project root removed source (before any test results existed). Full-project sync restored the tree; subsequent syncs preserve evidence, venv, build, shared libraries, and egg metadata via explicit excludes. The isolated built extension survived. No GPU result was claimed from the failed preflight.

## Completed validation and publication

Draft upstream PR: https://github.com/NVIDIA/cudnn-frontend/pull/1332 . Tested and pushed commit: `fc7a3b50e5b1df88222d4dcfdc737166cec26461`.

The benchmark uses Q=8192 and KV=8192/32768/131072/524288, corresponding to implied CP shapes 1/4/16/64. Edge and interior ranks use zigzag causal positions; no distributed collectives run. Reducing Q was unnecessary: every measured primary call took under 12 ms.

- 126 GPU tests passed in 58.71 s. The expected semantic negative control failed with 8,299 / 16,416 selected indices mismatched in 2.11 s.
- 30 primary comparisons produced 420 raw samples. Maximum additional latency was 5.2% for random scores and 17.5% for duplicate scores. Sparse-left stress added about 86%. Final CSVs and logs are in `evidence/primary-benchmark-001`; `primary-performance-body.md` contains the median and raw PR tables.
- Two supplementary construction-order sweeps each completed 320 records, checking independent CPU oracles, changed-input graph replay and Torch sync-debug checks. Final artifacts are in `evidence/optimized-validation-001`; earlier implementation results remain separate in `evidence/benchmark-initial-001`. Do not mix those versions.
- Executed source and benchmark hashes matched local HEAD and `primary-source-manifest-001.json`; the receipt is `evidence/runtime-source-sha256.txt`.
- All nine changed files passed scoped pre-commit. The PR includes test and benchmark commands, raw samples, limitations, and verified FlashInfer #3095 / #4295 / #4442 references.
- The C2 test node was released after GPU work completed and evidence was copied locally. Managed h confirmed deletion. No old C1 training fleets were touched.
- GitHub denied label changes from the external contributor account. The required label names remain in the PR body for maintainers.

## Repository-standard benchmark rerun

The `a7d8e376298e55b52935ca430402b6ec4bb723ce` benchmark-only follow-up uses the repository's one-call CUDA graph/event median pattern, 20 side-stream warmups before capture, 20 warmups after CPU references, 50 alternating samples per policy, primed/reused events, and a 256 MiB L2 flush before each start event. Flush time is excluded.

The new 30 comparisons contain 3,000 samples and supersede the historical seven-sample warm-cache table above. Random inputs add at most 5.2186%; duplicates 17.5116%; sparse-left stress 85.5892%. Raw CSV/logs are preserved in `evidence/cold-primary-benchmark-001`; `cold-primary-results.csv` aggregates all rows. `pr-body.md` and published FE PR1332 contain the complete new results. Remote source hashes match `cold-primary-source-manifest-001.json` (receipt `evidence/cold-runtime-source-sha256.txt`). GPU kernel/test source is unchanged from fc7a3b50.

The rerun used a new task-owned C2 infra/earth devbox `cudnn-dsa-topk-method-1001`, 1 node / 8 B300, the same frozen NVIDIA26.05 image; 32 CPU /256 GiB host memory /200 GiB disk. It is temporarily retained for the Megatron integration checks. The old test node remains released.

FE PR1332 was independently marked ready for review by zianglih at 2026-10-02T01:25:01Z; this workflow did not revert that user change. GitHub's merge-requirements failure is missing milestone/project assignments. Style/Docs runs require maintainer approval; local scoped pre-commit passes.

## NVIDIA Megatron integration

Independent clone `megatron-dev`, based on NVIDIA dev ac100f773f9d8fac918ce3e64698be4ed84fa428; feature issue https://github.com/NVIDIA/Megatron-LM/issues/7812. Native top-k uses tie_break=2 and removes epsilon perturbation; no version/fallback/config/package changes. Merge is gated on a release containing FE1332. Details and test evidence live in `megatron-validation/`.

The isolated GPU venv added the repository-pinned nvidia-resiliency-ext0.6.0 wheel with --no-deps because the reused NVIDIA image has0.5.0; no base-image package changes. A standalone torchrun rendezvous attempt could not resolve the physical hostname; later attempts explicitly use127.0.0.1. No model training was launched.

Initial manual GPU coverage reached the inherited flaky CP-prefix scorer test and failed. A control using the unmodified NVIDIA dev production module reproduced it: every one-row prefix call scores only key0, returning [0,-1] rather than expected later keys. This precedes selection and is independent of the new tie policy. Preserve this failure and its baseline control separately from direct selector validation.

## Final Megatron publication

Draft PR: https://github.com/NVIDIA/Megatron-LM/pull/7813 (base dev, head33fbd2e25a5b949c87c2c5dc1069a0455e1582f3). FE PR1332 links this separate consumer; feature issue7812 links the draft. Production remains a two-call native tie-break handoff plus deletion of legacy score bias.

Final actual GPU selection: `-k 'cudnn_indexer_topk and not real_kernel'`;32 passed per rank on all8 ranks (256 executions), including four actual selector GPU cases/rank. Original full-scorer failure is preserved/documented separately. All rank logs and complete output are in `evidence/megatron-gpu-004`, summary `megatron-validation/gpu-result-summary.txt`. Runtime source hashes match final commit (`source-manifest-final.json`, `megatron-runtime-source-final-sha256.txt`). Locked repository autoformat final run passed (mypy advisory unavailable).

The C2 node was deleted after complete evidence capture and verifying no GPU compute processes remained. Both source checkouts are committed and pushed. GitHub signing verification remains unknown_key although local SSH signature verification passes. No signature account setting, other devbox or historical C1 run was changed.

## Policy correction requested after publication

Commit48a2592a2c4cd932e39a2a2c5c48deda8ac28f1b supersedes the Megatron LARGE policy described in the historical sections above. Preserve the original CPU SMALL activation (`topk_k < width and not scores.is_cuda`); otherwise use policy0, including CUDA. No new user option or downstream alignment policy. Removing epsilon retains the intended tie policy while removing its near-distinct-score numerical artifacts.

Thirty CPU test bodies pass on the corrected source; six actualGPU-selector tests have not been rerun. Official formatting passes; mypy remains advisory/unavailable. Existing fullCPscorer test restored exactly to base. The previous eight-rank GPU results belong to33fbd2e25 and must not be presented as correction validation. PR7813 and issue7812 were revised to the corrected scope.

## Named Megatron CLI policy

Commit `067a57b764860be64d3e6963086cb1b7acf122e5` adds `--dsa-indexer-topk-tie-break {none,small,large}` to PR7813. The public optional string field automatically participates in Megatron's existing CLI/config conversion; initialization resolves the private kernel mode once. Omission retains the original CPU SMALL / CUDA arbitrary policy; explicit `none` selects arbitrary ties, `small` smaller logical keys and `large` larger logical keys. Ordinary cuDNN DSA supports the override through no-loss, sparse-loss, full fused attention/indexer and packed/CP helpers. Unsupported explicit configurations or reference-selector routes fail clearly; no new version probes or compatibility fallback are added.

Current CPU validation: 16 config/CLI/dispatch cases, 60 selector test bodies, 26 adapter/autograd bodies and eight full-forward fallback-guard cases pass (110 total). These are explicitly scoped CPU probes with repository kernel doubles and bypassed unrelated package/distributed startup, not official GPU pytest. The adapter probe uses an SM90 architecture double. Actual GPU selector cases (24) and the inherited disabled full-CP scorer remain unrun for this revision. Previous eight-rank GPU evidence remains historical and must not be counted for this CLI wiring.

Final receipts: `megatron-validation/cli-config-final.log`, `cli-wiring-final.log`, `cli-autoformat-002.log`, and `cli-source-manifest.json`. Official Black/isort/pylint/Ruff, compilation and diff checks pass; advisory mypy remains absent in the locked linting environment. No GPU allocation or model training was launched. The PR body includes self-contained probe commands and complete output; issue7812 now describes the named interface. Source changes are signed, signed off and pushed to the personal fork. The PR remains draft pending release of FE1332.
