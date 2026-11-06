# GLM W4A4 MMA instruction audit

2026-10-08. Read-only inspection of the actual GLM source, native logs, installed
CuTe DSL source, and retained files. No GPU workload was executed for this audit.

**Both measured W4A4 implementations select K64 in source. K96 is absent from
their AUTO candidate space; it was not a candidate that lost autotuning.**
This applies to FlashInfer `b730d5f6f5929fe666b24b466144a57f5587ba4b` with
CuTe DSL `4.7.1`, the recorded GLM campaign. Binary confirmation is still
pending because no generated MoE PTX/cubin was retained in the inspected
capture/cache locations.

All new audit files are under `evidence/glm5-mma-instruction-audit/`. Pinned
upstream files have URLs and SHA256 in `source-manifest.json`; installed DSL
files have hashes in `dsl471-source-manifest.json`.

## Exact source chain

| Component | Archived source and lines | Finding |
|---|---|---|
| Split FC1 | `blackwell-blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:618–646`, repeated construction at925 | Calls `sm100_utils.make_blockscaled_trivial_tiled_mma`; stage K is four instruction K extents. |
| Split FC2 | `blackwell-blockscaled_contiguous_grouped_gemm_finalize_fusion.py:475–503`, repeated construction at724 | Calls the same helper; stage K is four instruction K extents. |
| DSL helper actually installed | `dsl471-blackwell_helpers.py:1330–1377`, especially1353–1356 | For E2M1×E2M1 with scale-vector16, constructs `MmaMXF4NVF4Op(sf_dtype, (*mma_tiler_mn, 64), ...)`. No device-based K96 branch. |
| DSL operation | `dsl471-mma.py:1857–1943` | `MmaMXF4NVF4Op` verifies `instruction_k=64`. |
| Separate B300 helper | `dsl471-blackwell_helpers.py:1619–1663` | `sm103_make_blockscaled_trivial_tiled_mma` explicitly constructs the distinct `SM103MmaMXF4NVF4Op(..., (*MN,96), ...)`. The measured split kernels do not call it. |
| Separate B300 operation | `dsl471-mma.py:2125–2213` | `SM103MmaMXF4NVF4Op` verifies `instruction_k=96`. |
| Mega inheritance | `megamoe_kernel.py:162`; `kernel_fc12.py:289–339` | Mega inherits the shared NVFP4 FC1/FC2 kernel, whose layout uses the same K64 helper. |
| Mega actual MMA emission | `dynamic_mainloop.py:94–105,221,275–280`; called at `kernel_fc12.py:2291` | Explicit `_UMMA_K_NVFP4=64`; instruction descriptor K-size bit defaults0; K256 stage unrolls into four block16 `tcgen05.mma` operations. |

Mega explicitly builds a descriptor whose static K-size bit is0, and both FC
phases use the same K64 mainloop. One runtime detail still needs binary/address
verification: `compute_idesc` masks the scale-pointer top bits and right-shifts
signed `Int32` values. DSL signed shifts can sign-extend; field-position comments
alone do not prove bit31 stays clear for every actual scale pointer. This is
not evidence that K96 executes, and the candidate enumeration still contains
no deliberate K96 implementation. Inspect actual PTX shift signedness and the
valid scale-pointer address bits before asserting the final dynamic descriptor.

`actual-c2-source-receipt.json` verifies the retained C2 checkout is b730 and
its actual split FC1/FC2, Mega base kernel, and dynamic-mainloop files are
byte-identical to the archived pinned sources. The currently installed DSL
package reports4.7.1, matching the historical runtime receipt. C1's old
scratch capture no longer exists; its historical manifest pins the same
source/package, but no live C1 historical working-tree comparison is claimed.

## AUTO does not contain K96

Split, `tuner.py`:

- Lines79–143 enumerate FC1/FC2 `(M,N)` tiles, CTA clusters and raster order.
  `VALID_TILE_SIZES` at170 is128/256. FC1 N is128/256; FC2 N is128/256 and
  cluster N is1/2. There is no MMA K or MMA-operation-class candidate.
- `_get_arch_tactics` at426–433 selects a separate list only for SM107.
  SM100 and SM103 both receive `ALL_BLACKWELL_MOE_TACTICS`.
- `get_valid_tactics` at682–868 filters this list with the same Blackwell
  FC1/FC2 `can_implement` checks. Filtering cannot introduce a K96 candidate.
- `_extract_tactic_params` at368–423 passes the Blackwell M/N and cluster
  choices to the fixed kernel constructors above.

Mega, original pinned snapshot
`evidence/glm5-ep8-b730-source/mega_w4a4_autotune.py:50–91`:

- `nvfp4_candidates` uses only tiles `(256,128,256)` and `(256,256,256)`.
- It varies flag batches4/8 and token-return warp assignment, with an optional
  in-kernel-reduction axis that was disabled for this campaign.
- All candidates instantiate the same K64 implementation. None switches to
  `SM103MmaMXF4NVF4Op`, changes the descriptor K-size bit, or supplies a K96
  mainloop.

Therefore the scoped answer is: **these benchmarks never compiled a K96 MoE
candidate through their normal source paths**. This does not assert that no
other unrelated process on either machine ever compiled K96.

## Matched prefill tactics

`prefill-mega-tactics.json` parses all native `MEGAMOE_TACTIC_JSON` records,
including concatenated multiprocess lines, and binds each source log by SHA256.
All eight ranks, both sweeps, both hardware selected identical Mega knobs for
each prefill token count:

| Total tokens | Tile M/N/K | Flag batch | Token-return mode |
|---:|---|---:|---|
|4096|256/128/256|4|reuse_dispatch_warps|
|8192|256/128/256|4|reuse_dispatch_warps|
|16384|256/256/256|8|reuse_dispatch_warps|

All use cluster2/1/1, epilogue flag batches2/4, group hint512,
`atomic_counter` scheduling, and `in_kernel_fc2_reduce=false`. Here tile K256
is the staging tile; the separate source proof establishes four K64 MMA steps.

The split AUTO winner was not printed in the historical logs. A regenerated
AUTO choice cannot be presented as the historical winner. This does not weaken
the K64 implementation-wide result because every permitted split candidate
uses the same fixed MMA factory.

## Retained artifacts and next step

- Parent inventoried persistent GLM compilation caches in
  `runs/kimi-k3-ep8/c1-glm-artifact-inventory.json` and the C2 counterpart.
  CuTe's designated cache directory was empty. FlashInfer exported objects
  belonged to activation quantization/routing/communication helpers.
- A read-only recursive scan of C2's retained
  `/scratch/nvfp4-w4a16-blog-draft/glm5-ep8-b730/capture` found no generated
  MoE `.ptx`, `.cubin`, `.o`, `.mlir`, `.fatbin` or `.sass`. The eight PTX
  files found were checked-in KDA or experimental DeepGEMM sources.
- Native split wrappers call `cute.compile` directly
  (`blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:392`, FC2
  counterpart325); Mega frontend also calls `cute.compile` directly at628.
  They do not use FlashInfer's object-export wrapper. Its activation-quant
  cache is therefore not evidence that the MoE kernels were exported.
- DSL4.7.1 exposes `CUTE_DSL_KEEP=ptx,cubin,sass` and `CUTE_DSL_DUMP_DIR`
  (`dsl471-env_manager.py:520–536`), plus compiled-object artifact accessors
  (`dsl471-jit_executor.py:1094–1135,1237–1254`).

`DUMP_RECIPE.md` and `dump_native.py` prepare an isolated native-driver rerun
with per-rank artifact hashes and compile configuration metadata. Mega can be
replayed using its exact recorded knobs. Split can export every native AUTO
candidate, with the historical-winner limitation above. No kernel code changes
are needed. `py_compile` and Ruff passed; no GPU execution or live compile was
performed for this helper.

The executable `study.py` is now prepared on C2 at
`/data/home/ziangli/nvfp4-w4a16-blog-draft/glm-mma-study/c2`. Its independent
source clone and four independent submodule clones passed the source/runtime
guards without GPU execution or package installation. The original patch SHA
is `cd55f07c62fcf634dd3d6f5cde5f0d69d6d4ac3cab80a05ee208ac14b076d135`;
the canonical Git diff SHA is
`8915b29d14bd3e25eae23905c489056a92477932864606e71bb69ecab2f45f2b`.
Those differ only because the patcher's diff serialization omits index lines,
orders files differently and omits function names in hunk headers. Resulting
source-file hashes match the original capture exactly. The downloaded receipt
is `evidence/glm5-mma-instruction-audit/c2-study-receipt.json`.

The CPU wrapper check verified unchanged compile arguments/returned object,
all three artifact payloads and SHA256 references, and captured kernel
configuration. The study's `check` command additionally passed against the
actual prepared source, submodules, helper hashes and installed runtime.
The separate `run` command has not been executed. A failed initial preparation
was preserved at `c2-incomplete-guard-1`; it never executed GPU work.

## Interpretation for the blog

B300's K96 NVFP4 hardware capability and advertised FP4 peak remain hardware
facts, documented in `B300_PTX_ANALYSIS.md`. They are **not** the implemented
MMA throughput of these pinned W4A4 MoE curves. Avoid framing this specific
comparison as beating a W4A4 baseline that exploits B300's K96 mode.

The nearly equal B200/B300 prefill timings are compatible with this K64 source
finding. They do not identify the remaining limiter. Epilogue latency,
communication, memory traffic, occupancy and instruction issue require
separate matched profiling; neither source selection nor similar end-to-end
latency alone proves an epilogue bottleneck.

## Why the persistent CuTe cache is empty

This is now source-traced, not merely inferred from missing files:

1. Installed DSL `dsl471-__init__.py:232` binds `cute.compile` to
   `CompileCallable()`.
2. `dsl471-compiler.py:1514–1515` explicitly sets both
   `kwargs["compile_only"] = True` and `kwargs["no_cache"] = True`.
3. `dsl471-dsl.py:2227` only attempts the file cache when `not no_cache`;
   lines2353–2365 similarly gate the in-memory DSL cache and file write-through.
   The additional `compile_only` guard at2862–2864 also enforces no-cache.
4. The file-cache helper itself would honor `CUTE_DSL_CACHE_DIR`
   (`dsl471-cache_helpers.py:67–72`) and write compiled MLIR bytecode
   (`:290–325`). That path simply is not used by direct `cute.compile`.

The K3 collector deliberately sets `CUTE_DSL_NO_CACHE=0`,
`FLASHINFER_CUTE_DSL_DISABLE_CACHE=0`, and `CUDA_CACHE_DISABLE=0`, unsets
`CUTE_DSL_DISABLE_FILE_CACHING`, and provides a persistent cache directory.
Those settings preserve caches where supported; they do not override the
explicit no-cache kwargs in DSL's compile entry point. `CUTE_DSL_DUMP_DIR`
alone is an output-location setting, not an instruction to export artifacts or
reuse them. `KEEP=ptx,cubin,sass` must be requested for artifact dumping.

FlashInfer still reuses already compiled split objects in module dictionaries
(`blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:217–218,418`, FC2
counterpart179–180,351), and Mega's frontend retains its `_mega` object when
`_mega_compile_key` matches (`mega_w4a4_frontend.py:502–540,628–631`). These
objects do not survive a new process. Each fresh native sweep can therefore
recompile MoE specializations, despite the persistent cache environment.

The user clarified that preserving the slow C++ component cache is the goal;
the current setup meets that intent and no additional MoE cache feature is
requested. Explicit artifact export for this instruction study is a separate
operation. No active collector, source tree, environment or campaign was changed
for this audit.

Primary instruction reference:
[NVIDIA PTX ISA9.4, tcgen05 instruction descriptor](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-instruction-descriptor).
Descriptor bit31 distinguishes K64/K96; there is no `.k96` mnemonic suffix.
