# SF source vectorization experiment

Actual independent clone: `flashinfer-regular-tma-sf-vector-review`, base442 plus
the three frozen cleaned regular-TMA files. All changes remain unstaged. Only
`blackwell/moe_prepare.py` differs from the cleaned review control; regular TMA
GEMM, payload LDG/STG256, canonical SF layout, per-invocation workspace, grid,
PDL, full SF padding and per-token scale handling are unchanged.

The static policy minimizes
`ceil(sf_blocks / (32 * width)) * (1 + width)` over complete legal Uint32 vector
widths1/2/4/8. This estimates warp source-load plus scalar-scatter instructions;
ties choose the smaller register vector. It is independent of dtype/model
names. SF block counts56/112/256 select64/128/256-bit loads. Short rows and odd
block counts retain an explicit scalar branch. The CPU proof enumerates512
block extents, verifies minimal estimated issue count and exact destination
partitioning, and confirms unchanged payload/scalar-SF/allocation ASTs.

**Alignment delta:** the cleaned preparation API explicitly accepts4-byte
source SF alignment. The older generic GEMM wrappers assumed16-byte SF pointers
(`_blockscaled_ptr` default and the public gather wrapper's SF pointer), but
the new preparation must validate its own inputs. This trial explicitly
requires8/16/32-byte source SF alignment when the static geometry selects
width2/4/8. SF row stride is divisible by that width; no runtime alignment
fallback is added. Destination SF remains4-byte aligned. The exact probe tests
every4-byte offset within32bytes for all four selected widths. Stronger
alignment is a proposed contract delta, not silently assumed compatibility.

GPU3 diagnostics use the existing recovery candidate native cache and separate
CuTe caches. The focused byte probe has75 graph grow/shrink/zero-route cases
plus32 alignment checks. Four payload/SF-vector-size combinations cover the
preparation byte contracts shared by the six numerical formats; SF encodings
are copied as arbitrary raw bytes without arithmetic. K64/K128 minima, K7168,
width8 K16384 and nonvectorizable K832/K896 are included.

The phase callback reuses actual native routing from the unchanged
`probe_native_source.py` and captures whole prepared payload/SF equality before
timing. NV8K/N128, NV16K/N256 and MX16K/N256 each run ABA followed by BAB against
the cleaned review control. Every arm retains100 cold-L2 CUDA-graph CUPTI
samples after10 warmups. No historical baseline or full primary grid is
rerun. Phase evidence alone does not establish a whole-MoE speedup.

`inspect_width8.py` only compiles and inspects a width8 specialization; it never
launches that kernel. Phase cubins provide actual width2/4 instructions and
resource/occupancy records. Wider loads are not claimed from source alone.

```bash
bash scripts/prep_sf_vector_experiment/run_exact.sh
bash scripts/prep_sf_vector_experiment/run_phase.sh
```

No shared source, public PR, native JIT epoch, or existing benchmark artifact
is modified by these diagnostics. The earlier128-row shared-memory transpose
experiment is not repeated.
