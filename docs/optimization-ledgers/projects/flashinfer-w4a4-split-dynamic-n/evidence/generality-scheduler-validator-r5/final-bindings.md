# Final scheduler evidence bindings

Use the same two-command factory/render flow. Add `"validation_kind": "generality-scheduler"` to bindings, with these exact current gate inputs:

- `generality_gate`: `evidence/generality-scheduler-tests-r5/validation.json`
- `generality_gate_raw`: `evidence/generality-scheduler-tests-r5/raw`
- `generality_gate_helpers`: the three files under `evidence/generality-scheduler-tests-r5/helpers` (`run_gate.py`, `probe_chain.py`, `selectors.json`)
- `scheduler_gate`: `evidence/generality-scheduler-replay-r5/validation.json`
- `scheduler_gate_raw`: `evidence/generality-scheduler-replay-r5/raw`
- `scheduler_gate_helpers`: the two files under `evidence/generality-scheduler-replay-r5/helpers` (`run_scheduler_gate.py`, `probe_scheduler_chain.py`)

Keep `final_source`, `promotion_source`, and `retained_binding` pointing to the eventual verified promotion. Gate source pins must equal all 87 retained file hashes; the original gate HEAD and patch must equal the verified promotion snapshot. Do not add `generality_fc1_scheduler` or the old numerical-control reuse fields to this contract. It validates both explicit scheduler modes and the legacy CLC default rather than a fixed public default.

Use the passive scheduler observer for final tables. Each recorded saved AUTO choice must match the final public core call, including K pair and scheduler bool. This verifies requested scheduler selection; the 72-replay gate separately verifies effective compiled CLC/static behavior. `tables[model][family]` may name six distinct raw directories and GPUs. Every family must complete all 13 tokens with its own same-GPU TRT comparisons. NV includes initial quantization; MX stays prequantized.

```sh
python3 scripts/pr7290_scope_cleanup/prepare_generality_manifest.py --bindings evidence/FINAL/bindings.json --output evidence/FINAL/manifest.json
python3 scripts/pr7290_scope_cleanup/trt_only_final_body.py --manifest evidence/FINAL/manifest.json --output evidence/FINAL/pr-body.md
```

This file is preparation only. No pending retention or table evidence is accepted or published.
