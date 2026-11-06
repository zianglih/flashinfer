# Merged131 operand ring — bounded experiment

**Unretained recommendation: full-chain performance is neutral.** The candidate removes a duplicate full/empty operand pipeline while retaining distributed TMA issuance, but its small FC2 phase gain does not produce a useful full-chain improvement at both decode shapes. No production changes, source commits, primary benchmark, PDL changes, epilogue changes, or register sweep.

## Source and synchronization contract

Base `aab93f854054de834447bdd8985b8bbd653fb3c8`; independent unstaged clone `../../flashinfer-merged-operand-ring-review`. Final core SHA256 `53f3b78bd602058d6b57e50a809241b35af97771cc3664ddbfc16487389ab176`; [patch](source.patch) SHA256 `07e6dd9dff31217d140381bd5b867164ac72bbd45cecdc746b8aa21ac2086bfa`. Control is the fresh read-only remote `profile-aab93f`, core `7c0fe69faab5acecafdd3d67a157f016836e149fafdc29942542d44ef4852c66`.

The eligible branch is one CTA, non-TMA SFB (N<128), dedicated overlap epilogue. Warp0 issues A, warp1 SFA, warp2 B; all128 existing producer threads retain their original SFB cp.async copies. One full phase counts131 arrivals: three internally elected TMA issuers, each atomically announcing its own bytes before transfer, plus128 unelected asynchronous per-thread SF completions. All producers wait the same empty phase. MMA waits one full phase, retains the SF async.shared proxy fence, copies SF, issues MMA, and releases one common empty phase. Warp0 alone drains the wait-only tail; the whole-CTA final join remains. Stage/SMEM/TMEM layouts, arithmetic, static scheduler,288-thread roles, PDL and epilogue remain unchanged. Unused AB storage stays allocated.

[Full lifetime audit](../epilogue_codesign_audit/PIPELINE_SYNC.md), [independent source/codegen review](PEER_REVIEW.md), and [PTX proof](ptx-ordering-proof.json) document the happens-before chain. The CPU progress proof covers3,483 arrival/transaction states. Installed CuTe4.7.1 source hashes pin election and `.noinc` lowering. The enabled scope also includes eligible other formats and N32/N64, but those branches were **not** newly GPU-tested after this neutral screen.

## Compile and exact results

Initial source `5d3a2b89…` failed compile-only: CuTe did not expose `expected_bytes` assigned in staged runtime branches outside those branches. No kernel launched. `failed-r1/`, codegen-r1.log and the archive preserve the failure. Final source puts `arrive_and_expect_tx` directly inside each explicit warp branch, eliminating the undefined phi without an implicit default.

Final PTX initializes four full stages to131 and four empty stages to1. Three elected arrival sites announce32768/4096/8192 bytes for A/SFA/B; all128 producer threads reach the single SF `.noinc` site. One joint wait precedes the retained proxy fence and SF/MMA work; one TCGEN operand-empty commit follows the MMAs. The other TCGEN commit is accumulator-full completion. The four-slot producer tail has no additional arrival or transaction expectation.

Resources:197,504B dynamic SMEM,288 threads,64 registers,0 local bytes,128 TMEM columns,4 operand stages,2 accumulator stages,1 active CTA/SM. Same control resources. Static FC1 N16 SASS sites decreased1152→1120 total,79→71 branches and68→44 SYNCS;8 LDGSTS and5 UTMA sites remain. [Comparison receipt](static-codegen-comparison.json) uses an archived control compile with byte-identical aab core and helpers. These are static sites from separate compile epochs, not executed instruction counts or causal profiling.

Seven current-control/candidate pairs passed exact full-buffer output/SF hashes: K64/384/1216,17/33 live routed rows, quantized/per-token BF16, and zero routes. Original SF poison guards and invalid output bytes were preserved. Native T32/T128 full output and FC1/FC2 initialized full-buffer outputs matched before and after each timed arm, with input/source hashes unchanged. No sanitizer or broad format sweep was run for this unretained candidate.

## Same-input native screen

NVIDIA B200 on c1 `fi-w4a4-narrow-1025`, GPU3 UUID `GPU-8f15506e-8209-ef53-6b00-b04ece9e69d3`; image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.78, CuTe4.7.1. Actual `bench_moe_deepseek` inputs, NVFP4,32 local experts, unfused finalize, fixed N16/M128/1CTA for both FC1/FC2. T32 produced21 route tiles; T128 produced30. Both arms share the same actual routing within each process.

Each shape ran A-B-A-B-A-B (ABA then BAB),10 warmups and100 cold-L2 CUDA-graph CUPTI samples per arm. Observer capture was disabled during full-chain timing; FC1 phase includes regular preparation, and isolated phase times are not additive. Private CuTe cache; unchanged native cache epoch.12 full-chain arms plus24 phase arms =3,600 retained samples. Ratios below are geometric means of the three control medians divided by the three candidate medians.

|Tokens|Scope|Control medians, µs|Candidate medians, µs|Control/candidate|
|---:|---|---|---|---:|
|32|full|106.0800, 106.4320, 106.1600|106.5920, 106.3680, 106.1760|0.998546×|
|32|fc1|66.0480, 66.3200, 66.8640|66.4800, 66.5595, 66.2720|0.999590×|
|32|fc2|35.4400, 35.5200, 35.4240|35.3280, 35.3440, 35.3600|1.003319×|
|128|full|143.9360, 143.8720, 143.7765|143.7440, 143.5680, 143.6325|1.001485×|
|128|fc1|89.7760, 89.9200, 90.2400|90.1285, 89.9520, 89.9045|0.999817×|
|128|fc2|48.0000, 48.0965, 48.0475|47.7440, 47.7760, 47.9205|1.004905×|

Full-chain changes are +0.146% time at T32 and−0.148% at T128. FC2 improves0.33%/0.49%, while FC1 stays neutral. This screen does not justify retention or further broad validation. No inference about TRT or old-node absolute timing is made.

## Reproduction and archive

Source the existing `scripts/recovery442/env_candidate.sh` on the devbox before each process. GPU3 only, with `CUTE_DSL_CACHE_DIR=/workspace/flashinfer-w4a4-split-dynamic-n/cache/merged-operand-ring-aab`. [compile_resources.py](compile_resources.py) performs compile/resource inspection without launch. [probe_exact.py](probe_exact.py) is the unchanged seven-case oracle except for source-manifest adaptation. [probe_native.py](probe_native.py) imports actual candidate source, preserves the established graph/CUPTI protocol, and guards source/input/output bytes. [run_native.py](run_native.py) requires the seven paired receipts to match before timing. [collect.py](collect.py) verifies and archives all samples, source hashes and failures.

`build.py` records the first pre-compile source epoch; the final authoritative reconstruction is baseaab plus `source.patch` (or exact `selected_core.py`). `upload-r2/apply_epoch.py` documents the checked compile-scope repair. Frozen `manifest.json` retains its creation-time `gpu_executed:false` field; completed execution is recorded separately in the results and never changes the timing source manifest.

Verified archive: [raw.tar.gz](../../evidence/merged-operand-ring-aab/raw.tar.gz), SHA256 `aca17a807bbfab95de9fbd326151ff94ab7fdf39eeb652b93a12de37b16cb93f`. [summary.json](../../evidence/merged-operand-ring-aab/summary.json) and its raw directory retain all36 arms/3,600 samples, seven exact pairs, failed compile, codegen, resources, source/environment receipt, helpers and candidate/control source. GPU3 was released after the screen; no further GPU work is planned.
