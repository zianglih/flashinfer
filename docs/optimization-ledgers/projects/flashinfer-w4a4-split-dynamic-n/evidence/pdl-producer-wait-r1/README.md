# Producer-only dependency wait with FC1 startup prefetch (not retained)

Frozen independent source: `flashinfer-pdl-producer-wait-review`, base24c, patch `8c0186207be4bf505d2f8a6a7f323798b7b09ece341c7b1c5b2aa2b456f08874`. The source and every prior experiment remain unstaged and unchanged.

This experiment allows non-activation roles to pass the initial PDL wait only under the explicit published-routing/preload contract. All128 activation/SFB producer lanes still wait; consumer payload accesses are protected by the existing operand/accumulator rings. The metadata scheduler, role assignments, stage counts, cache hints, and teardown rendezvous are unchanged.

Validation: `gate-r2.json` records270 byte-exact changing-data graph replays, three formats, short/long K, zero-local routes, actual CLC, one/two-CTA variants and twoCTA FC2 fallback. The publication-False FC1/wide-FC2 case is explicit: FC1 consumer roles may proceed, while FC2 retains its unconditional wait. `codegen-review.json` binds14 named On/Off resource pairs, unchanged registers/stack/local memory, and8 FC1 Off artifacts byte-identical to the FC1-only control. The initial observer KeyError occurred before candidate execution; its failed receipt is preserved and r2 only fixes observer default handling.

Fixed screening used actual routes and fixed N16/M128 on both B300 V3 and V41, tokens4/32/128/512, native10warmup/100cold-L2 graph samples. Exact order is C1(reused from the immediately preceding FC1-only C2),F1,A1,A2,F2,C2. C is retained24c-equivalent FC2 preload, F adds FC1 preload, A adds producer-only waits. Full source/cache/route/tactic bindings and actual chronology are in `../pdl-producer-wait-r1-fixed/summary.json` and raw receipts; this is not native AUTO retention evidence.

C/A geometric means (NV/MXFP8/mixed): V3 `0.998696/1.006356/1.001813x`; V41 `1.002319/1.004784/0.998657x`. V41 mixed T32/T128/T512 remains `0.994614/0.993988/0.992748x`, negative in both repeats. Small incremental F/A gains do not recover the FC1 losses. Parent decision: hold both FC1 variants and isolate FC2-only producer wait atop retained8b74 next. No production integration.
