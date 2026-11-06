# FC2 producer-drain PDL result

Fresh actual source core fe188d18 preserves prepare/FC1 early all-thread signaling from adcc, moves FC2 signal into existing warp-zero loop exit before A drain, and uses independent cloned A/AB drain state. No cache hints are changed. The common A-before-AB drain reordering also affects FC1 source; both phase codegens were checked.

All 36 timed arms / 3,600 samples passed phase/full output exact checks. T1 native exact plus a true zero-route FC2 canary dispatch passed before timing; wide native exact also passed. GPU2 released. All samples retained; no first-arm filtering.

| Tokens | Phase | aab control medians (µs) | Candidate medians (µs) | Control/candidate |
|---:|---|---|---|---:|
| 4 | full_chain | 49.8240, 49.8080, 49.7445 | 47.1045, 47.2000, 47.3280 | 1.054678× |
| 4 | fc1 | 28.8325, 29.3120, 29.3285 | 28.2885, 28.3840, 28.1920 | 1.030709× |
| 4 | fc2 | 16.1600, 16.1915, 16.2080 | 16.1920, 16.2080, 16.1920 | 0.999331× |
| 16384 | full_chain | 484.0015, 485.1850, 484.4650 | 491.7770, 485.3280, 484.3530 | 0.994681× |
| 16384 | fc1 | 221.4085, 233.6160, 225.9045 | 221.5045, 228.9605, 228.4000 | 1.002907× |
| 16384 | fc2 | 133.5050, 133.5040, 133.4080 | 133.2480, 133.1680, 133.2010 | 1.002002× |

Decode improves5.47%; prefill aggregate is0.535%slower. The latter two prefill pairs are nearparity but the slower firstpair remains in the result. No stable prefillgain or broad retention claim.

Resources for aab/adcc/new are identical: FC1 N16/N25664/80registers, FC2N16/N25694/120; unchanged SMEM/288threads/1CTA residency and no local allocation. Candidate FC2PTX waits at145/141 then releases/signals at559/561 and862/864 respectively. All final joins/drains remain.

| Compile-only object | Static sites excluding final NOP padding |
|---|---:|
| allthread-fc1-n16 | 1141 |
| allthread-fc1-n256 | 5374 |
| control-fc1-n16 | 1141 |
| control-fc1-n256 | 5374 |
| publisher-fc1-n16 | 1167 |
| publisher-fc1-n256 | 5374 |
| allthread-fc2-n16 | 1319 |
| allthread-fc2-n256 | 2453 |
| control-fc2-n16 | 1311 |
| control-fc2-n256 | 2445 |
| publisher-fc2-n16 | 1320 |
| publisher-fc2-n256 | 2453 |

Static instruction sites are not dynamic execution counts; mixed-case instructions are counted. These artifacts are regenerated compile-only source/geometry checks, not timing-process cubin identity. Full paths/hashes and ordering are in codegen-verification.json.

Sourcecopy remains unstaged, production unchanged. No upstream baseline, AUTO or TRTLLM rerun. Broader dtype/per-token/fused coverage and sanitizers are deferred pending useful performance. No timing or causal claim is made by comparing this result with nonadjacent adcc historicalmedians.

Commands: `scripts/pdl_producer_drain_experiment/run_codegen.sh`, `run_codegen_fc1.sh`, `run_pairs.sh`; exact nativezero helper is `probe_zero.py --exact-only`. All capture/oracle/timer functions in the measured helper match prior ASTs. Source/module/caches are pinned per arm. Raw SHA256`6869589e39563aa34a00dfcd888e2e2b8678d3d8a902f9a3cb539656e503d380`.
