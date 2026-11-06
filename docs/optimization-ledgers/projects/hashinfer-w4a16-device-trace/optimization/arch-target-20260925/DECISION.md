# Keep automatic native architecture selection

Completed 2026-09-26 UTC (2026-09-25 local). The B300 trace already contains **SM103a machine code**. `Sm100W4A16MegaMoEKernel` and the `kernel_src/sm100` directory name the shared Blackwell implementation; they do not force its compiler target. CuTe DSL 4.8 automatically selects `sm_100a` for B200 CC10.0 and `sm_103a` for B300 CC10.3. This follows the capability-based patterns used by FlashInfer. The four original trace CUBINs were independently checked as SM103a; no production target-selection patch or naming change is needed.

Keep the existing automatic target selection. The complete same-source experiment does not establish a consistent aggregate performance advantage for either target, and matched generated code shows no static instruction-count reduction. No performance optimization is retained, no kernel/source/PR files changed for this study, and both existing PRs remain unmerged.

## Measured comparison

A is portable family target `sm_100f`; B is the existing native B300 target `sm_103a`. `sm_100a` is an exact-architecture target and is not the portable B300 comparison. Ratios below are **A latency / B latency**; above 1 favors SM103a.

| Scope | Pooled ratio | First A1/B1 | Reverse A2/B2 |
|---|---:|---:|---:|
| Native EP4 decode 4–512 geometric mean | 0.994497× | 1.009698× | 0.988683× |
| Native EP8 decode 4–512 geometric mean | 1.005684× | 0.994808× | 1.014956× |
| EP4 uniform 128 global tokens | 0.974207× | 1.005275× | 0.961974× |

Uniform128 pooled medians are **279.842µs SM100f versus 287.251µs SM103a**. Its individual A1/B1/B2/A2 medians are 280.643/279.171/289.906/278.883µs, and AUTO winners differ. The pooled result therefore does not establish a reproducible 2.6% family-target gain. Both native decode geometric means also change direction between orders. Some individual shapes consistently favor one target, but the favored target varies by shape; no workload-specific policy is retained from these data.

[Complete 27-row table](PERFORMANCE.md), [order, drift and selected-tactic summary](final-summary-1.md), and [full raw timing/numerical audit](final-audit-1.md) preserve all results, including token1/2 and prefill. Raw samples and per-run medians/MADs/quarter medians are retained in [the audit JSON](final-audit-1.json).

## Protocol and checks

- Same clean HashInfer commit `40d0ceb67aa67dbf366ff61f85309e8ef53aa743`, package SHA256 `df90d2d0aa8f65881624fef55fe7bcd8e1aa91a1227124796947a45e685cd716` for both arms. No historical before timings reused.
- Reused PR11 full public-forward protocol: three warmups and 100 cold-L2 CUDA-graph CUPTI samples per row; each sample is the maximum rank span, pooled untrimmed median over 200 samples/arm/shape. Runtime alpha copies, staging, collective compute/communication and finalization are included. Preparation, routing, compilation, tuning, capture and L2 flushing are excluded.
- Fresh native eight-candidate AUTO and separate tactic/compile/driver/Triton caches per trial/rank. Serial A1/B1/B2/A2 for each scope. Native H7168/I2048/E256/top8 seeded grouped routing at 13 global token counts on EP4 and EP8; separate H6144 EP4 uniform 128 trace fixture excluded from decode geometric means. Tuner scores are hot CUDA-event measurements, separate from cold performance timings.
- Independent audit passed 12 trials, 108 cold rows, 10,800 cold samples, 51,200 hot tuner samples and 640 source/target/tactic-bound winner exports. All 640 finite/repeated-output records pass; 160 distinct rank/shape output keys match across all four runs. All 64 independent-reference records at native/uniform global T128 pass. Other shapes have repeated/finite and cross-run equality checks, not independent-oracle checks; timed replays are not individually reference checked.
- Instrumentation was disabled for timing; exported winner SASS contains no IKET PMTRIG instructions. Main-kernel PTX/CUBIN targets are explicitly audited. The process-wide target override may also affect helper kernels, so end-to-end deltas cannot be attributed solely to the main kernel.

## Generated code

[Static-code audit](codegen-final-findings.md): 384 eligible cross-target rank/trial pairs across 152 exact configuration groups have identical static instruction counts, full opcode histograms and resource reports. Their instructions differ in order, register choices and reuse annotations. All 228 eligible same-target repeated pairs have identical complete CUBINs. There is **no observed static instruction reduction** among matched winners.

All 640 exports report 96 registers, zero local/stack bytes and 1,024 static shared bytes; static shared metadata is not total dynamic allocation. 108 groups/164 exports lack an opposite-target exact match and are excluded from code-delta claims. Repeated ranks/trials are not independent compiler configurations. Static disassembly is not dynamic instruction count or causal performance attribution. Resource reports are function-matched/read-hashed but were not hash-bound in the original worker sidecar; PTX/CUBIN/SASS were.

The family arm retains `.target sm_100f` in PTX; system cuobjdump 13.2 prints its CUBIN as bare `sm_100` with ELF SM100. The native arm declares/displays `sm_103a` with ELF SM103. The audit handles those representations explicitly. Exported W4A16 PTX uses `tcgen05.mma.cta_group::2.kind::f16`: weights are decoded to BF16 before MMA; changing target does not introduce native FP4 MMA.

## Environment, boundaries and artifacts

C2/infra `fi-w4a16-trace-0925`, node `hu-pdx-38`, 8×B300, driver 590.48.01. Image `nvcr.io/nvidia/pytorch:26.05-py3`, digest `sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`; Python 3.12.3, PyTorch 2.12.0a0+5aff3928d8.nv26.05, CUDA 13.2 runtime, CuTe DSL 4.8.0, system cuobjdump/ptxas 13.2.78. Retained PTX identifies bundled NVVM 23.0.0, CUDA 13.4 V13.4.59, PTX 9.4. This is not exclusively CUDA 13.2-generated code.

Only B300 was benchmarked. B200 selection is established by source review, not a B200 run. The current homogeneous node does not qualify mixed-device detection. [Architecture source references](architecture-patterns.md) document the exact FlashInfer/CuTe paths, compatibility rules and equal SM100/SM103 helper capacity limits. [Original trace target proof](target-audit.md) independently binds all four existing trace CUBINs to SM103a.

The complete campaign finished at 2026-09-26T00:15:10Z. Its selective archive was transferred and SHA256-verified (`83d949efb3b59f1d88dd28a77759fcd055ee382e1d52b6cbc3a3932eec007793`); local receipts and winner artifacts are in `final-evidence/abba-v2`. Failed initial probes/helper attempts and qualification smoke remain separately preserved and excluded. [Commands and method](README.md), [raw campaign receipts](final-evidence/abba-v2/campaign.json), [transfer receipt](transfer-receipt.json).

The devbox remains allocated for iteration. At 2026-09-26T00:28:47Z there were no GPU compute processes and the remote HashInfer checkout was clean at the tested commit. Local HashInfer 40d0ceb and FlashInfer 74ba96d remain clean and match their tracked upstream branches. All study scripts, results and traces stay outside the source repositories and PRs.
