# PR5319 final-head benchmark rerun

Requested: rerun the full CuTe DSL comparison and make the upstream PR body uniform. No kernel or benchmark source edits in this campaign.

- PR: https://github.com/flashinfer-ai/flashinfer/pull/5319
- Base: eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095
- Head: f9dd3c10541e087b716772245a9d033499745048
- Runtime: official 0.7.0.dev20260917 nightly at d233e27ddddbcfdc24eec38ab4dffda1f43ff49c.
- Image: nvcr.io/nvidia/pytorch:26.05-py3, newest CUDA13.2 image verified against live NGC.
- Devbox: fi-finalize-rerun-0918, c2/infra. First ziangli namespace request was quota-blocked and deleted before infra fallback. Managed /usr/local/bin/h was invoked from the user-approved existing HAI checkout.
- Hardware: GPU0 B300 UUID GPU-e32ead05-f360-d139-903a-f38cf17eecb8, one GPU timed;8GPUs provisioned.
- Matrix: three CuTe modes × base/head × fused/unfused ×15token counts=180rows; one ascending sweep per arm, sequential timing, independent caches.
- Completed: all12sweeps/180native rows validated, with no unfused regression point among45base/head comparisons. Allsource/log/tactic hashes verified. The three rawratio tables and complete nativeCSV are in artifacts/summary.
- Archive:51files,77435bytes,SHA2566511f4e83aa0e15fd8da201d96516fc9ba1f5a62a9a240bbdd7cbb4e4fe6423b.
- Devbox deleted after successful archive verification; see artifacts/devbox-delete.log.

PLAN_REVIEW.md defines comparison/timing/provenance. scripts/bench_one.py calls the unchanged head benchmark through its native Python API. REPRODUCE.sh is the self-contained PR reproduction command. scripts/summarize_results.py validates all180rows and native stdout before deriving tables.

FC2_LAYOUT_AUDIT.md answers the layout follow-up. The benchmark preserves each backend's layout; it is not a controlled layout A/B.

The first overlay preparation rejected macOS tar metadata before timing. Only generated ._ transfer entries were removed; all source hashes were then validated. setup.log records the nightly install and unrelated optional-backend dependency warnings. A one-time build is required for native helpers absent from the SM103 nightly cache; all arms share that cache.

Published: PR5319 body replaced with PR_BODY.md, verified byte-for-byte via GitHub. Head remains f9dd3c10541e087b716772245a9d033499745048 and ready for review. RESULT_AUDIT.md independently checks raw results, ratios and tactic-control caveats. Repository checkout remains clean.
