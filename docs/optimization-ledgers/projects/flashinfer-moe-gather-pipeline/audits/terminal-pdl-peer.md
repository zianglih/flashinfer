# Independent terminal-PDL source review

**Pass for bounded qualification; no numerical or performance claim.**
The candidate is exactly one three-line terminal wait deletion from02de. Every
other source byte in the kernel is unchanged. No new scheduling edge, producer,
publication, scratch owner, state, pipeline stage, or public option is added.

- FC1 public launches set prefetch false, so this block was absent there. PDL-off
  specializations likewise compile out both the original and removed block.
- For FC2, activation warp1 and epilogue warps4–7 retain their direct dependency
  waits before payload reads. MMA waits for the A/SFA/B/SFB transaction barrier
  before consuming operands. Its removed wait occurred only after all submissions.
- Weight warp0 retains its unconditional post-loop dependency wait, release fence
  where required, dependent launch signal, and pipeline tail. Consequently empty
  work also reaches prerequisite completion before signaling or final CTA teardown.
- Scheduler/MMA routing reads are intentionally earlier than parent completion.
  Their existing readiness comes from the ancestor release before the early launch
  signal. The removed exit wait cannot have made these earlier loads safe. Custom
  standalone FC2 callers must still meet the original ready-routing/weight contract.
- Per-token FC1→quantizer→FC2 remains covered: the shared quantizer retains its
  dependency wait and CTA0 ancestor-publication fence before the grid startup signal.
- Static scheduling and CLC retain every metadata arrival/acquire/release, sentinel,
  cancellation drain and final CTA join. No loop or conditional around a direct
  dependency wait changed. In2CTA mode each physical CTA has its own unchanged
  payload waits and final join, including the inactive follower MMA warp.
- The final all-thread barrier remains after all roles. Weight warp0 frees TMEM only
  after this join and after its own retained dependency wait. Other roles perform
  no new global payload read after the join; a CTA memory barrier is not being used
  as a substitute for an unperformed asynchronous/TMEM completion operation.
- This does not touch MegaMoE's terminal counter-reset boundary. W4A16's existing
  role-local activation wait is corroboration, not the proof of swap-AB correctness.

The PTX contract describes a per-executing-thread wait and requires dependent-grid
use before consuming prerequisite results; it does not require every independent
role to repeat it at kernel exit. Release-before-launch publication and operand
barrier completion remain the actual visibility edges. Source:
[PTX griddepcontrol](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-griddepcontrol).
Current9.4 wording was checked; the qualifier separately checked archived13.2/PTX9.2.

Required runtime boundary: existing exact/codegen pairs, graph active/empty/partial
work, static/CLC,1/2CTA andPDLoff. Inspect actual resource deltas and retained waits;
no performance execution is authorized by this source review itself.
