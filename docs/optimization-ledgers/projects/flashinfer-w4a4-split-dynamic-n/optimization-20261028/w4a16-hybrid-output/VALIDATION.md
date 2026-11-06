# W4A16 hybrid TMA/SIMT output experiment

Only the gated FC1 store policy changes relative to the frozen padded-output R2
candidate: full routed tiles retain TMA; partial routed tiles use predicated SIMT.
ReLU-squared FC1 and FC2 already use the hybrid policy. This directory contains
local validation/performance helpers and receipts, not upstream test additions.
The source remains unstaged in `../../flashinfer-w4a16-hybrid-output-review`.

## Paired correctness gate

The control is the persistent R2 candidate, not the descriptor-output experiment.
The deployment config and source manifests bind each run to exact file hashes.
A separate native/CuTe cache is retained for the candidate, with persistent native
cache links shared with prior runs.

`probe_outputs.py` reuses the established canonical output oracle. Existing W4
configurations 8–13 cover SwiGLU, SiTU, GeGLU-tanh, ReLU-squared, one/two CTA, and
both weight layouts; added local-only configurations 14/15 exercise SiTU and
GeGLU-tanh with the old layout as well. Every configuration runs static/CLC × PDL
off/on against ten changing CUDA-graph replays:

1. Balanced routing.
2. Skewed routing.
3. No local routes.
4. Reactivated routes with changed payloads.
5. Two exactly full expert tiles.
6. Full tiles plus a one-row tail per expert.
7. Full tiles plus a half-tile-plus-one tail per expert.
8. One row below the actual compiled `epi_tile_n`.
9. Exactly the compiled `epi_tile_n`.
10. One row above the compiled `epi_tile_n`.

Each replay compares byte hashes for final output and FC1/FC2 valid rows after
canonicalization by expanded route ID. Cross-scheduler/PDL invariance is retained.
The candidate must leave poisoned padding untouched. The control records its
padding behavior but does not require gated FC1 padding to remain NaN: the old
unconditional TMA writes that padding, which is the intentional difference.
Compiled GEMM PTX/SASS/resource metadata is captured to confirm the requested
scheduler/PDL modes and check for local spills. No sanitizer is run.

Planned GPU lanes after source freeze: GPU 1 first config 8 for quick feedback,
then configs 9/14; GPU 2 configs 10/12/15; GPU 3 configs 11/13. GPU 0 is reserved for
bounded performance after the first paired correctness result. Remaining GPU
allocations belong to the performance owner. No kernel work starts before the
source snapshot is frozen and the assigned GPU is checked idle.

Validation state: hybrid-01 passed the full gate described below.

## Hybrid-01 complete (2026-10-28)

The frozen W4 kernel SHA256 is
`838acecd15395755dec3b59422f99f886570b1bf237d02a10e439b53ec627b89`.
It is the only source file changed relative to R2. Each runtime process verified
all 348 source hashes before and after running. Existing image/runtime:
`nvcr.io/nvidia/pytorch:26.05-py3`, B300, CUDA 13.2; recovery box
`fi-moe-descriptor-recover-1028`, C3/ziangli. All native cache links were preserved.

- **400 paired replays passed**: 320 main cases at intermediate 512 plus 80 focused
  two-CTA old/swap GeGLU cases at intermediate 192. The latter exercises the
  partially occupied channel cluster (`intermediate % 128 == 64`) used by V41F TP.
  Every valid FC1/FC2 value and final output matched the R2 source byte-for-byte,
  including CLC/static and PDL invariance. All 800 candidate padding checks passed.
- The R2 gated FC1 implementation overwrote padding in 184 replay instances.
  Those bytes are intentionally excluded from cross-source equality; the hybrid
  candidate retained the NaN sentinel in every corresponding row.
- **76 captured GEMM compilations** have zero descriptor replacements, zero SASS
  LDL/STL spill sites, and zero stack/local bytes. Repeated configurations reuse
  cached compiled FC2 variants, so this count is lower than the 80 requested GEMM variants.
- **10 existing tests and four fused compatibility cases passed**. The fused
  cases have exact FC1 and observed maximum final absolute difference 0, while
  the required fused-final threshold remains `rtol=atol=1e-2`.

The consolidation is `hybrid-01/validation-status.json`; resource evidence is
`hybrid-01/compiler-resource-summary.json`. Reproduce the local receipt checks:

```sh
python3 summarize_gate.py --snapshot hybrid-01 --require-channel-tail
```

Raw graph receipts, exact commands, output hashes, and resource reports are in
`hybrid-01/evidence-metadata/`. Existing pytest/fused receipts are in
`existing-gate-01/`. Larger PTX/SASS/CUBIN files stay in the corresponding
persistent remote snapshot. No sanitizer or source modifications were made by
the validation harness. GPU reservations were released to the performance owner.
