# W4A16 Warp Specialization Constraints

This note records the hardware and CUTLASS contracts that govern the W4A16
CuTe DSL kernel's move from four transform warps to eight dedicated transform
warps. It separates documented requirements from measurements so future tuning
does not rely on register-budget guesses or accidental behavior.

## Primary Sources

- NVIDIA PTX ISA, `setmaxnreg`:
  https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg
- NVIDIA PTX ISA, Tensor Memory access restrictions and `tcgen05.st`:
  https://docs.nvidia.com/cuda/parallel-thread-execution/#tensor-memory-access-restrictions
  https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-instructions-tcgen05-st
- CUDA C++ Programming Guide, occupancy, launch bounds, and register limits:
  https://docs.nvidia.com/cuda/cuda-c-programming-guide/#occupancy-calculator
  https://docs.nvidia.com/cuda/cuda-c-programming-guide/#launch-bounds
- CUTLASS register reconfiguration policy:
  `3rdparty/cutlass/include/cutlass/gemm/kernel/sm100_gemm_tma_warpspecialized_input_transform.hpp`
- FlashInfer exact-budget register allocation:
  `flashinfer/cute_dsl/attention/monolithic/mla_decode_fp8.py`
- CUTLASS eight-transform-warp example:
  `3rdparty/cutlass/examples/python/CuTeDSL/blackwell/mixed_input_fmha/mixed_input_fmha_prefill_d256.py`
  and `mixed_input_fmha/prefill_helpers.py`.

## Register Reconfiguration Contract

PTX defines a per-CTA register pool. `setmaxnreg.dec` returns registers to that
pool, while `setmaxnreg.inc` blocks until the requested registers are available.
The immediate is an absolute per-thread maximum, must be a multiple of eight,
and must be between 24 and 256.

PTX states that all four warps in a warpgroup must execute the same
`setmaxnreg` instruction and must synchronize before a subsequent
reconfiguration. Some maintained CuTe DSL examples use different targets for
role-specialized warps 4-7, so that statement cannot by itself establish how
every existing kernel behaves. The CUTLASS C++ input-transform kernel provides
the cleaner precedent for this implementation: non-transform participants use
one generic target, and a role that keeps the computed launch default emits no
reconfiguration instruction.

CUTLASS computes the initial per-thread allocation as:

```text
floor_to_multiple_of_8(512 / number_of_warpgroups)
```

For the relevant launch shapes:

| CTA threads | Warpgroups | Initial registers/thread |
|---:|---:|---:|
| 384 | 3 | 168 |
| 512 | 4 | 128 |

The validated 512-thread role layout uses one control-warpgroup target and lets
both transform warpgroups retain the launch default:

| Warpgroup | Warps | Role | Target | Register total |
|---|---|---|---:|---:|
| 0 | 0-3 | Epilogue | 176 | 22,528 |
| 1 | 4-7 | MMA, scheduler, and TMA | 80 | 10,240 |
| 2 | 8-11 | Transform group 0 | 128 (default) | 16,384 |
| 3 | 12-15 | Transform group 1 | 128 (default) | 16,384 |
| | | **Total** | | **65,536** |

This exact allocation is legal and has a direct FlashInfer precedent:
`mla_decode_fp8.py` documents an exact 65,536-register allocation across four
warpgroups. The transform warps issue no `setmaxnreg` instruction because 128
is already their launch allocation. Warpgroup 1 decreases uniformly to 80,
which returns exactly enough registers for warpgroup 0 to increase from 128 to
176.

## Tensor Memory Read/Write Contract

On `sm_100`, a CTA's Tensor Memory is a 128-lane by 512-column matrix of 32-bit
cells. A TMEM address encodes the lane in bits 31:16 and the column in bits
15:0. Allocation is column-based: allocating one column allocates that column
for all 128 lanes.

`tcgen05.ld` and `tcgen05.st` divide those 128 lanes by **warp rank modulo 4**:

| Warp rank within any warpgroup | Accessible TMEM lanes |
|---:|---:|
| 0 | 0-31 |
| 1 | 32-63 |
| 2 | 64-95 |
| 3 | 96-127 |

All four ranks can address every TMEM column. A second warpgroup repeats this
same lane mapping; it does not gain a new set of lanes. For example, warps 8
and 12 both have rank 0 and can both access lanes 0-31. They can cooperate only
when their column regions are disjoint.

For `.32x32b.xN`, all 32 threads of a warp collectively access 32 TMEM lanes.
Thread `i` supplies `N` 32-bit registers for the warp's accessible lane `i`, so
`.x4` writes four 32-bit columns per lane and `.x8` writes eight. The base
`taddr` is warp-uniform. With BF16 packed two per 32-bit register and no
`.unpack::16b`, four columns correspond to eight BF16 logical values.

`tcgen05.st` is warp-collective:

- all 32 threads must execute the same instruction;
- all threads must provide the same base TMEM address;
- no participating thread may have exited;
- `.shape` and `.num` jointly define the written region;
- the store is asynchronous.

The W4A16 producer must call `fence_view_async_tmem_store()` after the final
TMEM store and before committing the transform-to-MMA pipeline stage. CuTe DSL
lowers this fence to `tcgen05.wait::st`, ensuring MMA cannot observe a partially
published transformed tile.

The packed NVFP4 read and E4M3 scale read must be partitioned from the same
tiled-copy ownership as the BF16 TMEM destination. A fixed tuple index is not a
general ownership contract: the extra mode produced by `make_tmem_copy` can
represent different logical dimensions for different MMA M/K and CTA-group
layouts.

For the current W4A16 `.32x32b.x4` prototype, CuTe emits this destination
layout, with stage count omitted:

```text
shape  = (((8,32),1), 2, 1, K/16)
stride = (((1,131072),0), 8, 0, 16)  # BF16 logical elements
```

The nested 32-way stride encodes TMEM lane movement. The size-2 mode has stride
8 BF16 values, or four 32-bit TMEM columns. It is therefore the disjoint column
ownership mode needed by two transform warpgroups: group 0 writes columns 0-3
within each K/16 block and group 1 writes columns 4-7. Together they replace the
single `.x8` store.

The corresponding E4M3 scale partition gives that size-2 mode stride 0. This is
intentional: the two groups own the first and second eight values of every
16-value NVFP4 block, so both groups load the same scale fragment. The decoder's
natural ownership unit is therefore four packed E2M1 bytes plus one E4M3 byte,
producing eight BF16 values. Each transform thread iterates over `K/16` such
half-blocks. Its zero-stride logical scale view selects one scale for each
iteration, while its register fragment accumulates 32, 64, or 128 BF16 values
for K64, K128, or K256. Regrouping the packed input into 16-value chunks after
slicing the size-2 mode mixes adjacent blocks that have different scales.

The two transform warpgroups are independent pipeline producers but jointly
complete one stage. `PipelineAsyncUmma` initializes its full barrier with the
256-thread producer-group size, and `producer_commit` contributes one arrival
per transform thread. Each 128-thread group therefore contributes half of the
stage arrival count; neither group may commit on behalf of the other.

The retained x8 mapping changes ownership from half-block columns to complete
NVFP4 blocks. CuTe emits source and TMEM block modes with logical stride 16
BF16 values, while the corresponding scale block mode has stride 1. Applying
`logical_divide(..., (None, None, None, 2, None))` changes those modes to
`(2, KBlocks/2)` with strides `(16, 32)` and `(1, 2)`. Selecting the first
coordinate with the transform-warpgroup index gives group 0 even blocks and
group 1 odd blocks. This has three important ownership properties:

1. Each group owns complete 16-value blocks, so the x16 decoder converts one
   E4M3 scale once for all eight packed E2M1 bytes.
2. The two groups still use matching physical warp ranks and therefore the
   same TMEM lane quartiles, but parity selects disjoint TMEM columns.
3. Both groups retain 128 threads and each commits one barrier arrival per
   thread, preserving the 256-thread producer contract.

This mapping passed every one-CTA/two-CTA route tactic and the complete W4A16
test class. The layout evidence is in
`logs/w4a16_x8_layout_probe_20260723_050400/run.log` and
`logs/w4a16_x8_stripe_probe_20260723_050625/run.log`.

Parity striping is not the best final ownership. Splitting the complete-block
mode into two contiguous ranges gives each transform warpgroup contiguous
packed E2M1 bytes, E4M3 scale bytes, and TMEM columns. The resulting coalesced
register fragment can contain 32, 64, or 128 BF16 outputs. A fragment with `N`
outputs owns exactly `N / 16` independent scale bytes, so data and scale must
be divided with separate tilers. Applying the BF16-element tiler to the
expanded zero-stride scale view produces the wrong compact scale cardinality.
The corrected compact-scale partition passed all tested K tiles and improved
the full EP8 geomean over both parity striping and the four-warp baseline.

## CUTLASS Pattern To Mirror

CUTLASS mixed-input FMHA uses two complete transform warpgroups (eight warps):

- the transform warps occupy contiguous warp IDs;
- each warp computes a local thread index modulo 256;
- source and destination tensors are partitioned by one 256-thread cotiled copy;
- all transform pipelines declare a 256-thread consumer or producer group;
- both transform warpgroups use the same register allocation;
- the role-control warpgroup uses one generic target, matching CUTLASS's C++
  input-transform kernel policy.

The W4A16 implementation should mirror those structural properties. Its TMEM
destination requires a TMEM tiled copy rather than FMHA's shared-memory copy,
but ownership still needs to originate from one explicit 256-thread layout.

## Current Hardware Evidence

The first uniform `St32x32b.x4` experiment split the CuTe-generated partition
by a hard-coded mode and used 120 registers for each of eight transform warps.
The route/topology numerical test produced:

| Case | Result |
|---|---|
| M128/K256 one-CTA SwiGLU | Pass |
| M128/K64 one-CTA SwiGLU | Fail |
| M256/K128 two-CTA SwiGLU, route 64 | Pass |
| M128/K256 plus M256/K256 ReLU2 | Fail |
| M256/K128 two-CTA SwiGLU, route 192 | Fail |

Evidence: `logs/w4a16_dedicated8_uniform_test_20260723_042732/run.log`.

This proves that two transform warpgroups can issue valid TMEM stores, but the
hard-coded group-axis slice is not a general mapping. It does not prove that
eight transform warps are invalid for the failing tactics.

The corrected half-block decoder and ownership-derived tiler subsequently
passed all five cases and the full 13-case W4A16 class. The decisive generated
register view is `(8, K/16)`: each loop iteration owns eight logical values and
uses one scale selected from the zero-stride scale mode. Evidence:
`logs/w4a16_dedicated8_halfblock_v3_20260723_045440/run.log` and
`logs/w4a16_dedicated8_full_test_20260723_045518/run.log`.

The first exact-budget attempts kept mixed 96/64/80 targets in the
role-control warpgroup and hung. Uniformizing that warpgroup to 80 passed the
five-case route/tactic probe first with 120-register transforms, then with both
transform warpgroups retaining the 128-register launch default. The latter
allocation totals exactly 65,536 registers and passed the full 13-case class.
Its PTX has four `setmaxnreg.dec 80` instructions, one
`setmaxnreg.inc 176`, and no transform-side reconfiguration. Evidence:
`logs/w4a16_uniform80_regs120_probe_20260723_061148/`,
`logs/w4a16_uniform80_regs128_exact_probe_retry_20260723_061637/`, and
`logs/w4a16_uniform80_regs128_full_validation_20260723_062747/`.

## Retained Implementation

1. Use one 80-register target for all four role-control warps and let all eight
   transform warps retain the 128-register launch default.
2. Inspect the CuTe tiled-copy layouts for every autotuned M/K and CTA-group
   topology. Record which logical modes map to TMEM columns, lanes, and stages.
3. Construct one explicit 256-thread transform ownership layout, following the
   CUTLASS mixed-input FMHA pattern. Partition packed inputs, E4M3 scales, and
   BF16 TMEM destinations from that same ownership mapping.
4. Preserve warp-uniform `tcgen05.st` control flow and keep the TMEM store wait
   before pipeline commit.
5. Gate performance measurement on all route/topology numerical cases passing.
6. Inspect emitted PTX/SASS to verify two disjoint transform warpgroups issue
   the intended `tcgen05.st` forms without local-memory spills.

NCU's launch-level registers per thread do not describe each role's dynamic
allocation after reconfiguration. The 512-thread kernel starts at 128
registers per thread. Transform warps keep that allocation, warpgroup 1
returns 48 registers per thread to the CTA pool, and warpgroup 0 acquires those
registers to reach 176. The exact-budget allocation works once warpgroup 1 uses
one coherent reconfiguration target.

## Devbox Workflow

Use `w4a16-opt132` for CUDA 13.2/B200 validation. After the initial full source
sync and editable install, transfer only the edited Python kernel file through
`h warp` and copy it into `/root/flashinfer-src`. A full `h sync` updates C++
source mtimes and unnecessarily rebuilds the common TRT-LLM routing module.
Run `pre-commit run --all-files` locally before each source transfer. Wrap every
GPU test in `timeout`, inspect `nvidia-smi` when output is silent, and terminate
a kernel that remains at 100% utilization without forward progress. Stage each
run under `/data/home/ziangli/agent/warp_logs` and download it to the local
`logs/` directory.
