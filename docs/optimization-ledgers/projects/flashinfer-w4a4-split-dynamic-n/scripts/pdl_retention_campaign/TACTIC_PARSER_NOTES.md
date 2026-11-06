# AUTO cache parser contract

Frozen campaign: control `aab93f854054de834447bdd8985b8bbd653fb3c8`; candidate `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e`. The nine source files below match all 14 observer receipts; the MX assembly matches all eight MX receipts. No GPU or source modification.

- `flashinfer/autotuner/autotuner.py:1352–1389` defines the persisted key `(op, runner class, full bucketed input shapes, extras)`. Runner hash is omitted from the serialized key. Lines 4132–4161 map linked dynamic dimensions and construct the lookup key. Lines 2663–2669 perform the measurement-time lookup.
- `flashinfer/fused_moe/cute_dsl/tuner.py:535–546` links dimensions 0, 1, 2, 3, 11 and uses the uncapped hybrid mapper. `flashinfer/fused_moe/utils.py:309–324` defines that mapper. Every measured CuTe token is an exact hybrid boundary, including 16384. `tuner.py:676–694` defines NV extras; lines 80–128 define the 13-tactic menu.
- `scripts/unfused-blockscaled/bench_cute_dsl_mxfp8.py:123–164` borrows the same dynamic shape policy and defines MX extras. Lines 337–357 supply the exact tensor list and choose_one operation name; lines 367–378 tune then measure outside the tuning context.
- `benchmarks/bench_moe_deepseek.py:954–993` calls native TRT without overriding the tuning maximum. `flashinfer/fused_moe/core.py:6571` defaults it to 8192; `shared/tuning.py:302–308` selects the capped mapper; `utils.py:284–287` caps every x>=8192. Therefore measured TRT T16384 selects the 8192 profile.
- `flashinfer/fused_moe/shared/inputs.py:31–55` supplies TRT tensor order; autotuner lines 3467–3472 serialize non-tensor inputs as `(0,)`. `backends/trtllm/sm100_runner.py:111–138` defines the remaining extras. `csrc/trtllm_fused_moe_kernel_launcher.cu:1116–1136` identifies TRT tactic as `(tile_N, config)`. The config ID is not an FC2 tile.
- `scripts/run_split_benchmark.py:163–189`, `scripts/unfused-blockscaled/run_split_benchmark.py:251`, and `scripts/trtllm_nvfp4_reference/run_trtllm_benchmark.py:167–193` save the snapshot after each measured token. The audit uses that exact row-to-snapshot link and verifies its SHA256.
- Autotuner lines 4309–4322 save the selected tactic and policy; lines 4420–4435 write metadata and generation digest. No candidate timing or winning margin is serialized. All cache generations were independently recomputed.

Parsing uses AST literal evaluation with one explicitly allowed attribute, `torch.bfloat16`, converted to a literal string. It never executes cache keys. Full shape/extras equality is required for every record; selection then uses the exact mapped bucket. Record counts, highest bucket and dictionary order never select a winner.

All 182 measured snapshots pass. The first-screen 91 selections/digests agree with the corresponding full-archive records. A separate peer independently reproduced all 26 TRT selections and their cache/result/archive hashes. T1 and T2 each contain 21 synthetic profile buckets already in their first snapshot; only the exact lookup key determines the measured selection.

Observed 16K boundaries:

| Format | C1 / A1 / A2 / C2 latency (us) | Tactics |
|---|---|---|
| MXFP8 | 791.314 / 784.067 / 830.195 / 793.5695 | All four: N256, FC1 M256/2CTA, FC2 M256/2CTA |
| Mixed W4A8 | 806.034 / 779.891 / 758.834 / 803.9695 | Both C: N128, FC1 logical M512/2CTA, FC2 M256/2CTA; both A: N256, M256/2CTA in both phases |

The MXFP8 A2 slowdown has no saved tactic switch. Mixed source comparisons include a stable source-dependent tactic switch, while mixed A1-to-A2 changes occur with the same tactic. Neither observation establishes the cause of the latency change. These are source-reconstructed cached selections, not an independent executed-cubin trace.

## Source SHA256

| Path relative to source repo | SHA256 |
|---|---|
| `flashinfer/autotuner/autotuner.py` | `0db42ad90d1a3fec6f81509a2c520c1892cea0a433f5dbd7f43468a2a10243ca` |
| `flashinfer/fused_moe/utils.py` | `6dc4c558f6fbf9284c190f22cc403fb850d1a4325f7b1fa6fc362a9c91b419a9` |
| `flashinfer/fused_moe/cute_dsl/tuner.py` | `8f165cea7243c2a98ffbc2c7b3d9c9a5d5e2e689e6e8afe99237b9c23120bc2b` |
| `flashinfer/fused_moe/shared/tuning.py` | `aefab172c34bb0e67a6014b9292d5b255e99700a4767523d01bf6199fada023f` |
| `flashinfer/fused_moe/shared/inputs.py` | `f9bbc0be9df8ec492c3c128c7d62fd93aa4b12fca8f672774903a2b1e2d4e61c` |
| `flashinfer/fused_moe/backends/trtllm/sm100_runner.py` | `00efb12f0b2d7fc2699f4d05544152feb64efcccef44b7450e171ab1cdad8483` |
| `flashinfer/fused_moe/core.py` | `58ac4fb451361d79e395cd241dfaae0e2fc8d61f859e221fe571aff4d65c062a` |
| `benchmarks/bench_moe_deepseek.py` | `b065e2e52b1dd8704b152e9c7e3e477f2a5c4d1e0e4e88b863bf92af7ea8442f` |
| `csrc/trtllm_fused_moe_kernel_launcher.cu` | `f7b9b43cc35063c5968d2ec6db408eba1199340210ce43b9c5d4705379922a9b` |

MX assembly `scripts/unfused-blockscaled/bench_cute_dsl_mxfp8.py`: `632e8587180b88c2fd867d42a03899c5072b04cdcea0fabc58badfcb883b9b23`

Audit command:

```sh
python3 scripts/pdl_retention_campaign/audit_tactics.py \
  --config scripts/pdl_retention_campaign/campaign.json \
  --results-root evidence/pdl-retention-8c1a/full/raw/results/pdl-behavior-retention \
  --output <new-output-path>.json
```

The helper creates the JSON and matching Markdown report using exclusive creation. Existing frozen reports are not overwritten.
