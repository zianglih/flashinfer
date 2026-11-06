# SM103 K96 source audit and isolated prototype

The experiment source is frozen at `13ca1475d96839f3bf3c46699cc63204b4d3b409`; parent-owned production work may advance independently. MegaMoE sources are read-only. No B200 run is evidence for SM103 K96 performance.

## Instruction and dtype contract

- Installed CuTe DSL4.7.1 has `SM103MmaMXF4NVF4Op`: E2M1×E2M1, F32 accumulation, atomK96, SF16 with E4M3/E8M0 scales. See captured [`mma.py:2125`](sources/installed/mma.py#L2125), constructor/verification at2175–2211.
- `SM103MmaMXF4Op` is E2M1×E2M1, F32 accumulation, atomK96, SF32/E8M0. See [`mma.py:1995`](sources/installed/mma.py#L1995).
- Both operands must be K-major. One CTA has M128 and N8..256 in steps of8. Two CTAs permit M128/M256 and N16..256 in steps of16. Dynamic MMA N rounded16 therefore remains compatible.
- K96 applies to FP4×FP4, not MXFP8×MXFP8 or mixed FP4×FP8. Instruction-descriptor bit31 selectsK96; this is SM103-specific. K64 remains necessary outside the explicit experiment.
- No public API, quantization, gated-channel layout, output metadata, or combine contract changes are part of this experiment.

## Operand addressing and scale factors

- The official [PTX absolute-address-mode section](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-leading-dimension-byte-offset-absolute-address) specifies the two-address solution for a48-byte operand span crossing a128-byte shared-memory segment. It requires SW128 with16-byte atomicity, K-major operands, and base-offset0. Matrix start/LBO/SBO addresses are16-byte aligned.
- CUTLASS explicitly sets the SMEM descriptor absolute-LBO mode, fills its leading field from a second descriptor's start address, and sets instructionK=96: [`mma_traits_sm100.hpp:4589`](sources/cutlass/mma_traits_sm100.hpp#L4589). [Pinned upstream source](https://github.com/NVIDIA/cutlass/blob/b46b16d003484063bca4ed365e44095c4c6ed633/include/cute/atom/mma_traits_sm100.hpp#L4589).
- CuTe's supported `tcgen05.make_umma_smem_desc(..., next_src=...)` builds that descriptor: [`helpers.py:406`](sources/installed/helpers.py#L406).
- K96 consumes6 SF16 scales or3 SF32 scales per row. SF data IDs select the subword start. The dense SM103 kernel has an explicit single-scale TMEM iteration view and advances it by6/3; see production dense source `flashinfer/gemm/kernels/dense_blockscaled_gemm_sm103.py:1129–1195`.
- SM103 dense source uses a different SF row factorization `(8,4,4):(16,128,4)` rather than the existing split contract `(32,4):(16,4)`. See [`blockscaled_layout.py:529`](sources/installed/blockscaled_layout.py#L529) and [`sm103_blockscaled_layout.hpp:48`](sources/cutlass/sm103_blockscaled_layout.hpp#L48). The prototype must prove TMEM scale placement while retaining the public split layout; adopting the dense global layout would change caller preparation.
- Current SM100 MegaMoE uses `sm100_utils.make_blockscaled_trivial_tiled_mma`, not the SM103K96 op: `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/kernel_fc12.py:296–321`. The newer Blackwell fork similarly delegates to the SM100 helper (`.../block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:453–466`).
- The existing dense SM103 dispatcher is disabled on Blackwell with a comment about absent CuTe APIs (`flashinfer/gemm/gemm_base.py:8570–8583`), but the installed4.7.1 package demonstrably contains both SM103 ops. Availability of the op alone does not validate the full dense dispatcher.

## First isolated design

`build_prototype.py` copies frozen13ca core/dependencies into `k96_trial/`. Initial support is explicit NVFP4 SF16/E4M3, per-tensor activations, M256N128/two-CTA, unfused FC1/FC2. It uses K768 per stage, eightK96 instructions, two operand stages, the same dynamicN descriptor, and the existing fused epilogues. This keeps each K96 operand within a fully acquired stage, avoiding a first prototype that changes cross-stage barrier lifetimes. Descriptor splits occur at K256/K512 boundaries; Gather4 still moves128-byte chunks. Native tails are zero-filled by existing load paths.

The first version retains current SF storage/copy and adds a single-scale TMEM addressing view. B300 random-data checks passed with varying scale bytes for FC1 and FC2 at K768/N17, followed by K64/256/832/2048/7168 with N128. This establishes placement through reduction tails and repeated stage reuse for the bounded cases. No public layout conversion or extra kernel is required. Native routed phase comparisons completed and rejected this wide-stage version for performance; see the raw medians below.

## B300 environment

- Managed CLI `/usr/local/bin/h`; C2 devbox `fi-w4a4-k96-1025`, namespace`ziangli`, bare, 8×NVIDIA B300 SXM6 AC, driver595.91.07.
- Image `nvcr.io/nvidia/pytorch:26.05-py3`; actual system nvcc13.2.78; PyTorch runtime`2.12.0a0+5aff3928d8.nv26.05`, CUDA13.2, compute capability(10,3).
- Parent verified the live [NGC catalog](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch) and [release matrix](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html):26.05 is the latest listed CUDA13.2 image;26.06 onward uses CUDA13.3+.
- Candidate clone `/workspace/flashinfer-w4a4-split-dynamic-n/candidate`; system-site-packages venv at the adjacent`.venv`; CuTe4.7.1, cupti-python13.4.0, CUPTI13.4.58. Exact commands are in `provision.sh`; raw remote logs are `logs/k96-provision.log` and `logs/k96-pip-freeze.txt`.
- Torch constraint uses installed wheel metadata (`importlib.metadata.version('torch')`): this image's runtime`torch.__version__` suffix differs from pip metadata. An initial resolver failure using the runtime string changed no source; corrected metadata constraint succeeded.
- GPUs0/1 are assigned to this experiment. The B300 primary campaign has not been launched; this is an initial screen only. Adjacent current 13ca versus K96 phase diagnostics use 10/100 cold-L2 CUDA-graph CUPTI after exact checks.

## Generated-code check

Resource probes for FC1 K7168 and FC2 K2048 report the same register allocation for both arms: 78 registers/thread for FC1 and 124 for FC2, zero stack/local allocation and no LDL/STL instructions. The generated PTX/cubins/SASS are retained under remote `logs/k96-dumps-fc1` and `logs/k96-dumps-fc2`; `inspect_resources.py` records SHA256 and emitted MMA instructions. These two repeated exact comparisons inspect generated resources, rather than extending numerical coverage.

## First routed screen: wide K768 / two stages (rejected)

Both phases use fixed M256N128 / two-CTA geometry, actual benchmark preparation and routing, per-tensor NVFP4, and unfused finalize. All four native output comparisons were byte-exact (FC1 includes output scales). Timings are isolated phases, not full-pipeline retention evidence; 10 warmups / 100 samples, cold L2, CUDA graph, CUPTI with fallback treated as an error.

| Tokens | Phase | Frozen 13ca K64 (us) | K96 K768 / 2 stages (us) |
|---:|:---|---:|---:|
| 128 | FC1 | 96.641 | 100.673 |
| 128 | FC2 | 55.3445 | 57.120 |
| 16384 | FC1 | 307.6985 | 356.5625 |
| 16384 | FC2 | 152.577 | 161.6655 |

Raw samples and commands: `logs/k96-native-fc{1,2}-r1.json`, corresponding `.log`, and `k96-native-fc{1,2}-r1.command.json` beside this document. The first native invocation compiled the fresh SM103 `moe_utils` cache before measurements.

## Cross-stage prototype

`build_crossstage.py` creates `k96_trial/cross_core.py` from the immutable wide-stage source. It retains K256 loads and five operand stages, rounds the final reduction group to three zero-padded stages, and reserves three SF blocks per operand in TMEM. An acquire cursor and a separate release cursor preserve exact stage ownership. In each K768 group, the MMA warp acquires stage 0 and issues two K96 MMAs; acquires stage 1, issues the crossing MMA, releases stage 0 and issues two more; then acquires stage 2, issues the crossing MMA, releases stage 1, issues the final two and releases stage 2. Each release uses the existing UMMA completion barriers, and both CTAs retain the CP completion relay.

The three scale banks are at 16-column intervals, formed by arithmetic on the original Float32 TMEM pointer before recasting to the 8-bit scale type. The single-scale iteration view spans those banks. Public layout and fused epilogue are unchanged. Initial K768 / partial-N17 FC2 matched exactly; tail and repeated-stage checks precede native performance screening.

The cross-stage TMEM allocation is explicit: N128 reserves 256 accumulator columns (two banks), 48 SFA columns, and 48 SFB columns, for 352 within the 512-column allocation. N256 would need 144 SF columns because SFB has two 128-row blocks; the current 448-column overlapping accumulator windows would total 592 and do not fit. Two N192 accumulator banks plus those scales would total 528. This experiment does not extend to those geometries or assume compatibility with independent FC1 overlap prototypes.

## Cross-stage native screen (rejected)

All 12 distinct partial-N17 checks passed for FC1/FC2 at K64/256/768/832/2048/7168; two full-N128 generated-resource checks and all four native routed comparisons passed. Initial/profile repeats are not counted as new coverage. Cross-stage register allocation was 72/thread for FC1 and 120 for FC2, with zero stack/local storage and no LDL/STL.

| Tokens | Phase | Matched frozen 13ca K64 (us) | K96 cross-stage (us) |
|---:|:---|---:|---:|
| 128 | FC1 | 96.7365 | 105.6005 |
| 128 | FC2 | 55.4725 | 58.1440 |
| 16384 | FC1 | 306.3380 | 342.6270 |
| 16384 | FC2 | 152.6570 | 169.5690 |

The adjacent controls were remeasured because this is a new paired experimental screen, not a primary baseline rerun. Both K96 variants are rejected for retention. No full AUTO campaign, sanitizer, all-format extension, or production integration was performed for K96.

One short NCU pair on native FC1 T16384 reproduced 305.632 us K64 versus 342.336 us cross-stage. K64/cross tensor-pipe active percentages were 34.53/22.15, DRAM throughput 26.02/23.16%, L1/TEX throughput 72.40/53.28%, and long-scoreboard stalls 69.58/66.48% of cycles per issued instruction. These counters do not show tensor saturation; the extra cross-stage bookkeeping and loading schedule did not turn the wider instruction into a phase gain. Kernel profiles are diagnostic and are not used as primary timing measurements. The profile does not isolate a single causal bottleneck.

Reproduce the native pairs from the effort root after provisioning/sync:

```bash
python3 scripts/sm103_k96_audit/launch_native.py fc1 1
python3 scripts/sm103_k96_audit/launch_native.py fc2 0
python3 scripts/sm103_k96_audit/launch_native.py fc1 1 cross
python3 scripts/sm103_k96_audit/launch_native.py fc2 0 cross
```

Output paths are protected against overwrite; choose new labels in the launcher for a new campaign. The task-local command manifests record the full remote environment and arguments.
