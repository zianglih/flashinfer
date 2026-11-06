# PDL frozen-source component isolation

Core-only reproduces wide prefill regression; preparation-only is nearneutral atT16384. Both provide decode gains independently; not retention evidence.

|Component|Tokens|Phase|Control medians (us)|Candidate medians (us)|Control/candidate|
|---|---:|---|---|---|---:|
|prepare|4|full_chain|49.8880, 49.8885, 49.7760|48.8000, 49.1360, 49.3925|1.015107x|
|prepare|4|fc1|28.8805, 29.2965, 29.3125|28.1920, 28.2880, 28.0805|1.034618x|
|prepare|4|fc2|16.1920, 16.1600, 16.1760|16.1280, 16.2080, 16.1600|1.000662x|
|prepare|16384|full_chain|484.4170, 482.0175, 481.5050|481.6815, 492.5770, 480.8015|0.995163x|
|prepare|16384|fc1|220.6570, 224.8325, 233.7930|223.4890, 225.5845, 223.9365|1.009034x|
|prepare|16384|fc2|133.3770, 133.4245, 133.5360|133.4885, 133.5365, 133.6000|0.999282x|
|core|4|full_chain|49.7285, 49.8560, 49.6960|48.1765, 48.4800, 48.6400|1.027427x|
|core|4|fc1|28.7840, 29.2800, 29.4080|29.1200, 29.2480, 29.1200|0.999777x|
|core|4|fc2|16.1600, 16.1600, 16.1600|16.2240, 16.1920, 16.1600|0.998025x|
|core|16384|full_chain|483.6975, 483.2815, 483.5530|546.7375, 547.5690, 545.2500|0.884711x|
|core|16384|fc1|220.3685, 229.4245, 224.8160|282.2890, 276.4170, 282.5445|0.801845x|
|core|16384|fc2|133.4880, 133.6000, 133.5685|138.3520, 138.3685, 138.3840|0.965194x|

Same frozen corrected-aab/PDL source components. `prepare` binds candidate preparation and aab core/utils/finalizer. `core` binds candidate core with aab preparation/finalizer. Every component actual source path/hash and independently loaded prep/finalizer module/cache are recorded. No source change or fullyearly rerun.

All72 phase/full-chain arms and7200samples passed exact pre/post checks. Six arms ABA/BAB percomponent/token,10warmups/100cold-L2 CUDAgraph/CUPTI, same native routing/input. N16T4 andN256T16384, GPU2B200-92 onlyadjacent controls. FC1includespreparation and excludesFC2, providing an independent discriminator.

The separate trace shows candidate wideFC1 already exceeds control duration before downstreamFC2 starts; generated FC1 registers80→88 are a concrete lead. This archive itself measures no timeline or codegen. Do not attribute the loss to generic resource contention without additional evidence.

Next parent-authorized actual-source candidate restores FC1 all-thread trigger organization at the same early point, preserving FC2 elected device-release/trigger and candidate preparation. No production change.

Immutable raw SHA `d72d8b9180fbafadc7a0434ed1401edd6deeece038b39dd6371c79c2f99617f0`. All medians recomputed from100samples; source and per-component ownership receipts verified locally.
