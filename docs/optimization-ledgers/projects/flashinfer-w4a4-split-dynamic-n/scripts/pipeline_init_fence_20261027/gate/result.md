# Independent initialization-fence gate: pass

Frozen patch `5112a25e2c70c5aec5cfdef0bbef02f1da22a08f2ad6b9240b0025c64a6753f6` against clean `9b4721b08057d0a488c1f0236467acb75c48cd00`. The candidate contains only pipeline initialization-fence consolidation, with no TMEM experiment changes.

All 64 CLC and 24 static exact replays per source pass across 32 + 12 core pairs. Coverage includes all four formats,1/2CTA, FC1/FC2, PDL off/on, route changes and empty routes. Static cases 0/1/8 cover one-CTA inline, one-CTA overlap and two-CTA overlap. Geometry, pipeline stages, shared storage, TMEM allocation and UMMA commits match controls. Registers are unchanged in all 44 core pairs, with no local-memory spills.

CLC static instruction count falls by 240 summed sites; static kernels fall by 55. Actual-source SASS removes 1–14 startup sites per core before the first TMEM allocation atomic, with 0–10 fewer non-NOP startup instructions. All44 post-init opcode streams match; 37 also match operands after control-flow relocation. The remaining seven have operand allocation differences, so full universal operand identity is not claimed. PTX initialization-fence counts fall by one or two per core. These are codegen observations, not dynamic instruction totals or measured end-to-end speedups.

Every control was reused on the same GPU. CLC controls use the unchanged original helper SHA `1ec42450323d8448ae3111e846690bd6b98e3318451e0a1c3e413f015ad9124c`; static controls use the repaired TMEM V2 helper SHA `c9177aef87dd3bd5b41653f649671799855acded26276877513503d12fde4234` and completed cases 0/1/8. Launch receipts bind original receipt and result hashes. The failed pre-repair static attempt was not used. No control GPU run was repeated for this gate.

Evidence is in `evidence/gate-validation.json`, `evidence/artifact-manifest.json` (408 verified files), `launch.json`, and `actual-source-startup-codegen.json`. Candidate source and DSL cache were isolated; persistent native C++ compilation artifacts were retained. The separate 48-point public-path timing screen remains the performance boundary; sanitizer validation was not run.
