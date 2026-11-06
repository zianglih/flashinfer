# Dedicated-warpgroup gather4 optimization

**Completed:** combined R14 is installed in the single unstaged review checkout.
[Final results and validation](RESULTS.md) contain both comparisons and full raw phase medians.


The review checkout remains `../../flashinfer-fc1-gather-review`, based on
retained PR head `d35fcfda`. Experiments are immutable artifact snapshots;
only qualified, useful changes will be combined into that one unstaged checkout.
FC2 stays regular TMA. W4A16, public APIs, arithmetic and tactic enumeration
remain outside this experiment.

Runtime: C3 `fi-fc1-gather-1028`, eight B300 GPUs, CUDA 13.2,
`nvcr.io/nvidia/pytorch:26.05-py3`, CuTe DSL 4.8.0. The nine native compilation
cache links remain in persistent storage. No sanitizer runs.

## Investigations

- R6 codegen audit: actual frozen public-benchmark winners, source-bound PTX,
  cubin and SASS. N3U TP8 16K MXFP8/MXFP4x8 FC1 spills at 168 registers/thread,
  with a 208-byte stack and 26 LDL / 46 STL static sites. K3 EP8 4K and V3 EP8
  16K captures are spill-free. See `codegen/REPORT.md`.
- R8: move asynchronous scale completion publication after Gather4 issue,
  preserving owners, barriers, stage depths and all 384 threads.
- R9: control80 / epilogue256 / gather128 donation before role dispatch.
  The emitted policy passes the physical CTA-pool guard but reconverges before
  role execution. Both gather and epilogue use only low registers and spilling
  increases. It is not retained. See `codegen/register-guard/spill-roles.json`.
- R10: vectorize complete four-index routing groups, preserving predicated
  partial-group loads and current narrow two-CTA task coverage.
- R11: the same register policy inside three non-reconverging warpgroup
  branches, with existing control roles nested together. Each role body is
  unchanged; FC2 compiles without register reconfiguration. Guarded codegen eliminated the N3U TP8 prefill spills; all44 existing
  cases pass. Paired performance is being collected.
- R12: shared-only release and acquire around relaxed cluster barrier
  publication, retaining local completion and proxy ordering. All44 cases pass.
  The four-job CUPTI screen is complete: V3 EP8 -4.75%, V41F EP4 -0.75%,
  K3 EP8 -3.34%, N3U TP8 +0.30% versus PR head across affected dtypes and
  8/256/4096/16384 tokens (geometric mean). See `../r12/report/`.
- R14: combined R10/R11/R12 plus unsigned valid routing arithmetic. All44 existing cases pass. The full15-job PR-head screen and the
  direct R6 comparison are complete.
  Guarded K3/N3U codegen has zero spills and preserves the narrowed publication.
  R13 is only an intermediate source snapshot; it was not GPU-qualified.
- iKET: sampled, source-bound K3 EP8 MXFP4x8 4K control/R6 diagnostic with
  weight-readiness and gather-readiness waits separated. Instrumented timing
  is not retention evidence. Split markers localized an approximately0.8us
  per-stage delay to the broad cluster arrival. R12 reduces K3 emitted GPU-wide
  fences from29 to1; the small required proxy fence remains.

## Measurement contract

Quick screening uses V3 EP8 NVFP4/per-token, V41F EP4 MXFP8/MXFP4x8,
K3 EP8 MXFP4x8, and N3U TP8 MXFP8/MXFP4x8 at 8/256/4096/16384 tokens.
Same-GPU C-A-A-C, frozen routes/tactics, 10 warmups and 100 strict CUPTI
cold-L2 CUDA-graph samples per phase. NVFP4 includes initial activation
quantization. W4A16 is an unchanged control. Raw receipts retain source,
cache, winner, route and GPU identities. Different quick-screen candidates
are not directly paired with each other merely because they share PR-head
controls. Useful combined changes require a fresh matched comparison and
broader EP/TP coverage.
