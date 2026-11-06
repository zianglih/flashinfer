# Paired-width N3U TP decode repeat

The32-token regression reproduced, and64tokens also regressed. Do not retain the width-only candidate based on its positive prefill average. This follow-up compares frozen374 with the same paired-width source, unchanged tactics/routes and complete same-GPU C-A-A-C;3cells/1,200strict CUPTI samples. Stock clocks; every observed clock quartile was2032MHz with reason0. No source, grid policy or clocks changed.

|Tokens|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|Intermediate quant C→A µs|
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|8|63.808|63.681|63.840|63.904|+0.150%|0.150%|0.250%|9.224→9.128|
|32|123.569|126.529|126.929|124.545|-2.109%|0.790%|0.316%|15.568→18.056|
|64|147.425|149.713|148.961|146.993|-1.425%|0.294%|0.505%|19.632→22.280|

At8tokens the statically allocated intermediate is2816 rows and the small-M width remains64; at32/64 tokens capacity exceeds4096 and the width changes64→32. Live routed rows are704/1408, surrounded by routing holes. The broader-screen report documents the extra scalar SF-clear loop and doubled grid cap hypotheses. Component durations overlap under PDL and should not be summed.

ArchiveSHA256 `1f6632937fe9d4f7e8dc40a5315997731d7d5cb2e485d301645f7a8b7a11160f`;184 files verified. All raw phase medians, clock samples and source/cache/resource guards are under `evidence/`. No sanitizer.
