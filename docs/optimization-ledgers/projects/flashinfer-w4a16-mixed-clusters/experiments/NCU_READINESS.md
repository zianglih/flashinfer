# Read-only profiler readiness

Checked 2026-10-24 at 21:39 UTC through the task transport, after verifying
`command -v h` resolves to `/usr/local/bin/h`. The remote command only ran
`command -v ncu`, `command -v nsys`, `ncu --version`, and `ncu --help`.
No remote files changed; no CUDA import, device/metric query, installation,
or profiling was performed. The active performance run retained GPU ownership.

```text
ncu:  /usr/local/bin/ncu
nsys: /usr/local/cuda/bin/nsys
NVIDIA Nsight Compute 2026.1.1.0 (build 37634170), public-release
```

All **22 NCU options** emitted by the validated native command builder appear
in this installed version's help. Both `all` and `mixed-only` use the same
option set. The key recipe requirements are documented:

- TCP communicator with hostname, port, and peer count.
- Application replay, strict matching, and name/grid/block matching.
- Kernel-launch lockstep and its NVTX include filter.
- `--profile-from-start=off`, demangled/regex kernel filtering, explicit metric
  lists, source import, and report export.
- `--warp-sampling-max-passes=1`; metric `group:` expansion is supported.

No CLI availability mismatch was found against
[`profile_ncu_policy.py`](../harness/profile_ncu_policy.py) or
[`NCU_RECIPE.md`](NCU_RECIPE.md). This resolves the recipe's pending
binary/version/help check only. NCU matches the version cited for historical
B300 metric evidence, but that does **not** validate this device's metric
availability or counter permissions.

Still deferred until GPU ownership permits a profile: metric/group queries and
pass count, performance-counter access, eight-peer TCP/lockstep behavior,
strict replay with stable AUTO winners, and eight complete nonempty rank
reports. Nsight Systems was checked for executable presence only.

Raw output: [`ncu-readiness-output.txt`](ncu-readiness-output.txt).
Machine-readable command, version, option-presence map, file hashes, and
remaining checks: [`ncu-readiness.json`](ncu-readiness.json).
