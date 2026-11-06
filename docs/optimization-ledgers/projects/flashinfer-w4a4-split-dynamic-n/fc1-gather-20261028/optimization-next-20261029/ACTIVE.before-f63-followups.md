# Active optimization handoff — 2026-10-29

Keep optimizing fork PR8 until the user stops. Include swap-AB and W4A16 no-standalone-FC1-permutation, four models, EP/TP, supported dtypes. Leave upstream PR7290 untouched. No sanitizer during iterations. Keep active source changes unstaged in separate review copies; retire rejected copies after preserving evidence.

## Retained and published

Canonical `flashinfer-fc1-gather-review` is clean at `475cae6b28a536e24aa8da2ed488d0f00fb5305b`, pushed to `zianglih/flashinfer:codex/fc1-gather-warpgroup`. W4 gather is the fifth/last WG; FC2 remains four WGs. Quotas144/80/96/96/64; swap120/256/128. Latest follow-up preserves source-bound514-file equivalence,40 integration exact cases plus6 alignment cases,17 swap exact and byte-identical shared-helper SASS samples.

PR8 title/body/EP+TP heatmaps refreshed: `composed-w4/publication/receipt.json`; bodySHA21fcd12b91ffa15a9e2e7eca0dc3ae403d7185cfda6e2b18e3fad37fd9744a27, assets378e59a3a9b614c23619f23b12433bfc747b17d3.468raw/396displayed cells vs saved d35: EP+0.65%,TP+5.25%; cross-GPU-instance limitation explicit. Separate W4 same-GPU104cell comparison vs old permutation: EPprefill+0.53%,TPprefill+20.79%, excluding1/2. Prefill=4096–16384, middle128–512,decode4–64. Do not use the obsolete17.30%prefill figure that included512.

## Current work / GPU ownership

| GPU | Owner | Work |
|---|---|---|
|0,2|w4a16_table_audit|Per-token quantizer CTA width follows usefulSF blocks; exact/codegen gate, then bounded performance.|
|1|root|Unsigned swap gather-warp offset:17exact passed,12cell CAAC screen running.|
|3,4,6|external_gap_audit|W4 live-group loop rejected; freezing final10cell evidence, then source audit for alternative low-overhead pruning. Check agent before GPU reuse.|
|5,7|full_bench_audit|Swap live loops rejected/frozen; read-only SF/payload coordinate reuse audit. GPUs released.|

Active source copies besides canonical:
- `flashinfer-fc1-gather-unsigned-review`: one-line Uint32 offset,475 base. `swap-gather-unsigned/` has paired codegen and active screen. Fewer MOV.SPILL uniform-register transfers, slightly more other instructions; zero local bytes. No speedup claim yet.
- `flashinfer-per-token-width-review`: quantizer geometry candidate, owned by tableagent.
- W4 live-group copy is being retired by its owner after evidence freeze; any successor must be a distinct active experiment.

## Recent decisions

- Swap live-group loop rejected: prefillGM−7.07%; row-outer reuse follow-up still−1.34%N3U EP and no robust general win.23exact, allFC2cubins unchanged, zero local. `live-groups/`, `live-groups-row-outer/` retain evidence; copies retired.
- W4 live-group row-outer candidate passes40exact and reduces static instructions/branches but stable V3EP4K−10.30%,N3UEP4K−5.37%; no retention. Avoid new runtime loop permutations without a different dataflow.
- Earlier unrolled live-row predicates also rejected; PTX predication increased branches. Read `live-rows/RESULTS.md` and `pipeline-audit.md` before repeating this direction.
- Row pruning saves issue/SMEM zero-fill/completion work, not corresponding HBM reads: invalid rows already use descriptor OOB fill.
- W4K3 fixed1500MHz diagnostic confirms residual FC1 gather overhead (4K−3.70%,8K−1.94%), FC2/combine neutral. GPU6 automatic clocks restored and verified. This diagnostic is not public stock-clock evidence.
- N3UTP16K per-token quantizer exposes~641us of1957us chain. Matched geometry CLC on is+3.122% vs off; exposedquantizer unchanged. TRTLLMper-token also has an intermediate standalonequantizer, so stageexistencealone is not the gap.
- Actual-route default tuning rejected earlier by dummy-warmup holdout. Routes are absent from cache keys; no first-call-route policy or new tactic axis.
- NCU hangs on trivial allocation on both old/new boxes; no hardware counters, do not retry routinely. Use CUPTI/SASS/iKET/NSYS.

## Runtime

Managed `/usr/local/bin/h`, cwd `/Users/ziangli/rl/hai`; wrapper `optimization-20261028/swap-ab-hybrid-output/remote_box.py`. Healthy C3 box `fi-gather-opt-1029`,namespaceziangli,8B300,explicitimage`nvcr.io/nvidia/pytorch:26.05-py3`,CUDA13.2,CuTeDSL4.8.0. Old1028 box disappeared; `/data` persisted.

Remote parent `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/fc1-gather-20261028`; active work under`optimization-next-20261029`. Native C++cache`compile`; explicitDSLcache`compile/cute-dsl-4.8.0-cuda13.2-sm103`. Retain caches; never mutate in-flight environments. Read-only telemetry helper at`optimization-next-20261029/w4a16-k3-clock-profile/nvml_clock_wrapper.py`,SHAe3f080d2461a8c2b9c558174f39cd34e157ae766b3f7943f01413a63bd3ee6cd. CUPTI and perf_counter epochs differ; use calibration.

Public GH operations: switch and verifyzianglih each batch, noauthsetup-git. Verify existing body receipt before editing; never put memory citations in PR. Original detailed handoff retained in`ACTIVE.before-475-followups.md`; olderREADME entries are historical, not current status.
