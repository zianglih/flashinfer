| Tokens | V3 EP8 | V4.1-Flash EP4 | Kimi K3 EP8 |
| ---: | ---: | ---: | ---: |
| 1 | 0.9972x | 1.0164x | 1.0181x |
| 2 | 0.9991x | 0.9727x | 1.0076x |
| 4 | 0.9989x | 0.9981x | 0.9964x |
| 8 | 0.9965x | 1.0033x | 0.9924x |
| 16 | 1.0073x | 1.0001x | 0.9952x |
| 32 | 1.0015x | 0.9987x | 1.0067x |
| 64 | 0.9988x | 0.9964x | 1.0043x |
| 128 | 0.9946x | 1.0042x | 1.0180x |
| 256 | 1.0045x | 0.9868x | 0.9980x |
| 512 | 0.9992x | 0.9855x | 0.9990x |
| 4096 | 0.9961x | 1.0002x | 0.9856x |
| 8192 | 1.0167x | 0.9929x | 1.0093x |
| 16384 | 1.0016x | 1.0146x | 1.0080x |

| Scope (excludes 1/2) | Overall | Decode 4–512 | Prefill 4096–16384 |
| --- | ---: | ---: | ---: |
| v3 | 1.0014x | 1.0001x | 1.0048x |
| v41-flash | 0.9982x | 0.9966x | 1.0025x |
| kimi-k3 | 1.0011x | 1.0012x | 1.0009x |
| all models | 1.0002x | 0.9993x | 1.0027x |

Both arms reuse the same existing23-tactic native winner cache. There is no new autotuning. Ratios use geometric means of the CAAC per-arm medians;1/2tokens are reported and excluded from retention. Source, benchmark/observer hashes, cache snapshots, frozen winners and routes are verified. W4A16 consumes BF16 directly, so the family include-activation-quant flag adds no standalone quantizer.
