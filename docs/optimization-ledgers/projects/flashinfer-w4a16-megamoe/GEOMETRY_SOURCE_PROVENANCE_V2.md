# Numerical geometry source provenance v2

The earlier launcher only hashed Git-tracked Python files. That omitted remote
untracked W4A16 shim/backend/test overlays. Old geometry observations and test
reports retain their original scope; their manifests cannot be backfilled with
later source hashes. Separate explicit codegen/timing manifests attest only
the snapshots they actually recorded.

Future `run_geometry_tests.sh` runs call `geometry_source_provenance.py` before
launch and after a successful run. Schema `flashinfer-w4a16-geometry-source/v2`
requires the core shim/backend/frontend/weight-preparation/public test/oracle
files to exist, discovers all Python files under the public/vendor MoE,
retained Blackwell MoE and quantization trees regardless of Git tracking, and
adds these to the tracked package/test inventory. Native scale-preparation
sources and the benchmark reference are included explicitly. Three launch/helper
files are hashed too. Installed dependency versions are recorded; this is not
full installed-dependency source closure or generated-code attestation.

Missing required files fail before launch. The post-run verifier requires the
same source/helper inventory and hashes, and rejects older unversioned manifests.
The independent per-rank `validate_records` check still requires all expected
passing numerical tests and actual compiled geometry; source attestation does
not replace that check.

Local CPU tests passed with a deliberately incomplete dummy Git index: the
untracked kernel/test are captured, missing/mutated required source fails, and
historical manifests are rejected. A real local capture also covers1571 source
files,337 explicitly required/discovered files, and3 helpers. Evidence:
`logs/geometry-provenance-v2-local-cpu-001.log` and `.json`.

The root confirmed the running numerical suite had finished before the updated
helper was transferred. The upload/run call returned success, but the managed
CLI subsequently reported the devbox missing while its log was fetched; the
remote validation log has not been verified. No remote-success claim or
historical manifest update is made. The failed fetch bytes are retained at
`logs/geometry-provenance-v2-remote-cpu-001.failed-fetch.bin`.
