# First-route metadata before PDL wait

Independent experiment, not yet retained. Base is frozen public full-capacity PDL integrationa92c on853a. Source copies are fully independent, changes unstaged. Production and prior experiments remain untouched.

- `flashinfer-pdl-first-metadata-review` / `evidence/pdl-first-metadata-r1`: preserved first draft. The gate failed during DSL staging because `valid` required an explicit initial value outside nested staged branches; no kernel execution occurred for that failing case.
- `flashinfer-pdl-first-metadata-r2-review` / `evidence/pdl-first-metadata-r2`: corrected Int32 initializers, patch `fb34e3e6ed0dfe871d7c1f34f513f3b7dfb0ec1b2159dc5f273acf3ceefea2eb`, core SHA `09bae49c7de305d7242588a41869924015f665f59951a4f0991b3810412da4ad`.

Only the common core differs froma92c. The supported static one-CTA prefetch path reads initial livecount/valid/expert/route origin beforewait and reuses them for the first tile in producer, epilogue and MMA roles. Expert loads are limited to roles that consume them. No alpha, weight, activation or scale payload traffic was added; B/SFB remainsafterwait. Subsequent persistent tiles load their own metadata normally; the first-tile reuse predicate is an explicit runtime cost to measure. No model/token threshold, scheduler change, new public flag, storage field or stage-policy change.

Scoped precommit passed. The unchanged actual-public chain gate passed324 changing-input/routing replays, includingzero-local work, threeformats, two-CTA fallback andPDL-off. Matching control/candidate namedK2304 NVN16 codegen each adds27 changing replays withSM reservation2 so subsequentpersistenttiles execute. All83source pins remain unchanged.

`control-codegen-review.json` verifies the movement rather than relying on source position: candidatebeforewait has livecount,limit,expert loads andvalid calculation, four45056Bstageacquires and12A/SFATMAs, noB/SFBload. AllFC1variants andFC2off/PDLoff PTX are byte-identical tocontrol. FC2On registers106→104,stack/local0,staticshared1024B unchanged. This is compiledH256/I2304 diagnostic geometry, not a claim of V41 model-register counts. Dynamic storage policy/types are source-identical; the resource dump does not report runtime dynamicSMEM.

Fixed full-chain screen uses actualV41 routes atT4/32/128/512, fixedN16/M128 forbothGEMMs, allthree affectedformats, C–A–A–C,10warmups/100cold-L2 CUDA-graph CUPTIsamples, same nativebenchmark/observer. Source,route,tactic,environment andcache hashes are checked perarm. W4A16 is an unchanged control column, excluded from affected aggregates. Timing artifacts live under `evidence/pdl-first-metadata-r2-fixed`; results are not a nativeAUTO retention campaign.

Reproducible task-local commands (unique destination directories, do not rerun over existing evidence):

```sh
python3 scripts/pdl_first_metadata_experiment/deploy_gate_r2.py
python3 scripts/pdl_first_metadata_experiment/deploy_codegen_r2.py
python3 scripts/pdl_first_metadata_experiment/deploy_control_codegen.py
python3 scripts/pdl_first_metadata_experiment/launch_fixed.py
python3 scripts/pdl_first_metadata_experiment/fetch_fixed.py
python3 scripts/pdl_first_metadata_experiment/summarize_fixed.py
```
