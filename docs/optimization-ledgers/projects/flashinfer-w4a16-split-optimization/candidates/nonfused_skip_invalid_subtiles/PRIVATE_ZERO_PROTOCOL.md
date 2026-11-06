# Private zero-route progress check (held)

Helper: [check_private_zero.py](check_private_zero.py), SHA256 `a4d8b3a239492609e5fb7aa48773077c9b316bbfaed6d41a7b3cbd14283aef18`. Local syntax/Ruff checks passed; no GPU execution has occurred. This helper is independent of006 and is intended for a later explicitly released007 validation.

The helper imports the real project checkout from `--repo` and calls the existing `TestCuteDslMoeW4A16.test_route_tile_boundary_accuracy` method. It uses its original tail-one geometry, input construction, forced catalog tactics, reference and tolerances. If the enhanced half-tail parameter is present, it passes False; no upstream test edits or replacement oracle are needed.

| Actual GEMM2 | Companion GEMM1 | Tokens | Top-k | PDL |
|---|---|---:|---:|---|
| M128/N64/K256, cluster2×1 | M256/N64/K256, cluster2×1 | 65 | 2 | False, True |
| M256/N128/K256, cluster2×1 | M256/N128/K256, cluster2×1 | 129 | 2 | False, True |

For each of the four mode cases, a public-launch wrapper only selects the requested PDL setting. A private-call wrapper intercepts only GEMM2 (`activation_type is None` and `use_fused_finalize=False`). Before the legitimate call, it invokes the saved actual `_run_grouped_gemm` with:

- identical weights, scales, alpha, activations, tactic, dimensions and other scalar arguments;
- a fresh output filled with exactly representable BF16 sentinel17;
- fresh metadata arrays containing expert0, limit0 and exactly one active route tile.

The physical tile is admitted despite having no valid routes. The helper synchronizes immediately after that private call, requires `torch.equal` against the saved sentinel and maximum absolute change0, then invokes the original legitimate private call with its unchanged original kwargs. The existing test reference checks that legitimate output. Expected counts are four zero probes and four oracle passes. This checks PDL-enabled execution, not actual overlap or a performance benefit.

Execution must have an outer process timeout: a missing ACC release could hang `torch.cuda.synchronize`. The helper writes `complete:false` and the active case before launching work, preserves partial/error results, and writes `complete:true` only after all four cases and unchanged source-file hashes. A timeout or missing final marker is a failure, not completion.

Example for the sole executor after source release (paths relative to project root):

```bash
timeout 300s .venv/bin/python \
  candidates/nonfused_skip_invalid_subtiles/check_private_zero.py \
  --repo flashinfer \
  --output logs/candidate007-private-zero.json \
  > logs/candidate007-private-zero.log 2>&1
```

Require process exit0 and `PRIVATE_ZERO_COMPLETE cases=4 probes=4 max_abs=0`, together with result `complete:true`, four `oracle_pass:true`, one `zero_probe_count` per case, and all sentinel errors0. Normal executor source/environment/idle closure still applies. This command is documentation, not an authorization to launch. No existing benchmark, native capture or numerical suite is rerun by this preparation.
