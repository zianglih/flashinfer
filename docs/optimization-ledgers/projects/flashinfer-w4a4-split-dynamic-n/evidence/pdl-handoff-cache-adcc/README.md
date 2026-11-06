# Paired FC2 handoff-cache result: unretained

Candidate keeps adcc all-thread PDL and adds FC2 output LAST + combine input FIRST. This bounded adjacent-control screen regresses both full-chain cases. Production and all frozen sources remain unchanged. GPU2 is released.

All 36 timed arms (3,600 individual samples), two additional exact-only native gates, full source hashes, actual module paths and emitted artifacts are preserved. No sample filters or retries. Live CUDA L2 cache size was 132,644,864 bytes (126.5 MiB).

| Tokens | Phase | Control medians (µs) | Candidate medians (µs) | Control/candidate |
|---:|---|---|---|---:|
| 4 | full_chain | 47.2000, 47.2000, 47.1360 | 47.3920, 47.5360, 47.7125 | 0.992260× |
| 4 | fc1 | 28.2720, 28.3520, 28.3365 | 28.2400, 28.3840, 28.2560 | 1.000950× |
| 4 | fc2 | 16.2880, 16.2560, 16.3840 | 16.2880, 16.2880, 16.2880 | 1.001304× |
| 16384 | full_chain | 491.5055, 490.8180, 490.3540 | 495.2495, 491.4420, 493.0735 | 0.995215× |
| 16384 | fc1 | 220.2085, 227.4570, 226.3205 | 225.0250, 228.1605, 228.6245 | 0.988449× |
| 16384 | fc2 | 133.1845, 133.4730, 133.4565 | 139.3930, 139.3930, 139.3280 | 0.956949× |

The FC1 source is unchanged; its phase variation is not attributed to a policy change. The wide FC2 phase slows 4.50%, while full chain slows 0.48%; the net hint result cannot be separated causally from the accompanying compiler changes by this screen alone.

| Compile-only object | Registers control→candidate | Nonpadding static SASS sites |
|---|---:|---:|
| FC2 N16 ordinary | 94→92 | 1319→1352 |
| FC2 N256 bulk | 120→134 | 2453→2511 |
| Combine T4 | 36→34 | 228→233 |
| Combine T16384 | 80→80 | 1296→1302 |

All SMEM, block sizes and occupancy are unchanged; no local-memory allocation or PTX/SASS local ops. FC2 ELECT/WARPSYNC counts stay fixed; BSSY sites increase 0→2 (N16) and 0→8 (N256). These are static instruction sites, not executed instruction counts. The parser accepts mixed-case mnemonics and excludes only final NOP padding.

Verified codegen: ordinary FC2 remains256bits (v8.b32 control; hinted v4.b64 candidate); combine expert reads remain128bits coherent global, not .nc. Bulk stores remain TMA with LAST descriptor. Model-output stores remain default128bits. FC2 wait→release.gpu→trigger and combine wait-before-payload ordering remain intact.

Source boundary: four unstaged candidate files on aab; control has precisely the two frozen adcc dirty files. Core adcc6506 and prepare a3b0042 are byte-identical in both arms. Only utils5f005c87 and finalizercb100e0a change. Shared combine also affects W4A16 semantically, but this rejected gate did not run W4A16/broad-format tests or sanitizers. No primary/AUTO/TRTLLM or original baseline rerun.

Commands and harness details: `scripts/pdl_handoff_cache_experiment/README.md`. Raw archive SHA256: `51a1cd777ff37bcb7140d94f8f570f666df3267a44a04fedeed9da44dff89049`.
