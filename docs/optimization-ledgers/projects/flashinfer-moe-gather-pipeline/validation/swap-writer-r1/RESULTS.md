# FC2 writer-owned bulk commit qualification

Base `82254e206a44b95d9925e4594fac936731f80d21`, control kernel SHA `194b903854c74fc79a422ec67a0539d9f57414987c8cc0a3325e94226d642eb4`; candidate SHA `2d7e69d946ae85c255061501df5aaf7673aca468204db0646742695b7a4cbe07`. The prototype changes only the indentation of the existing FC2 bulk commit into its existing two-warp writer branch. Source remains unstaged. The frozen candidate also contains the separately qualified W4 utility change, which these swap kernels do not call.

C2 B300 GPU6, container `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.1. Native compiler options and source-role caches are unchanged; the capture only keeps PTX/CUBIN artifacts. The parent13245-file manifests were verified before/after the campaign, with scoped parent-bound source checks per process. Full source receipts, commands, logs and codegen are in `full-evidence/`.

- 20 exact calls passed: ten control/candidate pairs across W4A4, per-token NVFP4, MXFP4x8 and MXFP8.
- Actual FC2 bulk output followed by SIMT tails: tokens193/385, N128/256, M128/256/512, one/two-CTA, ordinary scheduling, PDL off/on, nonoverlapping/overlapping accumulator windows and a partial H384 K extent. These are targeted correctness cases; the forced two-cluster limit is correctness-only.
- 60 loaded kernels (30 pairs): all zero local bytes; native resources including register count identical between arms.
- All 20 FC1/finalizer paired raw cubins are identical. All10 FC2 normalized PTX deltas consist solely of nonwriter branch destinations, bypassing36 static commit sites in total. The existing writer commit and following common block are preserved. Native SASS retains the real writer flushes; the pilot also removes the two now-unneeded pre-flush NOPs. Static instruction totals can include alignment padding and are not an executed-work count.
- CLC boundary correction: the correctness-only `sm_count=2` cap causes the current launcher to disable CLC, including cases whose requested tactic flag is true. All20 captured swap kernels used ordinary scheduling. These calls do not establish zero-tolerance CLC coverage; native CAAC uses its real frozen CLC decisions but is performance evidence.
- No full test suite, sanitizer, autotuning or timing was part of this qualification. N16/no-bulk paths are unchanged but not separately exercised here. Retention depends on the parent compact CAAC campaign.

Local reproduction of artifact checks:

```sh
python3 validation/harness/compare_swap_validation.py validation/swap-writer-r1/full-evidence
python3 validation/swap-writer-r1/verify_control_flow.py
```

Evidence archive SHA `58efe517a2e155cbb39176e90eb5e5404d356f4d8c10327b4b2d78fe3852f442` (4,195,860 bytes). `full-evidence/control-flow-proof.json` and `full-evidence/comparison/summary.json` bind checks to the preserved source and artifacts.
