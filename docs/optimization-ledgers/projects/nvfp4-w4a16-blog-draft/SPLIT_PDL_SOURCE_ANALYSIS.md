# Split W4A16 run-ahead and PDL source audit

Read-only audit, 2026-10-08. Source: FlashInfer `bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4`, locally archived under `evidence/layout-audit-current/`. This establishes implementation scheduling opportunities, not a new timing measurement or an overlap ablation.

## Recommended article explanation

Suggested heading: **Weight decode can get a head start**.

The weight-decoding work has no dependency on the incoming activation values: a packed E2M1 weight and its E4M3 scale are sufficient. Once routing identifies the expert, dedicated weight-load and decode warps can prepare BF16 tiles before the activation-producing kernel finishes. The activation load is the point that actually needs to wait. That distinction matters more than saying dequantization is merely “fused.”

The split implementation places Programmatic Dependent Launch (PDL) synchronization around that distinction. Only the activation-loading warp waits for the preceding grid; the scheduler, weight-loading warp, and decoder can proceed independently. FC1 issues its dependent-launch hint from the weight-loading warp before the weight-load loop. This makes FC2 eligible to initialize its pipelines and barriers and begin preparing its own weights while FC1 continues. In the ordinary separate-finalizer path, FC2 similarly hints the finalizer after its input dependency wait, so the finalizer can prepare routing metadata before waiting to read FC2 outputs.

Run-ahead has a finite window: the decoder still needs its raw-weight load to complete and an available decoded-weight TMEM stage, and MMA still waits for both operands. The contrast with W4A4 is specifically the activation-quantization work. Fused SwiGLU-output quantization needs the newly computed output values to find block maxima, generate scales, and pack E2M1; it cannot prepare those same values before they exist. This does not mean W4A4 lacks all pipeline overlap.

## Exact source anchors

Base URL: `https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/`

All kernel anchors below refer to `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py` unless another file is named.

| Claim | Source lines | Detail |
|---|---|---|
| Separate activation and weight producers | 153–160 | Warp 6 weight TMA, warp 7 activation TMA, warps 8–15 transform. |
| Own pipeline/barrier setup happens before decode | 931–1025; 1220–1225 | Initializes raw weight, transformed weight, activation, accumulator, and tile-metadata pipelines; waits for initialization and TMEM allocation before role loops. Do not say the decoder bypasses its own required initialization. |
| Scheduler need not wait on preceding activation grid | 1227–1236 | Reads routed tile information independently. Routing metadata must already be ready; “no data dependencies” should be scoped to activation values. |
| Only activation TMA role waits | 1411–1438 | `griddepcontrol_wait()` is inside the activation-warp branch. Before loading B it waits for preceding-grid completion. In unfused FC2, the early dependent-launch hint follows that wait. |
| Weight loads do not wait for activation readiness | 1484–1505; 1533–1566 | No grid wait in weight warp; static E2M1 and scale TMA loads start independently. FC1 (`fuse_activation`) issues `griddepcontrol_launch_dependents()` before the load loop. |
| Transform does not wait for activations | 1587–1675; 525–563 | Transform roles get routed work and decode only packed weight plus block scales. |
| Finite run-ahead buffers remain | 503–522; 568–586 | Wait for raw-weight TMA; acquire an empty decoded TMEM stage; commit/advance the stage. The transform cannot expand an unbounded amount of future work. |
| Compute joins the two operand paths | 1722–1774 | MMA waits separately for transformed weights and activation TMA, consumes both, then releases their stages. |
| Ordinary split call chain | `moe_w4a16.py` 440–511 | Permute → FC1 with fused activation → FC2 → standalone finalizer when unfused. |
| Finalizer can preload metadata but not incomplete expert output | `moe_finalize.py` 114–141; 170–174 | Routing-map/scales loads precede the dependency wait; all expert-output vector loads follow it. The function documents the metadata-readiness contract. |

The routing-readiness guarantee can also be traced to native `csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu`: `moePermuteKernel` waits for routing at lines 78–80 before its metadata reads and only signals its dependent FC1 at lines 100–102. Those pinned raw files, plus the Python wrapper and JIT source selector, were added to the evidence snapshot during this audit without changing repository/GitHub state.

W4A4 counterpart, `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py`:

- 2950–3059: FP32 scaling, optional clamps, and SwiGLU produce `tCompute`.
- 3062–3135: block max and output scale are derived from that new `tCompute` result.
- 3148–3219: stores/uses rounded output scale and quantizes output before storing.
- 1579: current W4A4 implementation's grid dependency wait occurs before specialized role execution; 3291 emits the dependent-launch hint at the kernel tail. The prose need not enumerate this additional implementation contrast; the output-data dependency is the durable argument.

## PDL interpretation boundaries

- PDL is an early-launch opportunity, not a promise that two grids execute simultaneously or that all preparation is hidden. Resource availability still controls overlap.
- An early launch hint does not publish incomplete activation/output data. The dependent activation loader/finalizer waits before reading those values.
- “Other kernel initialization” is safe: FC1 decode/compute can overlap a successor's pipeline/barrier setup when PDL launches it early. “Decode starts before its own pipeline/barriers initialize” is false for this source.
- The optional fused-finalize path has a different dependent-launch location and is not needed in the article; the task excludes unused in-kernel FC2 reduction discussion.
- #5319's local split results use PDL; #5019's distributed MegaMoE results disable it. Do not attribute the latter speedup to inter-kernel PDL, and do not claim the measured split speedup isolates PDL.

## Independent corroboration in archived PR material

`evidence/flashinfer-pr5319.md:13` describes the FC2 hint after the input dependency wait and finalizer metadata preparation before output reads. Lines 34–36 identify the historical source-overlay experiment and PDL-enabled local timing; these are supporting design/methodology records, not fresh measurements.

## Review of the edited article

Reviewed the actual **Give weight decoding a head start** subsection after the parent edit. The claims match the source, including the routed-work precondition, activation-only wait, PDL resource condition, finite staging, and the distinction between overlapping kernel lifetimes and observed inner roles. The finalizer paragraph is confirmed by the newly fetched source.

One citation improvement: move the article's “Early launch signal” link from `#L1477` to `#L1503`, where the `self.enable_pdl and self.fuse_activation` condition and actual `griddepcontrol_launch_dependents()` call appear. This is an anchor refinement, not a prose correctness issue.
