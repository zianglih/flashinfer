# Shared-prepare full-refresh helper review

The two-phase baseline selection is correct: all 15 saved 33b7 receipts have candidate phases 1 and 2; their 348 source hashes match the new control binding. Their receipt hashes match the new job config. Old 61249 control phases are not used. All 46 EP and 42 TP external provenance input hashes passed.

The source schema is consistent: `prepare_sha256` is the changed-file identifier and only `moe_swap_ab_prepare.py` differs. The analyzer records `candidate_prepare` from the source map; its separate kernel hash is unchanged context. The assembler uses the complete source map, so it does not depend on a nonexistent top-level kernel field.

All 104 W4A16 cells receive fresh values in the table/native outputs. Backend groups include W4A16; the historical top-level aggregate/best/worst remain scaled-only. W4A16 shares this changed preparation path and must not be described as an unchanged control.

The publication paragraph marker initially mismatched the saved body (`: source-identical` versus `: eight B300 GPUs`). The root corrected it to the stable head-and-colon prefix. Other inspected paragraph markers and prior report schemas match. External baseline fields, unsupported rows, raw public control blocks, PR template and historical sanitizer section are preserved by explicit assertions.

The root also added the saved baseline receipt SHA256 and physical GPU UUID checks, covering initial and every phase before/after record. This closes the ordinal-only verification gap. No remaining blocking helper issue found. Fresh measurements and qualification remain pending and are not certified by this helper-only review.
