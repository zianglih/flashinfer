# Regular-TMA CLC and scheduler-depth experiments

Production baseline: `fca8462cbd9096059d0019a206aa760fb34ca8c4`, benchmark SHA `2c24363d52238fcb0dbe2b300fce0e3d5cf9162e725606544dc74a8117f1ea70`. Final retained source: `0c1e00fc3e4f913c8c241796c70a29673737c542`, one-CTA CLC depth1 with a host launch-grid capacity guard. All experimental copies remain unstaged and independent. Earlier sections preserve the sequence of experiments; the final decision and measured-to-retained source boundary are recorded at the end.

## Design

The existing compute, producer and epilogue warp IDs are retained; CLC appends one scheduler warp. One routed tile is published per cancellation. The metadata slot is acquired before requesting cancellation, preventing a stalled producer from reserving more work. The full scheduler warp consumes the CLC response. All other threads consume and release terminal metadata too. No new register reconfiguration, MMA tiler, operand stages, PDL boundaries, cache policy, weight layout, or math/epilogue change.

CLC response storage and metadata rings enter the shared-memory budget before automatic operand-depth fitting. The one- and two-slot policies both fit: 360 actual SharedStorage layouts, capacity 232448 bytes, maximum actual storage 230400 bytes, automatic operand depths3–7. Compared to the retained automatic stage policy there are zero operand-depth, epilogue-bulk or operand-byte changes; scheduler storage adds0 or128 bytes after alignment. The inherited audit stdout's `stage_changes` field still compares against the earlier fixed-stage design; use `evidence/clc-regular-tma-r2/layout-summary.json` for the CLC attribution.

Scheduling is a direct compile-time behavior argument selected by callers. FC1 requests CLC; FC2 requests the existing strided persistent traversal. The host enables CLC only when allocated work exceeds resident cluster capacity. R2 additionally preserves an explicit reduced SM budget by disabling CLC; a full CLC problem grid otherwise may occupy the entire device.

## History

See `scripts/pr7290_scope_cleanup/clc-w4a16-history-resource-audit.md` for exact W4A16 ledger locations and raw evidence. W4A16 retained one-slot CLC, one work tile/cancellation, full-warp response handling, acquire-before-cancel. Static metadata depth3 was separately retained; larger CLC metadata queues hoarded work. Prior W4A4 CLC attempts predated regular TMA/current PDL and cache contracts, and had small/inconsistent whole-chain gains despite some phase gains.

## Frozen sources and validation

- `flashinfer-clc-scheduler-review`: R1, patch `595eea40ee038fc61e24331748250703999cfbc7e127426ff817620d2a8f1ab0`. Passed360 layouts and45 exact persistent configurations. Preserved as historical prototype because its host policy did not preserve explicit SM reservations. No retention benchmark on R1.
- `flashinfer-clc-scheduler-reservation-review`: R2, patch `eb431be438ba9ffabf0f160d283d9bcdb7106d37f0f63ed65255f6e0457f8d03`. Scoped pre-commit passed. Passed360 layouts and57 exact persistent configurations on GPU5: NVFP4, MXFP8 E4M3, MXFP4×MXFP8; narrow/wide, one/twoCTA, padded routes, zero-live sentinels, metadata depths1/2 and explicit SM2 static fallback. Payload and scale-factor bytes are exactly equal between static/CLC1/CLC2 at tested points. Private cache observation asserts the effective host scheduling choice, so zero-route coverage cannot silently use static fallback. Raw receipt and output: `evidence/clc-regular-tma-r2/`.
- `flashinfer-clc-static-control-review`: exact R2 core with FC1 requesting static scheduling; patch `d32be72863bf6f3496632a072d4d7ea81ab5d7d4f69c9f649e54b7dde2c74d97`. Isolates for→while/next_work codegen changes from CLC. Independent shallow clone was used after full-history cloning encountered a missing historical Git object; HEAD/tree/source pins remain identical to the required baseline. Existing sources were not repaired or changed.

The R2 first deployment guard found two untracked compiler dumps in the baseline checkout. The failed receipt was preserved; source pins were unchanged. Deployment resumed into a fresh gate2 output after checking tracked cleanliness. The resource agent subsequently moved those generated outputs to the artifact directory and restored full baseline cleanliness.

## Initial evidence

Fresh native AUTO C1 and R2 A1 exist for both models. V41 MXFP8 T16384 changed FC1 M256/N128→M512/N128 and regressed; fixed C/A/A/C comparisons at both geometries are in progress before assigning this loss to CLC.

Host enablement audited against fresh C1 native winners: all78 affected cells enable CLC. Twelve cells have allocated capacity above one wave but live work at/below one wave; all twelve are tokens1/2, excluded from retention. Every T>=4 winner has live work above resident capacity. This is source/route geometry evidence, not a timing prediction or candidate AUTO winner audit. See `evidence/clc-regular-tma-r2/enablement-baseline-tactics.json`.

Static-disabled C/A/A/C actual-route control (V41 NVFP4, warmup10/iters100, no fused finalize, fixed tactics, source/route/cache receipts): N16 T8=1.00128×,T512=1.00097×; N128 T8192=.99945×,T16384=1.00517×. The T16384 baseline drifted across the pair; these show no demonstrated static-loop regression, not proof of exact performance identity. Raw: `evidence/clc-static-control-r1/raw/`.

Broad correctness, sanitizer, per-token NVFP4 and Rubin execution remain deferred. CLC gate results cover tested scheduling/math cases and static layout policies, not the full dtype/API cross-product. Full V3+V41 native paired retention still required.

## CLC depth2 and compiler resource attribution

`flashinfer-clc-scheduler-depth2-review` is frozen at HEADfca with unstaged patch `ee646b2c395a89a868e00311708495723fcb4b39089b7eda6a19c39ab4afa83c`; the only change versus R2 is the FC1 metadata-depth request1→2. Scoped pre-commit passed, and R2's exact/layout gate covered both depth values. Native both-model screening is sequenced after the R2 paired quartet.

The resource agent matched30 regenerated full-model kernel pairs (`evidence/clc-r2-resources-r1/comparison.json`). All have zero local memory/spills, one CTA/SM,74 active two-CTA clusters, unchanged input stages. V41 MXFP8 FC1 M256/N128 registers72→78; M512/N12884→84. Static FC2 codegen also changes despite CLC disabled: V41 MXFP8 M256/N128 registers110→104, static SASS instructions1128→1136. Therefore static-loop attribution is measured separately, not assumed identical from shared math.

V41 MXFP8 T16384 initial fixed C/A/A/C: M256=.99128×,M512=1.01831×. M512 baseline drift1.008→1.174ms makes the apparent gain inconclusive; repeat with before/after GPU clocks, power and temperature snapshots is in progress. No12.4% native regression was reproduced in the fixed pair, but this does not yet establish whether AUTO selection or timing variability dominates.

## Fixed-tactic attribution follow-up

A second V41 MXFP8 T16384 C/A/A/C remained variable: M256=.97412×,M512=1.05425×. Before/after process snapshots show1965MHz SM,3996MHz memory,35–36°C after each run; they do not sample the timing window and cannot exclude transient clock variation. Matching static-disabled controls gave M256=1.00813×,M512=1.03453× with nontrivial spread. These controls and repetitions do not justify assigning the original native12.4% loss specifically to CLC or M512. Large-shape repeats were stopped; all raw evidence is preserved under `evidence/clc-r2-fixed-v41-mx8*` and `evidence/clc-static-fixed-v41-mx8/`.

The next focused diagnostic compares depth1 versus depth2 directly at V3T16 with N16/M128 FC1/FC2 for NVFP4,MXFP8 andmixed. Route identity and cache tactics are asserted. Actual routes contain17 local rows across13 nonempty experts, yielding416 FC1 work clusters on148 SMs; allocated capacity is1216 clusters. All actual MMA widths round to16. This isolates the depth effect; early work reservation is a plausible mechanism, not a measured causal attribution without scheduling trace evidence.

Static metadata-queue depth1/3 work is owned by the resource agent in independent `flashinfer-static-tile-info{,-depth3}-review` copies. It preserves strided scheduling and removes CLC fetch/grid/storage. Do not mix its measurements with the CLC arms.

## Depth2 rejection evidence

Fixed V3T16 N16/M128 FC1/FC2, C=CLC depth1 and A=depth2, actual routes, C/A/A/C:

| Precision | C1 us | A1 us | A2 us | C2 us | Depth2 latency increase |
|---|---:|---:|---:|---:|---:|
| NVFP4 W4A4 |71.840|73.968|73.952|71.584|3.1348%|
| MXFP8 |114.6405|118.352|118.3205|114.720|3.1880%|
| MXFP4×MXFP8 |73.921|80.704|80.800|73.888|9.2653%|

The paired repetitions are tight and reproduce the native same-tactic decode regressions. Recommendation: reject the second CLC metadata slot; preserve depth1 while evaluating the independent static-queue alternative. This establishes a depth effect at the tested case. Early work reservation matches the historical explanation but has not been separately established by a scheduler trace. Source, cache, and route identities all verified. Raw receipts/outputs: `evidence/clc-depth-fixed-v3-t16/raw/`; derived JSON: `summary.json`. GPUs5/7 are idle after these tests.

## One-CTA-only CLC1 policy trial

`flashinfer-clc-single-cta-review` is frozen, unstaged, at HEADfca; patch `6b3f1c4f532addca0a44a59c6b0b64207bff7a8c88819834f101e891773a1775`. Only FC1 caller policy differs from R2: `use_clc_scheduler=cluster_shape_mn == (1, 1)`. The kernel bytes, metadata depth1, capacity gate and explicit SM-budget guard are unchanged. This uses no model/token/dtype threshold. AST extraction of the live tactic generators and caller expression verifies all13 tactics:7 request CLC for FC1;6 two-CTA choices request static scheduling. FC2 remains static for all13. Scoped pre-commit passed. No new kernel or test was added.

The two-CTA fallback is the R2 static `next_work` loop, not a byte-identical return to the original fca kernel. Its earlier static-control results remain the attribution boundary. Native both-model A1 against the latest fca C2 controls is pending; this policy is not a retention decision. Source receipt and complete truth table: `evidence/clc-single-cta-r1/`.

## Final retention and launch-bound review

Retain the one-CTA-only CLC1 policy after paired native A1/A2 and matching fca controls for both V3 and V4.1. Parent and independent table audit agree on whole-grid geometric-mean speedups of 1.004298× V3 and 1.011253× V4.1 (tokens 1/2 excluded). Decode NVFP4 gains are 1.004833×/1.012591×, mixed 1.010407×/1.019266×, MXFP8 1.003144×/1.000542× for V3/V4.1. Prefill is near neutral on V3 and improves on V4.1; because those two-CTA paths remain static, small prefill differences include static codegen and run variation rather than proving a CLC scheduling gain. Full raw arms remain in `evidence/pr7290-{v3,v41}-clc-single-cta-{a1,a2,control-c2}/` and the matched earlier fca control directories.

The read-only final review found a real launch boundary before commit: allocated route tiles were grid Y with no 65535 limit guard. V3 T131072/top-k8/localE32/N16 allocates 65566 route tiles, producing an invalid CLC launch. The independent `flashinfer-clc-single-cta-grid-review` copy adds `_CUDA_GRID_Y_MAX = 65_535` and selects existing static scheduling above that capacity. This is a hardware launch constraint, with no model/token threshold. The actual B200 driver query confirms Y=65535. The common kernel and all other 82 source files remain byte-identical to the measured one-CTA source.

Measured patch `6b3f1c4f532addca0a44a59c6b0b64207bff7a8c88819834f101e891773a1775` becomes guarded patch `a5e9283a7021e563c991d125a140379bb7049135705fcc0e7608c727f832fd86`, retained as clean commit `0c1e00fc3e4f913c8c241796c70a29673737c542` in production and review clones. All 83 pinned source files match that commit exactly. Measured/guarded host SHA256 are `d70aa04adb5316e6b23a032fee54494dc7911e6812f3c3ed0ee3285171a04a9f` / `47024e3042a824528c86e981c96197da542b3b497698901c5533028c39015e4b`. The common kernel remains `bc36c575f8ae044818d5365198c0b016828dc630886b874caffd4edb11737882`.

`scripts/clc_regular_tma_experiment/audit_grid_guard.py` verifies that the host AST changes only by the named limit constant and admission predicate. All 156 recorded A1/A2 model/dtype/token dispatches are identical (route capacities 6–1055). All 338 model/token/tactic combinations across the 13 tactics remain identical (maximum capacity 8222). Boundary 65535 stays CLC and 65536 selects static. Explicit SM reservations remain honored. This proves unchanged resolved dispatch/constructor/key inputs for the measured shapes, not unchanged source-fingerprinted disk caches. Evidence: `evidence/clc-single-cta-grid-r1/{guard-equivalence.json,guard-only.diff,source.json,precommit.log,read-only-review.md}`. Scoped precommit passed. The parent is running final 49 focused tests and the four final CLI tables on the clean retained head.

R2 general CLC, depth 2, and static metadata queue depths 1/3 remain local rejected/nonretained experiments. Depth2 has the clear fixed decode regression recorded above. Static queue alone did not provide consistent benefits; V4.1 MXFP8 T16384 fixed M256/N128 regressed to 0.9450× at depth 1 and 0.9648× at depth 3. Deeper static buffering improved that point relative to depth 1 but still lost to fca. No speculative cleanup was applied to the measured kernel: comment-only rationale can be added later, while helper extraction or restoring static for loops requires renewed codegen/performance evidence.

No remaining synchronization/layout blocker was identified in this review. Broad sanitizer/dtype/per-token execution remains deferred. The large-grid correction is supported by host and SDK proof without a giant allocation; final focused execution validates the retained ordinary paths. All experiment copies remain available for review and the source inventory separates final production HEAD from frozen fca-based CLC copies.
