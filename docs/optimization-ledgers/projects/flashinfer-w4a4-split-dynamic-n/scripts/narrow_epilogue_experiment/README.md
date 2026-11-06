# Narrow N16 gated FC1 epilogue: shuffle variant (not retained)

Independent actual source clone `flashinfer-narrow-epilogue-review`, base `98fd3566b5f945c100f48cddacf25deb2432cbc2`; unstaged `blackwell/utils.py` only. Regular TMA, physical N32, MMA descriptor, up16/gate16 weights, fused activation, quantization, and per-token arithmetic remain unchanged. The prototype loads16 tokens, then uses two FP32 register/lane bit swaps into four-channel groups. This replaces TMEM transpose with16 shuffle instructions.

18 focused cases passed complete output and SF byte comparisons against98fd, including all six formats, SF16/SF32, K64/128/384, valid1/9/31, persistent channel/route tiles, quantized output and per-token BF16. Prepared private padding was poisoned, including FP8 NaN payload. This is differential numerical evidence, not initcheck or an independent reference.

Native NVFP4 FC1 timings include preparation, fixed N16/M128/one-CTA, DeepSeek H7168/I2048/top-k8/simulated EP8 (32 local experts). Each arm uses10 warmups and100 cold-L2 CUDA-graph CUPTI samples; both source variants compare full output and SF allocations before and after timing. No full-chain or primary AUTO timing was rerun.

| Tokens | ABA control/narrow/control (us) | BAB narrow/control/narrow (us) | Control/narrow geomean speedup |
|---:|---|---|---:|
|32|65.5360/65.8240/66.1280|65.5360/66.0800/66.2085|1.000889x|
|128|89.4250/89.8885/90.2880|89.4410/89.7600/90.1760|0.999877x|

The measured result is neutral. Compile-only code/resource receipts show64→42 registers, no local memory, and unchanged197504-byte dynamic SMEM,288 threads, four operand stages and one active CTA/SM. Lower register use did not change residency. Cubin/PTX/SASS are archived; regenerated from the identical source/specialization with keep-artifact flags, not used as new timing samples.

## Reproduction

```bash
source scripts/recovery442/env_candidate.sh
export CUDA_VISIBLE_DEVICES=4 CUTE_DSL_CACHE_DIR=$PWD/cache/narrow-epilogue-review/cute_dsl
D=scripts/narrow_epilogue_experiment
.venv/bin/python "$D/probe_exact.py" --control profile-98fd --candidate narrow-epilogue-review --output "$D/results/exact-r1.json"
for tokens in 32 128; do
  for order in control,narrow,control narrow,control,narrow; do
    .venv/bin/python "$D/probe_native.py" --control profile-98fd --candidate narrow-epilogue-review --tokens "$tokens" --tactic '[16,[[128,16],[1,1],false],[[128,16],[1,1],false]]' --variants "$order" --output "$D/results/native-T$tokens-$order.json"
  done
done
```

Outputs are immutable; reproduction requires new filenames. `manifest.json`, `selected-utils.py`, `source.patch`, `raw.tar.gz` and `archive-receipt.json` preserve source identity and every result. The initial harness SF-shape refusal and first FP4 register-alignment compile failure are archived separately; neither produced performance samples. The legal conversion packs eight values and stores only the low16bits for four outputs.

Raw archive SHA256 `dddbaeaba20660d4a1a9d46b206649959cd51544d325db7a15e8991675e20cc1`. Selected source SHA256 `905b7c9d87214ee78df619afea8fd3729b223b5eac5e5dc385c2bd3f54010406`.
