# W4A16 static gather task bounds

Active source flashinfer-w4a16-tma-staticbounds-review is based on retained475cae6b. Only experiment changes remain unstaged. The modulo candidate was rejected:20 complete cells (16EP+4V3TP), EP prefill−1.03%, decode−0.02%, more SASS/R2UR; remaining TP work stopped.

Preserve original warp IDs and use compile-time full-group proofs to omit row/K task bounds only when every warp has a valid task. Dynamic predicates remain for a genuine partial group. No model/dtype/tile-specific policy. Codegen-first; no retention claim.

Do not hoist register redistribution above the common PDL wait: current non-reconverging role scopes release other roles' live values before donating. A separate pre-wait role split would reconverge with common live ranges, add branches and potentially spills; the observed startup wait is only~5ns. No donation policy change is warranted.

Rejected from codegen: all four full models add64–65 instructions and significantly moreR2UR despite fewer branches. No runtime test/perf campaign was launched. Local source copy removed after measured kernel-hash verification; canonical475 remains the sole retained source.
