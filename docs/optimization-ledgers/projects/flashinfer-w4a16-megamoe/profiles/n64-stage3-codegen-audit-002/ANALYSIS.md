# N64 third decoded-stage codegen audit

Both M256/N64 and M128/N64 third-stage captures agree with the intended TMEM and pipeline layout. There is no new register, local-memory or generated barrier discrepancy. This is CPU-only inspection of existing artifacts; it does not replace numerical tests or establish a performance gain.

## Captures and source provenance

The audit compares `tmem-m256n64-codegen-001` / `tmem-m128n64-codegen-001` (two decoded stages) with `tmem-m256n64-transform3-codegen-002` / `tmem-m128n64-transform3-codegen-002` (three). All use global4096, EP8, the DSV3 H7168/I2048/E256/topk8 workload, K256, raw depth5, exactly two transform groups, flag4, group512, atomic scheduling, epilogue token return and epilogue flags `(2,4)`. Physical cluster is `(2,1,1)`: explicit in the older captures, defaulted by frozen stage3 `frontend.py:35` in the new ones. M256 uses CTA-group2 instructions; M128 uses CTA-group1 inside that physical two-CTA cluster.

- Stage2 kernel SHA256: `5ea9b59f882cef50e6da6c915295acaa626b92331f4fb592c0744b47628de866`.
- Stage3 kernel: `34bbdfba91e4743a7079d436c3181e3825ca771fe584f910c4ee1c37a4165152`.
- Frontend changed from `c358d4abf33de293101b67a5bceead1ca820140a84b916168d33eff4b465aa93` to `23692ad82f4e86b4d9015541066ad09b3b8c1e7a26ba05cfefe45eb2d3fe09c3`.
- Benchmark changed from `681cb0f8f4b2819068a69b3b69aabb0db697d8b2e6b0e18612a154adf2741f21` to `b4e845f3b43805e8056be2ac32dc87c452bed8211bfe612f74b04feb65681a09`.
- Epilogue, dynamic BF16 helper, reused local W4A16 helper and capture-script hashes match between captures. Full hashes and source deltas are in `comparisons.json` and the copied provenance logs. Frozen kernel/frontend/epilogue files are in `source-5ea9/` and `source-34bb/`; the helper verifies their hashes against each capture.

The captures ran in different devbox sessions with lineinfo enabled. Their logs explicitly exclude timing from performance evidence. Do not interpret the diagnostic benchmark rows or the different frontend/benchmark versions as a matched performance A/B.

## All-rank resources and binary consistency

| Geometry | Decoded stages | Registers | Stack | Resource LOCAL | SASS LDL/STL | Total static instructions | NOP | Non-NOP | MMA atoms / TMEM stores |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M256/N64 |2|96|0|0|0|5504|106|5398|16 /28|
| M256/N64 |3|96|0|0|0|5520|104|5416|16 /28|
| M128/N64 |2|96|0|0|0|5344|96|5248|16 /28|
| M128/N64 |3|96|0|0|0|5368|102|5266|16 /28|

Every row is verified for all eight ranks from the original `resources.txt`, PTX and SASS. Within each capture, all eight PTX files, all eight SASS files and all eight cubins are byte-identical. Every rank has no PTX local depot and no local-memory instructions anywhere, including transform and epilogue.

All four binaries require640 threads and retain register directives control80 / transform80 / epilogue176 / dispatch64. Both transform groups share the same uniform branch. The established pool remains `128*(176+80+64+80+80)=61440=640*96`; the third stage has no increased register-pool demand. No claim about absence of execution contention follows from this static result.

The third-stage binaries each add exactly18 non-NOP instructions. The opcode deltas are identical between geometries, except NOP padding: 3 branches, 2 moves, 1 shift, 2 barrier initializations, 1 blocking phase-check, 2 try-waits, 1 nanosleep, and 6 uniform arithmetic/select operations. No MMA, TMEM store, dequantization or global/shared load opcode count changes. Static text counts are not dynamic work or timing.

Resource `SHARED:1024` is not observed launch dynamic shared-memory usage: PTX declares external shared storage with1024-byte alignment. Generated raw-A/SF/B offsets remain58880/140800/151040 in both stage3 geometries, matching stage2. B stages remain16384 bytes per CTA for M256 or32768 for M128; the resulting last allocation ends at183808 or216576 bytes, respectively, consistent with the previously CPU-validated fitter. These captures do not provide launch-attribute measurements; do not add1024 to those sizes.

## TMEM and MMA operands

All PTX references below use the original line numbers preserved in this directory's numbered rank0 PTX copies. The audit independently checks the anchors against each new file, rather than carrying over old PCs.

Both new binaries allocate/free512 TMEM columns (M256 lines339–340 /6634–6635; M128319–320 /6466–6467). The two accumulator stages occupy columns0–127 at64-column pitch. Decoded A starts at128 with128-column stage pitch: stage0=128–255, stage1=256–383, stage2=384–511. The third stage fills the previously unused128 columns and stays within the same allocation.

| Generated evidence | M256/N64 stage3 PTX | M128/N64 stage3 PTX |
|---|---:|---:|
| Transform destination base +128 |2714|2602|
| FC1 /FC2 transform stage `<<7` |3454 /4218|3339 /4094|
| MMA A base +128 |4568|4435|
| Accumulator stage `<<6` |4604|4467|
| MMA A stage `<<7` |4658|4517|
| B stage in 16-byte descriptor units |4662 (`<<10`)|4521 (`<<11`)|
| First /last K16 MMA |4682 /5027|4541 /4886|

Each FC transform branch still has eight `tcgen05.st...x8` instructions, covering the two groups' disjoint64-column portions of a decoded stage. Twelve additional TMEM stores belong to epilogue scratch. All16 MMA atoms consume TMEM A and SMEM B with non-blockscaled BF16 operands and FP32 accumulation. The first atom disables accumulation at outer K tile0; subsequent atoms accumulate. Runtime valid-token N still uses the BF16 descriptor base `0x10000490` (M256) or `0x08000490` (M128), with fixed N64 storage pitch. The audit exhaustively checks descriptor rounding for valid tokens1–64.

M256 retains the leader-only MMA guard at4574–4583 and both FC nonleader B shifts `align16(valid)/2-32` at2335–2347 and2481–2493. M128 has no physical-CTA skip in its MMA work loop; its activation TMA uses multicast mask3 in both phases (2323–2350 /2444–2471), and each CTA issues its own group1 MMA. The epilogue source hash is unchanged.

## Barrier counts, phase wrap and persistent state

The helper verifies the complete ordered initialization prefix, rather than just counting barriers:

| Ring | Full offsets | Empty offsets | M256 full /empty arrivals | M128 full /empty arrivals |
|---|---|---|---|---|
| Raw5 |0,8,16,24,32|40,48,56,64,72|1 /8|1 /8|
| Decoded3 |80,88,96|104,112,120|512 /1|256 /1|
| Activation2 |128,136|144,152|1 /1|1 /2|
| Accumulator2 |160,168|176,184|1 /256|1 /128|

Thus the extra decoded full/empty pair shifts all later storage references by16 bytes while preserving the counts required by V2 versus V1. TMEM retrieve is still `bar.sync 2,416` (M256347/M128327), dispatch-to-scheduler160, and the final communication barrier640. The frozen source preserves scheduler/communication participant counts and both groups' local thread indexing.

Producer FC1 and FC2 and the MMA A consumer all advance using `add1; compare==3; select0; XOR phase on wrap`. Activation and accumulator still compare2. Verified wrap anchors are:

- M256 producer3556–3560 /4379–4383; MMA5049–5053. Producer/consumer work backedges4436 /5119 jump after initialization, preserving stage and phase.
- M128 producer3432–3436 /4246–4250; MMA4908–4912. Backedges4303 /4977 likewise retain state.

Only per-work K counts reset. The FC branch transition does not reset decoded stage or phase; source `kernel.py:1197–1224` and1236–1274 preserves the same state objects. For example, a sequential28-K-tile FC1 followed by8-K-tile FC2 progresses index0→1→0, toggling phase9 then3 times. It must not reset to index0 at the phase switch.

The producer tail now contains three distinct empty-stage waits at M2564448/4471/4494 or M1284315/4338/4361. Its two tail advances also wrap at3 and update parity. MMA release targets decoded-empty offset104, activation-empty144, and accumulator-full160, corroborating the shifted initialization. No modulo-two assumption survives in the decoded ring.

## Reproduction and limits

Run `python3 audit_n64_stage3_codegen.py` from the effort root. It reads existing artifacts, validates32 rank records, checks all-rank hashes, provenance, resources, barrier initialization, MMA kinds, TMEM allocation, descriptor arithmetic and independently traced stage3 PTX anchors, and writes `analysis.json`, `comparisons.json`, `ranks.csv`, frozen sources and numbered PTX. Ruff and Python syntax validation pass.

No GPU work or active repository edits were performed. Captures cover this full-model shape, epilogue token return and atomic scheduling. Small K/output tails, odd routing tails, both return modes, alternate scheduling, repeated graph execution and numerical accuracy remain independent test gates. Static absence of spills establishes no local-memory traffic in these binaries; it does not establish latency or lack of contention.
