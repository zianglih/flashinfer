# One-CTA SF proxy-ordering repair

The four-line correction is a correctness-ordering repair with a small measured
cost, not a retained performance optimization. No prior numerical failure was
observed. The actual experiment clone remains unstaged; production promotion is
owned by the parent task.

- Control: retained `98fd3566b5f945c100f48cddacf25deb2432cbc2`.
- Repair: actual `flashinfer-sf-proxy-fence-review`, core SHA256
  `7c0fe69faab5acecafdd3d67a157f016836e149fafdc29942542d44ef4852c66`.
- Patch SHA256: `2228fac41ed9f0791e8f220f0703a4b9ae2c2e92a6a457b1d3b49fca0dbd9884`.
  Removing the exact four added lines reconstructs the control core byte-for-byte.
- Scope: after the non-bulk SF full-barrier wait, one-CTA kernels execute
  `fence.proxy.async.shared::cta` before TCGEN shared-to-TMEM copies. The existing
  group-two fence and regular TMA SFB branches are unchanged, as are arithmetic,
  layouts, API, stages, tactics, launch geometry and iKET markers.

## Ordering evidence

Ordinary non-bulk `cp.async` uses the generic proxy, while TCGEN shared-memory
reads use the async proxy. Their shared-memory handoff requires a proxy fence.
The installed CuTe 4.7.1 full-barrier wait contains no implicit proxy fence.
See the [PTX cp.async definition](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async),
[TCGEN shared-memory rule](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-shared-memory-accesses),
and [source/helper audit](../sf_readiness_profile/INHERITED_PROXY_ORDERING.md).

The emitted NVFP4 FC1 N16 PTX has the SF completion parity wait at line1125,
the new proxy fence at1131 and the first TCGEN copy at1150. The repair has one
proxy fence in PTX; the control has none. The compiled resource counts are
identical: 64 registers/thread, 197504 B dynamic shared memory, 288 threads,
128 TMEM columns, zero local bytes and one resident CTA/SM.
The [machine-readable proof](ptx-ordering-proof.json) pins the source and PTX.
Other geometries were not separately dumped for this codegen inspection.

## Environment and exact checks

New adjacent-control epoch on B200-92, GPU3
`GPU-8f15506e-8209-ef53-6b00-b04ece9e69d3`, driver580.178.04,
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.78,
Torch2.12.0a0+5aff3928d8.nv26.05, CuTe4.7.1 and CUPTI13.4.0.
The remote devbox is `fi-w4a4-narrow-1025`, c1/ziangli. Both actual checkouts
resolve unchanged native data to the existing candidate native cache. CuTe
uses a fresh private `cache/sf-proxy-fence-r1` cache.

All31 focused comparisons pass byte-for-byte:

- Seven NVFP4 FC1 cases reuse the original saved98fd output oracle without
  rerunning it: K64/384/1216, generated FP4/SF and per-token BF16 output,
  partial routes, M384 channel tails and a zero-route case. Source SF guards
  and invalid output rows remain unchanged.
- Twenty-four new paired cases cover FP4/E4M3-SF16, FP4/E8M0-SF16,
  FP4/E8M0-SF32, E4M3/E8M0-SF32, E5M2/E8M0-SF32 and mixed
  FP4-weight/E4M3-activation/E8M0-SF32. Each format checks FC1N32 quantized
  output, FC1N64 per-token BF16, FC2N16 BF16 and FC2N64 per-route scaling at
  K384/M384, with partial routing and unchanged input/invalid-output bytes.
  The new cases required one fresh control process and one repair process.
- Native phase and final output bytes also match before and after every
  timing arm. Matching the known-ordering-gap comparator is a regression
  guard, not a proof that the comparator's ordering was valid.

No primary AUTO/full-grid campaign, TRTLLM comparison or broad sanitizer was
rerun. Existing full-grid/TRTLLM evidence remains attributed to98fd.

## Native fixed-tactic cost

Same `benchmarks/bench_moe_deepseek.py` native inputs and routing; NVFP4 without
per-token scaling, unfused finalize, activation quantization excluded exactly
as in the saved native harness. Tactic:
`[16,[[128,16],[1,1],false],[[128,16],[1,1],false]]`.
Each phase and full chain runs control/repair/control/repair/control/repair
(ABA followed by BAB), ten warmups and100 cold-L2 CUDA-graph/CUPTI samples per
arm. All36 arms/3600 individual samples are archived. FC1 timing includes
preparation. Observers and retained intermediate references are disabled
before full-chain capture. The inherited helper's `publisher` arm label means
only the four-line repair class here; no publisher optimization is included.

| Tokens | Scope | Control medians (us) | Repair medians (us) | Repair cost |
|---:|---|---|---|---:|
|32|Full chain|107.4240 /107.3120 /107.7440|107.9840 /108.0325 /108.6405|+0.675%|
|32|FC1 including preparation|66.1600 /66.9760 /66.9920|66.7840 /66.8480 /66.9600|+0.233%|
|32|FC2|35.3600 /35.4240 /35.3445|35.5200 /35.5200 /35.4720|+0.361%|
|128|Full chain|144.5605 /144.7520 /144.6090|145.1205 /145.3930 /145.9200|+0.579%|
|128|FC1 including preparation|89.3120 /90.1605 /90.3525|89.9200 /90.1600 /89.6320|-0.041%|
|128|FC2|47.9360 /47.8720 /47.9520|48.3360 /48.2560 /48.1120|+0.656%|

Cost is `100 * (geomean(repair medians) / geomean(control medians) - 1)`.
These bounded measurements do not establish statistical significance or
predict every AUTO-selected geometry. They show roughly0.6–0.7% full-chain
cost for this required-ordering correction on the measured two workloads.

## Executed commands and evidence

The exact managed-SSH invocation is in `command.json`; every remote subprocess
and the runtime environment are in the archive's
`logs/sf-proxy-fence/commands.json`. The coordinator executed:

```bash
cd /Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n
python3 scripts/sf_proxy_fence_experiment/run_remote.py
python3 scripts/sf_proxy_fence_experiment/collect.py
```

Both scripts refuse existing output directories. These commands document the
completed run, not a request to repeat it. Exact remote probe invocations,
after restoring the archived helpers and source copies, were:

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n
source scripts/recovery442/env_candidate.sh
export CUDA_VISIBLE_DEVICES=3
export CUTE_DSL_CACHE_DIR=$PWD/cache/sf-proxy-fence-r1
task_helpers=$PWD/scripts/sf_proxy_fence_experiment
task_output=$PWD/logs/sf-proxy-fence

.venv/bin/python "$task_helpers/probe_exact.py" \
  --repo "$PWD/sf-proxy-fence-review" --manifest "$task_helpers/manifest.json" \
  --arm regular --output "$task_output/exact-seven.json"
for task_arm in baseline regular; do
  case "$task_arm" in
    baseline) task_repo=$PWD/profile-98fd ;;
    regular) task_repo=$PWD/sf-proxy-fence-review ;;
  esac
  .venv/bin/python "$task_helpers/probe_formats.py" \
    --repo "$task_repo" --manifest "$task_helpers/manifest.json" \
    --arm "$task_arm" --output "$task_output/formats-$task_arm.json"
done
for task_tokens in 32 128; do
  .venv/bin/python "$task_helpers/probe_native.py" \
    --control "$PWD/profile-98fd" --candidate "$PWD/sf-proxy-fence-review" \
    --tokens "$task_tokens" \
    --tactic '[16,[[128,16],[1,1],false],[[128,16],[1,1],false]]' \
    --output "$task_output/native-T$task_tokens.json"
done
.venv/bin/python "$task_helpers/compile_resources.py" \
  --control "$PWD/profile-98fd" --candidate "$PWD/sf-proxy-fence-review" \
  --output "$task_output/resources"
```

Final coordinator output:

```text
STEP exact-seven 0
SEVEN_REUSED_ORACLE_EXACT
STEP formats-baseline 0
STEP formats-regular 0
24_FORMAT_CASES_EXACT
STEP native-T32 0
STEP native-T128 0
STEP resources 0
SF_PROXY_FENCE_GATE_COMPLETE
```

Archive: `evidence/sf-proxy-fence-98fd/raw.tar.gz`, SHA256
`1fceb4bc6c19af9e8f92838e880ad8d7df957e9aae3ceaa80382ea360d8d7f52`.
It contains source snapshots, helper hashes/adaptation receipt, commands,
unchanged reused oracle, all raw samples, exact logs, PTX/cubin/SASS and actual
source/environment guards. `summary.json` recomputes each median and ratio.
The later CPU ordering proof and this note are additional local receipts;
they do not modify the immutable raw archive.
