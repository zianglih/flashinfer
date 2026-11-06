# Scatter4 uniform issue refinement

Frozen r3 on retained cb35; the entire scatter4 family is now closed after the separate r4 refinement also failed retention. The r2 screen completed and is frozen under `../scatter4`; its remote source remains unchanged. Source hashes are in `source-local.json`.

Captured r2 SASS contains R2UR.OR/PLOP3 coordinate arbitration followed by backward BRA.U.ANY for each scatter4 command. This patch gives each of the four epilogue warps a compile-time loop of four-row groups. Every lane executes the coordinate broadcasts; one elected lane per warp issues both halves. The warp commits its group once after all row groups, preserving eight commands per issuer for64-token slabs and four for32-token slabs. All threads still execute the existing read waits and128-thread joins, so no source buffer may be reused before every issuer has finished reading it.

Invalid routed rows are initialized once to the positive output-row upper bound in the existing metadata pass. The bulk issue loop consumes these prevalidated coordinates without repeating per-row tail predicates. The private metadata helper preserves its old default0 for other paths. Scale expressions, source swizzle, shared capacity/stages, accumulator release, output allocation, combine, tactics, and all barriers/waits are unchanged.

Required gate: reuse the passed combined control and replay96 candidate graphs with exact output bytes; inspect48 core kernels and compare launch/stage geometry, spills, registers, and implicit TMA issue backedges. A performance screen is conditional on codegen actually removing the identified overhead. No sanitizer.


The96-comparison exact gate passed; all48 core pairs retain stage/launch geometry and have zero stack/local spills. All24 FC2 variants remove R2UR.OR and backward BRA.U.ANY arbitration loops. Static unrolling increases register pressure and code size: config4 control/r2/r3 registers99/124/167 and text26,624/28,416/31,488bytes; config5 registers150/180/193, text39,296/44,416/51,712bytes; config6 registers112/144/183, text29,568/35,200/43,776bytes. Full three-way code/resource/cubin-size evidence is in `gate-evidence/codegen-three-way.json`. Gate archive SHA256 `46b0b34e8a6d202519c4d82eff6d8aa87088d5886ad1a87f4c909cec7d0ee9fe`.

The same64-cell CAAC screen completed onGPUs0/2/3/4, unchanged native winners and100-sample CUPTI methodology. Source3e59f19e remains frozen. Sole-announcer is deliberately excluded so the comparison remains causal againstcb35. No baseline timing was rerun outside this matched local control.


R3 rejected: primary overall geometric change −0.167%, affected prefill −0.344%. All four MX family geometric means are negative (V3 −0.287%, V41F −0.321%, K3 −0.780%, N3U −0.221%); NV is mixed. Independent codegen audit in `../../producers/next-audit/scatter4-r3-review/` verifies all artifact/exact hashes and no lifetime blocker, but finds uniform-register-to-GPR MOV.SPILL/R2UR.FILL in18 of24 FC2 variants (15–94 static pairs), despite zero local-memory/stack spills. Full performance audit is under `../../scheduler/caac-audit/scatter4-r3/verified/`. R4 changes only the row-group unroll policy to reduce code and coordinate lifetimes; no further layout or synchronization experiment is folded into it.
