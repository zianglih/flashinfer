# Full TMA subtiles in an ordinary route tail

Held source/test proposal against retained `b90b34744491c36d0039f44cba664191f7bb0eb0`. The repository is untouched. No native compilation, numerical run, or performance measurement has been performed for this candidate.

The ordinary epilogue currently requires an entire route CTA tile to be valid before using any TMA output stores. The proposal instead tests the end of each epilogue subtile: `distance_to_boundary >= (subtile_idx + 1) * epi_tile_n`. Fully valid prefix subtiles use the existing TMA body; the final partial subtile and invalid suffix retain the existing SIMT predicates. For N128 with 65 valid routes and 32-route epilogue subtiles, this changes the first two subtiles to TMA and leaves the remaining two on SIMT.

## Exact scope and source proof

- [source.patch](source.patch): `8206598af7cbed6f704a75623991f0e8f4f0ae98f8cf0ee04d0f3c9950f62ef2`; proposed kernel `1fe29f6f802508034c2fc5daaf7a24271e35bf98a0ca1b052548bfc955f5f97b`.
- [tests.patch](tests.patch): `4a491f16ed9d6df7bc41f226d527ad180d283b37b808f08ec1cf7b8b28056b3c`; proposed tests `102a3501f51862beeb1acbcc27c5a9601c3869780919d6b2f4be9530fe3c4b95`.
- [candidate.patch](candidate.patch): `417f1fb60c059d6b228d547b979757aef76e5a09c369fa35f016e5756f41448d`.
- [source-review.json](source-review.json) records syntax, AST, lint, and integer-boundary checks. Whole kernel AST matches the baseline after restoring this one condition; both TMA and SIMT branch bodies are unchanged. No interfaces, caches, resource fitting, decode warps, or tactic definitions change.

Source references below use the saved baseline under `baseline/` and the retained checkout paths.

| Contract | Source evidence |
|---|---|
| Subtiles advance along route N | The host `_get_compiled_kernel` at `moe_w4a16.py:126–128` maps public MMA M128 and M256 to CTA M128. Kernel `:201–236` gets its epilogue shape from the installed DSL helper. Saved DSL 4.7.1 `blackwell_helpers.py:1831–1889` selects epi M128 and epi N=min(route N,32) for these no-source BF16 outputs. Therefore flattening the remaining epilogue tile modes at kernel `:2109–2117` leaves only ascending N subtiles. |
| TMA and SIMT address the same routes | Kernel `:1892–1913` rebases the TMA descriptor by `work_tile.coord_n`; `:1914–1927` applies the same route offset to SIMT. The TMA copy already indexes `(None, subtile_idx)` at `:2273`; SIMT partitions use the same index at `:2292,2311`. |
| No route padding is stored by TMA | Selected subtile i covers `[i*epiN,(i+1)*epiN)`, wholly below the valid-route count. Remaining subtiles retain the original route and partial-feature predicates. Existing TMA feature-domain bounds still handle feature padding. All integer valid counts from 0 through each public N in {8,16,32,64,128,192} preserve exactly the original valid-route set. |
| Warpgroup-uniform control and buffer lifetime | Work-tile metadata and subtile index are uniform across the epilogue warpgroup. Existing SMEM store, proxy fence, both epilogue barriers, elected TMA warp, `producer_commit`, and `producer_acquire` remain in their original order. The C-buffer index advances only when a TMA store occurs, exactly as before; SIMT does not consume a C-buffer stage. The existing final producer tail remains unchanged. |
| Scope by mode | The fused-finalize branch precedes this condition and excludes it at compile time. Gated SwiGLU/GeGLU FC1 uses its separate path and has zero iterations in this loop. Thus the SwiGLU benchmark changes only ordinary GEMM2. Non-gated ReLU2 FC1 also uses this ordinary store path, including when the overall MoE uses fused finalization. |

## Precision remains unchanged

The ordinary path has a BF16 intermediate, followed by FP32 routing reduction. It does not retain GEMM2 expert outputs in FP32:

1. `moe_w4a16.py:474–510` sends ordinary GEMM2 to `hidden_workspace`, then calls the existing `moe_unpermute` with router scales and the expanded-to-permuted map.
2. Both store bodies at kernel `:2248–2283` multiply the FP32 accumulator by FP32 expert alpha and convert to BF16. The proposal preserves both bodies exactly and only changes the store mechanism for complete subtiles.
3. `csrc/moe_utils_binding.cu:154–167` selects BF16 input / float router scales. `csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu:159–205` uses `AccumType=float`, iterates top-k in order, skips negative mapping entries, accumulates BF16 expert values times FP32 routing scales in private FP32 registers, and casts once to BF16 output. There is no atomic reduction in this ordinary path. Compiler FMA contraction is not asserted without emitted-code evidence.

No reducer, routing scale, accumulator type, rounding placement, or finalization synchronization changes. This is the precision-preserving opportunity identified by the ordinary-path audit; prior shared-reducer caching and launch-geometry experiments are not repeated.

## Existing numerical coverage

Only `TestCuteDslMoeW4A16.test_route_tile_boundary_accuracy` is extended with `half_tile_tail=[False,True]`. Its six geometries, top-k 2/3, ordinary/fused modes, input helper, forced catalog tactics, reference, and tolerance calls remain unchanged. The count grows from 24 to 48 cases.

| Route CTA N | Added tail rows | Fully valid TMA subtiles in the tail | Final partial rows |
|---:|---:|---:|---:|
| 8 | 5 | 0 | 5 |
| 16 | 9 | 0 | 9 |
| 32 | 17 | 0 | 17 |
| 64 | 33 | 1 | 1 |
| 128 | 65 | 2 | 1 |
| 192 | 97 | 3 | 1 |

Each case still has one complete route tile before its boundary tile. The original tail-one product remains. The six new ordinary N64/128/192 × top-k2/3 cases exercise the changed branch; their fused counterparts are controls. The previous partial-finalize cases can remain in the focused suite without fixture expansion. If combined with the prior four partial, two EP8, and twelve graph cases, the proposed suite has 66 cases; no collection or GPU execution has yet verified that count.

```bash
python -m pytest -q tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy
```

Local checks: Python syntax without imports, repository-config Ruff lint, Ruff format, and `git apply --check` pass. Running Ruff initially from the artifact root missed the repository E402 exemption for the existing test imports; rechecking with each original `--stdin-filename` from the repository passed without changing imports.

Native validation should establish that ordinary N64/N128/N192 retains the partial SIMT path while its TMA condition depends on the subtile end, that branch joins preserve C-buffer accounting, and that fused controls retain the previous body/resources. Numerical tests must establish actual mixed-store correctness. No speedup is claimed: TMA adds SMEM traffic and synchronization in exchange for fewer global SIMT stores, so native instruction count alone cannot establish latency benefit.
