# W4A16 trace result

The optional markers are ready for review in `flashinfer-w4a16-iket-review` (unstaged, base374ed4c0). Default-off AST proof passes; both paired33-case exact runs pass, and all33 corresponding PTX files and CUBINs are byte-identical. This includes FC1/FC2, one/twoCTA, old/new weight layouts and several activation contracts. No wrapper argument, autotune tactic or MegaMoE file changed. No sanitizer.

Eight captures completed: current374 plus markers versus original PR7290 d35 regular-TMA implementation, K3 EP8 at4096/8192 tokens, clusters0/1 captured separately on the same respective GPU. Source, frozen native tactic/cache and routing hashes all pass. Matching marker-only baseline source has an AST proof and never modifies the baseline repository. Current marker sampling also preserves all non-marker AST nodes.

Native FC1 tactics match between arms: M256/N128/K256 at4K and M256/N192/K256 at8K, cluster2x1, CLC+PDL. Raw-weight/activation pipeline stages are4/3, decoded-weight stages2, accumulator stages2/1. Current uses640threads and regular-TMA d35 uses512threads.

| Mean sampled range (ns) | d35 4K | Current 4K | d35 8K | Current 8K |
|---|---:|---:|---:|---:|
| MMA A-ready wait | 134.41 | 87.64 | 327.07 | 240.45 |
| MMA B-ready wait | 46.10 | 194.58 | 40.19 | 174.58 |
| Transform raw-weight wait | 32.72 | 27.38 | 26.99 | 26.51 |
| Transform decoded-slot wait | 27.68 | 25.36 | 30.85 | 25.24 |
| Transform load/decode | 316.40 | 312.63 | 318.18 | 309.41 |
| Transform store/commit | 85.81 | 83.09 | 80.98 | 80.47 |
| Scheduler CLC-ready | 238.19 | 238.73 | 111.77 | 111.57 |
| MMA accumulator-empty | 82.42 | 77.71 | 2968.76 | 2990.05 |
| Epilogue body | 3258.91 | 3018.74 | 2736.76 | 2739.27 |

The paired diagnostic supports activation delivery/issue as the main new wait: B-wait grows by148ns at4K and134ns at8K while A-wait falls. Dequantization work and its upstream/downstream waits do not grow, providing no support for another register-budget sweep. CLC-ready spans are unchanged. The N192 accumulator/epilogue serialization already exists in d35 and is not the new Gather4 regression.

Current Gather4 issue averages432ns/568ns per issuer, versus58ns/38ns in the old regular activation-TMA warp. Four issuers versus one is a different ownership pattern: these spans must not be added or treated as equal-instruction timings. The source geometry issues16/24 Gather4 operations per issuer perK256 stage forN128/N192 (fourK64 chunks, four/six4-row groups). This makes issue efficiency a useful next audit target, with prior rejected elected-scope/live-group experiments checked before proposing another edit. The current data does not justify changing cache/tactic/stage policy yet.

Limitations: only two independently captured resident clusters, with different CLC work counts per arm. Marker overhead changes scheduling; range durations overlap across warps and are not end-to-end timing or retention evidence. A-ready is tested before B-ready, so the two spans describe program-order waits, not independent operand arrival latencies. Full counts, per-CTA/warp statistics and hashes are in `trace-summary.json` and `trace-table-4096.md`/`trace-table-8192.md`.

The first enabled attempt failed before kernel execution because automatic trace allocation used the entire padded CLC grid (840/1070GB). Native `--enabled-cluster` filtering reduced current trace storage to60MB and baseline to48MB without changing kernel work/tactics. The failed receipts are preserved. Optional CUDA-compatibility warnings were reported by the tool; all bounded captures and source/tactic/route guards completed. Normal exact/default-off validation is separate from this instrumented diagnostic.

Raw evidence archive SHA256: `457a0182ac62a4f2bf6015bdf7eed339355537e1dde3521037d3f431ab4b14f2`. GPUs5/7 are idle and released. The source remains unstaged for the parent review/retention decision.

Own-file pre-commit passes, including mypy/ruff. Final review kernel SHA256 `1abcd0b9412e1951e8a86cc3115f8364e0fec8b8a8bf50fd1db262170a9b270e`; `retention-source.json` binds it to the measured marker source. The only post-measurement change is the `typing.Any` import and module-level `_iket: Any = None` initializer required by mypy. Default-off AST proof was refreshed; no device or marker AST changed. The archived 33 paired PTX/CUBIN proofs and eight enabled traces refer to the measured marker hash above.

Trace aggregation: arithmetic mean of range duration, weighted by observed range count across clusters; no geometric aggregation. Range counts differ under CLC and overlapping warp durations are not summed into end-to-end latency.
