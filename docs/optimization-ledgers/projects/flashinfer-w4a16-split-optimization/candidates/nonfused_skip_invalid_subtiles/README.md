# Skip wholly invalid ordinary epilogue subtiles

Outcome: **not retained**. The trial was applied independently over retained `88ff7db6a558e8acbc0cd964275410cf94e5c22c`, producing kernel SHA256 `ae6ef44ce1aa0c64bdad284e8ecae69977709bd125f397683c012639f25b3e72`. Native review, four private zero-route probes, 36 bitwise launches and 66 existing numerical tests passed. Two complete 1–8192 non-fused sweeps gave −0.1044% and +0.2084% geometric latency change over 8–8192. The small gains at matched affected rows did not justify the extra dynamic bound calculation. The 8192 variance does not establish a source regression. No row minima were selected.

Source, proof and all results remain here; the live local kernel was restored to retained005 (`1fe29f6f`). See `BENCHMARK_COMPARISON.md`, `BENCHMARK_REPEAT_COMPARISON.md` and `OUTCOME.json`. No candidate007 commit was published.

## Original preparation and proof

The following proposal was initially held against retained `b90b34744491c36d0039f44cba664191f7bb0eb0`. No live repository edit, GPU call, new test, or native compilation. The proposal changes only the nongated ordinary epilogue loop bound; FP32 accumulation, BF16 scratch/output types, router scales, and the fixed-order combiner remain unchanged.

- [source.patch](source.patch): `106b07705fec7e176ee83c861e49921e6dbdd9beb7f7ea93248cc842a38d7a93`.
- Proposed kernel: `c9e756381a24d7003d898905b3650701d185e77807ce40deb9b17eb7662972d0`.
- [source-review.json](source-review.json): whole AST equals b90 after removing the single new bound block. Syntax, Ruff and apply checks pass. The patch applies independently to b90 and the saved005 TMA-prefix source; it does not include006's unroll hint.

## Routing validity proof

**Current W4A16 requires GEMM1 N == GEMM2 N.** `moe_w4a16.py:395–397` chooses GEMM1's routed-row tile N and raises if GEMM2 differs. It does not use max(GEMM1N,GEMM2N). That same N feeds workspace allocation, `moe_sort(tile_tokens_dim=N)` at405–425, BF16 permutation at439–449, and both private GEMM tactics. A proof based on unequal route tiles is unnecessary for this accepted path.

For local expert e, let c[e] be its nonnegative route count, q[e]=ceil(c[e]/N), and o[e] the exclusive sum of q for earlier experts. Every routing implementation writes only local tile indices j in `[0,q[e])`:

```
global_tile = o[e] + j
route_start = global_tile * N
mn_limit = min((global_tile + 1) * N, o[e] * N + c[e])
D = mn_limit - route_start = min(N, c[e] - j*N)
```

Because j<ceil(c/N), `c-j*N >= 1`, hence **1 <= D <= N** for every emitted active tile. If c=0, q=0, so there is no record. Counts for nonlocal experts are zero. Route order and duplicate-ID handling can change c, but not this arithmetic invariant. This assumes the existing Int32 routing-size contract is respected.

Exact producer trail:

| Producer path | Relevant source |
|---|---|
| Host entry and tile width | `csrc/moe_utils_binding.cu:353–438` supplies precomputed IDs, stores tile N in `mTileTokensDim` and its power-of-two encoding in `mPaddingLog2`, binds the output arrays and active count. `trtllm_fused_moe_routing_deepseek.cu:492–504` delegates to `runPostTopKPipeline`. |
| Dispatch of all post-top-k paths | `csrc/fused_moe/trtllm_backend/trtllm_fused_moe_routing_common.cu:46–167`: static block, dynamic block, single cluster, cooperative, or histogram+offsets. |
| Static block | `trtllm_fused_moe_routing_custom.cuh:186–213` initializes nonlocal counts to0; `:219–229` computes q and exclusive offsets; `:244–282` writes exactly j<q, min limits and active sum. |
| Dynamic block | Same file `:501–576` initializes/localizes counts and scans q; `:578–614` writes the same min limits and active sum. |
| Single cluster | `include/flashinfer/trtllm/fused_moe/RoutingKernel.cuh:290–350` initializes/localizes counts; `:386–437` accumulates them and scans q; `:440–489` writes the same formula and active sum. |
| Multi-kernel offsets | Same header `:698–718` reads reset/histogram counts and scans q; `:740–770` writes the same active sum and min limits. |
| Cooperative | Same header `:1107–1136` accumulates histogram counts, synchronizes the grid and scans q; `:1138–1171` writes the same min limits and active sum. Contiguous route windows affect histogram work assignment, not this formula. |
| Pow2 and N192 arithmetic | Same header `:139–165` defines ordinary ceil division and multiplication for either power-of-two padding or exact tile N; count0 maps to q0 in both cases. |

No producer rounds the active route count up to a cluster width. Metadata after `num_non_exiting_tiles` is intentionally uninitialized and must not be read.

## Scheduler admission and padded peers

The owned kernel copies D as `tile_idx_to_mn_limit[route_idx] - route_idx*N` only after its routed-tile bound passes:

- **CLC:** kernel1217–1250 requires both scheduler validity and `route_idx < num_non_exiting_tiles`. Invalid CLC termination publishes group_idx=group_count and D=-1; the epilogue loop rejects it. Valid scheduler tiles beyond the routed count are skipped.
- **Static, M-first raster:** kernel1280–1310 uses scheduler validity and the same strict routed-count bound before reading/writing a work record; its terminating record has group_idx=group_count.
- **Static, N-first raster:** kernel1320–1367 separately checks the finite outer M extent and strict routed-count bound. Padded route positions are skipped; the terminal record again has group_idx=group_count.
- **Padded feature/M peer:** `_compute_grid` at2527–2545 rounds physical work to cluster geometry. Extra M peers still use the same route index and positive D. A feature-empty peer is not a zero-route tile. The proposed bound depends only on D, so every participating M peer retains the same number of epilogue iterations and the same single release.

The installed `ContiguousGroupWorkTileInfo.is_valid_tile` only checks `group_idx < group_count` (`mixed_input_helpers.py:934–936`); positivity is therefore a producer invariant, not a local assertion. Empty EP experts produce no records; if every expert is empty/nonlocal, the active count is0 and consumers receive only terminal work. Existing publication, PDL and metadata synchronization are untouched by the proposal.

## Private counterexample and safe bound

`_run_grouped_gemm` also accepts caller-supplied tile metadata. It does not validate device contents. A private call supplying expert_idx0, active_count1 and mn_limit0 admits a valid group with D=0. The current epilogue still loads its physical subtiles, stores no route values, and releases ACC once. A naive zero-useful-subtile loop would skip release and could prevent the producer tail from completing.

The held proposal handles that case without a new branch or API restriction:

```python
if cutlass.const_expr(
    not self.gated
    and not self.use_fused_finalize
    and self.cta_tile_shape_mnk[1] > self.epi_tile_n
):
    valid_routes = cutlass.max(
        1,
        cutlass.min(work_tile.distance_to_boundary, subtile_cnt * self.epi_tile_n),
    )
    subtile_cnt = cute.ceil_div(valid_routes, self.epi_tile_n)
```

Clipping before ceil division bounds its input to `[1,N]`, avoiding an overflow from arbitrary private D near Int32 max. The resulting loop length is `[1,full_subtile_count]`. D<=0 retains one load with the original all-false route store predicates; D>N retains the full physical tile. For public D, the last partial subtile remains and only wholly invalid suffix subtiles are omitted.

## ACC lifetime, ordering and alternatives

The original loop and body stay intact. The existing `subtile_idx == subtile_cnt - 1` condition now selects the last executed TMEM load. Every participating epilogue warp still executes one TMEM-load fence, one elected consumer release and one state advance after its last load. Subsequent conversion/store uses registers; omitted fragments were never required output values. The physical producer computes the same tile, and its ACC consumer barrier still receives the same arrival count. C-store stages advance only for actual TMA stores; skipped all-invalid SIMT subtiles never consumed a C stage. The next tile's state, work publication and final tails remain unchanged.

| Approach | Benefit and cost |
|---|---|
| **Dynamic useful-subtile bound (held)** | One compile-time exclusion and a short bound block, one body and the original release placement. Adds a small per-tile clamp/ceil expression, reduces dynamic TMEM loads/conversion/predication for N64/128/192 tails. The loop count is dynamic and may defeat006's full-unroll hint. |
| **Fixed unrolled loop with per-subtile activity guards** | Keeps constant offsets, but requires guarding each body and changing release detection to the last active subtile (plus a D<=0 first-iteration fallback). More joins and guards, larger code; do not combine speculatively. |

The final guard additionally requires route N > epi N at compile time. These are constructor/layout-derived static sizes (`:201–236`), so N8/N16/N32 omit all new clamp/ceil math; no compiler algebraic inference is needed to recover a one-trip loop. The initial unconditional one-subtile-math proposal970848e5 and its proof are preserved under `preparation_history/initial_bound/`.

For N128/D33, the bound becomes2 instead of4; for N192/D1 it becomes1 instead of6. N16/32 remain one subtile. No latency gain is established. Native review must verify reduced executed-loop extent, live bound/state joins, exactly one release, and unchanged resources. Use an ordinary N16 or N32 capture as a whole-PTX/SASS/encoding control: the new block is compile-time absent. Fused and gated controls likewise exclude it; ordinary N64/N128/N192 are the only public families that request the bound math. Existing tail-one and005 half-tail numerical cases can exercise the change without a new oracle; any raw D0 runtime case remains a separate validation decision.
