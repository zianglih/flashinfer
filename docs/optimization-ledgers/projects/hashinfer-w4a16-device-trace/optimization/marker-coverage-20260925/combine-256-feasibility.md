# True 256-bit combine feasibility

Decision from user: keep the current 128-bit implementation. This is an assessment of a separate prefill experiment, not a retained change. Source remains clean at cd7cc07; no new GPU benchmark or combine prototype was run.

## Hardware and present compiler evidence

NVIDIA PTX ISA documentation, freshly checked: global load/store .v8.b32 and .v4.b64 were introduced in PTX8.8 and require sm100 or newer. These access32 bytes/thread and require natural32-byte address alignment. Sources: https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-ld and the corresponding st and addresses-as-operands sections.

Current remote CuTe4.8.0 CopyUniversalOp/CopyG2ROp/CopyR2GOp Python wrappers accept a nonnegative num_bits_per_copy; this alone is not a compiler-lowering proof. Stronger current evidence: W4A16 epilogue.py:591–592 already requests a256-bit BF16 CopyUniversalOp, and the final cd7cc07 SM103a capture disassembly contains native STG.E.ENL2.256 at0x6e90,0x7170,0x8310,0x8320,0x8460,0x8470. This proves native256 stores elsewhere in the current kernel, not a256 combine load or benchmark speedup.

## Distinction from previous wider workers

Historical adjacent16 reducer used16 BF16 elements/thread but two128-bit halves for every route and output. The matched review at /Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/integrated-topk-20260918/reduce-tile16-current/codegen-selected-t4/MATCHED_T4_REVIEW.md reports8 LDG128+1 STG128 per width8 worker versus16 LDG128+2 STG128 per adjacent16 worker. Coalesced16 similarly retained two128-bit operations per route/store. Neither establishes a performance result for true256 combine.

## Opportunity and implementation boundary

True256 would give16 BF16 output positions/lane,512/warp. For top8 and the same16 output positions, route/output data instructions could change from16 loads+2stores at128 bits to8loads+1store at256 bits, while total payload bytes and per-element ordered FP32 accumulation stay unchanged. Wider workers also amortize score/address/loop work. They reduce available worker count and require16 FP32 accumulators instead of8; native spills/register scheduling need checking. Prefill has enough work that the parallelism reduction is less concerning than tiny decode, but bandwidth-limited behavior may leave little gain.

Current frontend.py:_to_cute defaults to16-byte assumed alignment and uses it for combine_output and reduced_output (lines242,430–436,459–460). Existing output-view support must remain valid. A candidate needs a genuine32-byte source/destination alignment check/proof and a128-bit fallback; never merely raise the assumption for all callers. CurrentH%32 ensures row stride divisibility, but does not prove base-pointer alignment. Prefer existing CuTe copy operations and a compact private specialization, without copying the whole reducer.

Recommended isolated trial: baseline current128; true256 candidate on prefill4K/8K/16K global EP4, with EP8 and decode guards. First confirm intended LDG/STG256 instructions and counts on the actual selected specialization, then compare the full forward using established same-node cold-L2 CUDA-graph CUPTI samples and exact outputs. Keep reductions in identical top-k order. Use observed break-even to choose any eventual prefill threshold; do not invent one from labels. No change to the current tracing PR or upstream.
