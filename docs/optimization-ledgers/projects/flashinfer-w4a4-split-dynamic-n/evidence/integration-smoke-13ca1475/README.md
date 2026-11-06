# Production integration smoke

- Candidate: `13ca1475d96839f3bf3c46699cc63204b4d3b409`, actual imported production kernel and epilogue.
- Control: frozen `7829fc00dc7121341cc40cd4190660507e006490` kernel/epilogue classes, with task-local import normalization only. Native preparation, routing, sorting, and combine use the common candidate checkout.
- Native DeepSeek benchmark workload: H7168, I2048, 256 experts, 32 local experts, top-k8. Unfused finalization; NVFP4 uses per-tensor activation scales.
- Twelve comparisons passed: NVFP4, MXFP8, mixed MXFP4×MXFP8; T128/T16384; routing N128/N256. Every final output byte is compared; no tolerance or sampled subset.
- N128: control FC1 M256/two-CTA versus candidate logical M512/two-CTA; both use FC2 M128/one-CTA. N256: both arms use M256/two-CTA for both phases.
- Runtime class/tactic swaps only. Both arms reuse returned intermediate output/scale allocations. No source checkout changes, native cache changes, timing runs, primary baseline reruns, or sanitizer runs.
- Executed on c1 `fi-w4a4-dyn-n-1024`, GPU5. Per-run GPU/software inventory, source hashes, routing counts, and final output hashes are in the six JSON records.

`summary.json` verifies all twelve results. `raw.tar.gz` includes the six JSON/log pairs, immutable frozen source modules, helper, and exact command manifests. Archive SHA256: `84cfce7f2a578e748548c600e6ddf820edf7c02b4dbc65708c06452882a460a2` (47,431 bytes).
