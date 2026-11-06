# Independent R3 coordinate review

The new tile_coordinates helper centralizes exactly the R1 arithmetic; all four calls remain inside the tile>=0 consumer loop. Therefore it does not decode the terminal sentinel and preserves the original static path quotient/remainder. CLC selects the published route and reconstructs channel from the flattened tile; no scheduler, publication, quorum, or reuse change was added after the prior protocol review.

The helper returns channel to roles that may not use it, which is compile-time dead output rather than extra protocol work. The owner must verify its generated instruction effect. Source/patch and helper AST are bound in producer-review.json.
