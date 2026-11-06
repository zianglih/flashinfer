# Retained regular-TMA prefill profiles

Source `98fd3566b5f945c100f48cddacf25deb2432cbc2`, independent
`../../flashinfer-profile-98fd` / remote `profile-98fd` clone. Production and
MegaMoE were not edited. Native NVFP4 benchmark routing, seed 42, H7168/I2048,
top-k8, 32 local experts, per-tensor activation scales, unfused finalization.
C1 B200 GPU4, UUID `GPU-5f3e1a0a-95b5-fca1-e723-ea2e1623c813`, driver580.178.04,
image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTeDSL4.7.1.

Saved A1 and A2 winners agree at both profiled sizes:

- T8192: `(128, ((512,128),(2,1),False), ((256,128),(2,1),False))`.
- T16384: `(256, ((256,256),(2,1),False), ((256,256),(2,1),False))`.

`manifest.json` pins the saved cache receipts, current source files and copied
baseline/sampled modules. The iKET variant adds only first-two-cluster sampling
around existing opt-in markers; it uses the current wrapper's regular preparation
and current prepared B/SFB arguments. It does not inject the historical442 core.

## NCU

Full metric set, 40 replay passes per GEMM, profile-from-start disabled. The kernel
filter selects only `Sm100BlockScaledGroupedGemmKernel`. FC1 preparation executes
normally but is excluded from these GEMM counters. NVTX labels independently
identify each phase; `summarize_ncu.py` validates them instead of assigning phases
from the number of exported kernels. No standalone CUPTI phase timings or primary
campaign were rerun.

| Tokens / phase | Replay µs | Tensor active % | DRAM reads MB | Registers | Dynamic SMEM bytes | SM max/mean active cycles |
|---|---:|---:|---:|---:|---:|---:|
|8192 FC1 NB2/N128|132.768|47.33|595.230|80|189312|1.100|
|8192 FC2 N128|90.112|32.88|274.908|110|178688|1.040|
|16384 FC1 N256|198.112|67.66|618.973|80|195584|1.076|
|16384 FC2 N256|139.776|42.83|285.505|120|229888|1.039|

All four profiles pass complete output bytes; FC1 additionally passes SF bytes.
Both phases at both sizes report zero LDGSTS payload bytes and zero local-memory
read/write sectors. Six unavailable CTC metrics are listed in the raw logs; all
requested GEMM replays completed successfully.

These are profiler durations, not retention medians. Historical442 FC1 profiles
used Gather4 and NB2/N128, while current16K uses regular TMA and N256. They do not
form a controlled before/after comparison. Current8K reads nearly as much DRAM as
16K with a different geometry; this suggests examining geometry/reuse separately,
not attributing the difference to a measured cache cause.

## iKET

Each of four traces contains six instrumented launches; the summaries use the
last launch and preserve every sampled CTA/warp. All eight tracker/profile
processes pass output/SF byte equality against the current uninstrumented snapshot.
Representative leader means:

| Tokens / phase | Output tiles | Accumulator-empty µs/tile | Epilogue body µs/tile | MMA TMA-ready ns/K | SF S2T issue ns/K |
|---|---:|---:|---:|---:|---:|
|8192 FC1|9|0.839|3.804|162.7|76.3|
|8192 FC2|30|0.068|2.212|161.7|43.7|
|16384 FC1|17|0.990|4.066|127.5|60.5|
|16384 FC2|30|1.281|3.616|119.5|61.7|

Marker overhead perturbs execution substantially; these durations cannot be added
to predict uninstrumented latency or compared directly with the NCU duration.
For route N>=128 the old local-SF and peer-relay markers compile out. The retained
`producer_gather4_issue` marker contains no Gather4 work, and idle producer warps
may execute marker-only loops. Do not interpret those spans as transfer latency.

The first tracker attempt failed the import-path guard before benchmark execution:
the sampled module imported a FlashInfer helper before `--repo` was selected.
The r2 launcher establishes the frozen repo path first. Original helpers, failed
log and correction receipt are preserved; no kernel or production change was made.
The iKET driver also reports its expected unsupported logical-endpoint capability
warning; all traces and exact checks complete.

## Diagnosis and next-step boundary

The historical fragmented-SF/relay diagnosis no longer describes this prefill
path. Current source uses one TMA ring for A/SFA/B/SFB
(`blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:908–920`), and
releases it only after all MMAs consume the stage (`:1498–1508`). Merely releasing
SF shared storage earlier cannot free the combined payload stage.

NCU's strongest FC1 long-scoreboard PCs are accumulator-ready barrier predicate
consumers in the epilogue, not global SF loads. Large barrier counts also include
the terminal barrier reached by the now-idle producer warps. Removing those
warps may remove samples without improving throughput; SMEM already limits the
current prefill kernel to one CTA per SM. The separate six-warp FC1 proposal needs
ordinary timings, while the old FC2 six-warp axis remains closed.

One distinct bounded pipeline hypothesis is to wait for and copy **only the first
K-stage scales into TMEM before waiting for the next accumulator window**. Today
`acc_pipe.producer_acquire` at `:1390` precedes the operand wait at `:1425` and scale
copies at `:1438–1448`. Scale TMEM starts at `acc_reserved_cols` (`:1329–1356`),
outside the epilogue accumulator/transpose interval. This could overlap first-stage
readiness/copy with the measured accumulator wait without another stage or changing
the payload ring's lifetime. It requires proving async-copy ordering against the
previous MMAs and keeping the shared operand stage owned until the new MMAs finish.
No implementation, safety proof or speedup is established here; only a fraction of
one stage per output tile can be hidden. Decode work now has higher priority.

Do not reopen plain balanced absmax. The later
`../fc1_arithmetic_experiment/README.md:27–43` supersedes the old note saying it was
untested: `abs3` was exact but324.2410 vs324.3685µs and rejected. Current FC1 emits
eight dependent `FMNMX3` operations per16 values with absolute-value modifiers
already folded in. Across128 static max3 PCs, 8K has16/7027 total samples and16K
has50/9617; all3/15 short-scoreboard samples are on the first max consuming TMEM
values, with zero long-scoreboard samples. Sparse sampling does not prove zero
arithmetic cost, but supplies no new evidence for that closed variant.

## Evidence and reproduction

Verified archive `../../evidence/iket98fd-prefill/raw.tar.gz`, SHA256:
`4aa769942bfdfc2675e9aeb43dcb0bf9c5018cecb1c21102098beb4ae773e781`.
It contains full NCU reports/CSV/SASS, compressed raw traces, summaries, source
snapshots, generated code, commands, environment and exact receipts. The current
README and local `results/ncu-summary.json` are post-collection analysis.

From the remote project root, after provisioning the independent copy:

```bash
source scripts/recovery442/env_candidate.sh
.venv/bin/python scripts/iket98fd_experiment/run_ncu.py
.venv/bin/python scripts/iket98fd_experiment/run_iket.py
```

The drivers fix GPU4 and private CuTe caches, use the saved winners, and refuse
existing profile outputs. Source snapshots and original attempt manifests remain
immutable; select fresh labels for another run.
