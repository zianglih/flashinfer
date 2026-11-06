# Two-warpgroup partial decode audit

Audit date: 2026-10-08. Read-only review of the retained local optimization ledger and the blog project's current FlashInfer source snapshots. No GPU execution or new performance measurement.

## Retained design

The split W4A16 kernel launches a 16-warp CTA. Warps 0–3 perform the epilogue; warps 4–7 specialize in MMA, scheduling, weight TMA, and activation TMA; warps 8–15 form two four-warp transform groups. The transform groups keep the 128-register launch allocation, with the epilogue at 176 and control group at 80 registers per thread. This divides conversion and output work without making epilogue warps alternate between those jobs.

Each transform group owns a **contiguous half of the complete NVFP4 blocks in the same K stage**. Source weights, compact scale bytes, and destination TMEM use matching ownership slices. Each 16-weight NVFP4 block remains whole, so its shared E4M3 scale is converted once, rather than redundantly by both groups. The groups do not alternate K stages.

Data flow:

```text
Global packed E2M1 weights + E4M3 scales
  → weight TMA → packed shared-memory stages
  → two transform warpgroups → packed register fragments
  → native packed conversion + BF16x2 multiply in registers
  → tcgen05.st.32x32b.x8 → BF16 operand TMEM
  → BF16 tensor-core MMA with separately loaded BF16 activations in SMEM
  → FP32 accumulator TMEM
  → epilogue register loads, FP32 global scaling, and fused activation
```

The transform role waits for its raw TMA stage and a free decoded-weight stage, loads scale and weight fragments, decodes into registers, stores to operand TMEM, executes the asynchronous TMEM-store visibility fence, then commits readiness to the MMA pipeline. MMA waits for both transformed weights and activations before consuming the stage. Multiple stages overlap this work. The conversion schedule therefore directly controls how quickly an MMA stage can become ready; weight-traffic savings alone do not guarantee a well-fed BF16 MMA pipeline.

Current source, relative to `evidence/layout-audit-current/`:

- `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:153–164`: CTA roles and register allocation.
- Same file, `325–374`: operand TMEM destination and contiguous complete-block partition across both groups.
- Same file, `386–425`: matching scale ownership and independent compact-scale tiling.
- Same file, `455–469`: TMEM-store fence and producer commit.
- Same file, `502–581`: load-ready/free-TMEM waits, register decode, TMEM store.
- Same file, `1161–1168`: `tcgen05.St32x32bOp(Repetition(8))`.
- Same file, `1680–1694` and `1734–1766`: MMA views and waits before consuming TMEM weights and SMEM activations.

## Partial decode arithmetic and instruction schedule

The CUDA 13.2 direct helper uses **native packed conversion instructions plus packed multiplication**, not one fused E2M1×E4M3→BF16 instruction:

```ptx
cvt.rn.bf16x2.e4m3x2  // duplicated shared E4M3 scale, once per 16-weight block
cvt.rn.bf16x2.e2m1x2  // each packed pair of weight values
mul.rn.bf16x2          // local E2M1 × E4M3 product
```

The result is exact in BF16 for finite NVFP4 code/scale values. E2M1 has at most two significant binary bits and E4M3 at most four, so their product needs at most six, within BF16's eight significant bits. Product magnitude ranges from 2^-10 for the smallest nonzero values through 6×448=2688, comfortably within BF16's normal range. This is exactness relative to the stored local NVFP4 representation; it does not undo the original weight quantization.

The arbitrary FP32 global weight scale is intentionally excluded. Applying it to BF16 operands would add scalar work to the decoder and introduce BF16 rounding. Instead, the epilogue multiplies the FP32 accumulator after loading it from TMEM, before SwiGLU. It is inaccurate to describe arithmetic occurring inside TMEM itself.

Current source: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py:18–61` contains the CUDA 13.2 direct helper; `167–243` uses packed word fragments and one 16-value helper per block. Older CUDA toolkits use an explicit-RN FP16 intermediate and exact widening compatibility path. The article can center CUDA 13.2, matching its capture recipe.

## Optimization history that supports the explanation

Source: `/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md`.

- **Lines 428–436, rejected full FP32 prologue scaling:** moving the global FP32 factor into weight decode materially slowed representative EP8 and TP8 rows and added BF16 rounding. This directly supports leaving the scalar in the FP32 epilogue.
- **Lines 1132–1147, rejected four-scale helper:** packing four E4M3 scale conversions reduced conversion count but put four blocks behind a larger opaque inline-assembly dependency region. EP8 geomean was about 0.838×. Fewer PTX conversion instructions alone did not produce a better schedule.
- **Lines 2021–2049, rejected two-scale helper:** a controlled same-node comparison measured 0.9987× EP8 geomean. A prior cross-node apparent gain was invalidated; use the controlled result. The one-block helper was restored.
- **Lines 2877–2909, superseded half-block checkpoint:** first dedicated eight-warp version split individual 16-weight blocks into eight-value halves, duplicated scale conversion, and broadly regressed. This is not the final design.
- **Lines 2922–2969, intermediate block-parity stripe:** keeping complete blocks gave the first overall eight-warp win, but preserved a dense tail regression.
- **Lines 2985–3033, retained contiguous complete-block ownership:** dividing block ranges contiguously improved EP8 geomean to 1.0264× over the four-warp baseline and removed its EP8/4096 regression. The packed fragment is bitcast to words once and consumed as two words per 16-value block, avoiding byte extraction/reconstruction.
- **Lines 3046–3082, retained register budgets:** uniform 80-register control group plus 128-register transform groups is valid; mixed control-group register reallocation previously hung. Do not imply the exact register budget alone caused performance gains.
- **Lines 5020–5060, retained shorter FC2 fragments:** decoding two 64-value register fragments rather than one 128-value fragment shortened live ranges and improved FC2 in its tested dense tactic. Tensor-pipe utilization rose from 65.50% to 66.29% of elapsed cycles (70.06% to 70.57% of active cycles), without spills. These are separate historical metrics, not the article's 80% PM-sampled main-phase observation.
- **Lines 5240–5270, rejected alternating K stages:** assigning a whole stage to each four-warp group instead of both groups sharing the same stage doubled each group's source/decode work before its TMEM store. GEMM2 increased from 153.952 to 169.088 µs; elapsed tensor-pipeline utilization fell from 66.29% to 59.61%, eligible warps per scheduler from 1.12 to 0.76, and long-scoreboard stalls increased. This is particularly strong evidence that the length and balance of the per-stage transform schedule can throttle MMA without register spilling.

## Wording and measurement boundaries

Suggested prose: “The weight decoder is part of the MMA supply line. BF16 tensor cores have less peak throughput than NVFP4 tensor cores, so we cannot afford to leave their pipeline waiting on an unnecessarily long conversion schedule. Two specialized warpgroups split each weight tile into contiguous ranges of complete NVFP4 blocks, decode the exact E2M1×E4M3 product, and write their disjoint results directly to operand TMEM. Keeping the global FP32 scale in the epilogue makes this supply line both shorter and more accurate.”

Do not state that conversion has zero cost or never throttles MMA. Exact products and the carefully bounded conversion schedule reduce avoidable work and rounding; their combination supports high observed utilization.

The blog's historical ~80% W4A16 main-phase utilization is a PM-sampling timeline observation for FC1 at 4096 tokens, with whole-kernel average 73.1%. It is not a matched two-WG ablation and cannot isolate that design choice as its sole cause. Do not combine its numbers with the older ledger's GEMM2 active/elapsed metrics. Fresh NCU capture remains pending; retain the draft placeholder and publication note.

MegaMoE can refer back to the same partial-decode and two-transform-group principles, then focus on its additional dispatch/combine overlap. Its total CTA has five groups and different role/register budgets; do not copy the split kernel's four-group table unchanged.
