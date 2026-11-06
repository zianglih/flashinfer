# Reuse baselines after the gated W1 layout change

These versioned tools preserve the completed baselines and the frozen
`run_split_benchmark.py` bytes for every mode. They accept exactly the native
gated-W1 preparation change from 64-row to 16-row up/gate groups on SM100/103.
Rubin keeps 64-row groups; nongated and FC2 weights keep their ordinary rows.

`preparation_contract.py` compares the two source arms before any campaign
measurement. Its AST audit permits only the group-selector addition/import/use;
the selector itself must return16 for SM100/103 and64 for SM107 and reject other
architectures. Native input creation, routing, activation preparation, weight
quantization, AUTO selection and the timed callable must otherwise be unchanged.
The native timer, routing utility, FP4/FP8 quantizers and CuTe layout utility must
remain byte-identical. The saved contract contains both exact file hashes and
the complete accepted source diffs. GPU validation of numerical equivalence is
separate from this structural audit.

For homogeneous phase measurements, the candidate adapter changes only the
gated FC1 interleave group. It retains ordinary FC2 preparation. The W4A8 adapter
already calls public preparation and stays byte-identical. W4A4, per-token
W4A4 and W4A16 continue through the native benchmark's preparation.

| Mode folder | Frozen baseline tools | Required original GPU |
| --- | --- | --- |
| `w4a4` | `scripts/` | Recorded in baseline R1 JSON |
| `per-token` | `scripts/per-token/` | Recorded in baseline R1 JSON |
| `w4a8` | `scripts/w4a8/` | Recorded in baseline R1 JSON |
| `w4a16` | `scripts/w4a16/` | 3 |
| `homogeneous` | `scripts/homogeneous/` | 2 |

Every mode retains H7168/I2048, simulated EP8/TP1, 32 local experts at offset0,
PDL on, normal AUTO in a fresh process, 10 warmups and100 cold-L2 CUDA-graph CUPTI
samples. The full grid is `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; only T1/T2
are excluded from retention. W4A8 uses its required fused finalize; the other
full-MoE modes use unfused finalize. Homogeneous results are independent BF16
FC1/FC2 phase timings, not full-MoE totals.

Use the baseline R1 JSON's recorded environment and assigned GPU. Existing
source arms and image remain the baseline commit below and
`nvcr.io/nvidia/pytorch:26.05-py3`. Set the actual committed candidate hash before
launch; the source/benchmark tree must be clean.

```bash
project=/workspace/flashinfer-w4a4-split-dynamic-n
export CUDA_VISIBLE_DEVICES=3
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1
# Keep all FLASHINFER_NVFP4_4OVER6* overrides unset.
"$project/.venv/bin/python" "$project/scripts/post-layout/w4a16/run_campaign.py" \
  --baseline-tools "$project/scripts/w4a16" \
  --baseline-repo "$project/baseline" \
  --candidate-repo "$project/candidate" \
  --baseline-sha a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
  --candidate-sha "$candidate_sha" \
  --image nvcr.io/nvidia/pytorch:26.05-py3 \
  --reuse-baseline-r1 "$project/results/w4a16-baseline-r1.json" \
  --output "$project/results/w4a16-primary-$candidate_sha"

"$project/.venv/bin/python" \
  "$project/scripts/post-layout/w4a16/summarize_results.py" \
  "$project/results/w4a16-primary-$candidate_sha" \
  --output-prefix "$project/results/w4a16-primary-$candidate_sha-summary"
```

For each homogeneous case use `scripts/post-layout/homogeneous/run_campaign.py`,
`--baseline-tools "$project/scripts/homogeneous"`, GPU2 and both `--dtype-config`
and `--phase`. The four configurations are `fp4-e8m0-sf16`, `mxfp4-sf32`,
`mxfp8-e4m3-sf32`, `mxfp8-e5m2-sf32`; phases are `fc1` and `fc2`. Reuse
`results/homogeneous-baseline-r1-v2/<config>-<phase>-baseline-r1.json`.

The campaign verifies the complete baseline source/environment/harness/log/cache
provenance before copying its raw evidence. It then executes candidateR1,
candidateR2 and baselineR2 sequentially, using the frozen original baseline
adapter for baselineR2. It archives both tool versions. The summary verifies
actual timestamp order, identical runtime fields, full token counts, histograms,
cache hashes, repeated source hashes, and the arm-specific preparation contract.
Speedup remains before/after per repeat, paired sqrt(R1*R2), and geometric means
over T4..T512 decode and T4096/T8192/T16384 prefill.

A full-grid candidate screening sweep can be retained as candidateR1. Audit
preparation before running that standalone sweep:

```bash
"$project/.venv/bin/python" "$project/scripts/post-layout/w4a16/preparation_contract.py" \
  --baseline-repo "$project/baseline" --candidate-repo "$project/candidate" \
  --baseline-tools "$project/scripts/w4a16" \
  --candidate-tools "$project/scripts/post-layout/w4a16" \
  --output "$project/results/w4a16-preparation-$candidate_sha.json"
```

Then run that mode's unchanged `run_split_benchmark.py` against the committed
candidate with the original full grid/environment and save its successful
same-stem log. Add `--reuse-candidate-r1 <screening.json>` to the campaign once
that implementation is retained. The campaign applies the complete-sweep
provenance checks to the candidate, requires it to follow baselineR1 in time,
copies its raw evidence, and proceeds directly to candidateR2 and baselineR2.
Changed candidate code, environment, harness or grid rejects reuse.

`check_saved_protocol.py` is a CPU-only task-local validation script. Its
synthetic measurements are temporary and never mixed with GPU evidence. It
checks all five mode summaries, token exclusions and rejection of changed timing
or an incorrect layout selector. Frozen original helpers are not modified.
