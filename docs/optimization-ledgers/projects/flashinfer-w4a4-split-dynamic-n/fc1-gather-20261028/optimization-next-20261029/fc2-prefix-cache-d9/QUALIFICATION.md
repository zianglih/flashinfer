# Prefix snapshot qualification ledger

Base d9dee2da; retained9037 differs only in the W4A16 kernel, so the swap execution path is unchanged. This is independent of the rejected wider cyclic-store candidate.

| Revision | Kernel SHA | Exact cases before stop | Failing FC2 registers / stack | Static non-NOP / branches | Result |
|---|---|---:|---:|---:|---|
| d9 control | 5037dea841027df0e3fccb4b214b2ea763408e5fd9c1233868c0356508e5cb0b | 39 passed | 128 / 0 | 2717 / 78 | Qualified control, reused |
| R0 half snapshot + copied output fragment | 6cb2d3cd12452cdac57c8d409b5dcbcb6f509edc318000951549bd41f782db8f | 16 passed | 255 / 56 | 3987 / 99 | Stopped before launching failing kernel |
| R1 explicit word snapshot + direct cached/fresh views | 465aa754f4bdd485aaa1bd61f6c254ed33417d6fd5c3c5e856b46df1b743ae7e | 16 passed | 255 / 8 | 4336 / 123 | Stopped before launching failing kernel |
| R2 streamed uncached partial stores | 53aa2c089e24848c3365111e6772d6b59dcf8bbe85d3285e0939c42da1734a73 | 17 passed | 200 / 0 | 3823 / 115 | Staged middle-slab membership compile error |
| R3 explicit static cache-membership guard | 7d6955fc1e4a6bf11569f9db5321890231cce068a5ea9d2ecf8c89741368e56a | 39 passed | 200 / 0 | 3823 / 115 | Qualified;12-cell performance screen completed |

The failing case is per-token NVFP4, M256/N256, K8, two CTA, ordinary scheduler, 480 rows with a224-row tail. FC2's newly enabled protected interval is128 columns with64-token slabs and two output shared stages. The failing resource check occurs inside the compile observer before returning the callable; no execution of that configuration occurred. This is not a numerical failure. Both stopped revisions passed the preceding16 zero-tolerance cases.

R0 emitted26 LDL/13 STL sites; R1 emitted4 LDL/8 STL sites. These are static instruction counts, not dynamic issue counts. Four no-overlap FC2 cases gained31–70 registers in R0/R1, so broader timing was deliberately deferred. R2 restores the existing `_run_token_group` streaming path for uncached tails, while cached protected tails keep their required snapshot lifetime. No shape-specific branch, tactic, scale policy, PDL wait, or barrier changed between these lifetime refinements.

Raw R0 evidence is under `evidence`, R1 under `r1/evidence`. Each archive has a SHA-bound manifest. Full514-file source hashes and exact dirty patches are in each revision's `local-source.json` and remote `config.json`; precommit passed for every frozen revision. The original control39-case/76-CUBIN gate is reused without rerunning it. No sanitizer was run. After R3 passed all39 exact cases and76 executable resource guards, a separate12-cell CAAC screen ran under `../fc2-prefix-cache-screen`; its result is mixed and does not justify retaining the larger snapshot implementation. No full matrix was launched.
