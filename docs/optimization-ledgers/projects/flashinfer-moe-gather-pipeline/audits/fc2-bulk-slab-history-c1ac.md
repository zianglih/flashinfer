# FC2 wider-slab history and current boundary

**Conclusion:** 128-token output slabs are not an untried mechanism. A source-qualified 128-token/single-stage trial was explicitly rejected. The current swizzled 2D-TMA path differs, so that is not a current-source performance result; nevertheless no simple, generally applicable widening is justified without a new profile signal. No source changes or GPU work were performed.

## Exact prior trial

Old project `../flashinfer-w4a4-split-dynamic-n/scripts/bulk_r2s_experiment/README.md` and `build_variant.py:93–113` replace the preferred 64-token/two-stage scratch with 128-token/one-stage scratch at equal 34,816-byte capacity (136 BF16 elements per padded row). Frozen source hashes match `source-sha256.json`: `stmatrix128_core.py` = `1237e4b2e9cb4220b5fd178ff000de7f720aa497484f6874f9413d03f6dcf999`, utils = `d5757c9b3fa5c710c9f6677934450e1e9b990189d4d459e22106f1574b36b1cc`.

The raw `evidence/bulk-r2s-7829fc00/raw/logs/bulk-r2s/native-nvfp4-slab128-v2.json` (SHA256 `52d6bcf016173c7e4ff1b2bd921a11c4675b809045ea2fbd359924f7b46492c9`) records native NVFP4 FC2 M256/N256/two-CTA, T16384, B200, CUDA13.2/CuTe4.7.1, commit7829fc00, 10 warmups/100 cold-L2 graph/CUPTI samples per arm:

| Variant | Median µs | Registers | Stack bytes | SASS LDL/STL sites |
|---|---:|---:|---:|---:|
| Scalar control | 181.457 | 126 | 0 | 0/0 |
| Padded STSM 64×2 | 177.7605 | 126 | 0 | 0/0 |
| Padded STSM 128×1 | 191.568 | 168 | 24 | 4/4 |

The wider slab increased latency 7.767% versus 64×2. The resource columns come from the archived `native-resources.json`; its `LOCAL:0` field does **not** erase the explicit stack/spill instructions. Candidate cubin SHA256 independently matches `433b5fb7b87c116b902917e6955cccf0adbcc557d7a3a3ca18800fd6138944ed`. Its saved PTX contains four `tcgen05.ld.sync.aligned.16x256b.x16.b32` sites. `stmatrix128-tail.log` preserves 24 passing six-format/per-token/tail checks. This was a fixed isolated-FC2 diagnostic with padded SMEM and per-row linear bulk scatter, not current no-permutation 2D TMA or an E2E retention campaign.

Slab/operand-depth balance also has history: `scripts/native_fc2_experiment/README.md:65` records a larger output buffer lowering operand depth 4→3 and losing; later `scripts/stage_capacity_experiment/AUDIT.md` explicitly retained capacity-derived sizing, including 12 policies trading 32×1/four operand stages for 64×2/three stages. The later paired retention is broader policy evidence, not an isolated claim that every shallower operand/deeper output trade wins.

## Current c1ac policy and constraints

- `moe_swap_ab_kernel.py:1660–1673,1730–1778,1920–1978`: only unfused scatter BF16/FP16 output without generated SF and route N≥128 enables bulk storage. Prefer `(64,2)` =32,768 bytes, then `(32,1)` =8,192 bytes; otherwise use the 512-byte direct-path scratch. Automatic sizing reserves this output working set before maximizing operand depth, with exact barrier/alignment overhead. Explicit depth recomputes output fit afterward. Changing that preference can also affect the existing K-step selector, so it is not merely an epilogue instruction change.
- `_run_bulk:1149–1150,1191–1200`: current code admits only32/64. The underlying `Ld16x256b` supports x16 for a128-token slab (vendored CuTe `tcgen05/copy.py:272–298` rejects only x64/x128); the old actual x16 PTX confirms this is not a TMEM-instruction legality limit. But FP32 `values` grows32→64 registers per half, and BF16/FP16 `packed` grows64→128 elements (32→64 register words). These are fragment extents, not a prediction of final register allocation; the prior spill shows the risk.
- `_run_bulk:1174–1180,1202–1208,1296–1314` and kernel setup `:2340–2359`: the overlapping accumulator path rotates and releases an exact64-column shared interval. With tokens128, `64 // tokens` becomes0 and `(step+1)*tokens == 64` is never true. Merely admitting128 or changing the scratch tuple therefore loses the required overlap release. A valid general version must explicitly change/reprove that ownership and release timing; it is not a drop-in constant substitution.
- A128×1 buffer retains32KiB but removes the second output stage;128×2 costs64KiB and may reduce operand depth or alter automatic K selection. Wider full-slab eligibility also sends live tails below128 through the existing32-token direct subslabs. Stmatrix sites and conversion work per output byte do not disappear; potential savings are the number of publication/TMA groups, balanced against larger live fragments and lost staging overlap.

Keep this as **historically rejected, current-path unmeasured**, not an open low-cost optimization awaiting a routine prototype. A fresh profile would need to isolate output publication/issue pressure strongly enough to justify revisiting the different TMA path and its ownership contract. No shape-specific gate or new tuning axis is proposed.
