# Final operand composition with aligned scheduler records

Base9334; patch `b8e3117608154c6e6f7aa62c28d9089601416178e54cb5ef561d4250137ecb6f`;
core `d502f33f48e3d6ed92e53814f5468ae5651627f23040d0d4ea53e8d9a449d27a`.

V4 combines the independently gated V1 allocation cleanup and V2 folded
readiness, then explicitly aligns the existing 16-byte `tile_info` records to
16 bytes. This is a layout requirement without a fallback or policy knob.

The alignment is necessary because V1's removed eight-byte slots shifted some
CLC records from 16-byte to eight-byte alignment. Actual isolated V1 SASS
replaced `LDS.128` with `LDS.64` plus `LDS` in eight compiled cases. Its aggregate
instruction count was +4 despite -8/-9 registers in some wide FC2 cores; that
was not an instruction-neutral result and should not be described as such.

The V3→V4 delta is only the `tile_info` field annotation. Every device method
AST equals V2; all operand storage declarations equal V1 except the removed
SF-ready array. The planner takes only `tma_sfb`, counts two common operand
barriers plus the optional local SF-full barrier, and retains its current
capacity-derived stage policy.

Validation:

- Scoped pre-commit, Python syntax and diff checks passed.
- Actual pure planner methods passed 1,152 metadata and 2,880 capacity cases;
  none of the sampled stage-capacity choices changed.
- Installed CuTe SDK4.7.1 `cute.struct` checked 2,304 combinations of stage,
  accumulator, scheduler, metadata queue, SF transport and scratch size. All
  tile-info offsets are 16-byte aligned; 864 live-record alignments improved.
  Every scratch offset, operand-start offset and total prefix size is
  unchanged. No shared-memory capacity increase occurs. Actual sizes stay
  within the planner; maximum conservative slack is128 bytes.

The struct probe extracts the real source metadata fields and substitutes a
zero-byte Align128 marker for the unchanged first operand array. It runs on
the installed SDK without GPU work; it is not device codegen or numerical
validation. Frozen receipts are `composition-check.json`,
`resource-check.json` and `actual-struct-check.json`.

V1 gate:44 core pairs/88 exact replays per source. V2 gate including narrow
M512:48 pairs/96 exact replays per source. Those isolated gates do not replace
the final combined-source gate. Root owns that composition and its timing;
the final gate also includes narrow M512 with static scheduling.
