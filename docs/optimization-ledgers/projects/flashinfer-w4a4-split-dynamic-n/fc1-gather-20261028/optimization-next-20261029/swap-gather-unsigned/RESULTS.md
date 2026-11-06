# Unsigned gather-warp offset — rejected

Retained control475 versus the single change `gather_warp = cutlass.Uint32(warp - 8)`. No pipeline, geometry, barrier, tactic, or FC2 changes. The17-case exact gate and16 runtime guards passed;4,800 strict-CUPTI samples cover12 fixed-winner cells.

The measured aggregate is−0.153%, with mostly small mixed changes. The largest negative (N3U EP16K MXFP4x8−3.004%) has3.570% control-repeat spread and is not a robust isolated regression. There is no broad performance improvement to justify carrying this cast. Native-wide FC1 reduces MOV.SPILL uniform-register transfers51→39 but adds18 non-NOP instructions and2branches; it is not an unambiguous instruction simplification. All captured kernels have zero local memory, and both FC2 SASS files are identical.

The first MX CAAC job spans a native-cache rebuild: a concurrently qualified checkout used different native include paths, causing moe_utils to rebuild twice. The held candidate pass spent1041s before completion, including compilation/wait; those seconds are not GPU latency. All phases ultimately completed normally with100 strictCUPTI samples per cell. Runtime and read-only10ms NVML telemetry remain preserved without filtering or normalization. Stable native-data paths have since been restored, and caches are retained.

See `screen-report/table.md` and `screen-report/cells.csv` for every outcome; `screen-evidence/` contains the complete177-file hash-verified archive. Archive SHA256`c6ba96e4c11ce6b7b803af361e15f50d1481585fe03fcb2cb6960f0d340f473b`. No sanitizer was run. The rejected source copy is retired; source patch/codegen remain local.
