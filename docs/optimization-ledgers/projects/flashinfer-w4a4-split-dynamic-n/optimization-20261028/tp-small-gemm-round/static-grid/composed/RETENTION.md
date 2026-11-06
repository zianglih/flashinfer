# Retained static launch capacity cap

Retained in `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8` on `d7e5ea1c67e6d5f011377e340811ffc377a41763`. This is a neutral launch-work cleanup: cap the static persistent launch at the existing routed metadata capacity while preserving full CTA groups and physical cluster zero. The CLC path, device code, tactics, W4A16 and old non-swap mode are unchanged.

The bound is a **launch-time capacity calculation** from existing host-wrapper shapes and compile-time channel/CTA geometry. It adds no GPU readback, device branch, cache specialization or public option. If the capacity is below the resident budget, each active cluster keeps its first tile and cannot have a second tile under either stride; only guaranteed-empty work disappears. The zero-work launch remains valid for PDL and initialization/final joins.

## Evidence

- Initial gate on2d60:128 paired exact graph replays per source;48 GEMM and4 combine raw PTX/cubin/SASS/resource pairs identical. It covers four scaled formats, one/two CTA, static/CLC, PDL off/on, T4/T257 and changing/empty/reactivated routes.621 archived files verified. Project-only failed fixture/coverage attempts remain separately recorded.
- Composed gate on retained SF source d7e5:16 paired exact replays per source,16 GEMM and2 combine raw artifact/resource pairs identical,348 source hashes verified.174 archived files verified. Eight CUDA activity traces confirm the expected actual launch grids with exact PDL-on symbol/register association; fixture dimensions H384/I256 differ from the real model shapes. The earlier101/102 register discrepancy was an incorrect PDL-off/PDL-on pairing, corrected in `TRACE-PAIRING-CORRECTION.md`.
- Fixed-winner C–A–A–C:15 cells,24 subprocess phases,60 medians,6,000 strict CUPTI cold-L2 graph samples. Public functional API, unfused swap-AB,10 warmups/100 samples; NV includes initial quantization. Six distinct GPUs, exact83df frozen winners/routes, no retune or external baseline rerun.781 archived files verified. Both raw audits pass.
- Scoped and commit hooks pass. No sanitizer was run, as requested. No broad latency improvement is claimed.

## Timing

The four affected V3 TP8 T4 FC1 launches shrink148→128 CTAs by the safe capacity bound. Their geometric speedup is **+0.095916%**; the per-token row is **−0.236257%** and remains part of the result. Eleven unchanged controls average−0.011909%; all15 cells average+0.016833%. The negative per-token observation is not dismissed as noise. The retained justification is the simpler safe launch bound, removed guaranteed-empty work and unchanged device instructions.

Speedup is100×(geomean(C1,C2)/geomean(A1,A2)−1). All pass medians below are milliseconds.

| Topology | Tokens | Backend | Affected | C1 | A1 | A2 | C2 | Speedup |
|---|---:|---|:---:|---:|---:|---:|---:|---:|
| V3 EP8 | 4 | CuteDSL MXFP8 | no | 0.0678410 | 0.0678570 | 0.0677280 | 0.0678245 | +0.059417% |
| V3 EP8 | 4 | CuteDSL MXFP4x8 | no | 0.0466080 | 0.0465765 | 0.0465765 | 0.0465285 | -0.017749% |
| V3 EP8 | 4 | CuteDSL W4A4 | no | 0.0468320 | 0.0468480 | 0.0468650 | 0.0468325 | -0.051752% |
| V3 EP8 | 4 | CuteDSL PER-TOKEN | no | 0.0501440 | 0.0502085 | 0.0502410 | 0.0501440 | -0.160772% |
| V3 EP8 | 4 | CuteDSL W4A16 | no | 0.0510240 | 0.0510400 | 0.0510080 | 0.0509920 | -0.031358% |
| V3 TP8 | 4 | CuteDSL MXFP8 | yes | 0.0463685 | 0.0464320 | 0.0463045 | 0.0463680 | +0.000095% |
| V3 TP8 | 4 | CuteDSL MXFP4x8 | yes | 0.0358720 | 0.0358405 | 0.0358080 | 0.0358560 | +0.110966% |
| V3 TP8 | 4096 | CuteDSL MXFP8 | no | 0.5740830 | 0.5741150 | 0.5742290 | 0.5744040 | +0.012449% |
| V3 TP8 | 4096 | CuteDSL MXFP4x8 | no | 0.5145145 | 0.5142425 | 0.5143885 | 0.5145325 | +0.040443% |
| V3 TP8 | 4 | CuteDSL W4A4 | yes | 0.0362400 | 0.0360485 | 0.0360640 | 0.0362405 | +0.510316% |
| V3 TP8 | 4 | CuteDSL PER-TOKEN | yes | 0.0403840 | 0.0404800 | 0.0405760 | 0.0404805 | -0.236257% |
| V3 TP8 | 4 | CuteDSL W4A16 | no | 0.0399365 | 0.0398880 | 0.0400640 | 0.0400320 | +0.020808% |
| V3 TP8 | 4096 | CuteDSL W4A4 | no | 0.4826125 | 0.4827895 | 0.4828690 | 0.4829500 | -0.009947% |
| V3 TP8 | 4096 | CuteDSL PER-TOKEN | no | 0.5937660 | 0.5945195 | 0.5942790 | 0.5945670 | -0.039178% |
| V3 TP8 | 4096 | CuteDSL W4A16 | no | 0.6474780 | 0.6470475 | 0.6466640 | 0.6468395 | +0.046834% |

## Source and audit links

- Patch:`candidate.patch`, SHA256`a15762dcb0602d3973f557129a22e9fb4c75017289b3382273dd3335d69d1626`; kernel SHA256`c9b6948d8f7645d5076d3aa06d1d32b43b99846eb36749f83e5262d56959aa38`.
- Source receipt:`source.json`, SHA256`0db74fa955fc9b388210a47811f4828b79d8e84f8d0d30419eaed3656f8170c3`.
- Independent reviews:`scheduler-source-review.json`, `scheduler-gate-review.json`, `scheduler-perf-review.json`.
- Raw archives:`gpu-evidence.tar.gz` SHA256`909c32058f6f8ab5c9aef4046445f19d0520ce66ea68d85d7cb7ab88054b499c`; `perf-evidence.tar.gz` SHA256`861ab9936f73b3f32310e056a9d23e02bc814af226b7a594d5c426bdfdd21f77`.
- Full numeric evidence:`perf-cells.csv`, `perf-analysis.json`; prior capacity audit:`../../epilogue/next-audit/RESULTS.md`.
- Cleanup and retained-tree equality are recorded separately in `integration-receipt.json` and source-cleanup receipts. Helpers/raw artifacts/native caches are preserved.
