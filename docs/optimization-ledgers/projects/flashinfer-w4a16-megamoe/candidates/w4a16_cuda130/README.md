# CUDA 13.0 / pre-13.2 decode validation

The second environment is a real `nvcr.io/nvidia/pytorch:25.11-py3` B300 box, with system CUDA13.0.2 components (observed nvcc13.0.88) and the image's PyTorch2.10.0a0+b558c986e8.nv25.11 built for CUDA13.0. Root owns the CUDA13.2 optimization/source branch. This box is pinned to pushed FlashInfer6315f94ceb279db53ec3149a7d81e19b332c8dd0, with no dirty-local source overlay. All second-box logs use `cu130-` prefixes.

## Decoder and capability gate

Both split W4A16 and Mega use the same decoder in `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py`:

- Lines13–15 evaluate `_HAS_DIRECT_FP4_TO_BF16_CVT` from **`cutlass.CUDA_VERSION`**, at Python module import. No nvcc, CUDA_HOME, PyTorch runtime or driver version participates in this choice.
- `decode_nvfp4_fragment_to_bf16` accepts32/64/128 decoded values, unpacks contiguous complete16-value blocks and invokes `e2m1x16_e4m3_to_bf16x16` once per shared scale (lines167–247).
- Direct branch (lines33–63): E2M1x2 and E4M3x2 convert directly to BF16x2, then `mul.rn.bf16x2`.
- Earlier-compiler branch (lines64–135): E2M1x2/E4M3x2 convert to FP16x2, `mul.rn.f16x2`, then each lane widens to FP32 and packs with `cvt.rn.bf16x2.f32`. It preserves the BF16 decoded-weight boundary; expert global alphas remain separate FP32 epilogue operands.
- Split `moe_w4a16_kernel.py:59,526–529` calls this helper. Mega `_MegaMixedInput` inherits that local grouped kernel and calls its `_transform_tile` for both FC1/FC2. Its producer writes decoded BF16 directly into TMEM with St32x32b; both transform groups retain their disjoint halves of the same K tile. No separate Mega decoder/fallback is needed.

In NVIDIA's v4.7.1 source, `cutlass/__init__.py:39–48` binds the native `_cutlass_ir._base_dsl.get_cuda_version`; `base_dsl/version_info.py:19` constructs `CUDA_VERSION`. `base_dsl/common.py:829` explicitly identifies it as the version used to build the DSL. The wheel compiler identity must be recorded separately from systemnvcc. `target_version` checks the same native identity; it is not a compiler override. Do not spoof the constant or patch the shared decoder to claim fallback coverage.

Official sources downloaded under `sources/`:

- [v4.7.1 CUDA_VERSION export](https://github.com/NVIDIA/cutlass/blob/v4.7.1/python/CuTeDSL/cutlass/__init__.py#L39)
- [v4.7.1 build-version definition](https://github.com/NVIDIA/cutlass/blob/v4.7.1/python/CuTeDSL/cutlass/base_dsl/common.py#L829)
- [v4.6.2 quick start](https://github.com/NVIDIA/cutlass/blob/v4.6.2/media/docs/pythonDSL/quick_start.rst)
- [v4.7.1 installation requirements](https://github.com/NVIDIA/cutlass/blob/v4.7.1/python/CuTeDSL/requirements-cu13.txt)

## Compiler dependency choice

Actual native probes supersede the tagged documentation's compiler mapping:

| Installed matching DSL packages | Native compiler observed | Shared decoder | Scope |
| --- | --- | --- | --- |
| 4.6.2 base/core/cu12/cu13 | 13.3 | Direct | CPU import only; rejected as fallback evidence |
| Isolated 4.6.0 base/core/cu12/cu13 | 13.3 | Direct | CPU import and native library maps; no global-library mixing |
| Isolated 4.5.3 with cu13 | 13.1 | Fallback | Current public imports and all12 catalog succeed; below overall FlashInfer dependency floor |
| **Isolated 4.7.1 base/core/cu12 only** | **12.9** | **Fallback** | **Preferred arm: CPU105; public10 EP1/10 perEP2 rank; all12 lifecycle EP1/EP2; six exact decoder checks pass** |

The preferred arm uses `.venv-cu130-dsl471-cu12` with matching four packages installed using `--no-deps`; its selected native-extension directory contains only `_cutlass_ir.cu12.cpython-312-x86_64-linux-gnu.so`. The venv inherits image Torch and installed CUDA13.0 runtime dependencies. Global cu13 metadata remains visible through system site packages, but that global extension is outside the selected directory and is not loaded. `logs/cu130-preflight-dsl471-cu12-002.json` records native extension hash, sibling inventory, namespace paths and process maps, as well as systemnvcc13.0.88, Torch CUDA13.0, and actual compiler12.9. No version gate or package floor is patched.

This package satisfies the repository's base `nvidia-cutlass-dsl>=4.6.2a0` requirement. Native compiler12.9 is explicitly distinct from system CUDA13.0. The historical [PR4048](https://github.com/flashinfer-ai/flashinfer/pull/4048) CUDA13.0 evidence used compiler13.1; our isolated4.5.3 probe establishes that native pairing as a possible older-package control, not the final support claim. Historical PR4048 performance is not fresh B300 Mega performance.

The native loader chooses the highest compatible CUDA-major extension **within its own directory**. `CUTE_DSL_LIBS` does not override that selection. A matching cu12-only directory therefore selects a real older compiler without spoofing `cutlass.CUDA_VERSION`. `create_torchrun.py` installs a venv-local wrapper invoking that exact Python interpreter; using the global Torch console script would otherwise import the global newer DSL. The wrapper's path/content/hash are captured in `logs/cu130-torchrun-dsl471-cu12-001.json` and preflight.

`preflight.py` records exact interpreter, torchrun, systemnvcc, Torch CUDA, package/native compiler identity, shared decoder gate, module/native-library hashes and maps. `--expect-fallback` fails for the observed4.6.2/4.6.0 compiler13.3 builds. `setup.sh` and the original setup log retain the first rejected4.6.2 pairing; they must not be described as the successful final environment.

Image Torch, CUDA-Python13.0.3, CUPTI Python13.0.1/runtime13.0.85 and NVSHMEM Python0.3.1/runtime-wheel metadata3.6.5 remain pinned. The image actually loads NVSHMEM3.4.5 (confirmed by its runtime initialization message); do not call the wheel metadata the loaded version. No system CUDA replacement or global dependency-floor change occurred.

## PTX dependency audit

No unconditional CUDA13.2 direct BF16 FP4 conversion is present in the selected W4A16 Mega compute path. Its new literal dynamic-N issue helper emits `tcgen05.mma.cta_group::{1,2}.kind::f16` with TMEM operand A and BF16 operand B, mirroring the old vendor operand/descriptors; BF16 FC1 and BF16 combine avoid activation quantization.

The vendored common helper does contain `cvt.rn.bf16x2.e4m3x2` in `src/common/moe_utils.py:174`. This is used by quantized scale paths; W4A16 specializes FC1 and takes the compile-time nonquantized FC2 branch (`epilogue_refactor.py:2923–2927`) and BF16-only TopkReduce (`topk_reduce.py:300–301`). Imported source text is not evidence that this instruction is emitted. Kernel compilation and generated PTX must confirm these branches are absent. Optional IKET already has a no-op compatibility shim, and current configurations disable it.

Required generated-code proof from an instrumented, untimed run: system13.0/nativecompiler<13.2; helper flagfalse; actual Mega and split transform PTX includes `cvt.rn.f16x2.e2m1x2`, `cvt.rn.f16x2.e4m3x2`, `mul.rn.f16x2`, `cvt.f32.f16`, `cvt.rn.bf16x2.f32`; no direct `cvt.rn.bf16x2.e2m1x2`/`e4m3x2` in the transform; TMEM store and TMEM-A MMA remain. Capture registers, spills/local operations and per-role attribution before interpreting fallback performance. If extra older-compiler local traffic appears, compare with the existing FC2 router's local footprint instead of automatically calling it a transform spill.

## Validation and timing gates

1. Exact committed source plus submodule hashes; preserve imageTorch/toolkit; actual native compiler and fallback preflight. Record Nsight versions before installing newer profilers.
2. Current105 host tests with CUDA hidden; public10 EP1 and10 per EP2 rank, unchanged fixture/tolerance; real all12 auto lifecycle with empty source rank, two fixed transform groups, cache and exact graph replay.
3. Separate codegen capture proves fallback and TMEM consumption. No instrumentation in benchmark timing. Both versions support `CUTE_DSL_CACHE_DIR` (v4.6.2 env_manager.py:600, v4.7.1:615); use isolated source/compiler caches.
4. Full13 global-token grid1–4096 on realEP8 with matching split control, actual per-rank tactics and selected Mega winner, then controlled fixed-tactic cross-stack repeat. Keep source, hardware, shape, data/routing, pipeline groups and measurement conventions matched. Automatic winners and compiler versions are different axes; distinguish them.
5. Use CUPTI GPU spans for final latency; tuner host-sync scores are not final latency. Preserve the existing split-vs-Mega final BF16 reduction-boundary caveat and independent oracle. A repeated >5% slowdown is an investigation trigger, not a changed tolerance or a guaranteed near-parity result.

The original image profilers are Nsight Systems2025.5.1 and Nsight Compute2025.3.1. Newer tools were subsequently extracted into the effort directory, without replacing system CUDA or image libraries; exact versions are recorded below. CPU105, public10 EP1/10 perEP2 rank, six exact decoder/scale mapping cases, and all12-candidate lifecycle EP1/EP2 passed on the preferred4.7.1/compiler12.9 arm. Production EP8 codegen and both full13 timing arms have also completed. Existing numerical tolerances remain unchanged.

## Completed fallback functional evidence

- `logs/cu130-public-host-dsl471-cu12-001.{log,provenance.json}`:105 passed, CUDA hidden, all1572 source hashes unchanged.
- `logs/cu130-dsl471-cu12-public-001-ep1{.log,/}`:10 passed in245.68s, including first toolkit13.0 quantization JIT; actual M256/N128 geometry records for all10 tests.
- `logs/cu130-dsl471-cu12-public-001-ep2{.log,/}`:10 passed on each rank in86.46/86.12s, same observed geometry and unchanged source.
- `logs/cu130-dsl471-cu12-exact-decode-001.log`:existing `TestCuteDslMoeW4A16::test_weight_scale_mapping` six cases pass with rtol=atol=0; row/K scale variation across established1CTA/2CTA/cluster2 tactics.
- `logs/cu130-dsl471-cu12-auto-lifecycle-ep{1,2}-001{.log,/}`:independent oracle checks for every one of12 actual candidates; rank1 has zero source rows inEP2; winner agreement, persisted capacity/I cache reuse and exact repeated/changed-input graph replay pass. Tuner scores from these instrumented correctness runs are excluded from performance claims.

`logs/cu130-preflight-dsl471-cu12-003.json` adds the explicit Torch runtime version to the earlier002 package/native attestation; earlier records are retained. Fresh cross-stack source validation uses `candidates/cuda13_cross_version/common-source-6315.json`, transparently adding the clean6315 tracked autotune host test omitted from the historical overlay inventory. Every original1571 source blob and all four historical helper hashes remain identical; historical manifests are unchanged.

## Runtime-library distinction

The real CUDA13.0 image prints **NVSHMEM v3.4.5** when the runtime initializes; installed `nvidia-nvshmem-cu13` wheel metadata is3.6.5. The CUDA13.2 image prints3.6.5 despite its wheel metadata3.7.2. Preflight's `package_versions` entries describe distributions, not loaded runtime libraries. No NVSHMEM library search path is changed during the frozen full13 runs. These measurements compare the disclosed image/compiler/runtime stacks and do not isolate decoder cost alone. Actual worker maps/hashes are captured separately by `capture_loaded_libraries.py`.

## Fallback production codegen gate

`profiles/cu130-dsl471-cu12-codegen-001/` contains per-rank PTX/SASS/cubin from the public production H7168/I2048/EP8 kernel with fixed M256/N128/K256, flag4, epi(2,4), group512, atomic scheduling and epilogue return. All eight files use PTX8.8 targeting sm_103a and contain the real FP16 conversion/multiply→FP32→BF16 fallback sequence; direct BF16 E2M1/E4M3 conversion count is zero. `logs/cu130-fallback-ptx-gate-001.json` records all eight exact instruction counts. MMA consumes TMEM A (`tcgen05.mma...kind::f16 [acc],[A],Bdescriptor,...`), and transformation uses `tcgen05.st...32x32b` as required.

Every rank reports REG96, STACK112, LOCAL0 and21 static local instructions (8STL.64 +8STL +1LDL.128 +4LDL.64),6288 static SASS instructions. The aggregate local footprint matches the established explicit router footprint; independent per-role attribution is tracked separately. The single CUDA-event duration printed by this instrumented codegen run is excluded from every performance table.

`logs/cu130-loaded-libraries-control-002.json` records all eight active worker ranks and loaded binary SHA256 values: `/usr/lib/x86_64-linux-gnu/nvshmem/13/libnvshmem_host.so.3.4.5`, NCCL2.28.8, and only the selected venv cu12 native extension. The earlier map probe accidentally included the non-rank launcher as a ninth process; the corrected probe requires actual RANK0..7/WORLD_SIZE8. No result file was written for that failed assertion.

Profilers were extracted without system installation under `tools/cu130-profilers`. Verified binaries: Nsight Systems2026.2.1.210-262137639646v0 and Nsight Compute2026.1.1.0 build37634170. `logs/cu130-profiler-packages-001.sha256` records official downloaded package hashes; `logs/cu130-profiler-versions-001.log` records runtime tool versions. They are used only through explicit PATH prefixes in separate, untimed profiling runs.

## Prospective library control (CPU only; not used for benchmark)

`logs/cu130-nvshmem365-import-probe-001.{json,log}` records a separate CUDA-hidden process with only the installed wheel directory prepended to LD_LIBRARY_PATH. Torch, CuTe4.7.1/compiler12.9 and nvshmem.core import successfully, no CUDA context is initialized, and process maps contain only the wheel's `libnvshmem_host.so.3` (metadata3.6.5). ELF SONAME is unchanged, RPATH isORIGIN, and all host dependencies resolve. This establishes loader feasibility only. The active benchmark continues using image runtime3.4.5. A later source audit found no NVSHMEM/NCCL device calls in the timed fused path; bootstrap/heap differences do not establish a performance cause. GPU library-control testing is held pending baseline stage profiles and timer-alignment diagnostics.

## Completed first full13 timing run

`logs/cu130-cross-stack-full13-001/results.json` contains two successful arms (fixed thenauto), each26 raw latency rows,104 actual split selections and104 compiled-rank records; the auto arm additionally records104 returned Mega winners. Before/after source and native/interpreter guards pass. Timing uses100 CUPTI iterations, threewarmups, CUDAgraphs and coldL2 as frozen in the common runner. The isolated first-use native build took approximately18minutes before the first measured row; these builds are excluded from measured GPU spans.

At4096 globaltokens, fixedMega0.544453ms versus pairedsplit0.563108ms; autoMega0.540133ms versus pairedsplit0.570468ms. These are first-run values, not claimed cross-stack nearparity. The completed per-token/per-rank data, exact selected tactics and stackdifferences are retained for the separate cross-version analysis. The ordinary CUDA13.0 image/runtime remains unchanged. Baseline Nsight Systems32/4096 with the same fixedCONTROL has subsequently completed; no profiler duration enters the timing table.


## Completed baseline profiles and input audit

`profiles/cu130-fixed32-nsys-001/` and `profiles/cu130-fixed4096-nsys-001/` contain the raw Nsight Systems reports, SQLite databases and named-stage CSV summaries. Each has16 fused launches across all eight devices, with two launches per device:640 threads,96 registers, grid2x1x74, cluster2x1,216576 dynamic shared-memory bytes and zero reported local-memory bytes per thread. These are instrumented, non-graph captures and are excluded from CUPTI latency claims.

| Global tokens | Fused average (us; instrumented) | Fused share of named MoE stage GPU time |
| --- | --- | --- |
| 32 | 400.483188 | 98.053537% |
| 4096 | 684.055500 | 97.573128% |

The denominator excludes harness NCCL barriers and L2 flush kernels; it is not all captured GPU time. Each profile records contemporaneous HEAD6315 and10 source hashes covering the benchmark, W4A16 shim and public backend, plus command, tool version and observed resources. Unlike the frozen timing driver, `profile_tmem.sh` does not capture full source-before/after manifests. The earlier full13 source attestation and subsequent diagnostic guards provide adjacent source evidence but are not relabeled as full per-profile attestation.

`logs/cu130-input-identity-001/` records792 tensor digests across eight virtual ranks and all13 token counts (104 routed-input rows), using the exact shared benchmark input/weight factories. All ranks run sequentially on GPU0 with3.5GiB peak allocation. No NVSHMEM, MoEEpLayer or expert forward runs in this audit. It reuses only the verified completed same-stack/source native caches and records their inventory. The independent cross-stack comparison now passes all792 logical tensor byte/dtype/shape/layout matches; `logs/cross-stack-input-identity-comparison-001.json` records the comparison. This establishes identical factory inputs across the two boxes, separately from actual kernel execution.

`logs/cu130-sync-diagnostic-001.launch.log` preserves a prospective harness import failure (`analyze_ep8_autotune` was missing remotely), before any GPU work. The existing helper was uploaded without modifying the frozen benchmark, source or diagnostic scripts; retry002 completed separate fixed-CONTROL CUPTI and existing synchronized CUDA-event arms at1/256/4096, with both before/after source and native/interpreter guards passing. This comparison is not a pure barrier ablation: timing machinery and measured boundaries differ, so its rows will remain separate from the final full13 tables.


## Completed separate-method diagnostic

`logs/cu130-sync-diagnostic-002/results.json` preserves both successful arms, each24 actual compiled-rank records and24 actual split selections. Common source/helper/native identities remain unchanged. These are diagnostic rows, separate from the full13 automatic timing table.

| Global tokens | CUPTI split (ms) | CUPTI Mega (ms) | CUDA-event split (ms) | CUDA-event Mega (ms) |
| --- | --- | --- | --- | --- |
| 1 | 0.097792 | 0.105761 | 0.084400 | 0.101424 |
| 256 | 0.302353 | 0.269937 | 0.304416 | 0.278672 |
| 4096 | 0.568132 | 0.544068 | 0.585584 | 0.542448 |

Both methods keep the identical fixed Mega tactic and100 iterations, but split retunes independently. CUDA-event mode has an existing rank barrier before replay and no CUPTI callbacks; CUPTI mode uses activity spans and no per-iteration rank barrier. The0.544068/0.542448ms Mega4096 values show no substantial timer-driven reduction on this stack. This observation does not isolate a decoder or synchronization cost; matched CUDA13.2 results and separate source/runtime differences remain necessary for attribution.


## Same-node native compiler control (direct complete; fallback repeat incomplete)

`setup_direct_control.sh` was executed once to create `.venv-cu130-dsl471-cu13` beside the preserved fallback environment. Matching4.7.1 top/base/core/cu13 distributions select the sole local cu13 native extension and compiler13.3; the shared decoder gate is true. No CUDA_VERSION spoof, source change, system installation, Torch replacement or library-path change is involved. `logs/cu130-direct-control-setup-001.log` and `logs/cu130-preflight-dsl471-cu13-control-001.json` preserve the execution and identity.

CUDA-hidden identity probes show the same image Torch2.10/CUDA13.0 and identical loaded NVSHMEM3.4.5, NCCL2.28.8 and libcudart13.0.96 binaries for both venvs. All180 DSL core distribution files and eight top distribution files are byte-identical. The base distribution differs only in its run-iket console-script interpreter shebang and the resulting generated RECORD; the remaining103 files are identical. The intended changed component is the native compiler/backend library, with genuine direct versus fallback decode selected. These CPU imports establish loader identity; live worker maps will be captured during the new benchmark.

Evidence: `logs/cu130-{direct,fallback}-compiler-environment-001.json`, `logs/cu130-same-node-compiler-identity-001.json`, and `logs/cu130-same-node-entrypoint-difference-001.json`. The audit helper subsequently received formatting and an unused-import lint annotation only; the saved data describes its executed version. The fixed three-point direct-compiler run will use fresh compiler-specific native caches; the following fallback repeat may reuse only its own completed same-stack/source caches. Both remain separate from the already completed full13 stack tables.


`logs/cu130-same-node-compiler-001/direct.json` contains the completed three-point direct-compiler arm, with24 compiled and24 split records and before/after guards. The following fallback arm completed only tokens1/256 and the split4096 row. Its Mega4096 row is missing; no combined results.json was produced. This failed/partial arm is excluded from performance tables.

| Global tokens | Direct compiler13.3 split (ms) | Direct compiler13.3 Mega (ms) | Fallback repeat split (ms; partial arm) | Fallback repeat Mega (ms; partial arm) |
| --- | --- | --- | --- | --- |
| 1 | 0.071857 | 0.087633 | 0.109601 | 0.113056 |
| 256 | 0.245825 | 0.245011 | 0.301858 | 0.270274 |
| 4096 | 0.549813 | 0.509397 | 0.580724 | missing; stalled |

The fallback worker log stopped after all eight4096 compiled records at09:47:04 UTC. At09:50:52 workers remained active with no compiler processes; all eight GPUs subsequently showed100% utilization. A bounded parallel cuda-gdb13.0 attach started at09:54:57. The debugger reported driver attach error CUresult=10/no kernels, then rank1/rank6 received SIGSEGV during attachment and torchrun terminated the remaining workers. The debugger itself also crashed. No reliable GPU PC or phase evidence was obtained; the debugger-associated terminal failure does not explain the preceding stall. The GPU processes are now gone without a manual kill. Raw debugger/process/GPU/source snapshots are under `logs/cu130-same-node-compiler-hang-001/`; the terminal logs are preserved unchanged.

All16 actual direct/fallback-repeat worker maps retain identical NVSHMEM3.4.5/NCCL2.28.8 binary hashes. The post-run native JIT input audit finds17 common generated/downloaded C++/CUDA/header files, all byte-identical and no unmatched inputs. This strengthens the environment control but is not a decoder-instruction-only ablation. The previously completed fallback full13 and separate-method diagnostic remain distinct successful evidence.

The subsequent effort-only warm-cache reproduction used row/eager-warmup boundaries and a Python faulthandler deadline. It left CUPTI timestamps, graph replay and measured iteration bodies unchanged; all resulting durations are diagnostic-only. Further native cuda-gdb13.0 attachment is avoided after the observed attach failure.


## Bounded host-breadcrumb reproduction completed

`logs/cu130-stall-diagnostic-001/` and its control/launch logs record a successful source-guarded reproduction of the same1/256/4096 sequence on the preserved fallback environment. All48 rank/variant/shape row-end records exist, with exactly three eager-launch marker pairs per row. All eight Python stack files are empty: no120-second faulthandler deadline fired. The run has24 compiled records,24 split selections and identical full source-before/after inventories. The original stall did not recur under this limited host instrumentation; that is not a fix or proof of absence.

All durations are diagnostic-only: split/Mega at1=.094032/.112513ms,256=.312099/.275794ms,4096=.559731/.544373ms. They remain excluded from final performance tables. No per-iteration trace, CUDA synchronization, graph replay modification or CUPTI timestamp change was added. The helper logs host return boundaries, which do not imply GPU completion. The original failed fallback arm and debugger-associated errors remain preserved separately.

## Bounded uninstrumented fallback repeat

`logs/cu130-uninstrumented-repeat-001/` completed with exit0, all24 actual compiled records and24 split selections. Its before/after source inventories match all1572 files and the four frozen helpers, source ID `4a3716c6e6dc7f38ae84c182ffd7e06b083b4b606849031180f8939f340a8045`. The original stack entrypoint and benchmark remain unchanged. The saved shell changes only its two1800-second timeout literals to600 seconds; there are no breadcrumb, faulthandler or debugger hooks. Runtime/compiler guards confirm the original compiler12.9 fallback environment and fixed M256/N128/K256, two transform groups, raw5/decoded2/acc2.

| Global tokens | Split W4A16 (ms) | Mega W4A16 (ms) |
| --- | --- | --- |
| 1 | 0.099089 | 0.088704 |
| 256 | 0.308882 | 0.273667 |
| 4096 | 0.580915 | 0.543476 |

This is a separate three-point,100-CUPTI repeat; it does not replace rows in the full13 tables. The original stall did not recur, but remains unexplained. The4096 fallback result is consistent with the earlier successful0.544068–0.544453ms measurements. The1-token variation remains material and should not be generalized from one run. Matched same-node/source direct-versus-fallback production codegen is the next mechanism check; no NCU run has been launched.

The matched codegen check has now completed: `MATCHED_CODEGEN_002.md` and `profiles/codegen-comparison/cu130-matched-002{.json,.audit.json}` retain all16 rank captures, full source/native/runtime evidence and the focused next NCU question. Fallback adds a real FP16-to-FP32-to-BF16 producer dependency chain, including384 extra widening/packing instructions in the marked transform interval. Both compilers retain the same21 FC2-router local operations and no transform-interval local accesses. Static evidence supports a specific producer-cost hypothesis but does not establish its share of end-to-end latency. No NCU run or decoder source edit has been made.

## Register decoder A/B/A result

The isolated PR4746 register-table fallback is bitwise exact over all65536 GPU outputs but rejected by the integrated fixedCONTROL EP8 benchmark: Mega regresses24–25% atT1,8–10% atT256 and5% atT4096 against two adjacent original-decoder baselines. Both split and Mega use the candidate decoder in B. See [candidate report](register_decode_candidate/README.md) for all18 raw latencies and source/runtime proof. Clean6315 was restored; no full-grid expansion or source retention is justified for this candidate. This does not change the completed supported4.7.1/compiler12.9 fallback functional/full13 evidence.

## Follow-up conversion-tail audit

`NCU_MATCHED_001.md` records the completed all-rank initial and paired two-collective PC captures. Both have substantial profiler-induced collective launch skew; even the second capture is unsuitable for aggregate utilization/wait-share bottleneck attribution. No further NCU run is planned from that series. Exact source/runtime and source/CFG sites are preserved.

`packed_tail_candidate/README.md` records the distinct FP16-product-tail follow-up. The straightforward exact packed-bit formula is CPU-proved but lowers to a substantially larger instruction sequence and is not timed. The documented scalar hardware conversion alternative passes all65,536 original output bits under real DSL4.7.1/nativecompiler12.9, including512 canonical NaNs, with unchanged direct13.2 AST. Its same-count F2F/PRMT tail completed the original fixed three-point A/B/A and is rejected: Mega regresses16.25–21.83% at1 token,51.47–52.06% at256 and32.82–32.99% at4096 versus both controls. All18 raw timings, actual tactics and source/runtime evidence remain in `logs/cu130-scalar-tail-aba-001/` and the candidate README. Clean6315 is restored and GPUs/compiler processes are idle. No final table is changed.
