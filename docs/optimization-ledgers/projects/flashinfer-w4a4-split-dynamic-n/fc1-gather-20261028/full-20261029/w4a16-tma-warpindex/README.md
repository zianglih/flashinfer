# W4A16 within-warpgroup gather index

Active source: flashinfer-w4a16-tma-warpindex-review, unstaged. Parent/final control26bce remains unchanged.

One-line candidate: use warp_idx % len(gather_warp_id) instead of warp_idx - gather_warp_id[0]. Within the last input-gather WG these are identical. The modulo bounds the index to0..3 for compiler range analysis, allowing redundant per-task K/row bounds to simplify without a model/dtype/tile heuristic. Inspect codegen before performance; no retention claim yet.
