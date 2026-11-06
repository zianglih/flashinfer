# Additional instruction audit

The official [PTX 9.4 maximum instruction](https://docs.nvidia.com/cuda/parallel-thread-execution/#floating-point-instructions-max) lists scalar F32 (two or three inputs) and F64 forms, not an F32x2 maximum. Half/BF16 packed maxima do not preserve the FP32 activation contract. Therefore the two scalar ReLU maxima are not replaced by an invented packed-F32 maximum. Existing packed multiplication remains appropriate.

The shared 16-element absolute maximum is a different opportunity: its ternary tree has actual generated dependency depth three instead of eight, with equal instruction count in the sampled native FC1. The independent `amax-tree/` experiment checks its device semantics and whole-chain timing before a retention decision.
