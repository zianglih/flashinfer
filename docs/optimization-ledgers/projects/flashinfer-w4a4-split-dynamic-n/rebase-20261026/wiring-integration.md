# Resolved upstream wiring

Owned sources: `api.py`, `prepare.py`, `cute_dsl/fused_moe.py`, `cute_dsl/tuner.py`, `runners.py`. Source changes only; no staging, rebase commands, commit or push.

- `api.py` is byte-identical to fresh upstream `f45e1d6fdd62833ff8aa922f9eb139d590002ff8`, retaining new `CuteDslConfig.prepare_activations`.
- Following the user's later steering, `mxfp8` is the only canonical MXFP8×MXFP8 mode. The unmerged branch name `w8a8` is removed rather than retained as an alias. Existing NVFP4 deprecation remains.
- Functional/wrapper host and tuner ASTs match archived cleanup source `d3127e94` after only `w8a8` → `mxfp8` string replacement. Private K policy, replacement physical tactic geometry, and `blockscaled_route_n_v4` remain intact. Unified runner emits upstream `mxfp8` unchanged.
- Weight preparation uses upstream's single quantizer closure. It retains branch Blackwell 16-row / Rubin 64-row gate pairing, Blackwell-only MXFP8 guard, alignment128/CUDA quantization and byte-view scales, plus unchanged NV4over6 behavior. Other preparers retain exact upstream ASTs.
- Unified CuTe DSL activation matrix adds SiTU for both MX pairs. Only obsolete MX SiTU/fused-only guards are removed; per-token, scale layout, clamp, finalization and Rubin restrictions remain. Other backend runner ASTs remain upstream-identical.

Validation: `ruff check` and `ruff format --check` pass all five owned files. `python3 rebase-20261026/check_wiring_static.py` passes provenance and source-extracted host/tuner CPU execution, records hashes in `wiring-static.json`. It does not import/run GPU kernels or prove numerical integration. Existing tests are handled separately by the tests agent. Full owned-file diff against upstream is retained in `wiring-integration.patch`.
