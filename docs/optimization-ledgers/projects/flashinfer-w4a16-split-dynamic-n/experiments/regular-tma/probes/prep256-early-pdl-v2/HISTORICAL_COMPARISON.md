# Regular TMA versus saved HEAD and Gather4

Both controls are saved historical sweeps, without fresh bracketing drift control. Probe results are descriptive only; no probe aggregate or retention decision.

Both reference arms are reused unchanged. Identity checks require the same host, GPU UUID/model/power, runtime, routing, and native timing. Full tactic records and cumulative caches are compared separately in the JSON report.

| T | HEAD R1 µs | HEAD R2 µs | Gather4 R1 µs | Gather4 R2 µs | Candidate µs | HEAD/candidate | Gather4/candidate |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 76.961000 | 76.960500 | 72.449000 | 72.337000 | 74.465000 | 1.033516× | 0.972175× |
| 512 | 159.713000 | 159.713500 | 161.217000 | 160.609000 | 158.129500 | 1.010016× | 1.017601× |
| 4096 | 301.731000 | 300.482500 | 329.874500 | 329.346500 | 296.130000 | 1.016804× | 1.113060× |
| 16384 | 1235.834000 | 1202.218000 | 1215.546000 | 1205.370500 | 1203.337500 | 1.012941× | 1.005909× |

Raw compiler-stack fingerprints differ. The explicit reviewed receipt proves exact historical reconstruction using only three generated entrypoint shebangs and corresponding RECORD hash/size fields. No installed file or raw cache metadata is changed; all other metadata fields must match. This equivalence is specific to the recorded environments, not generic fingerprint normalization. Receipt SHA256: `20e561ef5b3e8f8fdde8fcfef981df986bd806c6e4054a2ab70499891fd00aa8`.
