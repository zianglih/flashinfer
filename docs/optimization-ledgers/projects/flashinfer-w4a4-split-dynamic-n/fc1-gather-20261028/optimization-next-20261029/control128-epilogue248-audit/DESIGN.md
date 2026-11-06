# Bounded register-budget lead:128/128/248

Recommend one paired compile-only probe after the full refresh, with no production edit or performance claim from this audit. The proposed control128/gather128/epilogue248 split retains the exact64,512-register CTA pool (`128*(128+128+248)`),384 threads and REG168 initial pool. Both target quotas are multiples of8, donors remain below168 and the epilogue remains above it. No additional role, tactic, synchronization or shape rule is needed.

## Existing evidence

The search of current and earlier project ledgers found the retained112→120 control adjustment, and the rejected uniform128 four-WG/two-epilogue feasibility diagnostic. It did not find this8-register control/epilogue trade. The prior120 adjustment removed genuine native local-stack accesses (STACK8→0), independently of unchanged UR/GPR spill-move sites; its broad screen was near neutral. The uniform128 design failed at MXFP8 N256ReLU2 with new epilogue local traffic, which is not a comparable248-register epilogue limit.

Current source is retainedce4 kernel77a5495c. `role-register-analysis.json` traces all41 FC1 CUBINs from the final80-capture exact gate, with direct branch/call traversal and implicit TMEM/global/shared/local vector register spans. Epilogue reachable registers top atR115 in this matrix; no epilogue unresolved indirect flow or local-memory sites occur. This is an assigned-register span, not a peak-live demand measurement or proof that recompilation at248 is spill-free. The older broader13-case native audit included MXFP8 N256ReLU2 reachingR161; the current41-case matrix should not be presented as replacing that missing geometry.

M512/N128/K8 MX captures48/50 retain160-byte stacks. All20STL.64+20LDL.64 sites are in the control/MMA region after `USETMAXREG.DEALLOC 0x78`; epilogue/gather have none. Control reachesR117 under the120 quota. The local stores hold64-bit descriptor pairs built from uniform/shared-memory descriptor values; later LDL pairs feed R2UR and UTCCP/UTCQMMA descriptor operands. Current capture48 has42 R2UR.FILL/UR2R.SPILL move sites in the same reachable region, distinct from the40 actual local-memory sites.

Thus the root pressure is long-lived uniform descriptor state, but there is a real second-level GPR/local-spill consequence under the control quota. Giving8 more GPRs may keep some pairs resident without fixing uniform-register capacity or the descriptor lifetime itself. It cannot be claimed to remove the entire160-byte stack or all uniform moves in advance. Two CLC control paths contain indirect BRX in the existing CFG report; the spilling48/50 paths and all epilogue traversals have no unknown flow.

## Small next step

Compile currentce4 control and the two-constant128/248 candidate only. Include the twoM512/K8 MX cases, native wideMX/FP4, per-tokenSiTU, MXFP8 N256ReLU2, K96 partialK, narrowN16 one-/two-CTA and CLC. Guard actual REG/pool/thread count and explicit128/128/248 role limits, verify FC2 identity, and require no new local sites anywhere. Inspect whether LDL/STL actually decline separately from UR moves; reject if there is no useful instruction/resource change or if new common-state/epilogue spills appear. Only a qualified result justifies existing exact gates and bounded native-tactic CAAC. Do not add a quota autotune axis or model/recipe exception.

Sources: current `gather-sf-arrivals-composed/evidence/exact/candidate/capture/{048,050}-fc1.*`; `control120-native/screen/RESULTS.md`; `two-epilogue-wg-audit-b139/compile-feasibility/RESULTS.md`; `native-tmem-fc1-audit/retained-epi-register-indices.json`. No source modifications, new compilation, kernel launches or timings were performed.
