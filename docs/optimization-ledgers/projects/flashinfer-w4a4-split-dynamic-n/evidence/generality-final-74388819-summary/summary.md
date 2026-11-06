Final current-backend summary for retained commit `74388819899d0abfd1a12102f7cc108bda13c812`. Ratios are TRTLLM / CuTe latency from each same-model/family/GPU public sweep; greater than one favors CuTe. Tokens1/2 remain in raw outputs and are excluded below. Decode is4–512; prefill is4096/8192/16384.

| Model | CuTe arm | TRT baseline | Decode | Prefill | Overall |
|---|---|---|---:|---:|---:|
| v3 | CuteDSL W4A4 | TRTLLM NVFP4 | 1.044845x | 1.127349x | 1.066728x |
| v3 | CuteDSL PER-TOKEN | TRTLLM NVFP4 | 0.990732x | 0.780996x | 0.928499x |
| v3 | CuteDSL PER-TOKEN | TRTLLM PER-TOKEN | 1.063257x | 0.938977x | 1.027816x |
| v41-flash | CuteDSL W4A4 | TRTLLM NVFP4 | 1.029149x | 1.067118x | 1.039368x |
| v41-flash | CuteDSL PER-TOKEN | TRTLLM NVFP4 | 0.950123x | 0.779367x | 0.900150x |
| v41-flash | CuteDSL PER-TOKEN | TRTLLM PER-TOKEN | 1.029270x | 0.917358x | 0.997460x |
| kimi-k3 | CuteDSL W4A4 | TRTLLM NVFP4 | 0.995638x | 1.060011x | 1.012797x |
| kimi-k3 | CuteDSL PER-TOKEN | TRTLLM NVFP4 | 0.925314x | 0.641738x | 0.837422x |
| kimi-k3 | CuteDSL PER-TOKEN | TRTLLM PER-TOKEN | N/A | N/A | N/A |
| v3 | CuteDSL MXFP4x8 | TRTLLM MXFP4x8 | 1.049618x | 1.055687x | 1.051270x |
| v3 | CuteDSL MXFP8 | TRTLLM MXFP8 | 1.034942x | 1.064230x | 1.042849x |
| v41-flash | CuteDSL MXFP4x8 | TRTLLM MXFP4x8 | 1.030195x | 1.048454x | 1.035143x |
| v41-flash | CuteDSL MXFP8 | TRTLLM MXFP8 | 1.002096x | 1.018354x | 1.006504x |
| kimi-k3 | CuteDSL MXFP4x8 | TRTLLM MXFP4x8 | 0.998087x | 1.147664x | 1.036832x |
| kimi-k3 | CuteDSL MXFP8 | TRTLLM MXFP8 | N/A | N/A | N/A |

NV quantized-input arms include initial activation quantization; W4A16 consumes BF16. MX activation quantization remains outside timing. Every run uses native AUTO, 10 warmups/100 iterations, cold L2, CUDA graphs/CUPTI, and no fused CuTe finalize. Per-token arms retain the explicit activation-only MSE4over6 recipe, independent of the standard arms.

All six public tables finished with exit0: 78 token rows,377 native latency records,156 saved blockscaled v4/outer5 choices, and87 exact clean source pins before/after. The strict summary binds117 inputs. Saved final choices are verified; actual host forwarding was observed separately in the source-identical bounded R5 screen. No final13 forwarding instrumentation claim or cross-GPU historical MX speedup is made.

Main remaining same-dtype gaps: V4.1-Flash MXFP8 T32–512 (T1280.971386x), K3 mixed T32–512 (T640.976356x), K3 standard NV T5120.964820x. Per-token CuTe beats per-token TRT on decode average in V3/V4.1, but loses on prefill; K3 TRT per-token is unavailable. These are single-sweep current-backend results, not repeat-stability claims.

Summary SHA256: `6435ca097e3df8864e6c5fcffeead218c21628a2b7dbd100519b311c21dc83a4`. Independent six-table check: `evidence/generality-final-74388819-independent/review.json`. Raw tables remain under `evidence/generality-final-74388819-{nv,mx}-r1-{v3,v41-flash,kimi-k3}/raw`.
