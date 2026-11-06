# Operand staging audit

The gather regression is not caused by a smaller operand ring. Executing the frozen source's host planner on all 112 scaled frozen benchmark cells (224 FC1/FC2 plans) gives exactly the same stage counts for retained d35, R3 and R4. Eight R3 compiled-kernel records match the derived K width, stages, accumulator count and TMEM columns exactly. The remaining plans are source-derived, not fresh compilations. No GPU activity was used.

FC1 has 2–11 stages: 2 cells at depth2,3 at depth3,38 at4,28 at5,11 at6,6 at8,7 at9,9 at10,8 at11. Every FC1 reserves only512 bytes of epilogue scratch. R4's extra8 bytes perstage never crosses an allocation boundary in these frozen tactics. Register count does not enter the stage planner; the sampled R3 FC1 cubins use70–88 registers with zero local/stack storage.

Representative MXFP4x8 prefill FC1 plans:

| Topology/model | M/N | Tile K | Stages | Bytes/stage | SF bytes/stage |
|---|---:|---:|---:|---:|---:|
| EP V3 / K3 |256/128|128|9|25,600|1,024|
| EP V41F |512/128|128|5|42,496|1,536|
| EP N3U / TP V3 |256/256|128|6|34,304|1,536|
| TP K3 |256/128|128|9|25,600|1,024|
| TP N3U |128/256|128|4|50,688|1,536|

`_operand_stage_capacity` fills the232,448-byte shared-memory budget after epilogue/metadata reservation; there is no fixed operand-stage cap. The separate accumulator ring is capped at two TMEM buffers and has a distinct early-release ownership constraint. The two depth2 FC1 cells use81,920 or110,592 bytes perstage, so a third stage cannot fit. The depth3 K3 NVFP4 cases use73,728 bytes perstage. These are capacity limits, not gather-specific policy.

A larger ring is therefore not the next justified change. Reducing SF metadata cannot buy another stage in these cells, and more staging would not remove R3's synchronous issue/completion bottleneck. R4 already removes that explicit wait. A later occupancy-oriented policy could use fewer stages for tiny reduction lengths, but producers can run across route tiles; capping to a single tile's K iterations could discard useful cross-tile lookahead and requires measurement. No stage cap, tactic, allocation or source change is proposed by this audit.

`stages.csv` contains all224 derived plans and byte breakdowns. `summary.json` binds frozen source and input hashes. The stage-count result is independent of CLC admission: both admission values were checked for every plan. This audit does not claim that the hardware keeps every allocated stage in flight or that staging explains the measured regression.
