# Regular TMA versus saved HEAD and Gather4

Both controls are saved historical sweeps, without fresh bracketing drift control. Full candidate R1/R2 sweeps use geometric paired ratios; T1/T2 are excluded from aggregates. Two repeats do not establish statistical significance, and no historical control was rerun.

Both reference arms are reused unchanged. Identity checks require the same host, GPU UUID/model/power, runtime, routing, and native timing. Full tactic records and cumulative caches are compared separately in the JSON report.

| T | HEAD R1 µs | HEAD R2 µs | Gather4 R1 µs | Gather4 R2 µs | Candidate R1 µs | Candidate R2 µs | HEAD paired | Gather4 paired |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 33.664000 | 33.280000 | 29.504500 | 29.536500 | 30.752500 | 31.552000 | 1.074536× | 0.947698× |
| 2 | 39.616500 | 40.256000 | 36.000000 | 35.712000 | 36.880000 | 36.624000 | 1.086613× | 0.975618× |
| 4 | 54.400000 | 54.368000 | 51.296000 | 51.488500 | 51.296000 | 51.041000 | 1.062845× | 1.004374× |
| 8 | 68.673000 | 68.000500 | 66.704500 | 66.720500 | 66.288500 | 66.849000 | 1.026556× | 1.002168× |
| 16 | 76.961000 | 76.960500 | 72.449000 | 72.337000 | 75.505000 | 74.528000 | 1.025939× | 0.965048× |
| 32 | 109.201000 | 110.241000 | 105.793500 | 106.512500 | 108.336500 | 107.617000 | 1.016148× | 0.983110× |
| 64 | 143.713500 | 145.761000 | 139.409000 | 140.049500 | 141.633500 | 141.857000 | 1.021083× | 0.985775× |
| 128 | 146.593500 | 146.753000 | 143.649000 | 143.329000 | 145.201500 | 144.512500 | 1.012541× | 0.990558× |
| 256 | 154.753000 | 155.313000 | 152.096500 | 152.257000 | 152.897000 | 152.706000 | 1.014602× | 0.995911× |
| 512 | 159.713000 | 159.713500 | 161.217000 | 160.609000 | 156.641000 | 156.577500 | 1.019820× | 1.027479× |
| 4096 | 301.731000 | 300.482500 | 329.874500 | 329.346500 | 294.322000 | 294.242500 | 1.023188× | 1.120049× |
| 8192 | 603.412500 | 594.613000 | 656.677000 | 634.517000 | 612.597000 | 586.677500 | 0.999165× | 1.076739× |
| 16384 | 1235.834000 | 1202.218000 | 1215.546000 | 1205.370500 | 1190.666000 | 1207.322500 | 1.016635× | 1.009577× |

T1/T2 are reported but excluded from aggregates. Primary paired ratio is sqrt((R1 × R2)/(C1 × C2)).

| Group | Saved control | R1 | R2 | Paired |
| --- | --- | ---: | ---: | ---: |
| Overall | head | 1.020548× | 1.022607× | 1.021577× |
| Overall | gather4 | 1.013026× | 1.014426× | 1.013726× |
| Decode | head | 1.022339× | 1.027332× | 1.024833× |
| Decode | gather4 | 0.992299× | 0.996018× | 0.994157× |
| Prefill | head | 1.015786× | 1.010112× | 1.012945× |
| Prefill | gather4 | 1.070438× | 1.065196× | 1.067814× |

Raw compiler-stack fingerprints differ. The explicit reviewed receipt proves exact historical reconstruction using only three generated entrypoint shebangs and corresponding RECORD hash/size fields. No installed file or raw cache metadata is changed; all other metadata fields must match. This equivalence is specific to the recorded environments, not generic fingerprint normalization. Receipt SHA256: `20e561ef5b3e8f8fdde8fcfef981df986bd806c6e4054a2ab70499891fd00aa8`.
