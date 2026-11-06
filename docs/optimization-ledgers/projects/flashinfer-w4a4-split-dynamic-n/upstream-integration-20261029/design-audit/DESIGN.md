# Gather design audit for PR #7290 integration

Source: `4376662a9ddefb1f62f0f81f4453964dc1f5a307`. Read-only audit; no GPU work or source edits. Whole-PR diff base: `002529e17b22567a071091053c6c4dc2a55e050e`, the merge base with current upstream head. The main PR checkout and fork experiment were source-identical when inspected.

## Suggested concise PR description

Introduce opt-in `swap_ab=True` for Blackwell (SM100/SM103) split CuTe DSL MoE: weights on MMA A, activations on B, dynamic MMA N, and FC1 activation gathering inside the GEMM. Legacy blockscaled kernels and up64/gate64 weights remain the default. W4A16 shares the new input-gathering design for both weight-layout options.

- **Input pipeline:** FC1 gathers original token rows with a dedicated four-warp group, avoiding a standalone activation permutation and its expanded input buffer. Swap-AB uses TMA gather4 for values and asynchronous word copies for scale factors; W4A16 uses TMA gather4 for BF16 values. Routing/sort remains separate. FC2 keeps regular TMA loads.
- **Warp specialization:** swap-AB FC1 has separate control, epilogue and gather warpgroups; W4A16 FC1 adds the gather group after its two dequantization groups. Register budgets and staging follow each role. FC1 startup publication lets FC2 prefetch weights/scales while activation payloads are still being produced; payload consumers keep the dependency wait.
- **Layout/API:** use the same `swap_ab` option when preparing weights and invoking the functional or wrapper API. Gated FC1 uses up16/gate16 weight-and-scale rows in swap-AB mode; W4A16 also accepts the original up64/gate64 layout through its in-kernel transpose. Existing non-swap blockscaled code remains available.
- **Reuse/testing:** share the per-token quantizer, combine path, routing and Blackwell utilities. Keep zero-tolerance swap-AB accuracy coverage and a standalone sanitizer driver. Performance tables use unfused swap-AB; the old MX baselines that require fused finalize are marked.

No need to publish the register-target table below in the PR body unless useful to reviewers.

## Concrete kernel roles

| Kernel | Threads/CTA | Warp groups and configured register targets |
|---|---:|---|
| Swap-AB FC1 | 384 | Warps0–3 control128; warps4–7 epilogue248; warps8–11 gather128 |
| Swap-AB FC2 | 256 | Warps0–3 control; warps4–7 epilogue; no added gather group |
| W4A16 FC1 | 640 | Warps0–3 epilogue144; warps4–7 control80; warps8–15 dequantization96; warps16–19 gather64 |
| W4A16 FC2 | 512 | Warps0–3 epilogue176; warps4–7 control80; warps8–15 dequantization128 |

These are source-configured role targets, not a claim that a newly compiled head was inspected. W4 FC1 supplies maxrregcount96; FC2 retains the128 launch default. Swap control roles are weight+weight-SF TMA warp0, activation/scale publication warp1, MMA warp2 and scheduler warp3. The activation control warp relays gathered SF-copy completion to the leader. Do not describe FC1 scale loads as TMA, and do not confuse retained completion publication with the rejected optional `self.gather_relay` experiment.

W4A16 FC1's original activation-TMA warp7 has no recurring mainloop work: after common startup and the control-group register decrease to80, `not self.gather_input` compiles out its loading path (`moe_w4a16_kernel.py:1716`). The routed-tile metadata consumer count excludes this warp (`:1255`). Its four BF16 gather issuers are warps16–19; unlike swap-AB, no activation-scale relay is needed. FC2 still uses warp7 for regular activation TMA. This is a source audit observation, not a new optimization or performance claim.

## Important boundaries

- No standalone *activation permutation* remains; routing metadata and per-token quantization still have separate kernels where required.
- W4A16 always uses activations on MMA B. Its `swap_ab` option changes weight-layout handling, not the tactics list; both layout choices now gather directly.
- Swap-AB autotuning keeps360 pre-filter tactics: five route sizes × three FC1 tiles × three FC2 tiles × four K-step pairs × one shared two-way CLC choice. It does not add independent FC1/FC2 CLC axes. W4A16 tactics are unchanged.
- Operand stage capacity and accumulator storage are computed from the compile-time geometry and memory capacity; no model-name dispatch is added.
- Quantized swap FC1 value/SF stores remain SIMT; FC2 uses the retained TMA/SIMT output pattern. A per-token FC1 result is quantized with the shared quantizer.
- `moe_swap_ab_prepare.py` and one-function `inline_ptx.py` have been removed. `tma_gather4` lives in Blackwell `utils.py`.
- `9c69b856` restores the linear FC1 absmax loop; `4376662a` restores ordinary operand `producer_tail` calls. Do not claim either reverted change as a retained optimization.
- `1e4b127a` retains the simpler one-PRMT W4 scale duplication, which is instruction-positive and register-neutral in its historical captures.
- Latest full benchmark source attribution and post-measurement changes must remain explicit; no current-head GPU rerun was done by this audit.

## Source locations

- `blackwell/moe_swap_ab_kernel.py:1593` roles/thread count; `:1901` capacity calculation; `:2710` gather barriers; `:2741` dependency waits; `:2766` role register targets; `:2999` SF publication; `:3403` four-warp gathered values/SF.
- `blackwell/moe_swap_ab.py:502` FC1 gather config; `:621` FC2 regular-TMA config; `:248` FC2 weight prefetch.
- `blackwell/moe_w4a16_kernel.py:352` roles/registers; `:1497` gathered-FC1 startup wait; `:2749` last-warpgroup gathering.
- `blackwell/moe_w4a16.py:492` FC1 gather config; `:522` FC2 regular-TMA config.
- `fused_moe.py:570` swap-vs-legacy dispatch; `:1115` public layout contract; `:1533` swap tuner versus unchanged W4 tactics.
- `prepare.py:2495` hidden layout selection; `:2523` public interleave helper; `:2555` prepare API.

LOC accounting is in `loc-breakdown.json` and `loc-table.md`. It includes all28 changed paths exactly once, including the removed old W4 prepare module, scripts/tests/docs; totals+9338/−1631.

## Correction: shared W4A16 dequantization reaches MegaMoE

The earlier follow-up claim that MegaMoE does not use the split W4A16 dequantizer was incorrect: searching only direct helper imports misses inheritance. `moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:55` defines `_MegaMixedInput(Sm100W4A16GroupedGemmKernel)`; FC1/FC2 invoke inherited `_transform_tile` at1596/1605; `blackwell/moe_w4a16_kernel.py:799` calls `decode_nvfp4_fragment_to_bf16`. Therefore the shared scale-duplication change also affects MegaMoE through its inherited transform path. No separate source change is required for that effect.
