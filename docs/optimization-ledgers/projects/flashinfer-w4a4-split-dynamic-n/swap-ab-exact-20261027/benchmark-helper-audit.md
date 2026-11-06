# Missing-table benchmark helper audit

The fresh campaign uses the existing public `bench_moe_deepseek.py` functional
API. The old arm uses the pre-PR source and legacy layout; the new arm requests
`--swap-ab`. W4A16 retains native 23-tactic admission on both sides. The
`--w4a16-only` observer uses the benchmark's backend selector and does not
replace tactic selection.

- Separate fresh native AUTO caches per source arm; measurement passes freeze
  their hashes and reject new tactic admission.
- Old/new/new/old paired passes for W4A16, including the combined Nemotron NVFP4
  campaign. `cutedsl` includes both W4A4 and W4A16, so current Nemotron NVFP4 also
  supplies its W4A16 pair. Nemotron MX uses two current matched-backend passes.
- Warmup 10, 100 public raw samples, CUDA graphs, cold L2 and CUPTI are asserted.
  The observer preserves native medians and captures routing identity only at
  the existing untimed histogram call.
- NVFP4 initial activation quantization is included for quantized-input arms;
  W4A16 consumes BF16 directly. MXFP input quantization remains outside timing,
  matching retained evidence.
- Current non-W4A16 swap-AB tactics must use
  `extract_swap_ab_tactic_params`; the legacy parser accepts a different tuple
  format and has no CLC fields. The local observer was corrected to import and
  use the dedicated parser only when `--swap-ab` is selected. This changes
  metadata observation only, not selection or measured code.

Static Python compilation of both helper modules passes. Runtime provenance and
completed measurements must come from the campaign receipts; this audit does
not imply a benchmark run has completed.
