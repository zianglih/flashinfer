# Current-best W4A16 full-metric profiles — 056ce / 0909e

Downloaded **10/10 reports**: two Nsight Systems captures and eight Nsight Compute rank reports.

Published commit `056ce0d090d425ee09171e47f6faea61c76c9551`; exact captured source `af938d808556e72925933208f0844cd92f44dff5cc7f407b050897c5660b2e9e`. These reports profile the retained eight-tactic implementation. This v2 bundle contains a new NCU `--set=full` capture on replacement 0909e and reuses the two completed 0909d NSYS traces. The physical node hu-pdx-115 and all eight GPU UUIDs match; each container and cache boundary is separately recorded. The earlier PC-only bundle remains unchanged.

| Capture | Report | Bytes | SHA256 |
|---|---|---:|---|
| NSYS T32 | [ep_w4a16_megamoe_t32.nsys-rep](../current-best-0909d-nsys-t32-001/ep_w4a16_megamoe_t32.nsys-rep) | 1,621,664 | `0d154e31b42b825835a3783276d49d95d0c418889ef9f71daef1b7aa366a9ea2` |
| NSYS T4096 | [ep_w4a16_megamoe_t4096.nsys-rep](../current-best-0909d-nsys-t4096-001/ep_w4a16_megamoe_t4096.nsys-rep) | 1,621,647 | `c6679fff0ee36ae37e5a106fb524f73d38e5aa5c84646833d8e40e579a8f311d` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank0.ncu-rep](../current-best-0909e-ncu-full-t4096-001/ep_w4a16_megamoe_t4096.rank0.ncu-rep) | 135,629,765 | `31873c13c3448e823052f4559520d0f2881beab34f2c0f34b7f1cdaa32fdbc0c` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank1.ncu-rep](../current-best-0909e-ncu-full-t4096-001/ep_w4a16_megamoe_t4096.rank1.ncu-rep) | 259,013,646 | `35fd551dd4306770ad98dc7e1f0572d46fc0efcf08a086bc3a894f2de4a2afad` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank2.ncu-rep](../current-best-0909e-ncu-full-t4096-001/ep_w4a16_megamoe_t4096.rank2.ncu-rep) | 19,842,763 | `cc99aa5a91e47df9e8ffd77aa347bab81817bc8d1c19517e2842fbc685840019` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank3.ncu-rep](../current-best-0909e-ncu-full-t4096-001/ep_w4a16_megamoe_t4096.rank3.ncu-rep) | 67,490,136 | `c1bebd2863d1f3e64732dd601f206671feb7eb2188a51a07dbb4f36fe745b2f1` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank4.ncu-rep](../current-best-0909e-ncu-full-t4096-001/ep_w4a16_megamoe_t4096.rank4.ncu-rep) | 284,794,954 | `c973f4d8ad528bfb047abe3790b56dc6d0d99712c0eeec980cab28552a390818` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank5.ncu-rep](../current-best-0909e-ncu-full-t4096-001/ep_w4a16_megamoe_t4096.rank5.ncu-rep) | 370,299,732 | `cbc27fde0c6d78f80402ef9b7bae7785f210a05a76d163381fcc29a640d1c264` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank6.ncu-rep](../current-best-0909e-ncu-full-t4096-001/ep_w4a16_megamoe_t4096.rank6.ncu-rep) | 64,949,639 | `2a45a72a366a3716576e026964ac7cbb932ddf255909f2f125a603d4da1ac550` |
| NCU T4096 | [ep_w4a16_megamoe_t4096.rank7.ncu-rep](../current-best-0909e-ncu-full-t4096-001/ep_w4a16_megamoe_t4096.rank7.ncu-rep) | 202,194,150 | `0789c39fb5b386da7831e8993781fcfdd20fefc7205200caf3d490b469a349f9` |

The adjacent capture folders include original commands, logs, source manifests, preflight, hardware UUIDs, tool versions, timestamps and closed execution/download receipts. NSYS SQLite exports and kernel CSV summaries, full NCU raw metric CSVs in both automatic and base units, per-report section/details exports and API source/action verification are included. [manifest.json](manifest.json) and [SHA256SUMS](SHA256SUMS) cover the downloaded files and supporting metadata.

## Capture setup

Container `nvcr.io/nvidia/pytorch:26.05-py3`; eight NVIDIA B300 SXM6 GPUs, driver 590.48.01; PyTorch 2.12.0a0+5aff3928d8.nv26.05 with CUDA 13.2; system nvcc 13.2.78. CUTLASS DSL 4.7.1 reports its separate CUDA 13.3 backend. Nsight Systems 2026.2.1.210; Nsight Compute 2026.1.1.0.

Both shapes use EP8, BF16 activations/NVFP4 weights, H7168/I2048, E256, top-k8, M256/K256/C2/S2/F4, atomic-counter scheduling and group_hint=512. T32 uses N64/epi_warps; T4096 uses N128/reuse_dispatch_warps. These exact dictionaries come from the completed retained AUTO run `1a763323d8f36f670ac2213f3580236a884a0fb033fe799ce21cfb31ec4575da`. Full dictionaries and original shell commands are in [metadata/binding-full-0909e.json](metadata/binding-full-0909e.json) and the capture folders. Capture completion is established by each completion.json; the separate binding preserves the launch declaration.

NSYS records two eager calls per rank after three warmups, with cuda-sw tracing. NCU requests one profiled Mega call per rank with the full metric set, coordinated strict application replay, grid matching and lockstep Mega NVTX launches. The custom metric filter is omitted, so the benchmark emits `--set=full`. Overall full-counter replay passes are unrestricted. `--warp-sampling-max-passes=1` only limits adaptive PC-sampling passes. The saved report API verifies one Mega action per report and records its replay metric below. The report filename suffix comes from NCU's `%q{RANK}` macro and names the torchrun distributed rank. NCU communicator peer IDs are a separate numbering scheme; their mapping is preserved in manifest.json and ncu.log. The report API supplies each action's CUDA device identifier and hashes its embedded project source against the captured manifest.

## Reading the timing

These instrumented eager calls show substantial inter-rank launch skew. Their kernel durations, whole-device spans and aggregate CSV GPU time are **not** the AUTO cold-L2, per-iteration rank-MAX latency and do not replace the published timing table. Each NSYS trace contains exactly 2×8 Mega kernels, with 96 registers/thread, 640 threads/block and zero local memory.

| Tokens | Eager call | Across-device start skew (µs) | First start to last end (µs) | Shortest rank kernel (µs) |
|---:|---:|---:|---:|---:|
| 32 | 1 | 909.747 | 1064.084 | 154.337 |
| 32 | 2 | 716.643 | 870.201 | 153.345 |
| 4096 | 1 | 1110.277 | 1540.957 | 430.531 |
| 4096 | 2 | 199.200 | 637.008 | 437.316 |

These saved observations join CUPTI_ACTIVITY_KIND_KERNEL.demangledName to StringIds, filter Sm100W4A16MegaMoEKernel, then pair calls by per-device start order. Raw rows and arithmetic are in [nsys-observations.json](nsys-observations.json).

## Source mapping

Open the .nsys-rep files in Nsight Systems and the .ncu-rep files in Nsight Compute. For source lookup, check out commit 056ce0d090d425ee09171e47f6faea61c76c9551 and map the captured repository prefix `/workspace/flashinfer-w4a16-megamoe/flashinfer/` to that checkout. The main Mega class is in `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/kernel.py`; shared decode/MMA routines are in `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`. Per-capture source-manifest.json records exact hashes. The included publication association confirms all 1,575 measured source files match that commit; remote Git HEAD is not used as a source identity. Driver/DSL compilation caches are deliberately omitted, so generated/cache paths may require source-prefix mapping or the recorded DSL installation.

## Verification and reproduction

All indexed captures have passed completion receipts and closed original/download sessions. Local report sizes, SHA256 hashes and file headers were checked against the receipts; the NSYS SQLite exports were read without modifying them. No profiler or benchmark was rerun for packaging. The final [source/native/idle closure](../current-best-0909e-ncu-full-closure-001/closure.json) confirms the exact retained source, records fresh first-build native additions and no remaining GPU compute processes; any diagnostic-log delta is recorded separately. Use SHA256SUMS from the project root (or archive root) to verify the included paths.

## Full NCU metric coverage

| Distributed rank | CUDA device | Mega actions | Metric names | profiler__replayer_passes | Embedded project sources |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 1 | 2472 | 40.0 | 14 |
| 1 | 1 | 1 | 2472 | 40.0 | 14 |
| 2 | 2 | 1 | 2472 | 40.0 | 14 |
| 3 | 3 | 1 | 2472 | 40.0 | 14 |
| 4 | 4 | 1 | 2472 | 40.0 | 14 |
| 5 | 5 | 1 | 2472 | 40.0 | 14 |
| 6 | 6 | 1 | 2472 | 40.0 | 14 |
| 7 | 7 | 1 | 2472 | 40.0 | 14 |

Exported sections: Compute Workload Analysis; GPU Speed Of Light Roofline Chart (Overview); GPU Speed Of Light Throughput; GPU and Memory Workload Distribution; Instruction Statistics; Launch Statistics; Memory Workload Analysis; Memory Workload Analysis Chart; Memory Workload Analysis Tables; Occupancy; PM Sampling; Scheduler Statistics; Source Counters; Warp State Statistics.

The installed generic full set lists 22 sections and estimates 7,314 metrics; each actual report exposes 2,472 metric names and 14 CLI-rendered section headings. Those counts have different scopes. Hierarchical roofline sections extend SpeedOfLight; NUMA and NVLink properties are present, and this kernel uses the SIMT execution model. Each report has valued named counters for SM (1,072), SMSP (262), DRAM (32), LTS (211), and L1TEX (314). Metric-name counts also include derived, metadata and instance-only/valueless entries: aggregate values are available for 2,459 names per report, except rank 2 with 2,436. All 14 embedded project source files per report match the captured manifest.

**Recorded limitations:** all peers report six C2C `ctc__rx/tx_bytes_data_user` variants unavailable. Some derived throughput percentages exceed 100% and per-rank duration fields vary substantially under coordinated application replay. Preserve these raw values as diagnostic artifacts; do not interpret them as stable physical throughput or AUTO latency. The [coverage record](../current-best-0909e-ncu-full-t4096-001/full-report-verification/coverage.json) contains exact counts, warnings and per-rank fields.

Logged application replay pass IDs, `profiler__replayer_passes`, and `smsp__pcsamp_aggregated_passes` are preserved separately; they have different semantics and were not required to be numerically equal. Warnings and unavailable metric values remain visible in the original logs and exports.

[Full API verification](../current-best-0909e-ncu-full-t4096-001/full-report-verification/summary.json) preserves every metric name, selected resource/replay fields and embedded source hash. The adjacent per-rank details and raw CSVs expose the full counters. These instrumented counters and replay durations are diagnostic evidence, not a replacement for the published AUTO latency table.
