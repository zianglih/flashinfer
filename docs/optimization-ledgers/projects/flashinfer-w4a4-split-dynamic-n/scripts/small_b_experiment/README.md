# Physical B16 with five operand stages

Closed without retention. Independent `flashinfer-small-b-review`, base
`98fd3566b5f945c100f48cddacf25deb2432cbc2`, keeps one unstaged core change.
The B operand's physical TMA/SMEM extent follows route N16, while accumulator
allocation and the existing epilogue remain N32. The reduced B storage permits
five operand stages. All route tiles >=32 are source-equivalent to98fd. This
does not include descriptor N8, narrow epilogue, or early TMEM permit changes.

Native NVFP4 fixed-N16 diagnostics use GPU2 (B200 UUID
`GPU-894104cd-e66f-26ec-9d60-cc820c38ebc5`), CUDA13.2/CuTe4.7.1,
`nvcr.io/nvidia/pytorch:26.05-py3`, H7168/I2048/top-k8, 256 experts/32 local,
per-tensor activation scale and unfused finalize. Whole chain and isolated FC1
wrapper/FC2 each use ABA then BAB, ten warmups and100 cold-L2 CUDA-graph CUPTI
samples per arm. FC1 wrapper includes unchanged preparation. No AUTO or primary
campaign rerun; isolated phase latencies are not additive.

|Tokens|Whole chain control / variant|FC1 control / variant|FC2 control / variant|
|---:|---:|---:|---:|
|32|0.991981|0.986372|0.969621|
|128|0.992374|0.993628|0.982291|

Ratios use geometric means of three medians per arm. All36 arms passed output
and SF byte equality before and after timing, with3,600 individual samples
saved. The coupled B16/five-stage change loses about0.8% whole-chain and is
rejected. This does not establish that B16 alone is harmful. No wider-format,
sanitizer or primary retention campaign was run for this losing prototype.

`evidence/small-b-stage5-98fd/summary.json` contains all raw medians and
`raw.tar.gz` preserves all samples, logs, source, helpers, hashes and final
unstaged-state verification. Archive SHA256:
`b43eb680d690f67c1c9efc4ce4e8bac872dfce3b03b656ef99d53fce42ea47e1`.

The first T32 ABA used `probe_native.py`; `run_remaining.sh` ran the other
three processes. `archive.py` retrieves and summarizes completed evidence.
