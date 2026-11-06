# Regular TMA versus saved HEAD and Gather4

Both controls are saved historical sweeps, without fresh bracketing drift control. Full candidate R1/R2 sweeps use geometric paired ratios; T1/T2 are excluded from aggregates. Two repeats do not establish statistical significance, and no historical control was rerun.

Both reference arms are reused unchanged. Identity checks require the same host, GPU UUID/model/power, runtime, routing, and native timing. Full tactic records and cumulative caches are compared separately in the JSON report.

| T | HEAD R1 µs | HEAD R2 µs | Gather4 R1 µs | Gather4 R2 µs | Candidate R1 µs | Candidate R2 µs | HEAD paired | Gather4 paired |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 33.664000 | 33.280000 | 29.504500 | 29.536500 | 33.056000 | 32.160000 | 1.026577× | 0.905400× |
| 2 | 39.616500 | 40.256000 | 36.000000 | 35.712000 | 39.520000 | 38.560000 | 1.023002× | 0.918505× |
| 4 | 54.400000 | 54.368000 | 51.296000 | 51.488500 | 53.600000 | 53.648500 | 1.014168× | 0.958375× |
| 8 | 68.673000 | 68.000500 | 66.704500 | 66.720500 | 67.233000 | 67.856500 | 1.011724× | 0.987689× |
| 16 | 76.961000 | 76.960500 | 72.449000 | 72.337000 | 75.457000 | 76.208500 | 1.014887× | 0.954652× |
| 32 | 109.201000 | 110.241000 | 105.793500 | 106.512500 | 109.456000 | 109.473000 | 1.002332× | 0.969743× |
| 64 | 143.713500 | 145.761000 | 139.409000 | 140.049500 | 143.872500 | 143.888500 | 1.005929× | 0.971145× |
| 128 | 146.593500 | 146.753000 | 143.649000 | 143.329000 | 146.497000 | 145.857000 | 1.003397× | 0.981613× |
| 256 | 154.753000 | 155.313000 | 152.096500 | 152.257000 | 153.585000 | 153.313000 | 1.010321× | 0.991709× |
| 512 | 159.713000 | 159.713500 | 161.217000 | 160.609000 | 157.009000 | 157.121000 | 1.016861× | 1.024498× |
| 4096 | 301.731000 | 300.482500 | 329.874500 | 329.346500 | 295.762000 | 295.634000 | 1.018289× | 1.114686× |
| 8192 | 603.412500 | 594.613000 | 656.677000 | 634.517000 | 616.996500 | 595.925000 | 0.987841× | 1.064536× |
| 16384 | 1235.834000 | 1202.218000 | 1215.546000 | 1205.370500 | 1189.161500 | 1201.290000 | 1.019829× | 1.012749× |

T1/T2 are reported but excluded from aggregates. Primary paired ratio is sqrt((R1 × R2)/(C1 × C2)).

| Group | Saved control | R1 | R2 | Paired |
| --- | --- | ---: | ---: | ---: |
| Overall | head | 1.010402× | 1.008717× | 1.009559× |
| Overall | gather4 | 1.002954× | 1.000647× | 1.001800× |
| Decode | head | 1.009749× | 1.010130× | 1.009940× |
| Decode | gather4 | 0.980079× | 0.979340× | 0.979709× |
| Prefill | head | 1.012145× | 1.004957× | 1.008545× |
| Prefill | gather4 | 1.066601× | 1.059760× | 1.063175× |

Raw compiler-stack fingerprints differ. The explicit reviewed receipt proves exact historical reconstruction using only three generated entrypoint shebangs and corresponding RECORD hash/size fields. No installed file or raw cache metadata is changed; all other metadata fields must match. This equivalence is specific to the recorded environments, not generic fingerprint normalization. Receipt SHA256: `20e561ef5b3e8f8fdde8fcfef981df986bd806c6e4054a2ab70499891fd00aa8`.
