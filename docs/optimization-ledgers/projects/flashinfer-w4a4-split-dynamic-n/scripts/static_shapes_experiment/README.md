# Compile-time dimensions already present in the host cache key

Frozen control13ca1475 passes channel count, reduction size and expert count as
Int64 kernel arguments, despite including all three in the host compilation
cache key. Candidate marks those three wrapper arguments Constexpr and omits
them from compiled runtime calls. Routes and token count remain dynamic. No
H/I/T values, additional host cache-key dimension, tactic, or stage policy.

The isolated host function explicitly dispatches runtime arguments by selected
class; the production integration simply has one correct static signature.
Initial r1 correctly compiled but failed launch because static arguments were
still included in compiled(*args), producing duplicate stream. No candidate
GPU result from that failed arm. Corrected calls pass only pointers/routes/T.

72 strict paired cases pass (48 FC1,24 FC2): six supported format families,
quantized/per-token outputs, short/nonmultiple-stage K, tails, single expert,
N16/N64. Allocations reset before each arm. Native final bytes also match at
T4/128/512 and4K/8K/16K with logicalM512FC1/two-CTA M256FC2; N256 overlapping
FC2 storage checked atT128/T16384. These are focused development checks, not
broad numerical/sanitizer completion.

Actual seeded native benchmark inputs, fixed tactics, unfused finalize,
10 warmups /100 cold-L2 CUDA-graph CUPTI samples. Whole-chain reverse controls:

| Mode/T | Static(us) |13ca control(us)| Static(us) |
|---|---:|---:|---:|
|NVFP4/4096|206.960|210.145|207.937|
|NVFP4/8192|319.744|321.665|320.129|
|NVFP4/16384|560.001|558.946|558.913|
|MXFP8/4096|332.480|335.089|332.353|
|MXFP8/8192|471.986|491.745|472.930|
|MXFP8/16384|849.794|878.802|835.363|
|mixed/4096|258.304|263.456|258.848|
|mixed/8192|434.512|442.240|432.064|
|mixed/16384|787.759|804.833|797.744|

Large-case phase/control drift exists; these are incremental directional
screens, not the final primary retention table. NV16K is neutral, with small
FC1 loss offset by FC2 improvement. Other cases consistently improve. Keep
this hardware-independent specialization and continue resolving the remaining
NVFP4 prefill regression. Raw JSON includes every sample and routing histogram;
no saved primary baseline was rerun. Changed-file pre-commit passes.
