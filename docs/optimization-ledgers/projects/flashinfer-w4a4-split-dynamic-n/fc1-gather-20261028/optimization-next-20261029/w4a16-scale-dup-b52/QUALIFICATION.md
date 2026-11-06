# Qualification: compile only

Source `d5105227` changes only scale-byte duplication in the independent16-value W4 helper, on b52. Existing source-equivalent W4 controls are reused; only the unrelated swap kernel differs between the old control snapshot and b52. All514 sources, immutable frozen winner caches and147 captured files were verified. No owned MoE kernel launched; no exactness or performance result is implied.

| Shape | Tokens | FC | Non-NOP change | PRMT change | REG before/after | LOCAL before/after |
|---|---:|---|---:|---:|---|---|
| ep-kimi-k3-w4a16 | 4096 | FC1 | -8 | -8 | 96/96 | 0/0 |
| ep-kimi-k3-w4a16 | 4096 | FC2 | -8 | -8 | 128/128 | 0/0 |
| ep-kimi-k3-w4a16 | 8192 | FC1 | -8 | -8 | 96/96 | 0/0 |
| ep-kimi-k3-w4a16 | 8192 | FC2 | -8 | -8 | 128/128 | 0/0 |
| ep-v41-flash-w4a16 | 4096 | FC1 | -8 | -8 | 96/96 | 0/0 |
| ep-v41-flash-w4a16 | 4096 | FC2 | -8 | -8 | 128/128 | 0/0 |
| tp-nemo3-ultra-w4a16 | 16384 | FC1 | -8 | -8 | 96/96 | 0/0 |
| tp-nemo3-ultra-w4a16 | 16384 | FC2 | -7 | -8 | 128/128 | 0/0 |
| tp-v3-w4a16 | 8 | FC1 | -8 | -8 | 96/96 | 0/0 |
| tp-v3-w4a16 | 8 | FC2 | -8 | -8 | 128/128 | 0/0 |

Every pair removes exactly eight low-byte extraction PRMTs and eight duplication PRMTs and introduces eight direct0x4400 PRMTs. Other conversion/multiply instruction counts are unchanged. N3U TP16K FC2 additionally replaces one CS2R with two IMAD.MOV instructions, giving net−7 rather than−8. All other non-NOP instruction counts differ only by the eight removed PRMTs.

Threads, tilers, cluster, raw/decoded/output/metadata stages, dynamic shared allocation, activation/layout/CLC selection and compiler options remain equal. Actual loaded resources remain FC1REG96/FC2REG128, zeroLOCAL and zeroLDL/STL. The inherited register donation policy is unchanged.

The39 existing exact/graph cases passed with40 actual MoE resource captures, all zeroLOCAL. A task-local kernel exercised both direct-BF16 and forced FP16 compatibility branches in both sources:16,384 block inputs/262,144 output values per branch, all256 scale bytes, all16 nibbles at every output position and four upper24-bit patterns. All four output byte streams are identical, including NaNs and signed zeros. Tiny-kernel registers remain17/18 and zeroLOCAL. This validates fallback under CUDA13.2, not an older-toolkit build. The1015-file gate archive and all514 sources were hash-verified; QUALIFICATION.json records the replay. The predeclared18-cell fixed-winner CAAC is authorized after these gates; performance remains pending.
