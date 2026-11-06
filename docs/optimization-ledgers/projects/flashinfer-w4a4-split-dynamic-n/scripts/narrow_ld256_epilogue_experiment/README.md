# Direct Ld16x256 N16 FP4 epilogue (not retained)

The final bounded narrow-epilogue branch is numerically exact in its tested scope but does not improve native decode latency. The independent source clone is `flashinfer-narrow-ld256-review`, base `98fd3566b5f945c100f48cddacf25deb2432cbc2`, with only unstaged `flashinfer/fused_moe/cute_dsl/blackwell/utils.py`. Production is unchanged.

## Mechanism and scope

- Load both up16/gate16 halves using `Ld16x256bOp(Repetition.x2)`, preserving our weight contract and physicalN32 allocation. Activation retains the original packed FP32 arithmetic and ordering.
- Raw lane/register ownership is token `2*(lane&3)+(i&1)+8*(i//4)`, channel `lane//4+8*((i//2)%2)`. Local two-channel maxima plus XOR4/8/16 span exactly16 channels of the same token. SF32 joins the adjacent warp's same-token maximum through existing shared scratch.
- Convert the native eight-value fragment toFP4, then swap the three packed nibble-index bits with channel lane bits using three Uint32 shuffle/bitfield operations. Each lane writes one32-bit word containing eight contiguous channels of one token. No FP32 matrix transpose and no TMEM scratch roundtrips.
- Dispatch is limited to gated N16 with generated FP4 output. Other output types use the original epilogue; per-token BF16 remains unchanged. This was an initial FP4 performance gate, not a retained format-specific production policy.
- `prove_mapping.py` exhaustively checks all256 lane/register coordinates, scale groups and packed-integer permutation. Seven NVFP4 output/SF byte checks passed at valid1/7/8/15/16/17/31, K64/384, persistent channel/route tiles and per-token BF16 fallback. The test poisons prepared padding; this is numerical isolation evidence, not initcheck or an independent reference.

## Native result

Fixed native DeepSeek NVFP4 FC1, N16/M128/one-CTA, H7168/I2048/top-k8/simulated EP8 (32 local experts). Preparation is included. Each arm uses10 warmups and100 cold-L2 CUDA-graph CUPTI samples. Full output and SF byte equality are checked before and after every arm; source and cache ownership are separate. No full-chain or primary AUTO timing was rerun.

|Tokens|ABA control/candidate/control(us)|BAB candidate/control/candidate(us)|Control/candidate speedup|
|---:|---|---|---:|
|32|65.4720/66.0160/66.1125|65.6320/65.8560/66.2720|0.997577x|

Compile-only cubin/PTX/SASS receipts show64→50 registers, no local memory, and unchanged197504B SMEM,288 threads, four operand stages, one active CTA/SM. SASS has two nativeLDTM operations and noTMEM stores; the packed permutation has three SHFL instructions, while four per-token scale reductions add12 more. Register reduction did not change occupancy. The gate did not justify broadening tests or integrating the branch.

## Reproduction

```bash
source scripts/recovery442/env_candidate.sh
export CUDA_VISIBLE_DEVICES=4 CUTE_DSL_CACHE_DIR=$PWD/cache/narrow-ld256-review/cute_dsl
D=scripts/narrow_ld256_epilogue_experiment
.venv/bin/python "$D/probe_exact_nv.py" --control profile-98fd --candidate narrow-ld256-review --output "$D/results/exact-nv-r1.json"
for order in control,narrow,control narrow,control,narrow; do
  .venv/bin/python "$D/probe_native.py" --control profile-98fd --candidate narrow-ld256-review --tokens 32 --tactic '[16,[[128,16],[1,1],false],[[128,16],[1,1],false]]' --variants "$order" --output "$D/results/native-T32-$order.json"
done
```

Outputs are immutable; use new filenames for reproduction. `manifest.json`, `selected-utils.py`, `source.patch`, `raw.tar.gz` and `archive-receipt.json` preserve source and result identity. `instruction-counts.json` is a local derived SASS-PC count, not an execution count. Cubins were regenerated from identical source and specialization with keep-artifact flags after timing.

Source SHA256 `b23062aa88e01c01017156d5e29fc8cf2531c62eeae831e6da23fb9f883b4257`. Raw archive SHA256 `cecd100d92b44f123c01e74ebda2501a27eba5d99e860964c5a6279f37eb75e3`. All six native arms/600 samples verified.
