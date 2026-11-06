# Source-bound R12 code generation

Run `deploy_remote.py` via the project remote-box wrapper; deployment does not
launch any GPU work. After a GPU is explicitly allocated, invoke the installed
`run_capture.py` using the Python interpreter from R12 `runtime.json`:

```bash
python run_capture.py \
  --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/fc1-gather-20261028/r12 \
  --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/fc1-gather-20261028/r12/relay-codegen/k3 \
  --job ep-kimi-k3-mxfp --tokens 4096 --gpu ASSIGNED_GPU \
  --expected-kernel-sha da060e963548bba403d4afac14e32143c0854b739c217e7028f8af3764890a9a
```

Second job: `--job tp-nemo3-ultra-mxfp --tokens 16384` with distinct output `n3u`.
They can run on separate assigned GPUs, or sequentially on one. Each has a
600-second process-group timeout and refuses a GPU with existing compute PIDs.

The driver verifies all 513 source hashes, Git head, full patch, observer hashes,
persistent native-cache links, frozen copied winner cache, routes and tactics.
It requires zero retunes and CUPTI; source hashes and cache manifests are checked
again afterward. Compilation artifacts come directly from the launched Python
callable's `compiled.artifacts`. Timings are diagnostic, excluded from retention.

The capture records PTX, cubin, SASS, REG/STACK/LOCAL, spill sites, and both shared
publication patterns. Compare FC1 against exact R6's existing K3 `000-fc1` and
N3U `004-fc1` / `006-fc1` captures. Compare FC2 instruction text after removing
address/encoding/source-name noise; do not infer identity from equal resources.
