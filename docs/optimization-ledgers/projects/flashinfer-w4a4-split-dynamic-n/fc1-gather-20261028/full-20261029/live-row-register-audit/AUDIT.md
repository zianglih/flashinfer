# Dynamic live-row issue and register-pressure audit

Four exact sources at N3U EP8,4096 tokens: clean fb66, control112, live rows,
and live rows+control112. All fresh CUBIN/ELF register guards pass. Diagnostic
timing is excluded from retention evidence.

| FC1 W4A4 arm | Stack | LDL/STL sites | Static instructions | Branches | Uniform fills |
|---|---:|---:|---:|---:|---:|
| fb66 |16B|62/9|7528|166|19|
| live |16B|62/9|7760|182|39|
|112|0|0/0|7448|166|19|
| live+112|0|0/0|7632|182|39|

This winner uses route tile256, one CTA, K256. The live predicate adds sixteen
branch sites and twenty uniform fills; it does not increase spills. Increasing
control registers removes the existing spills, but leaves the new branch
structure intact. Per-token (route128, twoCTA) adds eight branch sites with
unchanged28LDL/8STL;112 removes those spills without removing the extra branches.

Next possible emission experiment: retain dynamic transaction bytes but put
the live-row predicate directly on each Gather4 PTX instruction inside its
existing elected issuer, rather than wrapping the issue/election in a dynamic
branch. Verify actual generated predication and uniformity; no guarantee ptxas
will avoid branches. Keep every stage, count, barrier, release/acquire and
scheduler policy unchanged.

Evidence: `comparison.json`, full binary artifacts under `codegen-evidence/`.
Unstaged composed source: `flashinfer-fc1-gather-live-register-review`.
