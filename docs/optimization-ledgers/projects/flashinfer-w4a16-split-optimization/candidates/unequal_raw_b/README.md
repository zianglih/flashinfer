# Candidate 004: unequal raw/SF and B depths

Held artifact only, based on committed `b90b34744491c36d0039f44cba664191f7bb0eb0` (candidate 002). The live repository was not modified. This does not include or assume retention of candidate 003's separate raw-release reorder.

The existing fitter first chooses the same paired load, decoded, accumulator and output depths. A separate B depth retains that paired value. For fused finalize only, the remaining conservative budget may buy exactly one additional raw/SF slot, charged as the existing rounded raw payload plus the existing BF16-width SF charge plus 16 barrier bytes. There is no geometry dispatch, public knob, changed C-stage allocation, or dynamic runtime decision.

The two B barrier arrays, B pipeline and B producer/consumer states use the B depth. A and SF continue sharing the raw depth. Direct existing `make_smem_layout_a/a/b` calls replace the thin combined helper so each operand can use its own count. The saved installed DSL 4.7.1 helper signatures accept these exact four positional arguments; all majorness/swizzle defaults are retained. Storage allocation order, 1024-byte alignment, per-stage payloads, scale views, transaction byte counts and multicast groups are unchanged. Actual expanded dynamic shared allocation still requires native measurement.

The transform routine is AST exact. The kernel and launch/SharedStorage method are AST exact after normalizing only the new B-depth attribute back to the old common-depth attribute. Raw, decoded and B rings already keep independent index/phase state; no equality of their physical indices is assumed. Logical K counts, work boundaries, reset_count, waits, commits, releases and tails are unchanged. This is configuration separation rather than a new scheduling protocol.

## Source-only stage table

Current K256 catalog, static scheduling. M128 covers C1 and C2; M256 uses C2. `raw/B` is the number of stage slots, and D/ACC/C are decoded/accumulator/output depths. Ordinary and gated cases are unchanged. Residuals are conservative fitter bytes, not queried allocation sizes. The corresponding 30 rows are saved in [stage-table.json](stage-table.json).

| MMA M/N | Gated raw/B; C | Ordinary raw/B; C | Fused raw/B before → after | D / ACC | Fused residual after (bytes) |
| --- | --- | --- | --- | --- | ---: |
| 128/8 | 9/9; 10 | 9/9; 5 | 9/9 → 9/9 | 3 / 2 | 8720 |
| 128/16 | 7/7; 15 | 7/7; 7 | 7/7 → 8/7 | 3 / 2 | 6688 |
| 128/32 | 6/6; 2 | 5/5; 5 | 6/6 → 6/6 | 3 / 2 | 2576 |
| 128/64 | 4/4; 4 | 4/4; 2 | 4/4 → 4/4 | 3 / 2 | 10832 |
| 128/128 | 2/2; 14 | 2/2; 7 | 2/2 → 3/2 | 2 / 2 | 31376 |
| 256/16 | 9/9; 5 | 9/9; 2 | 9/9 → 9/9 | 3 / 2 | 6640 |
| 256/32 | 7/7; 7 | 7/7; 3 | 7/7 → 8/7 | 3 / 2 | 2528 |
| 256/64 | 6/6; 2 | 5/5; 5 | 6/6 → 6/6 | 3 / 2 | 2576 |
| 256/128 | 4/4; 4 | 4/4; 2 | 4/4 → 4/4 | 2 / 2 | 10848 |
| 256/192 | 3/3; 5 | 3/3; 2 | 3/3 → 3/3 | 2 / 1 | 14992 |

Fused C stays 1. Only M128/N16, M128/N128 and M256/N32 change. The extra conservative charge is 20496 bytes. FC1 CLC uses less tile-info storage but does not take the fused-only increment; its old stage choices remain unchanged. No performance benefit follows from capacity alone, and extra raw depth does not increase decoded or B capacity.

## Checks and pending admission

- Syntax compilation, Ruff lint/format and AST binding checks passed locally without CUDA imports. [source-review.json](source-review.json) pins both saved DSL helper files and records the checks.
- Independent source review passed; see [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md) (`35e11df0`). Native compilation, resource/actual shared-memory measurement, large-K numerical wrap coverage and performance are not run or claimed.
- Proposed kernel SHA256: `7a2bf6ca032fbfb6733fed5255684203d7b9f2300bdf6146e88dec1fd55838f0`.
- [source.patch](source.patch) SHA256: `d4f45ab8adeb55ee7b17634b8252bb464732cef14b904a8f99c730f6bfbdd044`; 38 additions, 15 removals, net +23 lines.
- Baseline kernel SHA256: `22fefac2a21e2efb5f9b5e0f2b402202dddf8f7136c1c50585105466ae2794a0`.

## Existing-oracle wrap checker

[check_ring_wraps.py](check_ring_wraps.py) (`7af40b66`) reuses the prior four-call harness with six calls: M128/N16/C1 at17 tokens, M128/N128/C1 at129 tokens, and M256/N32/C2 at33 tokens, each with ordinary and fused finalize. Every case uses SwiGLU, H=I8192, E2/top-k2 and the unchanged `_run_numerical_accuracy` helper. It verifies catalog membership, records each token count, and synchronizes/collects garbage between cases. This checker was syntax/Ruff/AST checked locally without imports or execution; expected completion is six `UNEQUAL_RING_WRAP_PASS` markers and `passed_calls=6`.
