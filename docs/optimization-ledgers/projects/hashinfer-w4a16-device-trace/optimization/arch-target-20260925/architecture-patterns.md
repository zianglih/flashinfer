# W4A16 compilation target: source audit and benchmark decision

Reviewed 2026-09-25, read-only. FlashInfer source: `74ba96d551640938edde68d628b36ba404a7f331`, independent checkout `/Users/ziangli/playground/projects/flashinfer-pr5019-merge-sync-20260921/flashinfer`. Installed CuTe DSL4.8.0 source was read on C2/infra `fi-w4a16-trace-0925`, without compiling or launching GPU work.

## Finding and production decision

`Sm100W4A16MegaMoEKernel` names the shared Blackwell implementation; it does not force an SM100 compilation target. The coordinating task separately inspected the captured B300 CUBIN and reported `code for sm_103a`, CUBIN-disassembly `.target sm_103a`, and `EF_CUDA_SM103`. No retained PTX file exists in that trace collection. The source path below explains that result. No new production architecture dispatch or class rename is needed. Renaming would add source-sync churn without changing generated code, and could break tools that identify the kernel by its existing name. Record the full compilation target and actual CUBIN target beside the kernel name instead.

## Exact FlashInfer source path

Paths below are relative to the reviewed FlashInfer checkout:

| File / lines | Observed behavior |
|---|---|
| `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/common/host_utils.py:42–47` | `get_cutedsl_target_arch()` reads `CuTeDSL._get_dsl().get_arch_enum()` and formats `sm_{major}{minor}`. It reads the already-selected target; removing the suffix only produces the architecture string used by internal helpers. |
| `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:30,220,1181–1190` | Imports that helper, stores its result as `self.arch`, and supplies it to the TMEM allocator. The class name is not a target option. |
| `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py:333–357` | Calls `cute.compile` with `--ptxas-options='-maxrregcount=96'` and optional `iket`; supplies no explicit `--gpu-arch`. CuTe default/override selection controls compilation. |
| `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py:669–676` | The standalone top-k reducer also obtains its helper architecture from `get_cutedsl_target_arch()`. |
| `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py:153–195` | Standalone split W4A16 instantiates `Sm100W4A16GroupedGemmKernel` and calls `cute.compile` without an explicit target. |

## Installed CuTe target selection

Installed source root: `/workspace/w4a16-trace-sync-0925/venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass`.

- `base_dsl/env_manager.py:412–436`: detection reads compute capability, appends `a` for major≥9 and returns `sm_{major}{minor}{suffix}`. Detection failure falls back to10.0; this fallback is not evidence that a successfully detected B300 targets SM100.
- `base_dsl/runtime/cuda.py:133–135`: the device table identifies B200 CC10.0 as `sm_100a` and CC10.3 as `sm_103a`.
- `base_dsl/dsl.py:3238–3245`: `get_arch_enum()` gives the explicit compile option precedence over the environment/default architecture.
- `base_dsl/compiler.py:702–728`: supported `--gpu-arch` option is normalized through `Arch.from_string` and sets `cubin-chip`.
- `base_dsl/env_manager.py:990–1010`: `CUTE_DSL_ARCH`/automatic detection is cached. Set the override before importing/constructing CuTe objects; use fresh processes for benchmark arms.
- `base_dsl/enums.py:28–39,143–156`: `sm_100a`, `sm_100f`, `sm_103a`, `sm_103f` are recognized. Exact `a` targets require the matching architecture; family `f` compatibility requires the same major family and hardware minor at least the target minor. `cutlass_dsl/cutlass.py:1027–1043` uses that compatibility check.

The default detector queries device ordinal0. This is sufficient for the current homogeneous eight-B300 node, but not a proof of correct target selection on a mixed-architecture node. Existing FlashInfer paths below explicitly resolve the requested device for that reason.

## Established FlashInfer patterns

- `flashinfer/compilation_context.py:81–109`: general normalization preserves the minor and uses an `a` suffix for major≥10 (with separate SM12 rules).
- `flashinfer/attention/cute_dsl/fmha.py:55–65`: derives an exact target from the requested device using that normalization.
- `flashinfer/attn_scores/attn_scores.py:187–201,222–240,1050`: derives a requested-device target, guards the launch device and passes `--gpu-arch {arch}` explicitly. Its comments identify the heterogeneous-device concern.
- `flashinfer/cake_dcp.py:212–234`: chooses `sm100a` for CC10.0 and `sm103a` for CC10.3, retaining a separate family-target route for other supported hardware.
- `flashinfer/jit/flash_kda_decode.py:203–212`: documents `sm100f` as its normal CUDA12.9+ CC10.0/10.3 target, with exact `sm103a` retained for two measured GB300 latency exceptions. This is workload-specific evidence, not a W4A16 performance claim.

## Supported benchmark decision

Retain native `sm_103a` production behavior. Compare it with `sm_100f` on B300 as a diagnostic family-target experiment, using fresh processes such as `CUTE_DSL_ARCH=sm_103a ...` and `CUTE_DSL_ARCH=sm_100f ...`, separate compile/tactic caches, identical source/input/tactic/timing conditions, and independent numerical checks. The environment route is appropriate here because it also selects the architecture seen during kernel-object construction and helper preparation; adding only a later compile option could leave earlier captured helper state describing another target.

`sm_100a` is not an appropriate B300 runtime comparison: it is exact-architecture, not the portable SM100-family variant. `sm_100f` supports B200/B300 family portability; `sm_103f` is recognized but does not make a B200-compatible binary. An unsuffixed target is not an equivalent substitute for the feature-qualified targets required by these kernels.

Record full selected target, device capability, environment override, compile options and actual PTX/CUBIN target. `get_cutedsl_target_arch()` alone cannot distinguish `a` from `f`. A performance result from the environment override includes any affected helper kernels; do not silently attribute an end-to-end difference to the main MegaMoE kernel alone. These source findings make no speedup or generated-code-parity claim.

Primary documentation: [CuTe JIT compilation options](https://docs.nvidia.com/cutlass/latest/media/docs/pythonDSL/cute_dsl_general/dsl_jit_compilation_options.html) documents `gpu-arch`; [NVIDIA target compatibility](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/index.html#gpu-name-gpuname-arch) distinguishes exact `a` targets from same-family forward-compatible `f` targets.

## Additional family-name checks

The HashInfer and FlashInfer knob caches key by the active device name (`shim/knob_cache.py:82–87,157,224`), so B200 and B300 do not share a tuning entry merely because the backend class is named Sm100. The experiment still uses empty separate cache paths because changing the compilation target on the same B300 does not change its device name.

Installed CuTe4.8 `cute/arch/tmem.py:32–44` assigns both SM100 and SM103 the same512maximum and32minimum TMEM columns. The W4A16 hardcodedSM100 TMEM-capacity queries therefore do not hide additional B300 capacity in this installed toolchain. This is separate from the actual compiler target.

Installed CuTe4.8 `cutlass_dsl/cutlass.py:170–178` also maps both SM100 and SM103 to `(228-1)*1024 =232448` usable shared-memory bytes. The explicit SM100 shared-memory capacity query likewise returns the same value as SM103; no larger B300 allocation is being suppressed by that query.
