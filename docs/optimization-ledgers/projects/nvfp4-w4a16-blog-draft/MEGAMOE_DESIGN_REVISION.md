# MegaMoE revision: dependency and warp-reuse audit

Read-only source audit, 2026-10-07. No new GPU experiments. This note supports
moving MegaMoE into its own top-level section after the general W4A16 mechanisms.

## Source pin and scope

The saved `evidence/flashinfer-pr5019-source/*.py` snapshot is the public source
pin `7ca3eb567a2400df70579d55e9bc717ea1784b0c`. The independent clone at
`/Users/ziangli/playground/projects/flashinfer-pr5019-merge-sync-20260921/flashinfer`
was also checked: clean tree and HEAD at exactly that commit. Additional shared
transport and frontend files below were read there at this exact pin.

Use `https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/`
plus the repository paths below for pinned source links. This source pin is not
the benchmark pin `44a04fd247cf2f93bee4052bf439bc93f32c7f8c`. It also is not a
recovered capture commit for the selected HashInfer traces. Preserve these
three provenance boundaries.

## What the conventional split implementation already does

The implementation is already carefully warp-specialized. It is not a serial
load-then-dequantize-then-compute baseline:

- `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:153-174`: 16 warps:
  epilogue 0–3, MMA 4, scheduler 5, weight TMA 6, activation TMA 7, decoders 8–15.
- `.../moe_w4a16_kernel.py:1411-1431`: only the activation-TMA role waits for the
  predecessor grid when PDL is enabled.
- `.../moe_w4a16_kernel.py:1477-1499`: weight/scales loading has an independent
  role. Static expert weights do not depend on activation values. With PDL and
  fused activation, this role can trigger the dependent grid early.
- `.../moe_w4a16_kernel.py:1534-1559`: raw weight and scale TMA are a pipelined
  producer; `1580-1643` gives the independent transform consumers/producers.
- `.../moe_w4a16_kernel.py:1729-1755`: MMA waits separately for decoded weights
  and activations before issuing the matrix instructions.

Thus conventional split W4A16 already pipelines weight movement, decoding,
activation movement, MMA, and epilogue work. Cross-kernel head start is an
additional possibility when PDL is enabled. The #5019 benchmark disables PDL,
so do not explain its measured speedup as a PDL gain. Routing/tile metadata,
finite stages, and operand readiness still bound the amount of look-ahead.

## What MegaMoE adds: a larger scheduling window

All abbreviated `megamoe_kernel.py`, `token_comm.py`, and `epilogue.py` paths
below are under `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/`.

1. **First obtain routing metadata.** In `megamoe_kernel.py:1245-1265`, scheduler
   warp 7 waits for dispatch metadata before publishing task records. Every
   compute role has its own consumer state (`1268-1277`, `1319-1327`,
   `1382-1404`, `1579-1582`).
2. **Release compute before the token-pull loop completes.** Shared transport
   `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:1579-1640`
   performs dispatch preparation, the metadata barrier, then signals
   `nb_dispatch_to_sched` at `1612-1616`, **before** calling `dispatch_pull` at
   `1622`. The scheduler can therefore issue work while dispatch moves inputs.
3. **Stage inputs into expert buffers concurrently with weight preparation.**
   Shared transport `:991-1005` pulls a source token into a per-warp shared
   staging buffer; `:1075-1114` waits for the pull, stores the row into the FC1
   expert input pool, and waits for that store before publishing readiness via
   the batched arrival counter (`:1120-1134`). Meanwhile, the separate weight
   role loads that expert's packed weights and scales (`megamoe_kernel.py:1269-1314`)
   and the two decoder groups prepare TMEM operands (`1525-1608`).
4. **Keep the true activation dependency local.** FC1 activation warp 6 waits
   for its input tile via `fc1_tma_b_predispatch_spin`
   (`megamoe_kernel.py:1328-1347`; shared transport `:578-599`). Weight load and
   decode do not perform this wait. MMA joins the operands only at
   `megamoe_kernel.py:1419-1425`.
5. **Apply the same separation at FC1→FC2.** A published FC2 task lets weight
   loading/decoding proceed through the same independent roles. Only activation
   warp 6 waits for the relevant FC1/SwiGLU intermediate's completion counter
   (`megamoe_kernel.py:1348-1374`). FC1 publication follows epilogue stores and
   epilogue-warp rendezvous (`epilogue.py:174-194`). This allows FC2 weight
   preparation to overlap preceding FC1 production, subject to finite scheduler
   and operand buffers. The scheduler is grouped FC1→FC2, not an arbitrary
   out-of-order task graph (`fc1_fc2_fuse_sched.py:226-233`).

This is more precise than saying all preprocessing is hidden: **once routing
metadata has released a task, the decoder can work while input delivery or the
previous GEMM's epilogue is still producing the activation operand.**

### Important distinction: three meanings of “input staging”

- Python backend `flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py:222-279`
  preserves hidden-state/ID/score source references for the kernel. It separately
  copies any supplied epilogue scale/normalization tensors (`254-275`). Those
  host-launched scale copies are not evidence of concurrent device decode.
- Kernel `token_comm.py:23-102` has optional local `stage_inputs`: 128-bit BF16
  copying and ID/score staging by dispatch warps. This runs **before** dispatch
  preparation (`megamoe_kernel.py:1476-1498`). The scheduler waits for the ensuing
  metadata publication. Do not say initial weight decode overlaps this local
  staging phase.
- The later `dispatch_pull` movement into expert input pools **does** occur
  after scheduler release and provides the extra overlap window identified
  above. “Input delivery and staging into expert buffers” is accurate; an
  unqualified “input staging overlaps decode” can imply the wrong phase.

## Trace support: concrete but limited

`TRACE_ANALYSIS.md` records a selected 128-token capture with K0/K1/K2 decoder
commit markers finishing at 23.584/24.832/25.888 microseconds, before the first
activation TMA at 27.712 microseconds. The selected 4096-token capture commits
two tiles at 48.544 and 50.400 microseconds, before its first activation TMA at
84.064 microseconds. Its third decoded tile waits for TMEM reuse: decoder warp
12 has a 35.296-microsecond slot-free wait. These captures show both useful
look-ahead and backpressure.

The safest article claim is that weight preparation runs ahead while the
activation path is waiting for dispatch. The source identifies which later
input-pull/staging work can overlap and additionally supports the FC2 readiness
mechanism. The older trace analysis does not itself enumerate a quantitative
FC2-readiness overlap, so do not invent a second measured latency saving from
the source alone. Selected instrumented cluster-local traces are explanatory
evidence, not whole-GPU utilization or benchmark-latency measurements.

## The extra warps also improve the final combine design

- W4A16's geometry is 640 threads / **20 warps**:
  `megamoe_kernel.py:244-248`. Eight decoder warps (12–19) are additional to
  epilogue (0–3), MMA/loads/scheduler (4–7), and dispatch (8–11).
- W4A4 has **12 or 16 warps**, depending on token-return tactic:
  `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/megamoe_kernel.py:297-318`.
  Its conventional final top-k combine is launched separately at `:1531-1557`.
  This is a property of the compared implementation, not a theorem that W4A4
  cannot fuse combine.
- W4A16's retired decoder groups prepare combine worker coordinates and local
  scores while the last MMA can still consume weights (`megamoe_kernel.py:1609-1626`).
  Other retired roles prepare while dispatch drains peer returns (`1648-1661`).
  Preparation explicitly avoids remote result reads (`1039-1058`).
- Compute roles rendezvous at `1633-1634`. Dispatch completes the cross-rank
  return drain (`1636-1644`), then all roles rendezvous again (`1662-1665`).
  **Only after that** do 16 retired warps (0–7 and 12–19) perform ordered final
  combine (`1666-1693`), while dispatch warps 8–11 clean up (`1694-1699`).
- Worker reuse preserves compute-phase warp counts and register allocation. It
  does not mean combine result reads run before FC2 completion or that no
  occupancy/resource cost exists. A persistent kernel retains a fixed grid and
  compute-phase resource allocation into its tail.
- Final combine uses 128-bit route reads/writes and packed FP32 arithmetic:
  `topk_reduce.py:70-118`. This makes sense for the fixed pool of retired workers
  and should accompany, not replace, the concurrency explanation.

For the 256-bit experiment, preserve `COMBINE_ANALYSIS.md`'s distinction: first
candidate spilled combine state; later spill-free refinements also failed to
improve the focused end-to-end timing. Avoid attributing all regression to
spilling. There is no clean isolated scalar-versus-128-bit timing ablation.

## Suggested narrative for the new top-level section

### MegaMoE gives the decoder more useful work to overlap

The split kernels already exploit the central freedom of weight-only
quantization: weights can be decoded before their activations arrive. MegaMoE
puts that pipeline inside a larger persistent schedule that also owns token
dispatch, both GEMMs, and output return. Once the routing metadata is ready,
the weight workers can start while dispatch is still pulling and staging the
expert's input rows. Only the activation-loading warp waits for those rows;
the decoder does not. The same separation applies to FC2: its weights can be
prepared while FC1's epilogue is still producing the SwiGLU output it needs.

This gives dequantization additional places to run. In the selected decode
trace, three weight tiles have already been decoded before the first activation
load. The larger capture makes the limit equally visible: two tiles run ahead,
then the decoder waits for free TMEM space. We are moving useful work into
existing waits, within a deliberately bounded pipeline.

### Decoder warps become combine warps

W4A16 brings another useful resource to the megakernel: workers. Its 20-warp
layout has two dedicated decoder groups, compared with 12 or 16 warps in the
W4A4 layout. Once their compute duties finish, 16 warps can become the final
combine workers while dispatch finishes cleanup. That lets us keep the ordered
combine inside MegaMoE without taking workers away from the compute pipeline.
Combine setup can start earlier, but reading the returned expert outputs still
waits for the cross-rank drain.

Those workers inherit the persistent kernel's resource allocation. They do not
have the independently sized grid of a standalone combine kernel, so making
each instruction do more work matters. The retained path uses 128-bit loads
and stores and packed FP32 arithmetic. Blackwell's wider 256-bit operations
looked attractive, but the first version spilled combine state, and later
spill-free variants still did not improve the measured end-to-end result.

## Editorial placement

Keep the byte table, precise dequantization/FP32 epilogue choices, and split
overlap explanation in “Why W4A16 decode is fast.” Keep the acceptance-length
result there as a distinct application-level benefit. Start a following H2
MegaMoE section with the broader schedule, then the concrete trace, then final
combine reuse, and finally the #5019 kernel-only performance table/plot.
