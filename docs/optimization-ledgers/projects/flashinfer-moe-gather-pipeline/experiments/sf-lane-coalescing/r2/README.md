# R2: cache routed SF row indices

Candidate kernel SHA `377f040445b488541d6e5b594f4e532875ccaa5af76f227e53942b5a98e61a76` remains unstaged in the same `flashinfer-sf-lane-coalescing-review` worktree at retained `2b8eb9d8`. Main is clean. No GPU work was launched by this source task.

The change from R1 `86836355` is exactly **5 added / 6 removed lines**: rename the existing register tensor `sf_source_rows`, store its existing Int32 `source_row`, then form `Int64(sf_source_rows[row_block,row_batch]) * stride` at source-pointer construction. The cast occurs before multiplication. No helper, PTX, volatile operation, branch, quota, mapping, barrier, zero predicate, or interface changes.

R1 source/patch/CPU receipts are copied byte-for-byte under `../r1-preserved/`; their original artifact leaves and failed wide native gate remain untouched. R1 had driver LOCAL64 and actual LDL/STL; R2 does not reinterpret or waive that failure.

The source-derived proof establishes:

- The only R2 delta reverses byte-for-byte to R1; the four original mapping regions still reverse to the retained control.
- The cached tensor is Int32 and stores the original routed row unchanged, including zero for invalid rows. Actual pointer arithmetic widens the cached value before the identical stride multiply.
- All 23,040 owned words, 38,076 live/zero/padding classifications and exact participant sets are unchanged. G1 ownership and all 4-byte copy predicates still match control.
- 105 signed-row/stride/channel algebra cases include products beyond Int32 range; the widened expression matches the original signed Int64 multiplication. This supports the algebra and cast order, not a new public index-range guarantee.
- Python syntax, scoped pre-commit hooks and `git diff --check` pass.

Explicit source storage halves from two logical 32-bit slots per offset to one per row: four slots saved in N256/G2 and eight in N256/G4. The compiler may hoist the multiply and recreate the same wide live values, or rematerialize it and add work in K. No spill-fix, resource, codegen, or performance claim is made. The single separately owned native probe must retain its existing strict resource gate.
