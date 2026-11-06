# Optional grouped row limits for per-token quantization

Independent unstaged source `../../flashinfer-row-limits-20261026`, based on frozen final A (`0def601d` + patch `8828ab24d607…`). Full candidate patch SHA256 is `bf62d3e7bd8f11efd7ae8ea51845aad30b9c3bbac87b0373d05b4884eebd1618`. `candidate-vs-finalA.patch` isolates the two-file addition; `source.json`/`source.patch` preserve the complete measured source.

The optional `row_limits` tensor gives an absolute exclusive row end for each fixed-size consecutive row group. An explicit compile-time `rows_per_group` controls indexing. The MoE inter-FC call uses its existing `tile_idx_to_mn_limit` and routing tile size. The quantizer reads these limits only inside the active prefix and after the PDL wait. It skips inactive payload reads, reductions and quantization, but zeroes SF slots in all layouts. Payload/per-token scales of inactive rows remain unspecified and FC2 masks their reads/stores. The initial quantizer omits the new arguments. No routing kernel/buffer, model threshold, dtype policy or scheduling policy changes.

The sign of `permuted_idx_to_expanded_idx` is deliberately not used: its padding is uninitialized. The supporting read-only audit is `../../perf-general-20261026/retained-policy/row-validity-audit.md`.

Static Ruff, format, Python compile and whitespace checks passed. Existing 37 NVFP4 cache-name tests passed on the candidate; group size is explicit in both getter and name-helper signatures. A source-paired task-local gate passed **290 graph replays** (65 direct +80 public chain per source), with every saved byte hash identical. Direct cases cover FP16/BF16, all three SF layouts, PDL off/on, changing group limits and live prefixes including zero, repeated grid traversal and the wide-row fallback with non-power-of-two group size17. Chain cases cover N16/32/128/256, one/two CTA, CLC/static, PDL off/on, SwiGLU/SiTU and changing routes/data including no local work. Routing-map padding is poisoned with a positive value to catch any mistaken sentinel dependency. Candidate inactive SF slots are checked zero, including linear layout; allocation slack remains untouched. No upstream tests were added.

GPU0 CAAC compares final A / candidate / candidate / final A using final A's saved native public AUTO cache, per-token only, tokens32/128/4096/8192, V41 first then V3/K3. Initial activation quantization is included, fused finalize disabled,10 warmups and100 cold-L2 CUDA-graph CUPTI samples. The observer asserts cache hits and exact raw sample/median consistency; source, routing and immutable tactic cache are checked per arm. Source-private CuTe caches and proven-identical persistent native C++ cache reuse are retained. Final raw receipts and derived summary are collected under `results/row-limits`.

Review note: root identified that `isinstance(rows_per_group, int)` accepts bool. The running source is frozen; strict `type(rows_per_group) is int` can be applied as a host-validation-only correction during final composition. It cannot alter any measured path (the benchmark passes ordinary integer routing tile sizes).

## Completed fixed-tactic screen

Every model completed on the same GPU0 with final-A / candidate / candidate / final-A order. `validate.py` checked the collection manifest, exact source patches, helper hashes, all native-cache hits recorded by the observer, unchanged GEMM tactics/configurations, route identities/histograms, activation recipe, input quantization, 48 medians and their 4,800 raw samples. All 12 timing arms exited successfully. The paired speedup is `sqrt(C0*C3/(A1*A2))`.

| Tokens | V3 | V41-Flash | Kimi K3 |
| ---: | ---: | ---: | ---: |
| 32 | 1.00112× | 1.00848× | 1.00440× |
| 128 | 0.99827× | 1.00459× | 1.00147× |
| 4096 | 1.00814× | 1.00773× | 1.01087× |
| 8192 | 1.01096× | 1.01419× | 1.01453× |

This is an isolated general improvement over final A, with stable prefill gains across all three models and a small neutral V3 decode change. It is not a new comparison with TRTLLM and does not substitute for the final composed candidate's full native-AUTO sweep. The initial quantizer remains the same in both arms; the measured change is only skipping inactive routed padding during inter-FC quantization.

Raw records and manifest: `results/row-limits/fixed-*/`, `results/manifest.json`. Exact validation result: `results/row-limits/validated-summary.json`. Each result includes medians, individual samples, source receipts, immutable native cache digest and routing identity. The measured source is intentionally left unstaged and unchanged for final composition by the parent agent.
