# W4A16 and swap-AB output work partition

The experiment tests **one epilogue warpgroup loading a native TMEM fragment once, then routing that converted fragment to shared/TMA for complete token subtiles or predicated direct global stores for tails**. Physical warp numbers need not match. W4A16's weight-dequantization warps are unrelated to this output ownership.

**Final result:** the native ownership candidate regresses in the completed 13-cell screen. Preserve this document as the source audit, not a retention recommendation. See [RESULT.md](RESULT.md) for measured comparisons, final source hashes and validation boundaries. The existing transposing SIMT tail remains the better measured partition.

## Checked sources

- Padded-R2 W4 kernel: `flashinfer-padded-output-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`; SHA256 `8acbdcf47b61cbe6256ff21023a4d15e78b0cf6c1b8ffa0d6f9469afb806af17`.
- Native swap-AB candidate at the native01 audit: `flashinfer-swap-ab-fc2-native-output-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`; formatted SHA256 `7137e5c8ebab52e829146b308f1ccc86926acd97dd27eb73157eaef38497030e`. Frozen `fc2-native-01` SHA256 is `c42142206b304cbcb0579399aad867caab08cc4100a83b221c08425d6f81e9d1`; `fc2-native-01/format-equivalence.json` confirms the two ASTs are equal.
- The actual remote runtime is **nvidia-cutlass-dsl 4.8.0**, inspected using the deployed candidate's Python on C3. Full function excerpts, line numbers and hashes are retained in `runtime-partition-sources.json`.
  - `/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/blackwell_helpers.py`
    SHA256 `c58c3d258de6c7338bcbc2a7f448501909e54760a6686b63a04e9428752c2225`.
  - `/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/mixed_input_helpers.py`
    SHA256 `b83ea13ff6afe0e261193f1088cfa837501f233ee8fcd293ed737a6f667bf7ee`.

## Ownership and transfer width

W4 sets epilogue warps0–3 and MMA warp4 (`moe_w4a16_kernel.py:335–336`), enters its epilogue at2011, and supplies `epi_tidx=tidx` to the CUTLASS partition at2020. Swap-AB assigns weight/activation/MMA/scheduler warps0/1/2/3 (`moe_swap_ab_kernel.py:1566–1570`) and uses the other four warps for epilogue, subtracting128 from the thread index at its calls. These both provide a local 128-thread epilogue warpgroup. Reordering all warp roles would add no output-layout benefit.

In the **runtime** `blackwell_helpers.py:504–514`, a 128-channel CTA selects warp shape(4,1), including a two-CTA MMA with128 channels per CTA. For FP32 accumulators and BF16/FP16 M-major output, lines538–549 select **Ld16x256b**. The repetition count covers the selected token subtile. The runtime `mixed_input_helpers.py:398–430` builds the TMEM tiled copy, partitions its source and matching global destination with the same per-thread slice, and allocates the register accumulator from that partition. Its direct-store helper at311–323 reuses the slice's `partition_D` and a `CopyUniversalOp`; it performs no warp shuffle or TMEM transpose to change ownership. The helper intentionally leaves the final copy width to lowering.

W4's full-subtile branch (`moe_w4a16_kernel.py:2539–2569`) converts the fragment, stages it, and issues TMA. Its tail branch at2570–2595 predicates that same fragment and copies directly to the partitioned global tensor. The native swap candidate follows this principle: lines1108–1161 load/scale/convert **Ld16x256b** fragments; full slabs use `stmatrix.trans` into the TMA slab at1162–1197, while partial slabs at1198–1218 directly store the already converted fragment. It avoids the separate `_run_token_group` fallback's TMEM transpose.

For the native swap fragment, one lane owns channel offsets `lane//4 + {{0,8,16,24}}`; neighboring register pairs advance the **token** coordinate. Global output is token-major with channels contiguous. Therefore the paired BF16 values are strided globally and cannot be reinterpreted as one contiguous32-bit store. Predicated16-bit element stores are a natural consequence of this ownership, not proof that the wrong TMEM opcode was chosen. W4's source helper also makes no promise of wider stores for this mapping; exact emitted instruction widths require PTX/SASS inspection.

Wider tail stores would need inter-lane shuffle/repacking, shared staging and a SIMT readback, or the prior TMEM transpose into lane=token/register=channel order. Each adds work to infrequent partial slabs. Keep the native direct store as the simple first candidate and retain a more elaborate redistribution only with measured benefit. Full slabs still get wide TMA transfers.

## General small-N storage policy

To extend the native path to N16/N32/N64 without reserving unused shared memory, keep the existing capacity-ranked candidates `(requested_tokens, requested_stages) = (64,2), (32,1)`, but compute **before fitting storage**:

```python
tokens = min(requested_tokens, route_tile)
stages = min(requested_stages, ceil_div(route_tile, tokens))
bytes_needed = tokens * 128 * stages * output_bits // 8
```

N16/N32/N64 then reserve one useful stage; N128/N256 keep their current preference. Keep the existing capacity fallback and derive descriptor shape, SMEM stage stride, loop count and wait depth from the selected values. Merely clamping `bulk_tokens` after storage selection would leave excess reservation and could unnecessarily reduce operand pipeline depth.

N16 is structurally compatible with the native mapping: `Ld16x256b` repetition2 gives8 FP32 values per half, conversion produces16 half values (8 words), and two `stmatrix.x4` iterations consume those8 words. Its only token-scale group is0; a 32-column physical TMEM allocation is still used. Runtime validation must cover it before retention. This planner change is a separate causal experiment: fc2-01/native01 retain the inherited route>=128 eligibility; the later native02 arm extends the native half-format path to N16/N32/N64 with compile-time storage fitting.

## FC1 payload arm

The FC1 arm uses the same converted fragment for its full-subtile shared payload and direct tail stores. Output payload slabs are `min(route_tile,32)` tokens by 64 gated or 128 nongated output channels. Packed FP4 has a Uint8 TMA descriptor and byte-scaled channel coordinates; FP8/BF16/FP16/FP32 use their ordinary element coordinates. The 512-byte SF32 reduction scratch remains disjoint from the payload buffer. Scale stores, activation math and quantization math are unchanged. The public per-token NVFP4 path emits an ordinary FC1 intermediate and then invokes the shared standalone quantizer; this arm does not duplicate that quantizer.

`fc1-01` failed compilation because reassignment of `channel` inside the elected-thread TMA region escaped its MLIR dominance scope. Line-info identified `channel //= 2` at kernel line 941. `fc1-02` computes a distinct `payload_channel` before the dynamic/elected regions, with no arithmetic or ownership change. Scoped pre-commit, AST parsing and diff checks pass. Frozen source SHA256 is `a813327258e82661070dc6ca9efff6e366282969d1459131a518907ba23723dc`; deployment verified all 348 source files.

The `fc1-02` N16/N128 NVFP4 gate passes all 128 paired exact graph replays across static/CLC and PDL off/on, with no valid-output or FC1-padding discrepancy. N128 retains the inherited FC2 owned-padding diagnostic, recorded independently of valid-output equality. The final FC1 gate also covers FP8, per-token BF16 and a channel-tail case, for 384 paired exact graph replays total. FP32 FC1 is source-level support only: the public harness does not expose an FP32 intermediate, and no separate harness was added. The completed performance results and correctness boundaries are in [RESULT.md](RESULT.md) and [VALIDATION.md](VALIDATION.md).

## Deliberate output-format boundary

The native02 FC2 path supports the existing BF16/FP16 bulk output formats, which cover every benchmark input mode (NVFP4 per-tensor/per-token, MXFP8 and MXFP4x8). Its `stmatrix.b16` staging is intrinsically a half-format path. FP32 and fused-finalize outputs retain their existing SIMT implementation; this experiment does not claim native hybrid FC2 coverage for them. The FC1 payload arm can cover FP32 using generic shared stores and a typed TMA descriptor, without modifying quantization arithmetic. Input quantization modes and final output element types are separate scopes.
