# Benchmark extension ready for review

Only `benchmarks/bench_moe_deepseek.py` changes (+81/−43). No unrelated source changes or final-review findings.

- Add `nemo3-ultra` EP8 with routed latent width2048, intermediate5120,512experts,top22, normalized sigmoid routing×5 and non-gated ReLU2; model width8192 and excluded outer layers are not charged to the expert benchmark.
- Derive FC1 rows/FLOPs from gated versus non-gated activation and pass the explicit activation through existing public preparation/dispatch.
- Replace manual CuTe NV weight packing with source-native public preparation, preserving old/current gated-layout ownership. Remove the obsolete benchmark MX fused-mode restriction so the existing functional API can select source-supported finalization.
- Preserve existing V3/V41/K3 inputs/routes/table bytes, backend order, activation recipes, native AUTO/timer and `include_activation_quant=False` default.

Validation: scoped pre-commit;65CPU contract checks plus8parser checks; prior8non-gated/4gated CPU packing fixtures;6source-bound GPU weight-payload comparisons (9.57GB) byte-exact. These packing checks do not substitute for the parent-owned complete native model campaign.

Frozen source `cf5cd581…`; patch `583066fe…`. Exact receipts and fresh check logs are bound by `final-review.json`. The channel-tiling performance experiment is separate and rejected; it is not part of this benchmark patch.
