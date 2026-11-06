# Paired logical-stage MMA handoff gate

Control is clean fd72759b15b8d417d6c791c0382f90d14262a8e4. Candidate applies only the blockscaled kernel patch4f862f84e977a0e27fac5361644bfb751380ffcb9e3bb76894b0499148690fe4 (kernel1caf433109d00017ce9806d430644128342aa01cf8d1a3143af0888a6bbdb3a3). The independent local W4A16 source edits are excluded from both snapshots.

Reuse the preceding private-workspace source-paired harness. Each geometry runs static/CLC × PDLoff/on and balanced/skewed/nonlocal-empty/reactivated routes. Strict uint8 output equality includes source pairs and scheduler/PDL variants. Geometry remains H=I=384, tokens257,96local experts, topK2. NV usesK4 and MX usesK8 stages so the partial last acquired stage is exercised. Models and production policy are unchanged.

Four primary-device lanes:

- GPU1: NVFP4 M128/N64 oneCTA and per-token M512/N128 twoCTA, native K96 enabled.
- GPU2: MXFP8 M512/N128 twoCTA and MXFP4x8 M256/N64 twoCTA, native K32.
- GPU3: NVFP4/per-token/MXFP8 M256/N256 twoCTA and MXFP4x8 M512/N128 twoCTA; dynamic N narrow tails, channel_tiles2.
- GPU4: repeat the two NV geometries with K96 capability disabled in the project-local harness on both sources. This qualifies existing K64 code; no production branch is added.

Expected160 paired graph replays and80 GEMM codegen pairs, plus generic combine checks and captured combine kernels. Every source/role/process has an isolated compiler CWD; native C++ cache symlinks are retained. Compare full native instruction streams, resources, local/stack and uniform-register spills, normalized PTX and compile-time state. Hash all raw PTX, cubins, SASS and resource dumps.

No timing, sanitizer, exhaustive native tactic search or repo test additions. This is a compile-time interface refactor; identical native code is the performance-equivalence criterion. Original full/tail stage ordering, scale publication and pipeline waits/releases remain unchanged.
