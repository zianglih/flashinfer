# Live Gather4 loop: source and generated-code gate

- Base retained `475cae6b28a536e24aa8da2ed488d0f00fb5305b`; one unstaged source file in `flashinfer-fc1-gather-live-groups-review`. Patch SHA `8e245181072ee512db8da95df1a2eb46c8828d93bb7841c169ecdcee7f731104`.
- Each lane retains one or two decoded route IDs outside K. A runtime live-group loop broadcasts four fixed-bank lanes before the elected Gather4 issue. The existing SF sequence is byte-identical; barrier quorum, layouts, reuse/release, PDL, tactics and FC2 are unchanged. Only announced Gather4 bytes track the rounded live payload rows.
- The exhaustive ownership proof passed2,976 combinations. Both control and candidate passed23 existing/reference-based exact cases: four formats, one/two CTA, one-token/partial/full tiles, N16/K4/K8, effective FC1 CLC, N256 one-CTA two-bank selection, M512 and partial K. No sanitizer was run.
- Generated-code gate:23 FC1 and21 FC2 pairs. All candidate STACK/LOCAL sizes and LDL/STL sites are zero. All21 FC2 cubins are byte-identical. Shared-memory/pipeline capacities and register-budget guards match. Full details in `codegen-summary.json`.
- Broad static code reduction at wide FP4 does not establish a speedup: four SHFLs and loop control now execute per Gather4 per K. Narrow N16 adds25–90 static sites. The bounded screen includes decode and fully occupied tiles to expose that cost.

| Index | N | CTA | K tile | Channel tiles | Activation | Instructions before→after | SHFL sites | Branch sites |
|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 0 | 128 | 1 | 512 | 1 | Float4E2M1FN | 1421→1227 | 32→8 | 118→121 |
| 2 | 128 | 1 | 512 | 1 | Float4E2M1FN | 1538→1337 | 32→8 | 119→122 |
| 4 | 128 | 2 | 128 | 1 | Float8E4M3FN | 1449→1444 | 16→8 | 123→127 |
| 6 | 128 | 2 | 128 | 1 | Float8E4M3FN | 1449→1444 | 16→8 | 123→127 |
| 8 | 16 | 1 | 256 | 1 | Float8E4M3FN | 1341→1410 | 4→8 | 74→77 |
| 10 | 16 | 1 | 256 | 1 | Float4E2M1FN | 928→962 | 4→4 | 82→84 |
| 11 | 128 | 1 | 512 | 1 | Float4E2M1FN | 1089→900 | 32→8 | 64→67 |
| 12 | 16 | 2 | 256 | 1 | Float4E2M1FN | 1489→1532 | 4→8 | 125→129 |
| 14 | 16 | 2 | 256 | 1 | Float4E2M1FN | 1469→1522 | 4→8 | 126→130 |
| 16 | 16 | 2 | 128 | 1 | Float8E4M3FN | 1769→1859 | 4→16 | 163→171 |
| 18 | 16 | 2 | 128 | 1 | Float8E4M3FN | 1769→1859 | 4→16 | 163→171 |
| 20 | 16 | 2 | 512 | 1 | Float4E2M1FN | 1435→1460 | 4→4 | 145→147 |
| 22 | 16 | 2 | 512 | 1 | Float4E2M1FN | 1450→1470 | 4→4 | 146→148 |
| 24 | 16 | 2 | 256 | 1 | Float8E4M3FN | 1601→1651 | 4→8 | 162→166 |
| 26 | 16 | 2 | 256 | 1 | Float8E4M3FN | 1601→1651 | 4→8 | 162→166 |
| 28 | 256 | 1 | 256 | 1 | Float4E2M1FN | 5816→5380 | 64→8 | 107→111 |
| 30 | 256 | 1 | 256 | 1 | Float4E2M1FN | 5954→5540 | 64→8 | 107→111 |
| 32 | 256 | 1 | 128 | 1 | Float8E4M3FN | 5853→5802 | 64→16 | 142→158 |
| 34 | 256 | 1 | 128 | 1 | Float8E4M3FN | 5853→5802 | 64→16 | 142→158 |
| 36 | 128 | 2 | 256 | 2 | Float4E2M1FN | 5644→5645 | 16→8 | 128→132 |
| 38 | 128 | 2 | 256 | 2 | Float4E2M1FN | 5820→5821 | 16→8 | 128→132 |
| 40 | 128 | 2 | 128 | 2 | Float8E4M3FN | 6186→6227 | 16→16 | 176→184 |
| 42 | 128 | 2 | 128 | 2 | Float8E4M3FN | 6186→6227 | 16→16 | 176→184 |

Instruction counts cover the whole generated kernel and are static, not dynamic execution counts. Branch counts include its other roles. Codegen uses keep-PTX/CUBIN and uncached compile for inspection; no codegen timings enter performance results. Runtime benchmark phases use normal compilation/caches.

Paired gate source is bound to the clean retained475 tree via513 file hashes. Remote source retains its actual1b0 Git parent plus the measured475 patch; candidate adds only this experiment. Source materialization first stopped before GPU work for a missing new shared-PTX file, then test-path setup and the standard source-data link were corrected. Failed receipts remain separate; all successful23-case gates are complete.

Archive `bc40fd2c264f599c36ef082e39146f5ecb335551da9871cf0a805e16de6d300b` contains288 verified files including FC1 PTX/SASS; all cubins and original dumps remain in persistent remote storage. No source was committed or pushed.
