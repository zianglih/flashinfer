# Synchronization audit validation

Retained base: `9334cb34fe9c81653dc4748632f44449e9aecd8d`, including the shared
FC1/FC2 CLC flag and retained initialization-fence cleanup. Canonical source is
read-only for these helpers. Source-only deployment creates one reusable clean
control and immutable candidate copies remotely, retaining verified native C++
artifacts and giving each changed DSL source its own persistent namespace.

Initial capacity inventory is `environment-inventory.json`: eight idle B300s,
CUDA13.2.78, driver595.91.07, CuTe4.7.1 and NV26.5 PyTorch. Root assigned operands
GPUs0/1, scheduler2/3, and quantizer4; recheck exclusivity immediately at launch.

## Exact and codegen gate

The proven initialization-fence probes change only the explicit tactic encoding
from equal six-field FC flags to one five-field shared flag. `reuse-origins.json`
records their provenance. Eight CLC cases cover four formats, one/two CTA MMA,
inline/overlapping epilogues, both PDL modes, multi-wave/live/empty/padded routes,
and terminal drain. They produce64 exact replays and32 core artifacts per source.
Static one-CTA inline, one-CTA overlap and two-CTA overlap add24 replays and12 cores.
Source-paired equality is bit exact; this is not sanitizer or exhaustive coverage.

`deploy.py --candidate <local clone> --name <iteration>` freezes receipts and
deploys source only. `launch_gate.py --deployment <deployment.json> --review
<approved protocol note> --gpus X,Y` is called only after root authorization.
The first gate establishes retained9334 controls. Later candidates reuse those
exact same-GPU controls, probe hash and input identities; old9b evidence is never
silently relabeled. Every compile keeps PTX/cubin and records resources/SASS.
Storage or capacity changes require an explicit reviewed validator contract;
the default validator requires unchanged geometry, stages, storage and UMMA.

## Fixed model screen

`selection-cache-receipts.json` pins the six completed native shared360 B search
caches and routing outputs. Reuse selections, not historical latency. No fresh
AUTO is needed for initial screens. All3 models ×4 formats use `run_fixed.py`:
standard NVFP4, per-token NVFP4, MXFP8 and MXFP4x8. V3/K3 EP8, V4.1-flash EP4.
NV includes input quantization; MX starts prequantized; fused finalize is disabled.
TRTLLM and W4A16 are excluded from this kernel diagnostic.

Default screen tokens32,128,4096,16384 produce48 points. Each cell uses four
processes CAAC,100 raw cold-L2 CUDA-graph/CUPTI samples plus10 warmups. Opening
control may reuse only a matching source/helper/cache/GPU prior closing control.
`analyze_fixed.py` requires the complete grid and computes
`sqrt(C0*C3/(A1*A2))`, then geometric means; tokens1/2 are excluded if requested.
Full13-token retention remains separate from this bounded diagnostic screen.

## Optional next AUTO telemetry

`observe_table.py` installs `nested_timing.py` only when native AUTO is already
needed. It preserves call arguments, return values, exceptions and tactic order,
adding no GPU synchronization. Nested context, `_profile_single_kernel` and
`cute.compile` spans report inclusive/exclusive host wall time. Profile-exclusive
time excludes nested compiler API calls but includes warmup, graph capture,
measurement and waiting. Compiler API wall includes SDK cache lookup; native C++
compilation/import time is not classified as CuTe compilation. This is not pure
GPU traversal time. Fixed replay never enables this instrumentation.

No automatic GPU launch, new autotune axis, production benchmark edit or policy
change is part of these helpers. Raw evidence and receipts remain project-local.

## Completed composed iteration

Source `b4fb9c7a20b216839f4e879b9b576df098d64a10ece2816bbd350f2dafb3223a`
against retained9334 is collected under `composed/`. The final exact gate adds
narrow M512 two-channel CLC and static probes, plus real N256 uniform/per-token
output-stage reuse. `final-gate-validation.json` records120 exact replay
comparisons and60 compiled core pairs, no spills, register deltas−8…+3 and
summed static instruction deltas−1049. Counts include repeated geometry with
additional telemetry; instruction sums are across variants, not dynamic totals.

The complete48-point fixed-winner CAAC screen is timing-neutral:1.000965× overall,
1.000658× decode and1.001271× prefill. Worst cell:V3 MXFP4x8 at16384tokens,0.992868×.
All twelve model/backend geomeans fall between0.999039× and1.003929×. See
`composed/screen-evidence/screen-validation.json` and the192 raw100-sample records.
The screen reused completed shared-policy selections but measured fresh9334
controls; it neither reran AUTO nor established a stable speedup. All eight GPUs
were idle after completion. Retention/publication remains parent-owned.
