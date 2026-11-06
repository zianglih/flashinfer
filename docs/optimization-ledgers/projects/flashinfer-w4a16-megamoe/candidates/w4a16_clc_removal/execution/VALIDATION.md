# CLC removal: completed validation

Source `eb036705ebe71f940bf567c94fdcb78020a5fdc21bdeb3e7ea361cc1d140a09d`, manifest `db4a5571b80679362414c68ed11154dfd316755c22ffc184f07c188b8e3325ad`, installed on `fi-w4a16-mega-0910a` / `hu-pdx-115`, same observed CUDA 13.2 stack and B300 hardware.

| Check | Result |
|---|---|
| Three retained host suites | 135 passed, 2 warnings, 4.14s |
| Actual default N64 compile | 5,504 instructions and both encoded words exact to central57e2 |
| Actual default N128 compile | 6,032 instructions and both encoded words exact to central57e2 |
| Native resources | Both REG96 / 640 threads / STACK0 / LOCAL0; launch and shared-memory fields exact |
| N64 EP2, both returns | 4 rank-tests /16 objects passed, 73.352s |
| N128 EP2, both returns | 4 rank-tests /16 objects passed, 75.922s |
| Actual numerical resources | All32 objects REG96 /640 threads /2 decode groups /LOCAL0 |
| Final source/native/idle | Exact eb036 /38a68fe8; no GPU apps or workers |

The original ordinary, H288/I448 tail, scale/routing, and graph reference helpers and numerical tolerances are unchanged. Per-job validators ran once; closure and this summary only read saved records. No full timing run or old control rerun was performed.

Final numerical closure: `logs/cu132-recovery0910a-clc-removal-default-numerical-001-idle.json`, SHA256 `d15d65756086f63b04ad28eae672416655134d438364e6fbab1f08549ca2e0eb`. Native and numerical summary JSONs are adjacent to this note. The task-terminal AUTO remains a preserved user-cancelled two-row partial result, not a benchmark baseline.

Next default optimization must compare against whole central57e2 default result `0c19b3eecd74b2d6e92c3d34d4474a6f1653d69930d94c47c188e748f8c9d567` / proof `d56db1c9303192c53d91a12e84e304ce206e3ea42981cc35ec25a69608b3438e`. Whole retained098c remains separate optional arithmetic context. CLC timings are excluded.
