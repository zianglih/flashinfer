# Cache-policy audit and descriptor-prefetch candidate

Base: public `fe4f8132439df1b812f77279e7d033a5128f1ed4`, kernel SHA256
`58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`.
Read-only audit; the patch was prepared unapplied, then the parent applied it
for coordinated validation. This audit performed no GPU use or active-source edits.

## Findings

The two retained PR4048 data-cache changes are already in the Mega kernel and
survive compilation. There is no missing streaming-weight cache hint to add.
The one missing retained startup pattern is explicit TMA descriptor prefetch.

| Operation | Current Mega source | Current policy | Retained split / PR4048 |
|---|---|---|---|
| Packed weight A, both phases | `shim/w4a16/kernel.py:773–780` | EVICT_FIRST `0x12F0000000000000` | Same, `moe_w4a16_kernel.py:1503–1513` |
| E4M3 scale A, both phases | `shim/w4a16/kernel.py:781–788` | DSL default; generated operand0 | Same, `moe_w4a16_kernel.py:1514–1523` |
| BF16 activation B, both phases | `shim/w4a16/kernel.py:837–844` | EVICT_LAST `0x14F0000000000000` | Same, `moe_w4a16_kernel.py:1417–1426` |
| Peer activation pull | `src/src/token_comm.py:1000`, `src/src/ptx_helpers.py:24–67` | EVICT_FIRST | Inherited Mega communication policy |
| Pulled activation to local FC1 pool | `src/src/token_comm.py:1093`, `src/src/ptx_helpers.py:71–92` | EVICT_NORMAL `0x1000000000000000` | Inherited Mega communication policy |
| BF16 FC1 intermediate | `shim/w4a16/epilogue.py:333–334,414` | Ordinary vector global store; no explicit eviction policy | Split uses its existing output path; prior explicit FC1 store retention was rejected |
| BF16 per-route FC2 | `src/moe_nvfp4_swapab/epilogue_refactor.py:2932–2936,2974–2979` | Inherited ordinary vector global store | Current vendor FC2 router/store helper reused unchanged |
| Startup TMA descriptor prefetch | Absent; kernel entry `kernel.py:878–883` | None | Present, split `moe_w4a16_kernel.py:870–875` |

Mega paths above are rooted at
`flashinfer/moe_ep/kernel_src/cutedsl_megamoe/`; split paths are rooted at
`flashinfer/fused_moe/cute_dsl/blackwell/`. The PR4048 merge is
`c9172e6aac70486d470c8b8d5d9b7455e9838359`; `git show` confirms the same two
load policies and startup prefetch in that commit. Constants also match
CUTLASS `cute::CacheHintSm100` in `copy_sm90_desc.hpp:193–197`.

The current NVFP4 Mega compute path does not add explicit cache policies at
its weight/SF and activation/SF TMA copies (`kernel_fc12.py:1826–1842,
1982–1998`). BF16 Mega likewise leaves the TMA cache-policy argument implicit.
Both share the communication helpers above. Their reference GEMMs explicitly
prefetch descriptor atoms; the swapped persistent scheduler's
`SwapABSwigluFp4Fc12SchedExtension.prefetch_for_expert` is a deliberate no-op
because its descriptor atoms are tile-invariant (`custom_ext.py:533–535`).
Calling that no-op in W4A16 does not supply startup prefetch.

## Reuse and hardware interpretation

Within one routed-token tile, B is reused across output-feature tiles; its
EVICT_LAST policy protects that reused operand against large streaming packed
weight traffic. A and its smaller SF tensor can also be reused across routed-N
tiles of the same expert, so EVICT_FIRST is a preference, not a statement that
every weight line is read only once. Communication has a different lifetime:
the peer source is pulled into the local expert pool, and the local pool is
then consumed repeatedly by GEMM. The inherited peer-load FIRST / pool-store
NORMAL distinction already reflects that lifetime.

The [PTX ISA cache-eviction documentation](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#cache-eviction-priority-hints)
defines eviction policies as performance hints, not residency guarantees or
changes to memory consistency. EVICT_FIRST favors eviction under pressure;
EVICT_LAST favors retention. Descriptor prefetch fetches the tensor map, not
the packed-weight or BF16 data tile. No synchronization can be removed because
of these hints.

`generated-evidence.json` reads existing, source-matched two-group production
PTX/SASS from all eight ranks. Every rank has the same static policy sites:

| Policy | Static sites | Interpretation |
|---|---:|---|
| EVICT_FIRST | 3 | Two packed-A phase copies plus peer bulk load |
| EVICT_LAST | 8 | BF16 B phase loops as emitted/unrolled by the compiler |
| Default0 | 2 | Two SF phase copies |
| EVICT_NORMAL | 1 | Dispatch bulk store into local pool |
| `prefetch.tensormap` | 0 | Missing startup descriptor prefetch |

PTX explicitly uses `.L2::cache_hint` with the listed 64-bit operands. SASS has
two `UTMALDG.3D` A sites, two `UTMALDG.4D` SF sites and eight
`UTMALDG.2D.2CTA` B sites; the SF sites use `desc[URZ]`. Ordinary 256-bit output
stores emit `st.global.v8.b32` and `STG.E.ENL2.256`. These are static instruction
counts, not runtime traffic counts. The report does not interpret undocumented
SASS modifier semantics or assert that a default-zero policy is a correctness
bug. There is no need for a new GPU capture to establish that existing hints
survived compilation.

## Prior experiments: do not silently retry rejected policies

The durable prior ledger is
`/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md`.
These are historical split-kernel results, not current Mega performance:

| Prior change | Ledger lines | Historical outcome |
|---|---|---|
| Activation B EVICT_LAST | 312–337 | Retained, EP8 geomean 1.0107× |
| Packed A EVICT_FIRST | 1048–1085 | Retained, two EP8 geomeans 1.0215×/1.0230× |
| SF EVICT_LAST | 607–625 | Rejected; dense EP8 regression despite geomean 1.0035× |
| SF EVICT_FIRST | 1087–1096 | Rejected; EP8 geomeans 0.9987×/0.9982× |
| Weight A EVICT_LAST | 654–667 | Rejected |
| FC1 TMA-store EVICT_LAST | 731–746 | Rejected; EP8 neutral, TP8 regression |
| Permute producer explicit load/store modifiers | 3272 onward | Rejected; default at least as good |

Current Mega data lifetimes differ enough that a future controlled retest could
be meaningful, but historical rejection is not evidence of a missing free win.
This candidate does not retest or combine those policies.

## Candidate and validation

`descriptor-prefetch.patch` adds only a warp0 startup block, prefetching the six
existing A/SF/B atoms for FC1 and FC2. It mirrors the retained split entry-point
pattern and reuses `cpasync.prefetch_descriptor` directly; no custom PTX,
policy constant, stage, memory layout, barrier, role or public knob is added.
The helper lowers through CuTe's `prefetch_tma_desc` operation. Warp0 is the
same first epilogue warp used by the established split path. Both CTAs may
prefetch as they do in that reference.

Python parsing/bytecode, Ruff check/format and `git apply --check` pass. Manifest
hashes are in `manifest.json`. At preparation, the patch was not CUDA-compiled, numerically
tested or timed; the parent owns subsequent GPU validation. A future coordinated test should first confirm emitted tensor
map prefetches and unchanged resources/steady-state pipeline, then compare the
same scheduling profile and source with/without this sole patch. Any benefit
is expected to concern startup descriptor latency; no performance gain is
claimed and extra prefetch instructions may be neutral or slower.
