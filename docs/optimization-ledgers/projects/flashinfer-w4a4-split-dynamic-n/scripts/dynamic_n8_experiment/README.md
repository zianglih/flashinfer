# Descriptor-only N8 decode experiment

Closed without retention. Independent `flashinfer-dynamic-n8-review` is based on
`98fd3566b5f945c100f48cddacf25deb2432cbc2` and keeps one unstaged core change.
One-CTA dynamic MMA N rounds live tokens to eight; two-CTA stays at sixteen.
Allocation, tactics, weight layout, preparation, epilogue and arithmetic are
unchanged. Group-1 N8 is supported by the official CuTe4.7 blockscaled operation
shape contract and appears in the current TRT-LLM decode cubins. Reducing
instruction N does not reduce the weight stream or the allocated epilogue work.

## Evidence and decision

C1 B200 GPU2, UUID `GPU-894104cd-e66f-26ec-9d60-cc820c38ebc5`, image
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe4.7.1. Native benchmark inputs,
seed42, H7168/I2048/top-k8, 256 experts/32 local, per-tensor NVFP4, unfused
finalize. Same-process control/variant/control followed by variant/control/variant.
Each arm uses ten warmups and 100 cold-L2 CUDA-graph CUPTI samples. Fixed route
N16 and M128/one-CTA for both GEMMs; no AUTO or primary retention rerun.

| Tokens | Whole chain control / variant | FC1 wrapper control / variant | FC2 control / variant |
|---:|---:|---:|---:|
|4|1.000004|1.001308|0.999345|
|32|1.000954|0.999286|0.999700|
|128|1.002535|0.999348|1.002673|
|512|0.999228|0.997604|0.997632|

Each ratio uses the geometric means of three control and three variant medians.
All 72 arms match output bytes before and after timing, including FC1 output and
SF buffers initialized identically. All 7,200 individual samples are preserved.
FC1 wrapper includes unchanged preparation; isolated phase times are not
additive. This is paired compatibility coverage, not an independent reference
proof or exhaustive invalid-TMEM/exceptional-value coverage.

There is no consistent whole-chain gain. The small T128 difference does not
justify retention; no wider-format or rigorous validation campaign was launched.
The source remains unstaged for review. A narrower epilogue is a separate
experiment and may later justify composing N8 with reduced accumulator work.

Raw control and variant medians are in
`evidence/dynamic-n8-98fd/summary.json`; the archive includes all samples, logs,
source, helpers, source hashes and final unstaged-state verification. Archive
SHA256 `2f71ef964a9ae7010b503313e409171a576cd41e03094b83e4ec01d16c9b74e5`.

## Commands

The first T32 ABA arm used `probe_native.py` directly. Remaining arms used
`run_remaining.sh`; both refuse to overwrite output records. `archive.py` fetches
the completed records and computes the summary without running GPU work.
