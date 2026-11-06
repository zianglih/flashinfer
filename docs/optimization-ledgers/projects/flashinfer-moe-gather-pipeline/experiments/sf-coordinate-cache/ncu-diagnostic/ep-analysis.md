# Independent EP wait interpretation

The EP evidence supports the measured SF request reduction, with a new coordinate-load dependency. It does not show a new bank conflict or an unnecessary wait, and it does not change the rejected full 56-cell decision.

The [independent replay](ep-analysis.json) matches all 8,248 EP source PCs to the actual loaded control/candidate FC1 images, checks seven captures per arm, and maps 25 barrier probe/branch/fallback groups per image. The [common report](RESULTS.md) retains the aggregate metrics and the distinct TP interpretation. This note uses the same archived evidence without modifying it.

| Mapped wait group: long-scoreboard observations | Control | Candidate |
|---|---:|---:|
| Weight producer: operand empty | 946 | 972 |
| Gather producer: operand empty | 2,350 | 715 |
| Gather completion relay | 1,149 | 1,065 |
| MMA: weight full | 66 | 48 |
| MMA: gather full | 190 | 214 |
| MMA: accumulator empty | 193 | 165 |
| Epilogue: accumulator full | 419 | 564 |

The large change is gather-producer operand-empty observations, 2,350→715. MMA gather-full does not fall (190→214), and epilogue accumulator-full rises modestly (419→564). Weight-full remains small (66→48); accumulator-empty falls (193→165). Thus the EP improvement should not be described as eliminating the MMA gather wait. The producer's reuse-wait observation shrinks while the consumer-ready observations remain, with no evidence that their synchronization is redundant. Probe/branch/fallback observations are grouped by actual barrier address and role; they are not estimates of isolated wait latency.

The eight SF copy sites and their completion instructions lose all 121 observed MIO stalls, while the SF theoretical sector requests fall exactly fourfold, 28,286,080→7,071,520. Unique addresses and payload bytes remain unchanged; measured DRAM reads fall only about 1.68%. Eight elected `LDS.128` sites feed four coordinate `R2UR` consumers each before Gather4. These consumers account for 1,512 of the candidate's 2,656 short-scoreboard observations. Every elected coordinate load has N-way 1 and zero excessive wavefronts. The exposed dependency is supported by the native register chain; a bank-conflict cause is not.

The native/resource boundary is unchanged from the common replay: 168 registers, LOCAL0, four stages and the same launch geometry; dynamic shared memory grows 189,440→190,464 bytes. Static non-NOP grows 4,027→4,100. The source synchronization remains required even where it lowers without a dedicated native WARPSYNC.

This is a serialized application-replay FC1 diagnostic. The shorter EP diagnostic duration and the primary EP +4.748737% observation agree in direction, but are separate evidence. The primary TP −4.687648% observation and all other primary rows remain unchanged. PC counts are observations, not additive time fractions; changed duration and sample totals prevent treating their differences as a causal latency decomposition. No additional profiling or source change is indicated by this note.

- Independent JSON SHA256: `f62e1b1476eff5d6e19100e9bad1f5e8edcd43792535e6d6aae8438aff5c0193`.
- Common analysis SHA256: `1602b5a472c359f657dcaaf8182ec3ff10fa1867354c66d23759d601fb58c970`.
- Evidence archive SHA256: `7e760dd1b3e193e5adc2c4f26f189249f3ffe61487d3c1974b529e9b76a5fac1`.
