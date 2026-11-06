# R2 zero-store codegen audit

The intended word clear was scalarized. `cute.recast_ptr` retains the incoming pointer alignment (local CUTLASS `cute/core.py:4454`); adding a runtime SF offset reduces its known alignment to one byte. Casting the pointee type toUint32 does not supply a4-byte alignment guarantee.

Example: `direct-codegen/resources.json` record121, K640/32threads/SF128x4/routed holes:

```text
R1: STG.E.U8 desc[UR10][R2.64], RZ
R2: STG.E.U8 desc[UR20][R2.64+0x3], RZ
    STG.E.U8 desc[UR20][R2.64+0x2], RZ
    STG.E.U8 desc[UR20][R2.64+0x1], RZ
    STG.E.U8 desc[UR20][R2.64], RZ
```

-209 paired captures have matching compile order and all recorded geometry/recipe metadata.155 add three byte-store sites;44 CUBINs and instruction streams are identical. No added16/32-bit zero-store sites occur in this recorder.
-22 captures change register counts;10 change stack usage. Some K3072/7168 variants acquire8/24B of stack, while some forced128-thread K16384 variants reduce stack. These are broader codegen effects, not a simple monotonic spill explanation for timing.
-The recorder has193 expected4-byte and16 expected1-byte cases, but no expected2-byte case. The separate18-case hole-layout correctness script did not install the codegen recorder. An aligned candidate must explicitly capture a linear2-byte case before claimingSTG16.
-Direct linear K2048/8192 captures are byte-identical, but they use `valid_rows`, which sets M and padded_M to the same loaded value for linear layout. They do not prove equivalence for TRT initial quantization without a valid_rows argument. Its M/padded_M are separate runtime arguments; baseline reuse needs its actual codegen or fresh evidence.

Minimal fix: construct the destination with `cute.make_ptr(self.sf_zero_dtype, get_ptr_as_int64(mScales, sf_offset), cute.AddressSpace.gmem, assumed_align=zero_bytes)`. The existing gcd-width address proof establishes this alignment for every generated store. No new low-level helper or runtime branch is necessary. Root owns the aligned candidate and its qualification; this audit makes no performance claim for that unmeasured source.

Artifacts: frozen gate archives under `../per-token-paired-width/gate-evidence` and `../per-token-paired-clear/gate-evidence`; all209 exact resource/SASS pointers and instruction deltas are preserved in `codegen-analysis.json`. Diagnostics use keep-cubin/no_cache and were not used for timings.
