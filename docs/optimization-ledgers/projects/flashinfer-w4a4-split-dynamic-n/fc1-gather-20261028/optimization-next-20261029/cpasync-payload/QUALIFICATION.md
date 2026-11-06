# cp.async payload qualification

Base `c0c0bc41c70100c694ac55585990971aba8b7fb9`; candidate kernel SHA256 `8baae0e09e8c6fc02900ae89404861026dcba50c14fa3fae48a31269d363703f`. One unstaged file, +90/−59. Scoped pre-commit checks and source-level transfer/invariance checks pass.

- **17 exact cases pass:** 7 existing cases, 8 M512 cases across four formats and CLC off/on, 2 local N16/two-CTA/K-steps4 cases with K64/192 and 17 tokens. Existing oracle and tolerance contracts are unchanged.
- **12 generated variants inspected:** 6 gathered FC1 and 6 FC2. All have zero local bytes and no LDL/STL sites. Gathered FC1 reserves 168 initial registers and has the intended 112/128/256 donor/receiver instructions in actual SASS.
- **Transport lowering:** `cp.async.ca.shared.global` with 16-byte payload operations lowers to `LDGSTS.E.LTC128B.128`; there are no Gather4 operations in the captured FC1 PTX/SASS. Predicate zero-fill and per-thread asynchronous barrier arrivals remain.
- **Runtime guards:** every compiled test observation passes; local bytes are zero. Both one-CTA and two-CTA gathers, route tiles 16/128 and M512 reuse are exercised. The smallest two-CTA case explicitly confirms route N16, tile K256 and two CTA in runtime guard records.
- **Boundary:** dump-enabled benchmark captures establish lowering/resources and successful execution only. Their timings are excluded from retention. The C-A-A-C screen is pending. No sanitizer run.
- **Harness failure:** the initial exact launcher inserted plugin arguments into a logging-helper call and stopped before running pytest. Only the helper was corrected; candidate source and successful codegen stayed unchanged. The failed receipt remains under `validation/smoke-harness-failure`.

Raw evidence: `qualification-evidence/`; archive SHA256 `d29bc37583923fab563ad880b6717dfade51fabff72293c3a48d8fe79de7d3c1` (139 files). `qualification-summary.json` records observation counts. No source commit or push.
