# R1 diagnostic screen (not a retention source)

All three models and both families completed on the same GPUs as the existing controls. Candidate tokens are4/32/128/512/4096; all full-precision source/runtime/route/timer audits pass. NV includes initial activation quantization on both sides; MX does not. The archived MX completion-parser defect is explicitly bridged by its hash-bound corrected parser audit.

R1 omitted8 failing NV explicit-K tactics; the corrected R2 source has passed210 exact replays and is screened separately. These results combine resource planning, expanded geometry, generalized CLC and K choices; they do not isolate K selection.

## v3

| Backend | T4 | T32 | T128 | T512 | T4096 |
|---|---:|---:|---:|---:|---:|
| CuteDSL W4A4 | 1.00300× | 1.00409× | 0.99988× | 0.99076× | 0.99862× |
| CuteDSL PER-TOKEN | 1.00369× | 0.99940× | 1.00165× | 0.99231× | 0.99614× |
| CuteDSL W4A16 | 0.99854× | 1.00361× | 1.00065× | 1.00150× | 1.00260× |
| CuteDSL MXFP8 | 1.00670× | 0.99695× | 1.00315× | 1.00058× | 1.00052× |
| CuteDSL MXFP4x8 | 1.00811× | 0.99383× | 1.00446× | 1.00010× | 1.00113× |

## v41-flash

| Backend | T4 | T32 | T128 | T512 | T4096 |
|---|---:|---:|---:|---:|---:|
| CuteDSL W4A4 | 1.03818× | 1.00715× | 1.00126× | 1.00701× | 1.01584× |
| CuteDSL PER-TOKEN | 1.00712× | 1.00234× | 0.99949× | 0.99961× | 1.01080× |
| CuteDSL W4A16 | 0.99127× | 0.99461× | 0.99640× | 0.99995× | 1.02060× |
| CuteDSL MXFP8 | 0.99877× | 1.00231× | 1.00014× | 0.99731× | 1.00937× |
| CuteDSL MXFP4x8 | 0.98710× | 1.00350× | 0.99858× | 1.00085× | 1.03490× |

## kimi-k3

| Backend | T4 | T32 | T128 | T512 | T4096 |
|---|---:|---:|---:|---:|---:|
| CuteDSL W4A4 | 0.99883× | 0.99973× | 1.00482× | 0.99604× | 0.94701× |
| CuteDSL PER-TOKEN | 1.00134× | 0.99805× | 1.00146× | 0.98022× | 0.96382× |
| CuteDSL W4A16 | 0.99194× | 1.00410× | 1.00208× | 1.00189× | 1.00638× |
| CuteDSL MXFP8 | 1.00215× | 0.99567× | 1.00064× | 0.99938× | 0.97204× |
| CuteDSL MXFP4x8 | 0.99851× | 0.99540× | 0.99826× | 0.99986× | 0.97009× |

Ratios are retained-control latency / R1 latency. The unchanged W4A16 backend provides a drift/control observation. V4.1T4NV gains3.82%, while K3T4096 loses3–5% in affected arms. Both remain single-sweep observations.

Process walltime (seconds, NV/MX) was V3317.7/524.3, V4.1428.8/530.3, K3315.0/393.8. This includes fresh native AUTO, first-use compilation and TRT startup; token counts/cache states differ from archived controls, so it is not a normalized compiler-cost comparison. The observer records selected tactics, not a unique compilation counter. The source-private FlashInfer object inventory only exposes quantization objects; core CuTe compilation count cannot be inferred from it.
