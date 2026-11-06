# Independent read-only FC2 bulk review

Reviewed frozen bulk32 patch `19b18874bd31c6654785bdffd862f74a7264f2851d701468119a53e429467399` and bulk16 patch `f2bb5f50a6c8de22308e666995111389cd6b7857f38d58291c0954dfca17832c`, both based on clean0c. No source changes or GPU runs by this review. Source pins and exact patches are beside this note.

## Finding in unrestricted 16-token fallback

`_run_bulk_direction` in `blackwell/utils.py` assumes each slab contains a multiple of32 tokens when indexing `output_rows[group * (tokens // 32)]` and `scales[group * (tokens // 32) + i // 16]`, and when choosing the row/scaling shuffle lane. For tokens16, these indices lose the slab offset. Logical N16 uses only group0 and is correct. A later16-token slab for logical N32+ would read the first16 rows/scales again and overwrite/reuse the wrong output rows.

The bulk16 configuration offers16 as a fallback for every route tile whenever capacity admits16 but not32. This includes explicit stage-count configurations. This is a conditional high-confidence indexing finding; the review has not established a concrete supported stage configuration that selects that fallback. Restrict16 to route_tile16 for the proposed minimal change, or generalize metadata group/lane indexing before exposing16 to wider tiles.

## Bulk32 and intended N16 mapping

- Physical accumulator N is already `max(32, route_tile)`. The32-token slab for logical N16 stays inside its accumulator allocation; the extra lanes may contain unspecified values but cannot reach output because the bulk-copy row predicate uses `valid_tokens`.
- Every token-mapping/per-token-scale load is guarded by the logical live-token bound. Output rows beyond live routes are not read or written. All-zero live work skips the slab uniformly and still reaches the final empty-group wait/barrier. The supplied45-case gate covers zero-valued output and padded rows, not a zero-live-route case; static review covers that branch.
- Four epilogue warps perform the TMEM load/stmatrix fragment layout. The128-thread barrier is reached uniformly. Shared writes precede the async-proxy fence and barrier; bulk copies commit per thread, and `wait_group(0, read=True)` plus the barrier completes shared reads before scratch reuse.
- For intended tokens16/group0, `Ld16x256bOp(Repetition(2))`, two halves of8 values, two stmatrix4 calls and four copy rows per warp map16 rows×128 channels. Registers and shared accesses remain within their allocated ranges.
- Scratch bytes are `tokens*136*stages*2`; output rows and shared rows retain16-byte alignment. Channels are required to be multiples of128. The capacity fitter includes metadata and scratch, then verifies actual operand layouts and final SharedStorage size.
- CTA count, warp ownership, TMEM allocation and `min_blocks_per_mp=1` are unchanged. This is a shared-memory tradeoff within the existing one-CTA resource contract.
- Bulk32 keeps the existing wide configuration choices and slab counts. Fused/atomic, FP32 and FC1 paths remain excluded. The unrestricted bulk16 fallback is the only additional wide-path caveat above.

## Boundary

This is a focused source review complementing the parent's45 exact cases and fixed-tactic timing. It is not sanitizer evidence or proof for arbitrary direct-internal API configurations.
