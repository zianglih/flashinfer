# W4 role-scoped TMEM allocation rendezvous

Status: rejected. The wait policy is dependency-correct and passes exact coverage, but the bounded screen and fresh K3 repeat are negative. No broadening, shape gating, quota change or retention.

Candidate: reduce TMEM pointer-publication barrier participants from640/512 to416 and place waits immediately before the three existing user-role pointer reads. MMAwarp4, including each nonleader CTA, epiloguewarps0–3 and DQwarps8–15 participate unconditionally before work loops. Weight, activation, scheduler and Gather4 roles bypass it. The full pipeline initialization wait, allocatorwarp0, PDL, pipeline phases/bytes, final epilogue join and paired-CTA free remain unchanged. See DESIGN.md for the pointer/dependency audit.

Source: logical retained control `6c6515f2f804af420661d95e4595b5663d7f92d1`,514-file hash-bound manifest. Control W4 kernel `b8f124f187ec169b101c56a72cce2732833b89bf6ef3b72eaa0695f7a04b5da7`; unstaged6+/2− candidate kernel `780725b675d6d952eb5173817b3c1e8196f7db95be10b05a44c729cd0bb61bef`. Remote materialized copies have actual Git HEAD `1b0f1f69acbb7e20055d5aaf76cc29c840779304`, distinguished from their logical source identities. No commit/push.

Validation:33 existing cases passed, no failures/errors/skips, including one/twoCTA, static/CLC, small N, route boundaries, partial/padded outputs, weight-scale updates, SiTU and GeGLU. All33 captured kernels are zero-local with no LDL/STL. Own-file pre-commit passes. No sanitizer.

Codegen: representative Gather4 N16/N128/N192 keeps registers and every opcode count except `BAR.SYNC.DEFER_BLOCKING`+2 and NOP−2. The old common barrier2,count640 becomes three role-local sites, each barrier2,count416; no new runtime role-dispatch predicate. All11 regular-TMA/non-gather captures similarly have only BAR+2/NOP−2 versus retained6c-equivalent FC2. Source/control provenance is explicit in `control-codegen-reuse.json` and `regular-codegen-comparison.json`. The prior lookahead candidate is used only as the unchanged FC2 reference, never as the Gather4 performance control.

Method: stock-clock B300 GPU3 (`GPU-828e523f-00a8-c70b-c818-2837a056cc49`), `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.1/CuTeDSL4.8.0, strict source-keyed persistent caches. C-A-A-C, frozen native W4 winners/routes, functional unfused swap-AB, cold-L2 CUDA graphs,10 warmups/100 strict CUPTI samples, no AUTO. Read-only2ms NVML. All source/route/winner/runtime/executable/CUPTI guards pass. No clocks/power settings changed.

Each phase latency is its100-sample median. Arm latency is the median of two phase medians (the arithmetic mean for two values), not a geometric mean. Gain is C/A−1. Repeat spread is max/min−1 within an arm. All original and repeat rows remain separate below.

| Run | Case | Tokens | C ms | A ms | Gain | C spread | A spread |
|---|---|---:|---:|---:|---:|---:|---:|
|Original|K3 EP8|4096|0.5597235|0.5787643|−3.290%|0.094%|5.060%|
|Original|K3 EP8|8192|1.0294625|1.0345985|−0.496%|0.627%|2.195%|
|Original|V3 TP8|8|0.0570565|0.0570083|+0.085%|0.056%|0.001%|
|Original|V3 TP8|4096|0.4797945|0.4794990|+0.062%|0.173%|0.338%|
|Fresh repeat|K3 EP8|4096|0.5593228|0.5738915|−2.539%|0.548%|5.376%|
|Fresh repeat|K3 EP8|8192|0.9397975|1.0238703|−8.211%|2.068%|1.117%|

C-A-A-C phase medians, milliseconds:

```
Original K3 EP8 4096: .5594600, .5930450, .5644835, .5599870
Original K3 EP8 8192: 1.0326790, 1.0233665, 1.0458305, 1.0262460
Original V3 TP8    8: .0570405, .0570085, .0570080, .0570725
Original V3 TP8 4096: .4802100, .4786905, .4803075, .4793790
Repeat   K3 EP8 4096: .5577940, .5889150, .5588680, .5608515
Repeat   K3 EP8 8192: .9494135, 1.0181820, 1.0295585, .9301815
```

K3 has pronounced within-phase slowdowns in the25-sample quartiles, so neither the magnitude nor every timing fluctuation is attributed solely to source. However, both8K repeat candidate medians exceed both control medians, and both campaigns have negative K3 signs. The clean structural change is not sufficient reason to retain that result. Do not replace these rows with a selected faster phase or combine phases across campaigns.

Read-only NVML shows variation: in the repeat, candidate8K windows report1462–2032MHz and1545–2032MHz, with reason4 samples; the last control also has reason4 samples and2017–2032MHz. Memory clock stays3996MHz. Coarse telemetry cannot identify the cause of every sample slowdown; changed utilization/power behavior from the candidate remains possible. No frequency-normalized or iso-clock speedup is claimed.

Artifacts: complete raw100-sample timings and CUPTI activities, quartiles, read-only NVML, immutable source/patch/winner receipts, exact logs/cubins, saved helper scripts. Original archive SHA256 `9c19675896c88f6249553c8112d5fefec743750af5b447f0becd76484745075f`,7,032,262 bytes. Repeat archive SHA256 `a3726ef41a70be308b4d9c6170ea5bdefb0d6d9ed4e16bff1a04cad9b65a4016`,2,503,556 bytes. Chunk and full hashes verified. Local review retired after all514 source hashes and exact patch equality were verified; remote immutable evidence remains. GPU3 verified idle and released.
