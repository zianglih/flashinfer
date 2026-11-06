| Tokens | V3 EP8 | V4.1-Flash EP4 | Kimi K3 EP8 |
| ---: | ---: | ---: | ---: |
| 1 | 0.9539x | 1.0483x | 1.1618x |
| 2 | 0.9758x | 0.9741x | 1.0119x |
| 4 | 1.0033x | 0.9893x | 0.9928x |
| 8 | 0.9857x | 0.9935x | 0.9702x |
| 16 | 0.9885x | 0.9950x | 0.9736x |
| 32 | 1.0044x | 1.0065x | 1.0065x |
| 64 | 1.0012x | 1.0109x | 1.0083x |
| 128 | 1.0021x | 1.0142x | 1.0337x |
| 256 | 0.9956x | 1.0009x | 1.0102x |
| 512 | 0.9914x | 0.9786x | 1.0172x |
| 4096 | 0.9989x | 0.9908x | 1.0629x |
| 8192 | 0.9859x | 1.0115x | 1.0062x |
| 16384 | 1.0005x | 0.9475x | 1.0246x |

| Scope (excludes 1/2) | Overall | Decode 4–512 | Prefill 4096–16384 |
| --- | ---: | ---: | ---: |
| v3 | 0.9961x | 0.9965x | 0.9951x |
| v41-flash | 0.9943x | 0.9986x | 0.9829x |
| kimi-k3 | 1.0093x | 1.0013x | 1.0310x |
| all models | 0.9999x | 0.9988x | 1.0028x |

| Model | AUTO process s | AUTO context s | CuTe compile s | Profile exclusive s | Profile calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| v3 | 83.467 | 64.745 | 49.837 | 12.737 | 1012 |
| v41-flash | 60.833 | 43.278 | 27.107 | 14.225 | 1012 |
| kimi-k3 | 94.216 | 68.427 | 49.667 | 16.557 | 1012 |

Profile-exclusive host time includes warmup, graph capture, GPU waits and profiling machinery; it is not isolated tactic traversal. CuTe compilation includes SDK cache work. All timing fields above are seconds.

Ratios use geometric means of the CAAC per-arm medians. 1/2 tokens are reported, excluded from every retention aggregate. Source hash, benchmark/observer hashes, all saved cache snapshots, cache hits/tactics and routing identities were verified. W4A16 consumes BF16 directly, so its arm has no standalone activation quantizer despite the family include-activation-quant flag.
