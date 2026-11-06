# CuTe DSL gate/up layout API audit

Read-only snapshot: `7ae6244de4ad60d92b6341f8f04dc73d2b1b0549`; source hashes in `receipt.json`.

Users of `CuteDslConfig.prepare_weights` do **not** query a gate/up group size. `api.py:2584–2620` forwards canonical BF16 `[up, gate]` weights to `prepare_cute_dsl_weights`; `prepare.py:2615–2619` chooses and applies the grouping internally after moving weights to the requested device. Non-gated activations bypass the permutation. The selector returns 16 for SM100/SM103 and 64 for SM107 (`prepare.py:2495–2504`).

Neither `get_cutedsl_gate_up_group_size` nor a public `interleave_linear_and_gate` in `flashinfer/cute_dsl/utils.py` exists at this snapshot. A history search for the former in the named utility/preparation files returned no commits. The current private selector was introduced in `c9b840ba`; upstream base `002529e1` already had the generic private permutation with default 64.

Manual forward preparation still exposes two private operations:

- `benchmarks/bench_cute_dsl_moe_distributed.py:765–824`: already-quantized payload and logical scale rows, following a canonical gate/up-to-up/gate swap. It deliberately quantizes once across backends; replacing it with BF16 preparation would requantize.
- `benchmarks/bench_frost_low_latency_w4a16.py:251–277`: already-quantized payload and logical scales, then scale-layout conversion.
- `benchmarks/routines/moe.py:1300–1346`: BF16 row interleave before quantization, using a duplicated generic permutation.
- `tests/moe/utils.py:921–928`: test-data preparation before quantization, currently using its separate generic permutation plus the production architecture selector.

A minimal internal cleanup is `_interleave_cute_dsl_linear_and_gate(x, dim=-1)` beside the existing generic helper. It should obtain the grouping from `x.device` and delegate to `_interleave_linear_and_gate`. Use it in the public preparation implementation and the forward producers above. No new public API, layout, quantization recipe, or runtime kernel knob is needed. For prequantized tensors, payload and logical SF rows both use this helper before SF swizzling.

Keep the generic `_interleave_linear_and_gate(..., group_size=64)` and explicit-64 consumers unchanged: Cake uses it, and the Rubin localized test calls its separate generic helper with 64. Keep the private group selector available to the trace/reference **inverse** (`flashinfer/trace/templates/moe.py:5058–5068`) and internal W4A16 decode setup (`moe_w4a16.py:228–230`), which need the layout parameter rather than a forward permutation.

Test independence: the test-data path already shares the architecture selector. Moving only its forward permutation to the helper does not newly couple the architecture choice, but an independent permutation oracle should remain separate. A CPU equivalence proof for the original and encapsulated calls at group sizes 16/64, positive/negative dimensions and payload/SF shapes is enough for this source-only refactor; no GPU timing rerun is justified. The existing generic test helper still has an explicit Rubin caller and should not be removed or silently changed.

This audit changed no production source and ran no tests or GPU work.
