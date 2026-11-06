# V4.1 per-token trace after live-row and bounded-grid changes

FinalA source patch8828ab24, B300GPU7, CUDA13.2, three cold-L2 CUDA-graph diagnostic replays using the frozen current0def native8192-token tactics. Both arms include the same updated standalone input quantizer. Intermediate quantization is backend-specific. Full source/cache/tactic and command receipts plus NSYSreports are in raw/. These profiler durations are not retention medians.

| Phase | CuTe duration us | TRT duration us | CuTe endpoint us | TRT endpoint us |
|---|---:|---:|---:|---:|
| input quantization | 44.800 | 44.544 | 44.800 | 44.544 |
| routing | 14.336 | 14.433 | 55.680 | 55.617 |
| prepare | 17.601 | N/A | 72.961 | N/A |
| FC1 | 227.617 | 256.032 | 298.273 | 311.2 |
| intermediate quantization | 79.840 | 49.057 | 372.577 | 354.881 |
| FC2 | 146.657 | 124.608 | 503.010 | 478.242 |
| combine | 44.256 | 48.832 | 542.274 | 526.273 |

Kernel durations overlap under PDL and cannot be summed. Endpoints are relative to the first input-quantizer launch. CuTe FC1 compensates for much of its preparation and quantization cost; the intermediate quantizer remains a useful target. The active prefix includes padded expert rows. The existing tile row limits, not the undefined expanded-map padding, identify the rows that need quantization. No performance claim is derived from these three samples.
