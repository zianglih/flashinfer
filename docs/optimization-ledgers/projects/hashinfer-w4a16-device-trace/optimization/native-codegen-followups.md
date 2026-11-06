# Native T4, N128, x32 and count-publication audit

This extends `native-codegen-analysis.md` with matched uninstrumented rank0 exports. The original five-arm evidence was preserved. `analyze_native_codegen.py` now selects the timed artifact by its recorded ABI instead of its ordinal, derives the FC1 K count from hidden size, and derives TMEM/decoded-barrier offsets from stage metadata. A CPU rerun matched every field of the original five-arm result after removing the newly added artifact-index/export-label metadata.

## T4 and N128 store16 qualification

The native benchmark explicitly converts routed IDs to contiguous Int32 (`benchmarks/bench_cute_dsl_moe_distributed.py:141`), and its hidden input is contiguous BF16. Selecting these fields in each manifest identifies artifact00 uniquely; artifact03 is the Int64-ID coverage variant and is not the timed input.

**The native T4 benchmark and uniform trace target differ in hidden size as well as token capacity.** Native T4 is H7168, global4/EP4 (one token/rank), with28 FC1 K-steps. Uniform256 is H6144, global1024/EP4, with24 FC1 K-steps. FC2 has eight K-steps in both. Comparison of store widths is matched within each fixture; T4 should not be presented as just a sparse-token version of the H6144 trace fixture.

| Export pair | Tactic / stages raw,decoded | Whole instructions before→after | FC1 body | FC2 body | REG / STACK / LDL / STL |
|---|---|---:|---:|---:|---|
| native T4 | N64/G512, 5,3 | 5136→5120 | 233→225 | 239→231 | 96 / 0 / 0 / 0 both |
| uniform256 N128 | N128/G512, 4,2 | 5624→5608 | 233→225 | 239→231 | 96 / 0 / 0 / 0 both |

In **both** pairs and **both** phases, the complete repeated-body delta is exactly `STTM.x8:-8`, `STTM.x16:+4`, `R2UR:-4`. Conversion, BF16 scale arithmetic, shared loads, PRMT, branches, waits, fence, and arrival counts are otherwise unchanged. No additional packing or stack/local-memory cost appears. Store16's native instruction reduction therefore generalizes to these two specializations.

This does not establish the cause of the initially reported native T4 slowdown. There is no T4-specific spill/packing regression in the matched generated code. Wider stores change issue granularity and schedule even with fewer instructions; their runtime consequence cannot be inferred from static counts. The serialized T4 ABBA result remains the appropriate performance evidence.

Artifacts with exact source/PTX/cubin/SASS/manifest hashes and phase extracts:

- `native-codegen-t4-analysis/comparison.json`
- `native-codegen-n128-analysis/comparison.json`

```bash
python3 optimization/analyze_native_codegen.py \
  --arms control-native-t4-codegen store16-native-t4-codegen \
  --per-rank-tokens 1 --output optimization/native-codegen-t4-analysis
python3 optimization/analyze_native_codegen.py \
  --arms control-uniform-n128-codegen store16-uniform-n128-codegen \
  --tile-n 128 --output optimization/native-codegen-n128-analysis
```

## Store32: fewer repeated decoder instructions, more code elsewhere

The initial whole-kernel count is **5112→5152** versus store16, and MOV-family count426→461. It would be incorrect to conclude this is40 extra repeated decoder/packing instructions. Exact phase extraction gives:

| Per-K body | store16 | store32 | Complete delta versus store16 |
|---|---:|---:|---|
| FC1 | 225 | 223 | STTM.x16 -4, STTM.x32 +2, R2UR -2, BRA +1, MOV +1 |
| FC2 | 231 | 226 | STTM.x16 -4, STTM.x32 +2, R2UR -2, IADD3 -1, comparison -1, VIADD +1 |

All64 decoded payload registers per thread are still written in each K-step, now via two x32 stores. Both store32 operations use R4–R35, recycling that tuple between the two halves; there is no added per-K payload shuffle sequence. The one FC1 MOV at f500 updates the loop counter; it is not weight packing. Conversion, scale math and PRMT counts are unchanged. REG96/STACK0, no LDL/STL. Each of the four decoder out-of-line raw/decoded wait helpers remains a five-instruction retry path, without added moves or memory operations. Thus there is a real decoder K-loop instruction saving; it is not canceled by an uncounted slow-path spill.

The compiler also changes register placement in other parts of this single kernel. The following are **native layout regions**, not dynamic occupancy measurements; the later region contains common work and outlined helpers belonging to earlier roles:

| Region | store16 range | store32 range | Instruction delta | MOV-family delta |
|---|---|---|---:|---:|
| Early bootstrap/control | 0000–4b30 | 0000–4b40 | +1 | +4 |
| Main epilogue region | 4b40–9240 | 4b50–9320 | +13 | +11 |
| Main dispatch region | 9250–e120 | 9330–e270 | +7 | 0 |
| Main transform region | e130–107e0 | e280–10910 | -2 | +7 |
| Later common/outlined paths | 107f0–13f70 | 10920–141f0 | +21 | +13 |
| Total | | | +40 | +35 |

Within the transform region, the two repeated K-bodies save seven instructions while outer setup/work handling adds five. The other42 net extra instructions are outside that region. They are **not all once-per-kernel costs**: epilogue work and dispatch helpers can execute repeatedly for work tiles/tokens. For a concrete non-decoder example, an outlined dispatch vote/min reduction at store32 132d0–13390 adds `IMAD.MOV R17,...R0` to preserve the vote result and `MOV R0,R7` to place the minimum input; it returns to dispatch at b080. Similar helpers return at b800/bf00/c600/cd00. They are distinct from the decoder's unchanged raw/TMEM retry helpers.

The wider contiguous register tuple plausibly changes the compiler's register assignment elsewhere, but these instructions are not proof of a specific allocator algorithm or a runtime cost. The target result0.9973× versus store16 is near-flat and does not measure the native decode matrix. Given the user's preference for instruction reductions, the per-K saving/no-resource-cost finding supports **native incremental qualification against store16**, not automatic rejection based on the whole-kernel total. Retention still depends on that evidence.

Reproduce phase/localization output:

```bash
python3 optimization/analyze_native_codegen.py \
  --arms control store16 store32-uniform-n64-codegen counts_overlap-uniform-n64-codegen \
  --output optimization/native-codegen-followup-analysis
python3 optimization/native_codegen_extras.py
```

`native-codegen-followup-analysis/comparison.json` contains full phase counts and exact hashes; `extra-regions.json` contains the region counts. Source and selected ABI checks are the same as the original audit. The previously reported store64 ptxas failure is not represented as successful native code evidence here.

## Count-overlap release fences: native mechanism confirmed

The count-overlap candidate includes store16. Its decoder K-bodies are identical in opcode counts to store16: FC1 225, FC2 231. Whole code grows5112→5200, with REG96/STACK0 and no LDL/STL.

Two unrolled expert-count contributions per publishing thread are present for E256/128 dispatch threads. In store16, the relaxed64-bit count reductions at a3d0/a530 follow the corresponding per-source `STG.E.64` without an immediate release-fence bundle. In counts_overlap, the release REDs at a740/a8f0 each have the following new ordering sequence:

```text
a6f0 STG.E.64 desc[UR4][R14.64], R16
a700 MEMBAR.ALL.CTA
a710 MEMBAR.ALL.SYS
a720 ERRBAR
a730 CGAERRBAR
a740 REDG.E.ADD.64.STRONG.SYS desc[UR4][R2.64], R18
```

The second contribution repeats that bundle at a8b0–a8e0 before RED at a8f0. The original trailing system-fence bundle is also retained (begins a560 in store16, a920 in counts_overlap). The RED mnemonic itself is identical: native ordering is distinguished by the fence sequence, consistent with the PTX release versus relaxed semantic difference.

This establishes the concrete redundant-work hypothesis tested by `counts_fence`: one prefix system-fence bundle could replace these two per-contribution bundles while retaining the trailing publication. It does not establish timing benefit; scheduler polling and the readiness boundary may dominate. The source proof and the post-prefix per-source-count visibility limitation are documented in `counts-fence.md`. Actual counts_fence native artifacts must confirm its final lowering before instruction savings are claimed.

Exact neighboring native instructions are in `native-codegen-followup-analysis/{store16,counts_overlap-uniform-n64-codegen}-count-red.sass.txt`, with fingerprints in `extra-regions.json`. No GPU work was run for this audit.
