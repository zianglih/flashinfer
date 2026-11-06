# R3 bounded screen: do not retain universal static FC1

Single bounded candidate sweep against existing same-GPU controls, exact matching route/input/timer contracts. Combined expanded geometry, resource planner, explicit K choices, universal static FC1 and PDL publication-owner change; no isolated-mechanism or stability claim.

Ratios below are retained dea2 / R3, >1 favors R3. Tokens4/32/128/512/4096; NV includes initial quantization, MX excludes it. All75 rows and6source/route/runtime/GPU/timing checks pass.

| Model | Backend | T4 | T32 | T128 | T512 | T4096 |
|---|---|---:|---:|---:|---:|---:|
| v3 | CuteDSL MXFP4x8 | 0.9953x | 0.9916x | 1.0015x | 1.0044x | 1.0044x |
| v3 | CuteDSL MXFP8 | 1.0104x | 0.9933x | 0.9892x | 0.9970x | 1.0022x |
| v3 | CuteDSL PER-TOKEN | 1.0341x | 1.0092x | 1.0007x | 1.0035x | 1.0010x |
| v3 | CuteDSL W4A16 | 0.9896x | 1.0095x | 0.9956x | 0.9997x | 1.0010x |
| v3 | CuteDSL W4A4 | 1.0253x | 1.0104x | 0.9992x | 1.0034x | 1.0039x |
| v41-flash | CuteDSL MXFP4x8 | 1.0168x | 1.0038x | 0.9962x | 0.9906x | 1.0247x |
| v41-flash | CuteDSL MXFP8 | 1.0238x | 0.9906x | 0.9805x | 0.9717x | 1.0062x |
| v41-flash | CuteDSL PER-TOKEN | 1.0363x | 0.9944x | 0.9909x | 0.9841x | 0.9980x |
| v41-flash | CuteDSL W4A16 | 1.0058x | 0.9811x | 0.9967x | 0.9979x | 1.0453x |
| v41-flash | CuteDSL W4A4 | 1.0330x | 0.9960x | 0.9823x | 0.9863x | 0.9967x |
| kimi-k3 | CuteDSL MXFP4x8 | 1.0204x | 0.9902x | 0.9873x | 1.0076x | 1.0336x |
| kimi-k3 | CuteDSL MXFP8 | 0.9934x | 0.9880x | 0.9861x | 0.9646x | 1.0004x |
| kimi-k3 | CuteDSL PER-TOKEN | 1.0143x | 0.9793x | 0.9871x | 0.9923x | 1.0077x |
| kimi-k3 | CuteDSL W4A16 | 0.9968x | 1.0016x | 0.9998x | 0.9995x | 0.9673x |
| kimi-k3 | CuteDSL W4A4 | 1.0182x | 0.9796x | 0.9797x | 0.9762x | 1.0071x |

Static FC1 recovers K3 prefill but loses meaningful middle decode. W4A16 controls are near-flat at those middle points; its prefill drift is substantial and must not be attributed to this source. Different AUTO winners also prevent attribution of this combined screen to scheduling alone. The separate fixed-tactic C–A–A–C isolates the prefill scheduler effect.

Next candidate: flat internal FC1 static/CLC axis with existing complete-chain profiling. No new workload heuristic or public knob. Original and R3 data remain immutable. TRT ratios in comparison.json are explicitly provisional reused-control ratios, not fresh same-sweep comparisons.
