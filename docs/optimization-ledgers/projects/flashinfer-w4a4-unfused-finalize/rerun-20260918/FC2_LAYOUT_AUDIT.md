# FC2 output layout: W4A4 versus W4A16

Source inspected: `f9dd3c10541e087b716772245a9d033499745048`. This is a source/history audit; no new GPU run or layout A/B was performed.

## Direct answer

The two unfused paths arrange the same kind of intermediate—BF16 expert contributions—in different row orders. The difference is inherited from their producer kernels, not mandated by W4A4 versus W4A16 arithmetic. W4A4 optimizes the consumer's row addressing by scattering into token/top-k order; W4A16 preserves the producer's expert-grouped order and lets the consumer gather row bases. Neither layout is established as universally faster by the current benchmarks.

| Property | W4A4 unfused | W4A16 unfused |
|---|---|---|
| Logical FC2 scratch | `[N * K, H]` | `[route_slots, H]`, expert-permuted rows with route-tile padding |
| Route `(t, k)` source row for finalizer | `t * K + k` | `expanded_idx_to_permuted_idx[t, k]` |
| FC2 store | Row-segment scatter copy using the existing scatter epilogue | Ordinary tiled TMA store for fully valid subtiles; predicated SIMT store at route tails |
| Scratch allocation in current implementation | Additional BF16 expanded-route allocation | Reuses the BF16 permuted input workspace after FC1 is done |
| Finalizer access | Regular row-base arithmetic; mapping only masks nonlocal routes | Indirect row-base lookup through the routing map |
| Per-row memory access | Contiguous, vectorized/coalesced | Equally contiguous, vectorized/coalesced once the row base is known |
| Arithmetic | Ordered FP32 FMA over BF16 expert outputs, one BF16 cast | Same finalizer arithmetic |

Here `N` is input token count, `K` top-k, and `H` hidden size. The table describes unfused finalize only. Fused finalize writes/atomically combines directly into token output and is a separate tradeoff.

## Current source evidence

- W4A4 allocates `[num_tokens * top_k, hidden_size]` at `flashinfer/fused_moe/cute_dsl/fused_moe.py:475-479` and passes `input_is_expanded=True` at 512-520.
- W4A4's metadata warp reads the permuted-to-expanded mapping, sets `output_idx = safe_idx` for unfused output, and removes routing-weight application from FC2 at `blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:1992-2010`. The epilogue resolves that output row and uses `blk_copy` at 2195-2212. `blackwell/utils.py:167` emits a shared-to-global bulk copy; this is scatter of contiguous row segments, not scalar random stores.
- W4A16 allocates `hidden_workspace` and `intermediate` in expert-permuted capacity at `blackwell/moe_w4a16.py:68-90`. Native permutation fills that hidden workspace at 441-450, FC1 consumes it at 452-473, and unfused FC2 reuses it as output at 474-485. The finalizer takes the default permuted mode at 502-510.
- W4A16's kernel expresses output as `(hidden, routed_rows, 1)` with hidden dimension contiguous (`blackwell/moe_w4a16_kernel.py:595-597`). This is a logical transpose convention for the swapped GEMM operands, physically matching row-major `[routed_rows, hidden]`; it is not a column-major output penalty.
- W4A16 creates an ordinary shared-to-global tiled TMA atom at 752-758. Complete valid subtiles take that path at 2254-2286; incomplete route tails use predicated stores at 2288-2318. The unfused kernel does not even instantiate the routing-map/weight tensors used by fused scatter (`616-629`).
- The shared finalizer chooses sign-only mapping for expanded mode versus mapped row for permuted mode at `blackwell/moe_finalize.py:117-122,129-140`. Both use the same contiguous 128-bit BF16 vector copy and the same ordered FMA loop.

## Why the implementations evolved this way

Local history establishes the sequence without needing to infer from precision labels:

1. W4A4's deterministic mode was added by commit `ce29c1a58dedb22424b2cbe123e7c244aa48544f`, PR [#3976](https://github.com/flashinfer-ai/flashinfer/pull/3976). Its existing FC2 epilogue already scattered atomic contributions into token rows. The new unfused specialization minimally changed that destination to a unique expanded route row and replaced bulk reduction with bulk copy. The accompanying commit description explicitly chose compact expanded scratch instead of a larger expert-padded output buffer.
2. W4A16 arrived in commit `c9172e6a`, PR [#4048](https://github.com/flashinfer-ai/flashinfer/pull/4048), with native BF16 input permutation, BF16 grouped GEMMs, an expert-permuted intermediate, and reuse of the permuted input buffer for FC2 output. Its source already used the normal `moe_unpermute` mapped-row mode. This organization naturally keeps ordinary FC2 output in the GEMM's grouped order.
3. PR [#5186](https://github.com/flashinfer-ai/flashinfer/pull/5186), commit `0ef005a2cdbd9cbcb70a818f66655205c8a7558e`, subsequently improved W4A16 ordinary scratch stores by using TMA for each full valid subtile and retaining predicated route tails. It did not change ownership or finalizer layout.
4. This PR retains those layouts and provides a shared faster finalizer for both. It has not benchmarked either producer with the other layout.

Historical documentation caveat: the prose of #4048 called its unfused rows “expanded” in one bullet, but its actual host code reused `hidden_workspace` and called the existing permuted-row `moe_unpermute` without `input_is_expanded=True`. The code is authoritative; that prose does not establish an expanded-layout W4A16 implementation.

## Memory and EP8 tradeoffs

- W4A4 expanded scratch is exactly `2 * N * K * H` bytes of BF16 capacity. Nonlocal route slots exist but are never loaded by the finalizer; they need not be initialized.
- W4A16 scratch capacity comes from `moe_utils.py:79-148`: let `E=N*K`, `L=num_local_experts`, and `T=route_tile`. Capacity is `R=E*T` when `E<=L`, otherwise `R=((E+(T-1)*L)//T)*T`. It is a worst-case routing bound, not the observed local-route count. The currently reused hidden workspace has `2*R*H` bytes.
- For example, at `N=16384,K=8,H=7168,L=32,T=128`, expanded capacity is 1.75 GiB; padded permuted capacity is about 1.803 GiB (54.25 MiB more). This example fixes T128 for illustration; autotuning may select other route tiles.
- The expected local route count in a balanced EP8 simulation is `N*K/8`, or approximately one local route per input token at top-k8. Active permuted output is concentrated in the local expert ranges plus tile gaps. Expanded output is spread across the full `N*K` route-address range. Both store/read only valid local contributions; an 8x difference in reserved versus active route counts is not an 8x difference in bytes transferred.
- Buffer reuse is an implementation/lifetime benefit, not a fundamental advantage of permuted output: W4A16 could also write expanded rows into its already large hidden workspace after FC1, because R covers N*K. It would still need a different scatter epilogue. W4A4 currently has no analogous BF16 permuted-input H-wide buffer to reuse: its FC1 gathers/quantizes through a different path.

## Which is better, and what experiment would answer it?

- **Producer preference:** permuted output makes full-subtile TMA stores straightforward and avoids per-route destination scatter. That is a plausible direction for improving W4A4 FC2, particularly at large batches with many full expert tiles.
- **Consumer preference:** expanded output removes indirect row addressing and groups a token's route rows together. However both paths already coalesce/vectorize within each H-wide row; calling W4A16 a fully uncoalesced gather would be inaccurate. EP8's roughly one local route per token also reduces the opportunity for top-k row adjacency to matter.
- **Small batches/tails:** padding capacity and incomplete expert tiles weaken the benefit of a permuted TMA path. Actual latency depends on store issue overhead, tile shape, TMA use, finalizer cache/TLB behavior, and the producer/finalizer overlap—not layout names alone.
- **Current evidence:** W4A4 and W4A16 use different arithmetic pipelines, activation precision/quantization, operand orientation, weight-decode work, and tuned tiles. Their benchmark difference cannot isolate FC2 output layout. The current PR's before/after comparison also preserves each layout, so it cannot prove a winner.
- **Controlled follow-up:** add a W4A4 expert-permuted-output variant using the same FC2 arithmetic/tactics; compare FC2, finalizer, their overlapped span, and complete MoE under the existing EP8 token sweep. Keep routing and correctness identical. A mirror W4A16 expanded-store variant is possible but unnecessary for a first targeted test. Do not adopt a layout change based only on the current cross-backend timings.
