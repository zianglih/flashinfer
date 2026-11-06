# K3 EP MXFP4x8 16K: resolve the retained comparison gap

Status: prepared only. All GPUs belong to the GLM5 campaign until root releases
them. The composed full matrix remains on hold until this diagnosis is reviewed.

The original writer-only R1 and static-SF runs measured −4.463% and −3.557% for
this cell. Both losses remain in their original reports. The original controls
drifted, and some clock samples showed power/SM-clock changes; those observations
do not establish that the changes are harmless. The complete initial audit is
`INITIAL_RESULTS.md`, with all 800 samples and 32 quartiles in adjacent CSV files.

## Frozen comparisons

- Control: exact `82254e206a44b95d9925e4594fac936731f80d21` source inventory.
- Writer R1: immutable `candidate-r1`; only its FC2 writer-owned commit affects
  MXFP4x8. Its additional W4A16 utility experiment is not called by this arm.
- Static SF: immutable `candidate-static-sf`, tested separately.
- Same existing K3 EP8, tokens16384, SiTU, MXFP4x8, unfused finalization, public
  benchmark/API, original route IDs/weights and recorded tactic. No retuning or
  external baseline rerun. MXFP8 is unsupported for this K3 comparison.
- Recorded tactic: route128; FC1/FC2 `(256,128)`, cluster `(2,1)`, static scheduler,
  K steps4/4. No new tactic or experimental policy flag.

## Phase-order-balanced measurement

Run each variant's fresh C-A-A-C and A-C-C-A as separate four-process campaigns
on one fixed physical GPU per variant. The two variants may use different GPUs;
only within-variant, same-GPU comparisons are causal. Record GPU UUIDs and idle
checks. Keep both independent order blocks and every negative result; do not pick
the better order. This is 16 processes and 1,600 CUPTI samples in total.

Use the original10warmups,100samples, cold-L2 CUDA-Graph CUPTI method. Keep the
normal persistent C++/CuTe/driver caches and frozen autotune entries. Do not add
thermal warmups, trim early/late samples, normalize by clocks, or set clocks or
power. The existing NVML sampler records all quartiles and exceptions. A later
fixed-clock diagnostic would be a separately authorized comparison.

The primary result per order block is
`100 * (sqrt(C1*C2/(A1*A2)) - 1)`, using each process's full100-sample median.
Report the four raw medians, both repeat spreads, FC1/FC2/combine durations and
exposed critical-path extensions, and every quartile's clock/power/temperature.
Component medians are attribution evidence and must not be summed as E2E time.

## Native image and resource binding

Before returning each owned compiled kernel to the benchmark, the unchanged
runtime register guard checks the actual CUDA library/kernel handle. A private
observer retains `compiled.__ptx__` and `compiled.__cubin__` from that same object,
then saves SASS/resources and hashes plus geometry/role/compile options/library
handles. `CUTE_DSL_KEEP=ptx,cubin` and a unique dump directory retain artifacts;
the callable, source, optimizer options, cache policy and timed operations do not
change. Missing artifacts or nonzero LOCAL stop before the owned launch.

Compare actual R1 FC1 cubins against control for this native winner. Do not infer
identity from earlier targeted signatures or from repeated CuTe symbol names;
those names are not unique across loaded libraries. All single-cell captures
must match the frozen native tactic and the resource receipts. Static-SF may
change FC1/FC2 code, so compare its arithmetic/MMA/synchronization counts and
resources without an unjustified binary-identity requirement.

The private harness differs only by this retention hook/environment; its static
normalization proof is `harness-proof.json`. Original compact harnesses, sources
and reports remain immutable. New configs/source manifests are under `prepared/`.

## Decision boundary

A reproducible 3–4% loss in the balanced fresh comparison argues for rejection,
even if static instruction counts decrease. If results remain sensitive to
phase order or clock trajectory, report the uncertainty and keep the composed
full matrix on hold for root's decision; do not silently accept or filter it.
