# W4A16 cleanup with the original 23 tactics

The user requested removing the CLC tactic doubling. The final implementation restores the original two-field tactic tuple and FC1 scheduling heuristic while keeping shared preparation, metadata synchronization cleanup, static weight dimensions/K-loop count, and the max-active-cluster compile-cache key fix. Earlier46-tactic results remain historical evidence in `../composed/` and `../composed-recheck/` and are not used for this comparison.

The timed deployment is `no-tactic-expansion-d084b4b9a4f4`: base `1496b557f9b606f3a0bb36bcebf5293d3e11555a` plus full-index patch SHA256 `d084b4b9a4f44953fed38fb80d696601473e8af9e035769dc15bd6f0aa169338`. Independent Git-diff hashing binds it exactly to local retained commit `0b7fe90151340d4fca6a5ec41a91019dde743819`; see `commit-binding.json`. The root-owned deployment receipt is `../no-tactic-expansion/deployment.json`.

The comparison reuses the existing original23 native winner cache for both sources, with no new AUTO search. This isolates the retained implementation cleanup from tactic-selection changes. V3 EP8 used GPU4, V4.1-Flash EP4 GPU5 and Kimi K3 EP8 GPU6. Each ran all13 tokens in control/candidate/candidate/control order with10 warmups and100 CUPTI cold-L2 CUDA-graph samples, fused finalize disabled. W4A16 consumes BF16 directly; the NVFP4-family activation-quantization flag adds no standalone quantizer to this arm. Exact invocations, worker, launch configuration and environment are preserved in `evidence/launch/` and phase receipts.

All39 cells completed. Source manifests and live source file hashes/HEAD/diff, observer/benchmark hashes,156 routing identities and per-token cache snapshots,780 cache hits, and all15,600 raw sample medians pass independent verification. Both sources enumerate23 tactics and use identical two-field winners in all four phases. All three shared baseline cache hashes remain unchanged before/after.

| Model | Overall | Decode 4–512 | Prefill 4096–16384 |
| --- | ---: | ---: | ---: |
| V3 EP8 |1.0014x |1.0001x |1.0048x |
| V4.1-Flash EP4 |0.9982x |0.9966x |1.0025x |
| Kimi K3 EP8 |1.0011x |1.0012x |1.0009x |
| All models |1.0002x |0.9993x |1.0027x |

Tokens1/2 are reported but excluded from every retention aggregate. All33 retained cells fall between0.9855x and1.0180x. This is neutral performance with a simpler shared implementation and fewer unnecessary instructions; it is not a broad speedup claim. K3 T128's1.0180x gain and V4.1-Flash T512's0.9855x ratio are repeat-stable. Larger prefill points show repeat drift: V3 T8192 shifts about2% in both arms, V4.1-Flash T16384 about3–6%, and K3 T4096 about3% in the candidate arm. No additional GPU rounds were launched.

- `speedups.md`: full13×3 table and group aggregates.
- `raw-median-speedups.csv`: all39 cells, four phase medians, repeat ratios and identical selected tactics.
- `raw-samples.csv`: all15,600 CAAC measurements.
- `summary.json`: exact numbers, groups, source binding, routing identities, winner caches and checks.
- `evidence/`:199 raw/source/launch files.

This cache-only comparison contains no native AUTO compilation/profile split; process wall times are recorded per phase. A read-only evidence transfer briefly lost its SSH connection and was retried; detached GPU workers completed normally, and all collected evidence passed validation. Correctness gates remain separately owned by root/audit.
