# Matched native NVFP4 phase profiles: a65d5b09 vs 13ca1475

Native actual top-k-8 routing,32localexperts, hidden7168, intermediate2048, frozen revision-specific input preparation. Same B200 GPU6,148SM, nvcr.io/nvidia/pytorch:26.05-py3, CUDA13.2, Nsight Compute2026.1.1, CuTe DSL4.7.1. No primary benchmark rerun. Each profile has3warm phase replays and one cudaProfilerStart/Stop gated call, full metric set/40replay passes. These durations are profiler replay observations, not substitute primary CUPTI timings. All retained phase replays byteexact; final canonical BF16 samples at stride257 are bitwise equal across revisions at8K(32rows) and16K(64rows), maxdifference0. Input payload hash and actual routing histogram match.

| Tokens | Phase | Old AUTO us | Current AUTO us | Old/current tensor-active elapsed% | Old/current DRAM read MB | Old/current LSU global-load requests |
|---:|---|---:|---:|---|---|---|
|8192|FC1|139.104|166.272|53.40 /35.95|585.163 /589.512|1503460 /603972|
|8192|FC2|88.544|96.128|40.20 /31.69|275.679 /274.941|31368 /697132|
|16384|FC1|223.040|293.952|69.13 /40.49|586.951 /638.440|2923876 /1113428|
|16384|FC2|127.264|164.192|56.88 /37.45|287.096 /284.481|31368 /1289444|

Saved AUTO tactics: old16K `(256,((256,256),(2,1),False),((256,256),(2,1),False))`; old8K `(128,((128,256),(1,1),False),((128,128),(1,2),False))`; current8K/16K `(128,((512,128),(2,1),False),((256,128),(2,1),False))`. `old8k` (without `auto`) is a separate N256 geometry control, excluded from table.

At16K current FC1 executes970528391168FP4tensorops vs1157493686272old (-16.15%) but takes31.8%longer. FC2 executes485264195584 vs578746843136. Lower active fractions are not solely a utilization measure: current dynamicN reduces padded arithmetic. Current FC1 SMmax/avgactivecycles1.099 vs1.036old; FC2 1.018 vs1.025. Current FC1 94registers and0localspillsectors vs168registers and78848load/2368store sectorsold. FC2 current124vs64registers and43.975Mvs16.694M SIMT instructions.

FC1 read paths must account for old payload cp.async.cg separately: old TMA1412.956MB + cache-access SF933.560MB + bypass payload933.560MB =3280.077MB; current TMA2866.282MB +cache-access SF933.560MB =3799.842MB (+15.85%). These are read-path/sector traffic counters, not HBM bytes and not logical useful payload. Current TMA op count1272320vs137984old combines Gather4 and regular loads. FC2 current activationSF adds128.221MB cache-access traffic, versus0old, and~41x LSU global-load requests. This motivates canonical-SFB TMA, which is possible without changing external layout or adding a payload intermediate.

Current FC1 major not-issued samples map to producer SF-ring empty and epilogue accumulator-full waits; MMA TMA-full and peer-relay-full waits each have29samples. This does not establish TMA issue saturation. Long-scoreboard labels at mbarrier predicate consumers cannot be interpreted as direct GMEM load misses. Source audit includes barrier offsets; iKET interval evidence is owned by the parallel pipeline investigation.

## Reproduction

See profile_phases.py and each outputJSON for immutable revision check,sourcehashes,tactic,routing,harnesshash andphaseinputcontracts. Old native extensions were warmed outsideNCU using a private FLASHINFER_WORKSPACE_BASE; shared candidate caches were never cleared or epoch-switched. Representative invocation from remote project:

```bash
CUDA_VISIBLE_DEVICES=6 ncu --set full --profile-from-start off --nvtx --force-overwrite -o logs/native-ncu/current16k-r2 .venv/bin/python scripts/native-ncu-comparison/profile_phases.py --repo candidate --expected-head 13ca1475d96839f3bf3c46699cc63204b4d3b409 --tokens 16384 --tactic '[128,[[512,128],[2,1],false],[[256,128],[2,1],false]]' --profile --output logs/native-ncu/current16k-r2.json --sample-output logs/native-ncu/current16k-r2-sample.pt
```

Source hashes in the output JSON are authoritative. Corrected harness pins output allocations and sentinel-fills padding before byte comparison. `current16k` first attempt used fresh output allocations and failed padding equality: superseded by `current16k-r2`; retained as diagnostic history. First coldoldNCU build stalled intercepting native fatbinary compilation and was stopped; `old16k-r2` used the subsequently warmed private cache and is valid. CSVs preserve per-column units; `old8k-auto` was exported in base units (nanoseconds/bytes), others have microseconds/MB. summary.json preserves those units explicitly.
