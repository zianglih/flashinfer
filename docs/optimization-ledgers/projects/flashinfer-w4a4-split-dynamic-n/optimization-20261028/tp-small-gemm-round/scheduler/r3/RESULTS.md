# Scheduler coordinate publication: R3 qualification

Source: base `1054743780dda2919c1424124c1e3258248b8c19`, candidate kernel `765237475be178e0b968f81f6fdca5a616deedb25ef288e9005440c3b2943c67`, patch `0480aeb453bc91af7f38d95e8bbb31d1074b140fad5a50623538e766c4b088ed`. Only `moe_swap_ab_kernel.py` changes; the review checkout remains unstaged.

The CLC publisher writes the route coordinate into the already reserved fourth metadata word. Consumers keep that value across their existing release, avoiding repeated division of the linear tile ID. One `tile_coordinates` helper resolves CLC and ordinary coordinates at the original position inside each consumer loop. No new storage, queue depth, barrier, arrival, scheduling tactic, public API or numerical operation is introduced.

Qualification passed 40 source-paired storage-byte replay comparisons and 20 GEMM codegen pairs, with three unchanged combine codegen pairs. The bounded cases cover four scaled formats, static and CLC scheduling, PDL on, one/two CTA, M512, partial K, and balanced/skewed/empty/reactivated routes. This is comparison against the retained implementation, not a new independent-reference suite. Generic combine checks also pass. No sanitizer or autotuning was run.

All kernels retain zero local-memory/stack spills. The eight TP-like CLC kernels remove 1–16 non-NOP static instructions, with registers unchanged or reduced by up to five. Two mixed-format kernels remove two/eight static uniform spill sites. Shared metadata code becomes 128-bit stores/loads: net one fewer static STS site and two fewer LDS sites in each CLC kernel. These are static code counts, not dynamic instruction measurements.

The EP-like mixed control has a tradeoff: FC1 adds two non-NOP sites and one register while removing eight uniform spill sites; FC2 removes 17 sites but adds four registers and one uniform spill site. Static factoring preserves six of ten SASS instruction streams. Other static streams have resource/scheduling changes, including mixed EP FC1 +9 registers and mixed TP FC1 +22 sites/+4 registers while removing six uniform spills. All raw resource and opcode counts remain in `gpu-evidence/analysis.json`.

R1 preserved all ten ordinary SASS streams but repeated four policy selections. R2 moved coordinate calculation into `next_work`; that shifted work across the loop boundary and increased up to 123 static sites/13 registers, so that form was not timed. R3 keeps the clearer shared helper at the original scheduling point. R1/R2 source and native artifacts are preserved separately; the R3 timing decision will use its own frozen source only.

Evidence: `GATE.json`, `gpu-evidence/`, `producer-review.json`; candidate archive SHA `118efbc5776812528b3a7c86d0c9b27eaab4c422339bd1813e2bd46fa48de1a9`, saved-control archive SHA `e4ee1bf7ec9990cc31d730e920d63e2be475eb1e4873b92831d88bde814a10f5`. Full source hashes were checked before and after each gate process, and each process used its own compiler-dump directory with existing native C++ caches preserved.

The authorized 144-cell fixed-winner C-A-A-C screen is complete: 112 scaled-format cells and 32 unchanged W4A16 sanity cells, 576 pass medians and 57,600 raw CUPTI samples. Four models in EP/TP, T4/64/4096/16384, with existing unsupported arms skipped. Public functional API, unfused swap-AB, NV input quantization, cold L2, 10 warmups and 100 CUPTI samples per measurement. The median of each pass is preserved, then the two control and two candidate pass medians are combined geometrically. No full published matrix or external baseline was rerun.

| Scope | Cells | Speedup GM |
|---|---:|---:|
| All scaled formats | 112 | −0.037% |
| Frozen tactic requests CLC | 50 | +0.090% |
| Frozen tactic requests static | 62 | −0.140% |
| Unchanged W4A16 sanity | 32 | −0.052% |
| EP decode / prefill | 30 / 30 | +0.068% / −0.255% |
| TP decode / prefill | 26 / 26 | −0.0001% / +0.056% |

The frozen tactic flag is not proof of effective CLC execution: existing launch admission can select static for small grids. All four EP MX 16K winners request static. Largest scaled loss is V41F EP MXFP8 16K, −2.107% (C1 0.925625, A1 0.9471365, A2 0.9580255, C2 0.9394165 ms). Both candidate passes are slower; control drift is +1.49%, but this is not grounds to discard the row. Other large negatives include single elevated candidate passes, and the unchanged W4A16 arm also varies. Raw medians remain authoritative; no time-strata substitution, noise adjustment, or selective rerun was used.

This screen demonstrates no broad performance improvement. Retention, if accepted by the parent, is for general CLC bookkeeping/instruction cleanup with neutral aggregate performance and the stated static-codegen/prefill costs. No additional source variant or run is proposed. The local review remains unstaged pending that decision.

`audit_perf.py` independently verified 2,024 archived file hashes, all source manifests, frozen winners and cache identities, routing identities, command/environment contracts, per-pass medians, 100-sample strict-CUPTI use, no profiling during measurement, and all 60 phase results. Archive SHA `9586dffc82f68567238af1b644ede28b5ca761d16e54ec6076eb19f621ea307e`; complete rows are in `perf-cells.csv` and `perf-analysis.json`. Source postflight passed; secondary GPUs0–3 were idle and released after completion.
