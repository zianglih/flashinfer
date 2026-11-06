# Packed per-token FC2 independent review

No source or gate blocker. Only the existing per-token bulk scale loop changes; AST outside that body is identical. All 8,192 lane/register/scale-group mappings match. For even i, floor(i/4)=floor((i+1)/4) and floor(i/16)=floor((i+1)/16); the second value uses the adjacent shuffle lane. The admitted bulk slabs are 32/64 tokens, so every pair is complete. Reverse tile order and partial token validity do not alter this bijection.

Captured PTX uses `mul.rn.f32x2` without FTZ/saturation; the original `mul.f32` defaults to the same rounding. No arithmetic reassociation or synchronization change. The [PTX mul contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#floating-point-instructions-mul) defines the packed result as two independent FP32 products.

105 artifact hashes pass. The gate has 18 paired exact output comparisons (36 source executions), 12 paired GEMM builds; all six FC1 executable text sections are byte-identical. FC2 geometry/stages/storage and SHFL counts are unchanged, with zero stack/local spills. Counts below exclude NOP padding.

|Config|PDL|Non-NOP control→candidate|Delta|REG control→candidate|Scalar FMUL removed|Packed FMUL2 added|
|---|---|---:|---:|---:|---:|---:|
|nv-n256|False|2563→2307|-256|151→154|512|256|
|nv-n256|True|2822→2566|-256|152→154|512|256|
|nv-n128|False|1441→1377|-64|128→117|128|64|
|nv-n128|True|1720→1656|-64|128→123|128|64|
|nv-m512|False|1959→1831|-128|148→148|256|128|
|nv-m512|True|2226→2098|-128|150→150|256|128|

Summed FC2 non-NOP change: -896. This establishes instruction simplification, not an end-to-end latency gain. Finite exact tests do not constitute exhaustive NaN/Inf or sanitizer validation. No production/helper edits or GPU work were performed by this review.
