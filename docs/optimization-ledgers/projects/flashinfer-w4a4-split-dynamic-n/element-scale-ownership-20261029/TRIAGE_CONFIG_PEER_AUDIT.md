# A/B triage configuration audit

Passed read-only audit of the current rebound-cache configurations. No GPU runs or source edits. Replayable checks and complete route/tactic bindings are in `audit_triage_configs.py` and `triage-config-peer-audit.json`.

| Coverage | EP | TP |
|---|---:|---:|
| V3 |5 modes|5 modes|
| V41F |5 modes|3 modes|
| K3 |4 modes|4 modes|
| N3U |5 modes|5 modes|

Each variant has31 jobs,36 supported model/topology/dtype arms, and72 cells at tokens4/4096. The established exclusions remain K3 MXFP8 and V41F TP MXFP4x8/MXFP8. No TRTLLM, CUTLASS or fused candidate is introduced.

- A/B job definitions, current658a control, seven observers, register policies and timing flags match. Only candidate source/cache paths and output destinations differ. All3,165 source-file hashes per arm match their local canonical/review sources; the13,245-entry tracked manifests differ only in the two owned kernels.
- All1,455 original frozen cache files match their historical receipts. All1,424 entry hashes and72 selected explicit key/runner/tactic/profiling-policy identities match the cache-rebinding receipt. This imports existing choices into the observed runtime namespace without changing entry bytes or tuning. Original expected-output files remain hash-bound to their completed historical receipts.
- Native flags preserve public functional API, swap-AB, unfused finalize,10 warmups,100 strict CUPTI cold-L2 graph samples, and no autotuning. Observer-only W4A4/W4A16 filtering selects the intended result. NVFP4 includes initial quantization; W4A16 consumes BF16 directly; MX omits initial quantization. Per-token recipe scope remains unchanged.
- Exclusive eight-lane assignment covers each job once. Each variant uses fresh same-GPU C-A-A-C with source/cache checks, route/tactic identity checks, driver register/local-memory guards and NVML telemetry. The existing analyzer uses the geometric mean of each arm's two phase medians, matching the declared split campaign contract.

No configuration blocker found. This is not run-completion or performance evidence. Rebound cache files themselves were not fetched locally; their original bytes and rebinding receipt were checked independently, and the runtime driver checks every selected hit against the original exact identity. The namespace-mismatch attempt stays separate from the new campaign.
