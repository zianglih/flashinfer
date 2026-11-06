# Post-13ca full native A1 campaign

Prepared locally on 2026-10-25. **No deployment or GPU launch has occurred.**
Root supplies the final 40-character candidate SHA, confirms deployment, native
JIT readiness and GPU0/GPU1 availability, then authorizes the A1 launch.

This campaign reuses the original three B1 sweeps. It runs exactly one A1 sweep
for each mode: NVFP4 on GPU0, MXFP8 then MXFP4 × MXFP8 sequentially on GPU1.
All use the original frozen helpers, native AUTO with persistent bucket history,
H7168/I2048, EP8/TP1, 256 global/32 local experts, top-k8 and seed42. Timing is
10 warmups and 100 cold-L2 CUDA-graph CUPTI samples; CUPTI fallback is fatal.
All use unfused finalize; NVFP4 has per-tensor activation scales. Initial
quantization and inter-GPU communication are excluded. The full token grid is
`1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; 1 and 2 are measured but excluded
from retention aggregates. No B1 rerun or A2/B2 is part of these commands.

## Source and evidence boundary

- Previous candidate: `13ca1475d96839f3bf3c46699cc63204b4d3b409`.
- Required retained ancestry: dimension specialization `df55694942f634302ed5da60497b075c2d3b06e1`,
  PR7196 finalize rounding `2476de1e03696d122a9917ac28da8d2a70c619c5`, and weight
  cache/iKET changes `1904964d09db7f9a56d370d510ed03a0222e15c9`.
- Required changed production files: Blackwell grouped finalize core,
  Blackwell `utils.py`, and `moe_finalize.py`. Every changed file since 13ca is
  recorded, including the generic cached wrapper from retained specialization.
- Native `csrc/` and `include/` must be unchanged since 13ca. The driver does
  not rebuild native libraries, clear caches, switch checkouts, or deploy code.
- The original preparation checker remains frozen. A separate preflight removes
  only `moe_finalize.py` from its protected-byte-equality list because the user
  explicitly authorized that measured kernel change. Old/new finalizer hashes
  and the complete diff are recorded. All original timing, input, routing,
  quantization, native AUTO bucket-policy and up64/gate64→up16/gate16 checks remain.
- Exact helper hashes and retained B1 JSON hashes are pinned in
  `candidate_common.py`. All 39 B1 cache hashes are checked before launch.
  Environment must match B1, including the cache directory initialized by
  FlashInfer import. No iKET/profiling/experimental environment overrides are
  accepted unless they were already present in B1.
- Unique SHA-prefix result paths refuse replacement. Preparation hashes every
  transferred orchestration Python file; launch rejects edits after preflight.
  Native-readiness and validation logs must exist and are hashed/archived; their
  scope is supplied explicitly, without inferring an old pass count.

## Stage and launch after authorization

Use the managed `/usr/local/bin/h` for transfer/SSH to
`fi-w4a4-dyn-n-1024 -c c1 -n ziangli`. The image remains
`nvcr.io/nvidia/pytorch:26.05-py3` (B200). Copy this campaign directory into the
new remote project-local `transfer/combined-benchmark-campaign-${label}/`;
refuse an existing transfer directory. Do not overwrite the frozen benchmark
helpers. Transfer only after final SHA is known; preparation records this copy.

Run remotely after root confirms the final commit and current validation log:

```bash
set -euo pipefail
project=/workspace/flashinfer-w4a4-split-dynamic-n
candidate_sha=ROOT_CONFIRMED_40_CHARACTER_SHA
label=${candidate_sha:0:8}
campaign="$project/transfer/combined-benchmark-campaign-$label"
cd "$project/candidate"
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0
for recipe_name in ${!FLASHINFER_NVFP4_4OVER6@}; do unset "$recipe_name"; done
"$project/.venv/bin/python" "$campaign/prepare_candidate.py" \
  --sha "$candidate_sha" \
  --native-epoch-log logs/native-candidate-prewarm-before-integration.log \
  --validation-log ROOT_CONFIRMED_PROJECT_RELATIVE_LOG \
  --validation-scope 'ROOT_CONFIRMED_CURRENT_CHECKS_AND_EXPLICIT_REUSED_BOUNDARIES'
"$project/.venv/bin/python" "$campaign/launch_candidate.py" --sha "$candidate_sha"
```

The prewarm log above is historical readiness evidence for the unchanged native
sources. Root must explicitly confirm that the native epoch still belongs to the
candidate; a historical log alone does not prove that no intervening epoch switch
occurred. If root supplies a newer readiness log, use its exact relative path.

## Archive and verify locally

After all three modes exit zero, archive before source changes. From the local
project root, with the same final SHA:

```bash
candidate_sha=ROOT_CONFIRMED_40_CHARACTER_SHA
label=${candidate_sha:0:8}
python3 scripts/combined-benchmark-campaign/archive_candidate.py \
  --label "$label" --output "evidence/combined-screen-$label"
python3 scripts/combined-benchmark-campaign/summarize_screen.py \
  "evidence/combined-screen-$label"
python3 scripts/combined-benchmark-campaign/finish_candidate.py --sha "$candidate_sha"
```

The unchanged summarizer checks all 39 rows, 78 B1/A1 cache hashes, complete
routing histograms, timing/software/environment invariants, preparation/source
contracts and frozen helper hashes. The generic finalizer additionally verifies
all source hashes against the final Git commit and all three run manifests,
retained ancestry receipts, orchestration/log hashes, exact AUTO buckets and
preserved earlier profiles. It emits raw medians, selected tactics, a comparison
with the 13ca screen and a provenance receipt. Ratios are **B1/A1 screening
ratios**, not completed ABBA retention results. Root decides whether to run A2/B2.

## Local readiness validation

- All five generic orchestration modules compile; all CLI `--help` entrypoints run.
- `check_next_policy.py` passes on temporary source snapshots: authorized finalizer
  hash/diff receipt, protected timing-source rejection, invalid weight-layout
  rejection, and the existing MXFP8/mixed 13-row aggregate/timing checks.
  Output: `logs/combined-next-candidate-policy.log`.
- `scripts/post-layout/check_saved_protocol.py` passes all five existing modes.
- The unmodified legacy `scripts/unfused-blockscaled/check_saved_protocol.py`
  rejects the new finalizer byte difference as expected. It was not edited;
  `check_next_policy.py` reruns its same synthetic checks with only the approved
  finalizer policy exception. This is a methodology boundary, not a GPU failure.
- The final exact-SHA preflight, launch, archive and 39-row verification remain
  pending the frozen candidate and root's deployment/launch confirmation.
