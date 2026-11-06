# BF16 NVFP4 optional in-kernel FC2 reduction validation

Base source: `4bc278892b3ced0a8c81501f858de517931e2ae9` plus the local IKR patch. Exact local source hashes are in `source-manifest.json`; GPU source upload hashes and launch commands are in `../gpu-setup/`. No HashInfer files changed.

Environment: dedicated C2 node with 8 NVIDIA B300 SXM6 AC GPUs, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA toolkit13.2.78, imageTorch2.12.0a0+5aff3928d8.nv26.05, CuTeDSL4.7.1/cu13. See `../gpu-setup/verified.json` for complete versions.

- `host-contracts.log`: 26 passed. Session permission defaults, both candidate sets, cache separation, deterministic fallback, global-scale capability rejection for BF16 and BF16xMXFP8.
- `single-reference-v2.log`: 20 passed. Original W4A4 paths, BF16xNVFP4 default paths and IKR N64/N128, regular/tail/single-expert geometries, non-unit global scales and routing, repeated eager and graph execution, original bit-exact cancellation fixtures.
- The optional BF16 atomic combine uses existing repository term-magnitude tolerance; default-path comparisons remain unchanged. The graph-replay test additionally replays all-zero activations and requires exactly zero output.

The first whole-file test run incorrectly pinned the W4A4 control to M256 with its default cluster1, causing six test-configuration failures. The final test restores its original knobs; all controls pass. This was a test-only issue, with no production change. A torchrun standalone attempt could not resolve the node hostname before worker launch; final multirank invocation uses explicit127.0.0.1 rendezvous.

- `multirank-v2.log`: all 9 selected tests pass on each of 2 ranks (65.81s). Includes random/skew routing, unequal input counts, an empty source, all-empty/refill, static and atomic-counter scheduling, IKR off/on, and lockstep graph mutation/zero-input replay. No GPU compute process or allocation remains after completion.
