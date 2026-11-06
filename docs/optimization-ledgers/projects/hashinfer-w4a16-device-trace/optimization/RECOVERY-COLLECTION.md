# Read-only evidence collection after pod replacement

The old `devbox-hashinfer-trace-labels-0924-0` disappeared during final
qualification. Completed native/codegen evidence is already local. The
replacement requested by the parent task is `hashinfer-trace-final-0925` on
C2/ziangli, using the same explicit `nvcr.io/nvidia/pytorch:26.05-py3` image.
This note does not establish why the old pod disappeared or that any pending
GPU validation completed.

The four read-only helpers below accept `--pod`. Omission preserves the old
pod default for historical invocations. Context `c2`, namespace `ziangli`,
container `devbox`, remote selection allowlists and all source/cubin/evidence
comparisons are unchanged. The override changes only the Kubernetes endpoint;
it does not bypass identity checks or relocate artifacts. New copy/binding
receipts record the selected pod. All four helpers accept `--remote-root`;
use the resolved output location recorded by the driver. Existing evidence
must not be overwritten.

Run from the owning project directory after the replacement's actual pod
name and the completed remote output paths are confirmed:

```bash
cd /Users/ziangli/playground/projects/hashinfer-w4a16-device-trace
trace_pod=devbox-hashinfer-trace-final-0925-0
recovery_root=/data/ziangli/hashinfer-w4a16-device-trace/recovery-20260925
trace_remote="$recovery_root/results/owned-r2-final-winner-1"
trace_local=optimization/results/owned-r2-final-winner-recovery-1

python3 optimization/pull_causal_artifacts.py \
  --pod "$trace_pod" --arm final \
  --remote-root "$trace_remote" --local-root "$trace_local"

python3 optimization/audit_causal_instrumentation.py \
  --pod "$trace_pod" --arm final \
  --source optimization/retained_owned_r2 \
  --causal-driver optimization/causal_trace_driver.py \
  --remote-root "$trace_remote" --local-root "$trace_local"

python3 optimization/final_correctness_evidence.py collect \
  --pod "$trace_pod" \
  --remote-root "$recovery_root/results" \
  --output optimization/results/owned-r2-final-correctness-recovery-1

python3 optimization/final_correctness_evidence.py audit \
  --snapshot optimization/results/owned-r2-final-correctness-recovery-1 \
  --source optimization/retained_owned_r2 --repository hashinfer \
  --output-prefix optimization/results/owned-r2-final-correctness-recovery-1-audit
```

Use a fresh local destination for every snapshot/trace collection. Match the
remote root to the resumed driver's real directory; the examples retain its
existing `owned-r2-final-*` labels. A partial/failed suite is preserved but
fails the final correctness audit. The causal artifact collector requires a
completed capture manifest. Instrumentation auditing reads the original
cubin on the selected pod, verifies its hash against the local copy, and runs
CPU `cuobjdump`; it does not compile or launch the workload. A different cubin
or source fails normally. Do not audit an old capture against a replacement
path unless that exact original cubin is present there.

The replacement's `/workspace/hashinfer-trace/optimization/results` and
`codegen` directories are symlinks into `$recovery_root`. The capture driver
records resolved `/data/...` paths, so collection and instrumentation auditing
must use those same real paths. The frozen remote source remains at
`/workspace/hashinfer-trace/optimization/retained_owned_r2`; its local audited
copy remains `optimization/retained_owned_r2`.

The native/codegen collector also accepts the override:

```bash
python3 optimization/collect_owned_r2_final_evidence.py \
  --pod "$trace_pod" --remote-root "$recovery_root"
```

There is no need to rerun this collector for the completed old-pod native and
codegen files already preserved locally. Invoke it on the replacement only
if the exact allowlisted native/codegen outputs exist there. It retains the
existing local files/hash checks and records the latest collection endpoint;
it cannot recover deleted remote files or turn partial runs into completed
ones.

These commands are collection/auditing only. They do not request a devbox,
launch GPU work, change frozen drivers/source, edit dependencies or publish
to GitHub.

CPU verification for the endpoint override:

```bash
python3 optimization/test_final_correctness_evidence.py \
  --output optimization/recovery-collector-cpu-check-0925
```

That output is explicitly synthetic. The test exercises strict positive and
negative evidence cases plus the actual selective collector program locally,
including separation of partial suites and exclusion of cache/tensor files.
For reruns, choose a new output path; the test refuses to overwrite one.
