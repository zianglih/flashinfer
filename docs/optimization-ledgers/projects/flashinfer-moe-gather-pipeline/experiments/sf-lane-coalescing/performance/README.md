# SF lane coalescing: held fixed-choice screen

Status: **cancelled without launch**. Root rejected R1 and R2 after the wide MXFP8 resource gate failed; R2's PTX/cubin matched R1. `cancellation.json` records the remote filesystem check: no launch, campaign, controller log or results exist. The original sealed plan/config below remain unchanged as preparation history.

- Control: retained `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`.
- Candidate: only swap kernel `868363559094068c95c1c5c85257ac1a351e4a59d8efb594b029e7530347faab` differs. Both source trees belong to the qualification owner; this harness creates no source copy and changes neither tree.
- Scope: the established 23 jobs / 28 supported swap and per-token model/topology/dtype arms, at **32 and 16384 tokens**. This produces 56 paired cells and 22,400 samples. W4A16 and unsupported arms are absent. Missing arms are not assigned synthetic values.
- Timing: control–candidate–candidate–control, 100 strict CUPTI samples per phase, 10 warmups, native CUDA Graph replay with cold L2. The existing runner requires frozen choice and route equality, no autotuning or timer fallback. NVFP4 includes the initial activation quantizer; per-token keeps the established activation recipe. The estimator is the ratio of geometric means of the two phase medians per arm, with all four raw medians retained.
- Runtime: existing C2 `fi-gather-pipeline-recovery-1030`, image `nvcr.io/nvidia/pytorch:26.05-py3`. `runtime-binding.json` pins the observed recovery/native-library cohort. Launch still requires fresh matching actual ELF/build.ninja hashes, native generated-command equality, Ninja no-op checks, and idle GPU observations.
- Resources: unchanged native guard and register policy. No exception for a failed resource check. All source, raw timing, stage-span, native-resource and NVML rows—including negatives and clock exceptions—must remain in the report.

`prepare_inputs.py` seals the 56 selected explicit choices, 46 token-route records, original expected-result hashes, recovery receipts and all 12 byte-identical helper files. It does not access a GPU or remote host. `prepare.py` performs filesystem-only remote preparation against the qualification owner's full/guard manifests. Its `screen/preparation.json` proves zero source copies and the held status.

The final config is `screen/perf-config.json`; its remote counterpart is `runs/sf-lane-coalescing-screen/perf-config.json` under the project storage root. The qualification manifests are under the sibling `qualification/` directory. No launch script or process is created by either preparation step.

The final launch must bind the completed qualification/native gate and root's release before choosing idle GPUs. Reuse `harness/campaign.py` and `harness/run_perf.py` without measurement changes. After completion, reuse the project's raw-evidence reporter and native resource-sequence comparator, then obtain independent replay before any retention decision. Existing initializer/readiness and TP/EP profiler results are historical context and are not replaced by this campaign.
