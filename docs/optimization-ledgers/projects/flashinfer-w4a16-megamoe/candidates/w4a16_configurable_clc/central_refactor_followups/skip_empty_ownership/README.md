# Skip empty CLC ownership broadcasts

Held source trial, separate from the launch-budget and task-or-terminal changes.
Only `claim_and_publish_bundle` changes. Move its existing bundle bounds check
outside the elected-lane claim so an invalid bundle leaves both returned pipeline
states unchanged and performs no ownership broadcast. Valid bundles keep the
same atomic claim, broadcast, task publication and ordering. No new scheduler
state, buffer, stage or public tactic is added.

The bounds condition is uniform across participating owner warps. Initial IDs
use `blockIdx.x // cluster_x + blockIdx.z`, identical for both CTAs of the
supported C2 cluster. Fallback scan IDs already pass through the cluster
broadcast. The captured CLC query uses
`clusterlaunchcontrol.try_cancel...multicast::cluster::all.b128`; each CTA waits
for its local full barrier before decoding the same response, fences that read,
and releases CTA 0's empty barrier. The saved installed DSL implementation is
`candidates/cuda132_recovery_0909e/dsl_pipeline_source/cutlass/pipeline/sm100.py`,
class `PipelineClcFetchAsync`, lines 796–1005. Captured PTX is under
`profiles/cu132-recovery0909e-central-clc-{small-c1,n64,n128}-001/codegen/dsl/`.

Once cancellation and the scan are exhausted, the existing loop repeatedly
passes `bundle == -1` while waiting for ready FC2 work. These calls now skip the
otherwise empty ownership round trip. The task, termination and fallback-ID
broadcasts are unchanged. Each participating CTA advances or preserves `ds`
identically; `claim_state` advances only for owned work as before. A failed
atomic claim on a valid bundle still broadcasts zero, because its result is
known only to the elected lane. The remaining consumer read/release fences,
producer tails, local epilogue drain and fixed finish launch are unchanged.

Base `clc.py`: `b2b7d6c310e525d35571e0304c0938f9b672bd4e09c8ad506d155c44091fc2a8`.
Proposed: `0dc79a78438aba1e816bbc0fa5d8781fba1ca3374cac4338622b30868de06c54`.
Patch: `eceefc318d7d2d1cc03b495799d6528dfc0a318ea7f2df2d1a8832bd70031484`.
Syntax, repository Ruff lint/format, patch applicability and equality of every
other module AST pass. Primary source has not been changed for this proposal.
Native lowering, loop-state resources, numerical progress and full AUTO timing
remain untested. Port the patch to the primary checkout before any GPU trial;
retain it only after a separate before/after comparison.
