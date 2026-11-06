# Old versus current CuTe DSL MoE

Primary comparison source: `0b7fe90151340d4fca6a5ec41a91019dde743819` (PR7290). Retained head is now `7ae6244de4ad60d92b6341f8f04dc73d2b1b0549`; the later packed-scale change has its own bounded timing evidence below.
Old source: `002529e17b22567a071091053c6c4dc2a55e050e`, the merge base before the replacement kernel. W4A16 is excluded.

The latest user instruction permits the old implementation's fused finalize when its unfused path is unavailable. Current remains unfused throughout. Old NVFP4 and per-token NVFP4 are unfused; old MXFP8 and MXFP4x8 use native fused finalize. Old K3 MX modes remain unavailable because they reject SiTU. These are native backend performance comparisons; old fused accumulation does not have the same rounding contract as current unfused accumulation.

Both arms use the public functional API in the same benchmark script. The old wrapper does not admit homogeneous MXFP8 and lacks the current AUTO graph keyword; the functional API supports both. Initial wrapper and parser admission failures are preserved as diagnostic receipts, not timings.

Four model presets: V3 EP8, V4.1-Flash EP4, Kimi K3 EP8, Nemotron-3-Ultra EP8. Nemotron benchmarks routed experts with latent hidden size2048, intermediate5120,512 experts, top22 and non-gated ReLU2. It excludes latent projections, shared experts and communication. Primary-source model evidence and independently checked benchmark snapshots live under `model-provenance/`.

Use source-native public weight preparation. The original3-model current NVFP4 preparation is byte-identical to prior manual packing: six cases and9,569,304,576 payload/scale bytes, plus alpha/global scales (`model-provenance/weight-payload-proof/`). Old and new weight layouts differ deliberately. No old kernel modifications are allowed.

Timing: PDL; cold L2; CUPTI;10 warmups and100 captured samples per pass. Native AUTO per source, then old/current/current/old frozen-cache replay. Current-only K3 MX uses two current passes. Tokens1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Report1/2 but exclude them from retention. NV includes input activation quantization; MX starts prequantized. Existing compatible winner caches may be reused only with explicit source, payload, API and key-mapping proof; latency samples are fresh.

Environment: existing C3 `fi-moe-nvfp4-port-1026`,8 B300s, explicit `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2. Each model/family owns one GPU; experiments serialize on released GPUs. Native C++ artifacts are retained in persistent storage after complete source/header identity checks. DSL caches remain source-specific.

Status: all eight model/family groups completed and independently audited. The 208 cells contain 182 old/current pairs and 26 current-only K3 MX cases, totaling 78,000 primary samples. Excluding tokens 1/2, geometric speedup is +16.16% overall, +20.00% decode and +6.51% prefill. All 112 comparable decode cells improve, but standard NVFP4 and MX prefill gaps remain. See `speedups.md`, `raw-median-speedups.csv`, `raw-samples.csv`, `summary.json` and `independent-numeric-audit.json`.

Benchmark extension committed and pushed as `d02c487a`; measured kernel source is unchanged from `0b7fe901`. PR7290 now includes complete old/current raw pass medians and retains the original attribution of its historical TRTLLM tables. `pr-publication.json` verifies readback. The completed benchmark review clone was removed after confirming its file matches the pushed commit.

Completed experiments: one-CTA channel reuse loses in all four wide-prefill cases; a PDL half-grid preparation policy is neutral/slower at prefill; destination-linear scale stores regress MXFP8 by 5.04%. These policies are rejected. Their bounded exact checks, fixed-tactic samples, source receipts and cleanup records remain under `channel-tiling/`, `prepare-pdl/` and `prepare-linear-sf/`. The existing N256 tactic also loses to native N128 on Nemotron NVFP4 16K by 5.75%; no extra AUTO axis or model-specific override is added (`nemo-tactic-screen/`).

NSYS traces for V3 and Nemotron standard NVFP4 16K locate exposed preparation and FC1/FC2 differences. The selected-kernel NCU preparation profile shows low DRAM throughput with high long-scoreboard stalls and scattered stores; it does not establish bandwidth saturation. These diagnostic profiles are separate from primary timing (`profiles/`).

Retained: packed per-token FC2 scale multiplication (`7ae6244d`), four net source lines and 64–256 fewer instructions per tested FC2 specialization, with 18 paired exact comparisons and no spills. The four-model/eight-cell native CAAC screen is neutral overall (1.000217×); V4.1 prefill loses 0.688%. No end-to-end speedup is claimed. Source copies are removed, caches preserved, and the PR update is verified (`bulk-scale-pairs/`, `pr-packed-publication.json`).

The delayed bulk drain is rejected because its gains did not repeat. Protected-prefix buffering is also rejected after a stable 2.54% Nemo per-token 4096 loss; the screen stopped after four complete brackets, with the next partial case excluded. All completed/rejected source copies, including both prefix versions, are removed after verification. No active experiment remains; all eight GPUs are idle. See `round-decision.md` and `final-status.json`.

See `contract.json`, deployment receipts and worker source/command/cache receipts for full provenance. Historical measured sources and native caches remain immutable.

The ternary amax tree is also rejected: current codegen already has eight ternary instructions, the tree only shortens dependency depth8→3, decode is unchanged, and Nemo NV16K loses0.895%. Bounded exact outputs/special values passed; both source copies were verified and removed while caches/evidence remain in `amax-tree/`.
