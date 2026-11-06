# FC2-only producer dependency wait (held)

Frozen source: `flashinfer-pdl-fc2-producer-wait-review`, base `8b74eb6fa77651bb20dacb56b8e13872f3ad9885`, unstaged patch `d631e9c0519d09bb07ba6b08fdcd62a390f17497cdbb0f2e8db4205bbed19ead`. Two changed files,17insertions/1deletion. FC1, prepare, benchmark and retained cache tiers are unchanged; `scope-proof.json` binds81of83 identical source files. No production integration.

The private compile-time `wait_for_activation_in_producers` knob defaultsFalse and is cache-keyed. FC2 selectsTrue exactly when its existing startup-prefetch flag isTrue (published routing, unfused, static oneCTA). It permits MMA/epilogue roles to initialize/read published metadata while the128 activation/SFB producer lanes still wait. Payload consumers remain protected by existing operand/accumulator rings; no ring, stage count, scheduler or launch geometry change.

`gate.json` records162 full-chain output-exact graph replays: three formats, K384/K2304, N16/N128, twoCTA fallback, changingroutes/data, and forcedSM2 persistent work. All54 nonlocal-routing output replays are zero. A metadata observer bug in this original receipt bound the final captured graph's count pointer, making some Off/On `live_route_tiles` fields stale; those fields must not be used as evidence. The source did not change. The bounded correction in `../pdl-fc2-producer-wait-r2-empty` records18 replays with per-graph metadata pointers and confirms6 actual empty-route counts.

Named NV On/Off codegen: four startup variants preserve exact operand-stage counts, SMEM and register/local/stack resources. The emitted wait is guarded by `tid<=127`; A/SFA preload remains before it, B/SFB payload transfers remain after it. `codegen-review.json` and `codegen-audit.log` record the reproducible audit. Additional clean8b74/default-False captures confirm four PTX files byte-identical, including inactive FC1 and twoCTA FC2. Three cubins are identical; inactive FC1 N128 differs by uniform-register assignments despite identical PTX/resources. The fixed N16 timing path has identical inactive FC1 cubin.

Fresh paired whole-chain C-A-A-C screening uses both V3/EP8 and V41/EP4 on B300 GPUs1/0, actual routes, fixedN16/M128, tokens4/32/128/512, native10warmup/100cold-L2 graph samples. Results are under `../pdl-fc2-producer-wait-r1-fixed`. Clean control8b74 is independently cloned; no prior24c timing is reused because the retained cache tiers changed. Final decision pending the paired screen; broad tests/sanitizers deferred.

## Decision

Parent accepted hold after the paired screen. Geometric means NV/MXFP8/mixed: V3 `1.000149/1.000753/1.000886x`; V41 `1.001265/1.000028/0.999828x`. Only11of24 points improve in both repeats. V3 NV T512 loses0.52%, V41 mixed T32 loses0.33%, and V41 MXFP8 T4 loses0.14%, all in both repeats. This is not enough to justify the new runtime behavior; no native AUTO campaign or production integration. All frozen source/evidence remains preserved.
