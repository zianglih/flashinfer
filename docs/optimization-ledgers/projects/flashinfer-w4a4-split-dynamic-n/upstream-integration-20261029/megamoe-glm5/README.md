# MegaMoE GLM5 shared dequantization utility regression check

Authorized scope: benchmark the two-to-one byte-permutation scale duplication
change in `moe_w4a16_utils.py` as consumed by MegaMoE. No production edits,
sanitizer, new optimization, or independent arm retuning.

## Source contract

Both arms use upstream PR7290 head
`4376662a9ddefb1f62f0f81f4453964dc1f5a307`. Control replaces only
`flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py` with the content
preceding commit `1e4b127a0901282bda5faec70ef6d5a19c835943`.
The two exact helper files and their SHA256 hashes are in `plan.json`.
`run_comparison.py` asserts that this helper is the only source difference.
Its per-phase source manifests also reject mutation during the run.

MegaMoE's `_MegaMixedInput` subclasses `Sm100W4A16GroupedGemmKernel`; its FC1
and FC2 call inherited `_transform_tile`, which invokes
`decode_nvfp4_fragment_to_bf16` from this helper. This is an actual MegaMoE
dependency despite the helper not being imported directly in MegaMoE.

## Environment

C2 devbox `fi-mega-scale-1029`, node `hu-pdx-59`, all eight B300 SXM6 AC GPUs.
Image `nvcr.io/nvidia/pytorch:26.05-py3`, NVIDIA driver 595.91.07.
The live NVIDIA NGC catalog and release notes were checked before creating
the devbox; 26.05 is the latest CUDA13.2 release (26.06/26.07 use13.3).
`/usr/local/bin/h` was invoked from the HAI checkout, with `--bare`, namespace
`ziangli`, and no size override.

Exact runtime versions are captured by the harness. Setup installed:

```bash
unset PIP_CONSTRAINT
python3 -m pip install \
  'nvidia-cutlass-dsl[cu13]==4.8.0' 'apache-tvm-ffi==0.1.14.post1' \
  'nvshmem4py-cu13==0.3.1' 'nvidia-nvshmem-cu13==3.6.5' \
  'cupti-python==13.2.0' 'nvidia-cuda-cupti==13.2.86' \
  'cuda-core==1.2.1' ninja rich einops expecttest
```

The container's PyTorch was preserved. Source include/csrc are the437 tree;
header dependencies are existing persistent-storage checkouts at the exact
437 submodule revisions: CUTLASS `b46b16d003484063bca4ed365e44095c4c6ed633`,
CCCL `16bd510c9b712e82b0ab6cbb630d8e29ba1f7116`,
spdlog `c3aed4b68373955e1cc94307683d44dca1515d2b`.

## Measurement

Reference methodology: https://github.com/flashinfer-ai/flashinfer/pull/6277.
The native `benchmarks/bench_cute_dsl_moe_distributed.py --model glm5` uses
real EP8 with D6144, I2048, 256 experts, top8, SwiGLU and grouped routing.
Global token counts are1,2,4,8,16,32,64,128,256,512,4096,8192,16384.

One untimed control AUTO pass selects a tactic per token count. The same
explicit tactic map is then used in fresh-process C1,A1,A2,C2 phases.
Each phase uses3 warmups and100 untrimmed CUPTI cold-L2 CUDA-graph samples,
with per-iteration rank-MAX GPU activity spans. Routing is precomputed;
PDL and fused deterministic combine are enabled; in-kernel FC2 reduction is
disabled. Route fingerprints for all eight ranks must match across phases.
Tokens1/2 are measured but excluded from aggregate retention statistics.

`native_frozen.py` wraps only untimed setup to set the token-specific frozen
tactic and record routing fingerprints. All timed calls are native.
The native benchmark validates CUPTI at startup, and a warning filter makes
its CUDA-event fallback fatal. `analyze.py` validates all timing metadata,
sample counts, rank participation, tactics and routes before aggregating.

C++ compilation artifacts remain in a persistent shared cache. Control and
candidate use separate persistent CuTe DSL cache directories. No cache is
removed during measurement.

The native direct `cute.compile` path did not populate those DSL file-cache
directories. PTX/cubin retention was enabled before all measured phases with
`CUTE_DSL_KEEP=ptx,cubin`; it adds only compiler artifact output, no profiling
or debug instrumentation. The control/current source paths changed C++ JIT
command hashes, so switching arms rebuilt `fp4_quantization_103` (the C2 CUDA
object took about89 seconds according to `.ninja_log`). These are persistent
artifacts, not a claim that every arm switch hit the native cache. Future
Python-only experiments can share immutable include/csrc paths to retain
stable native JIT command hashes.

Run `python3 run_comparison.py` in the remote task folder; after fetching
artifacts run `python3 analyze.py` locally. The public PR section is written
only once the entire qualified comparison and native codegen check finish.
