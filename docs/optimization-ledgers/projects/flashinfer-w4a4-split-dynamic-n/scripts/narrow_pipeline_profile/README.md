# Independent-producer FC2 profile

Read-only NCU comparison of retained `98fd3566b5` against the frozen
`producer-roles-shared-empty-review` source (`52ef9298…`), native T128,
N16/M128 one-CTA tactics, unfused finalization. Both use the same captured FC2
input and initialized output allocation. Output bytes and input fingerprints
match before and after profiling. No primary timing or original baseline
campaign was rerun.

Environment: replacement C1 `fi-w4a4-narrow-1025`, B200-92 GPU2,
`nvcr.io/nvidia/pytorch:26.05-py3`, existing CUDA13.2/CuTe4.7.1 environment.
Full GPU UUID, NCU version, command and source hashes are archived.

| Metric | Control | Separate weight warp, shared empty |
|---|---:|---:|
| NCU replay duration (us) | 44.064 | 44.960 |
| DRAM reads (MB, decimal) | 248.301312 | 248.302592 |
| DRAM read throughput (% peak) | 73.54 | 72.06 |
| Executed warp instructions | 4,085,066 | 4,560,428 |
| Eligible warps / scheduler cycle | 0.11 | 0.13 |
| MIO-throttle stalled warps / issued instruction | 0.25 | 0.05 |
| Long-scoreboard stalled warps / issued instruction | 17.64 | 17.99 |
| Registers / thread | 90 | 86 |
| Threads / CTA | 288 | 320 |
| Grid CTAs | 148 | 148 |

The reorganization reduces the MIO-throttle ratio but executes 11.64% more warp
instructions for essentially identical traffic and MMA/TMEM work. It does not
establish that warp specialization is intrinsically slower. It motivates
distributing TMA issue across the existing producers while reducing duplicated
control work. These are replay diagnostics, not cold-L2 graph/CUPTI medians,
and individual stall ratios do not prove a unique causal explanation.

`probe.py` imports the actual source files under separate module identities and
checks their Git/source manifests. `run_remote.py` profiles only the two marked
FC2 launches on GPU2, then exports raw metrics. `collect.py` preserves raw NCU,
JSON, CSV, helper and source files. `summarize.py` derives `summary.json` locally.
All output paths reject overwrites; completed runs must not be rerun in place.

Archive: `evidence/narrow-pipeline-profile/raw.tar.gz`, SHA256
`c2829ca7fa87f364497b96dec357a7b967428d60dc6df8abd30a152b4a1843b6`.
