# Full wide B1 screening

PASS: three independently verified finished B1 scopes. This is screening-only, not a final ABBA retention decision.

Native H7168 EP4 decode geometric mean over global T4,8,16,32,64,128,256,512; T1/T2 and every prefill shape reported separately. EP8 is a separate guard; uniform H6144 is separate and never pooled into native decode.

| Scope | Decode GM T4–512 | T1 | T2 | T128 | T4096 | T8192 | T16384 |
|---|---:|---:|---:|---:|---:|---:|---:|
| native-ep4 | 1.003794× | 0.866899× | 1.088617× | 1.006498× | 0.989584× | 0.981015× | 0.989438× |
| native-ep8 | 1.001312× | 0.977105× | 0.956667× | 0.982935× | 0.999555× | 1.013417× | 1.014146× |
| uniform-ep4 | — | — | — | 0.977410× | 0.986170× | 1.000111× | 0.989800× |

All 172 candidate winner exports have STACK0, LOCAL0 and no native LDL/STL or PTX local loads/stores. The same reducer structural signature confirms16→8 route loads and2→1 output stores per16 BF16 output elements. This is winner-only coverage.

## native-ep4 raw screening rows

AUTO tactic changes: global tokens [2, 4, 8, 64, 256, 16384]. Only A1/B1 exists, so temporal repeat drift cannot be measured yet.

| Global T | A1 µs | B1 µs | A1/B1 | B1 latency change | Same tactic |
|---:|---:|---:|---:|---:|---|
| 1 | 68.257000 | 78.737000 | 0.866899 | +15.354% | True |
| 2 | 105.745000 | 97.137000 | 1.088617 | -8.140% | False |
| 4 | 116.033000 | 113.200500 | 1.025022 | -2.441% | False |
| 8 | 160.256500 | 159.969000 | 1.001797 | -0.179% | False |
| 16 | 201.442000 | 198.946000 | 1.012546 | -1.239% | True |
| 32 | 263.649500 | 268.866000 | 0.980598 | +1.979% | True |
| 64 | 296.115000 | 297.315000 | 0.995964 | +0.405% | False |
| 128 | 324.674500 | 322.578500 | 1.006498 | -0.646% | True |
| 256 | 333.538500 | 334.483000 | 0.997176 | +0.283% | False |
| 512 | 347.330500 | 343.426500 | 1.011368 | -1.124% | True |
| 4096 | 798.119500 | 806.520000 | 0.989584 | +1.053% | True |
| 8192 | 1459.386500 | 1487.629000 | 0.981015 | +1.935% | True |
| 16384 | 2852.805000 | 2883.258500 | 0.989438 | +1.067% | False |
## native-ep8 raw screening rows

AUTO tactic changes: global tokens [2, 4, 8, 16, 128, 8192]. Only A1/B1 exists, so temporal repeat drift cannot be measured yet.

| Global T | A1 µs | B1 µs | A1/B1 | B1 latency change | Same tactic |
|---:|---:|---:|---:|---:|---|
| 1 | 67.600500 | 69.184500 | 0.977105 | +2.343% | True |
| 2 | 89.744000 | 93.809000 | 0.956667 | +4.530% | False |
| 4 | 102.097000 | 106.817000 | 0.955812 | +4.623% | False |
| 8 | 131.168000 | 126.481500 | 1.037053 | -3.573% | False |
| 16 | 139.488500 | 145.761000 | 0.956967 | +4.497% | False |
| 32 | 172.641000 | 168.578000 | 1.024102 | -2.353% | True |
| 64 | 196.527500 | 192.834000 | 1.019154 | -1.879% | True |
| 128 | 192.641500 | 195.986000 | 0.982935 | +1.736% | False |
| 256 | 200.720000 | 194.561000 | 1.031656 | -3.068% | True |
| 512 | 208.448500 | 207.088000 | 1.006570 | -0.653% | True |
| 4096 | 462.356000 | 462.562000 | 0.999555 | +0.045% | True |
| 8192 | 796.485000 | 785.940000 | 1.013417 | -1.324% | False |
| 16384 | 1518.747500 | 1497.562500 | 1.014146 | -1.395% | True |
## uniform-ep4 raw screening rows

AUTO tactic changes: global tokens [128, 16384]. Only A1/B1 exists, so temporal repeat drift cannot be measured yet.

| Global T | A1 µs | B1 µs | A1/B1 | B1 latency change | Same tactic |
|---:|---:|---:|---:|---:|---|
| 128 | 287.299000 | 293.939000 | 0.977410 | +2.311% | False |
| 4096 | 597.925000 | 606.310000 | 0.986170 | +1.402% | True |
| 8192 | 1154.298000 | 1154.170000 | 1.000111 | -0.011% | True |
| 16384 | 2349.524000 | 2373.736500 | 0.989800 | +1.031% | False |

Single ordered A1/B1 pair only; B2/A2 temporal replication is absent. No positive retention conclusion is justified.
The all256-variant hard gate remains open:172 selected winners are not1376 actual full-matrix catalog exports.
AUTO changes are part of the native end-to-end comparison, but unmatched tactics prevent attributing each difference solely to generated code.
No source, test, benchmark worker or active campaign was edited; no GPU workload was launched by this screening audit.
