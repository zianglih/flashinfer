# Predicated live-row Gather4: rejected at codegen gate

PTX predication lowers to additional branches around unpredicated SASS
`UTMALDG.2D.GATHER4`. N3U EP T4096 W4A4 grows from7632 instructions/182 branches
for live+112 to7696/198; per-token grows1920/171→1944/179. No spilling appears,
but the intended branch reduction fails.

Pre-commit and binary register-pool guards pass. No seven-case correctness or
paired performance campaign was run; diagnostic benchmark timing is not
retention evidence. The rejected local source copy was removed. Exact source
patch/hashes, all CUBIN/SASS, and `codegen-summary.json` are retained locally.
