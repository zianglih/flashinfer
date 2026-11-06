# PR7290 current-head benchmark refresh

The complete original campaign passed: 31 jobs, 468 cells, four CAAC phases, 187,200 strict CUPTI samples. Tokens 1/2 remain in raw results; 396 cells enter retention summaries. Candidate `2b4732791a3ce48bc3ae6c030a283fab73854e0e` and control `a620ce7790b32f7f0ae524a811417d2c6cee1152` used the same frozen choices/routes on each job's original GPU. No source changes, retuning or compiler-policy changes were made.

Runtime: C3 `fi-pr7290-perf-1102`, namespace `ziangli`, node `hu-wtc-157`, eight B300 SXM6 AC GPUs, `nvcr.io/nvidia/pytorch:26.05-py3`, NVCC 13.2.78 and CuTe DSL 4.8.0. Source inventories (34,759 candidate files / 31,070 control files, including pinned submodules) passed before and after. Both source-specific native caches passed normal loader, Ninja no-op and final ELF/Ninja hash checks. Data symlinks resolve to their own source roots.

| Retention group | Cells | Candidate vs a620 |
|---|---:|---:|
| Decode (4–64) | 180 | +0.017% |
| Middle (128–512) | 108 | +0.005% |
| Prefill (4096–16384) | 108 | −0.355% |
| All | 396 | −0.088% |

Elapsed campaign time: 1,094.03 s. The raw evidence contains 2,176 loaded-kernel records. All timing samples passed; NVML has 179 exception quartiles and 10 missing quartiles, retained without imputation or filtering. Some large prefill negatives coincide with SM clock changes. Resource/configuration equality is verified separately; no SASS identity is claimed because normal compilation did not persist MoE cubins.

Verified full dataset: `fetched/1793691596500669000/data`; derived audit: sibling `report`. Downloaded archive SHA256: `3398f3067d72954914d2ef34cf4466eba7a1fa29dd5ae87c969b74d2c896211a` (4,070 files, 265,684,617 bytes compressed). The archive includes exact wrappers, original frozen inputs, migrated-key proofs, source manifests, native build proofs, clocks and raw traces. The original historical TRTLLM/non-swap/pre-PR W4 denominators are unchanged.

A separate diagnostic was sealed after the main campaign: every retained loss below −2%, plus 1–2% losses only when both repeat spreads are <=0.5% and every clock sample is 2032 MHz/reason0. This selected 10 negative cells and retained two additional paired MX dtype cells: 12 cells across eight jobs, 4,800 samples. The diagnostic reverses phase order to ACCA, serializes jobs on their original GPUs, and leaves stock clocks/power unchanged. Its results remain separate; no main heatmap value was replaced.

Diagnostic plan SHA256: `3a6c3ea10284a4fcfa64b0a66c2ec6d3a485badc674c7dd7c1c19c70717b3666`; config SHA256: `b4c907c037d05f223d61bddbcbb53b8ef6dfa02e5647e9ac93ffb8567ba5e8af`. See `isolation-proposal.json` and the isolated evidence bundle for all selected and excluded >1% negatives.

## Completed isolated diagnostic

All eight serial jobs passed in 624.14 s: 12 cells and 4,800 additional strict CUPTI samples. Source and native postflight checks passed again. Geomean +0.418%; six cells remain negative, worst -2.636%. The diagnostic still has 35 clock-exception quartiles. It does not establish a per-cell performance guarantee, and none of these values replace the main campaign.

| Job | Tokens | Mode | Original CAAC | Isolated ACCA | Control spread | Candidate spread |
|---|---:|---|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | 4096 | CuteDSL W4A16 | -6.170% | +1.738% | 3.122% | 0.110% |
| ep-nemo3-ultra-mxfp | 8192 | CuteDSL MXFP4x8 | +0.079% | -1.194% | 0.077% | 2.409% |
| ep-nemo3-ultra-mxfp | 8192 | CuteDSL MXFP8 | -2.526% | +0.122% | 0.156% | 0.156% |
| ep-nemo3-ultra-w4a16 | 16384 | CuteDSL W4A16 | -5.795% | -0.287% | 1.354% | 1.269% |
| ep-v3-mxfp | 16384 | CuteDSL MXFP4x8 | -0.406% | +3.012% | 3.194% | 6.234% |
| ep-v3-mxfp | 16384 | CuteDSL MXFP8 | -2.234% | +4.661% | 3.978% | 5.807% |
| ep-v3-w4a16 | 8192 | CuteDSL W4A16 | -3.217% | +1.038% | 2.122% | 0.482% |
| ep-v41-flash-mxfp | 16384 | CuteDSL MXFP4x8 | -2.736% | -2.636% | 6.530% | 0.491% |
| ep-v41-flash-mxfp | 16384 | CuteDSL MXFP8 | -3.752% | -2.141% | 4.484% | 2.862% |
| ep-v41-flash-w4a16 | 8192 | CuteDSL W4A16 | -5.975% | -0.970% | 2.424% | 4.113% |
| ep-v41-flash-w4a16 | 16384 | CuteDSL W4A16 | -3.957% | -0.481% | 0.727% | 2.567% |
| tp-v41-flash-w4a16 | 8192 | CuteDSL W4A16 | -2.538% | +2.415% | 3.216% | 1.741% |

Verified diagnostic dataset: `isolated-fetched/1793692299844142000/data`; complete raw spans, telemetry, sealed selection/protocol and exact executed runner are included. Archive SHA256: `9b7fefb0896fe527525aedcc9f949b0cd7acad3c53ddb451b39d6c907ecad7a4` (268 files). No additional GPU runs or source modifications were performed after this selection.
