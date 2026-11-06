# W4A16 loop-interchange qualification

The plain compile-time loop interchange is a ten-addition/eleven-deletion instruction-sanity improvement. Retained by parent as6c6515f2, measured from base22ffe662, kernelb8f124f187ec169b101c56a72cce2732833b89bf6ef3b72eaa0695f7a04b5da7. All24 CAAC cells and runtime/source/tactic/route guards passed. Parent retained it for instruction sanity after the bounded negative-case repeat below.

| Model | T8 | T4096 | T16384 |
|---|---:|---:|---:|
| V3 EP | +0.047% | +1.170% | +3.880% |
| V41F EP | +0.141% | +2.756% | +1.817% |
| K3 EP | -0.019% | +2.183% | +0.591% |
| N3U EP | +0.109% | +0.377% | -0.301% |
| V3 TP | +0.028% | +0.177% | -0.663% |
| V41F TP | +0.125% | +3.095% | -0.619% |
| K3 TP | -0.116% | +1.255% | -0.030% |
| N3U TP | +0.024% | +0.630% | -2.861% |

Values are retained latency / candidate latency−1, all raw rows included. EP geometric means: decode+0.069%, prefill+1.551%; TP: decode+0.015%, prefill+0.110%. These summaries are descriptive and not claims that drift-affected individual gaps have closed.

N3UTP4K improves+0.630% with0.035/0.003% control/candidate repeat spreads. V41FTP16K loses−0.619% with0.035/0.137% spreads; this is a small consistent median cost. N3UTP16K loses−2.861% in the aggregated median, but its control repeats differ6.189%:1.8539/1.9686ms, versus candidate1.9700/1.9650ms. Quartiles ramp during all four phases. Attribution is unresolved, not proof of external noise. A bounded same-protocol repeat is recommended before retention. V3TP16K−0.663% also has1.18/1.79% repeat spreads. Earlier four-cell K3 drift remains preserved in w4a16-linear-issue.

SASS and validation:33 existing exact W4 cases passed on the measured linear-task form; plain loop interchange produces byte-identical PTX+CUBIN at N16/N128/N192. The144-combination per-warp geometry proof preserves copy multiset, cached route slots and multicastKpartition. N128/N192 remove39/61 non-NOP gather instructions and12/20 uniform branches; other warp scopes unchanged, zero local storage, N16 byte-identical to retained. Pre-commit passes. Fifth WG, register quotas, FC2, PDL, shared storage, staging, tactics and barriers are unchanged.

Protocol: all four models EP/TP at8/4096/16384, same source-paired fixed native winners, actual frozen routes, fresh22ffe same-GPU controls, C-A-A-C with100 strictCUPTI cold-L2 graph samples and10 warmups, read-only2ms NVML. GPUs3/4/5/7 map to V3/V41F/K3/N3U. No retune, clock/power settings or sanitizer.16K phases show SM-clock transitions/reasonmask4 in both arms while memory stays3996MHz; NVML is coarse and workload utilization may itself change power behavior. All telemetry and sample quartiles are retained.

Raw archive SHA25690b2191c96860837ce02cef4cc5fc30e6f6a73be66de050bf2415686f816f96b (21,710,334bytes), reconstructed from hash-checked2MB chunks. All four GPUs were verified idle and released after completion. Only one active local review source remains.

```csv
job,tokens,backend,control_ms,candidate_ms,speedup_pct,control_spread_pct,candidate_spread_pct
ep-kimi-k3-w4a16,8,CuteDSL W4A16,0.0839685,0.0839845,-0.019051134435521533,0.038116792233711116,0.03810952916867283
ep-kimi-k3-w4a16,4096,CuteDSL W4A16,0.55350075,0.54167575,2.183040315170093,2.1176681093624916,0.31646388816981563
ep-kimi-k3-w4a16,16384,CuteDSL W4A16,1.99658475,1.984846,0.5914186793332998,0.22255198457854508,0.365025766821625
ep-nemo3-ultra-w4a16,8,CuteDSL W4A16,0.051376500000000005,0.05132075,0.10863052469032297,0.06230468940138234,0.03215590742997598
ep-nemo3-ultra-w4a16,4096,CuteDSL W4A16,0.40256349999999996,0.40105075,0.3771966515459635,0.07927356586912016,0.7326314419638269
ep-nemo3-ultra-w4a16,16384,CuteDSL W4A16,1.51406975,1.5186427500000002,-0.3011241452277158,2.180112949914337,5.471543986700067
ep-v3-w4a16,8,CuteDSL W4A16,0.06960875,0.06957624999999999,0.046711341873129086,0.11427503629488633,0.023717801287959084
ep-v3-w4a16,4096,CuteDSL W4A16,0.2919855,0.28860925,1.1698343001826927,0.6924922159063485,0.29998924272234273
ep-v3-w4a16,16384,CuteDSL W4A16,1.21520625,1.16982125,3.8796525537555526,1.6782508252468409,4.2675300762235135
ep-v41-flash-w4a16,8,CuteDSL W4A16,0.051008500000000005,0.050936499999999996,0.14135246826934011,0.19034536891679998,0.15718173155325754
ep-v41-flash-w4a16,4096,CuteDSL W4A16,0.458101,0.44581275,2.7563702473740292,4.055260948291406,0.23006935765848002
ep-v41-flash-w4a16,16384,CuteDSL W4A16,1.54558575,1.5180007500000001,1.8171927780668007,0.34015754767697803,2.201605424008757
tp-kimi-k3-w4a16,8,CuteDSL W4A16,0.08896899999999999,0.08907225,-0.11591713468561693,0.053965934004174265,0.10727384034732168
tp-kimi-k3-w4a16,4096,CuteDSL W4A16,0.70085375,0.69216575,1.2551906822896086,1.244834128598149,1.6454788115379593
tp-kimi-k3-w4a16,16384,CuteDSL W4A16,2.45058125,2.45131575,-0.029963500214125194,0.5997122690836632,0.3805800560764627
tp-nemo3-ultra-w4a16,8,CuteDSL W4A16,0.06632,0.066304,0.024131274131278246,0.04826254826255649,0.0
tp-nemo3-ultra-w4a16,4096,CuteDSL W4A16,0.54842075,0.5449882500000001,0.6298300926671274,0.03474213765364276,0.003027634041607996
tp-nemo3-ultra-w4a16,16384,CuteDSL W4A16,1.91122525,1.9675115,-2.860783787032506,6.188958377610354,0.25322852373013127
tp-v3-w4a16,8,CuteDSL W4A16,0.057111999999999996,0.05709625,0.027584999014806932,0.028019052955996493,0.14108945597306466
tp-v3-w4a16,4096,CuteDSL W4A16,0.480939,0.48009050000000003,0.1767375109484437,0.2102265867944375,0.20350185830975143
tp-v3-w4a16,16384,CuteDSL W4A16,1.7512995,1.76299425,-0.6633458957679528,1.180743942778406,1.7882584145720637
tp-v41-flash-w4a16,8,CuteDSL W4A16,0.06380075,0.063721,0.12515497245806362,0.07447826018784909,0.1759208356239661
tp-v41-flash-w4a16,4096,CuteDSL W4A16,0.58354325,0.5660225000000001,3.0954158182757485,1.4639143936765686,5.108112319405134
tp-v41-flash-w4a16,16384,CuteDSL W4A16,1.8927765,1.90457425,-0.6194429017403746,0.03529829836308451,0.1370535972300413
```

## Bounded N3U TP16K repeat

Same source, fixed native winner, route guards,100strictCUPTI cold-L2 protocol and stock clocks, GPU7. Control1.960320ms versus candidate1.961184ms:−0.044%; control/candidate repeat spreads1.344/0.018%. Phase medians C-A-A-C:1.9472315/1.9610075/1.9613605/1.973408ms. All phases show intra-run latency ramps and clock/power-state variation; the data does not isolate a causal clock effect. The repeat supplies no evidence of a material persistent regression. The original−2.861% row remains unchanged above rather than being replaced.

Recommendation: retain the general compile-time loop interchange for its verified instruction reduction and simpler source, accepting the small stable V41FTP16K−0.619% median loss under the user's slight-prefill allowance. No headline end-to-end gain is claimed from drifted rows. Keep raw24-cell geomeans separate from this targeted qualification.

Repeat archive SHA256e9013c4638bf88400524596490a539b8145c6cbaf524d0659d5cdf391537eb7a (2,065,818bytes), all source/tactic/route/runtime checks pass. Repeat raw files, sample quartiles and read-only NVML in repeat-evidence/repeat-perf; GPU7 released.

Retained/pushed commit6c6515f2. All514 source files match both canonical6c and the immutable measured remote candidate. The completed local review copy was retired after patch/hash proof; all helpers and raw evidence remain. `retained-source6c.json` explicitly separates logical source commit6c from actual remoteGit1b0.

Aggregation definition: each phase latency is the median of100 CUPTI samples; each arm latency is the median of its two phase medians (for two values this equals their arithmetic mean). Cell speedup is the ratio of those arm latencies minus1. Any reported cross-cell geometric mean is the geometric mean of cell latency ratios, not a geometric average of the raw phase medians. Raw rows are unchanged.
