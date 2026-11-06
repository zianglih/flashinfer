# Direct one-CTA gather completion: compile gate

Source `c5373aa1` on b52. All26 predeclared captures passed the unchanged matched-resource gate. This was compile-only: zero owned MoE launches; input/setup kernels may run.

- Eight changed one-CTA FC1 instances remove24–46 non-NOP instructions and6–14 branch/control sites. The number of CTA/proxy fence sites does not change: their execution moves onto MMA after direct local completion.
- All six two-CTA FC1 and all12 FC2 PTX/CUBIN pairs are byte-identical. No unintended two-CTA instruction change.
- REG, STACK, LOCAL and local-site counts never increase. The captured inherited M512/K8 MX stress is unchanged128B/16LDL/16STL. It is not labeled spill-free.
- All shared allocations, stage counts, role quotas and geometry are identical. CLC participants reflect actual consuming warps, as proven by the CPU source audit.
- Archive `9e3c61d17dfac5342a13f3930b280074be00025c286f14cc61eeb06a240786d2`,168 verified files; full pairs and role-level counts in `codegen-analysis.json`.

Next: candidate-only41 existing exact cases, matched against immutable b52 control captures; no performance yet. Reducing instructions does not establish lower end-to-end latency.
