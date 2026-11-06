# Corrected two-transform-group codegen review

Capture `profiles/tmem-raw5-transform2-codegen-002` completed its production warmup on all eight ranks and its parent exited 0. The instrumented single-event result is excluded from performance. Numerical validation and ordinary paired timing are separate gates owned by root.

The kernel source snapshot matches SHA256 `8ca2c45217c9d07680adf3fb4f670eb8ec3acbd04be84c779253513be8f0b9d6`. The corrected run retains raw depth 5, two transformed-A stages, M256/N128/K256 dynamic N, flag4-epi scheduling and two transform groups. Snapshots and provenance are under `profiles/codegen-comparison/raw5-transform2-corrected-sources/` and `logs/tmem-raw5-transform2-codegen-002.provenance.log`.

All eight cubins report:

| Property | Corrected capture |
| --- | --- |
| Required threads |640 ×1 ×1|
| Launch register allocation |96/thread|
| Stack |112 bytes|
| Reported LOCAL/static SHARED |0/1024 bytes|
| PTX local depot |96 bytes|
| Static PTX local loads/stores |40|
| Static SASS local loads/stores |21|
| Static SASS instructions |5672|

The local instructions remain 8 STL.64, 8 STL, 1 LDL.128 and 4 LDL.64. Nineteen source annotations map directly to the existing FC2 output router; two remain helper/source-anchor annotations within its pointer/validity-array sequence. No transform-attributed local operation appears after lowering its register target, and no additional local footprint appears elsewhere. Source-attributed transform instructions mention registers through R58; this is an audit hint, not a liveness measure.

The generated register-control sites are now:

| SASS PC | Target | Source condition | Meaning |
| --- | --- | --- | --- |
|0x0f70|decrease80|`warp >=4 and warp <8`|One uniform control-warpgroup site|
|0x5d10|decrease80|`warp >=12`|Both complete transform warpgroups|
|0x8fa0|increase176|`warp <4`|Epilogue warpgroup|
|0xcbf0|decrease64|`warp >=8 and warp <12`|Dispatch warpgroup|

The targets consume `128×(176+80+64+80+80)=61,440` registers, matching the `640×96` CTA launch allocation. The failed 001 candidate remains preserved separately; it required 65,536 registers and stalled in the epilogue allocation loop. The successful corrected warmup resolves that observed liveness failure without adding implicit transform local storage.

Detailed per-rank SASS/PTX sites, role attribution and comparisons against one-group raw5 and failed 001 are in `profiles/codegen-comparison/transform2-corrected.json` and `.md`. Reproduce with:

```bash
python3 compare_public_codegen.py \
  profiles/codegen-comparison/transform2-corrected.config.json \
  --output profiles/codegen-comparison/transform2-corrected.json
```

Before choosing producer count, the ordinary one-group control also needs the uniform control-site correction and an adjacent timing run. Changing that correctness detail only in the two-group arm would obscure the performance comparison. Root has scheduled that matched control; neither codegen event timing nor static instruction count is a performance result.
