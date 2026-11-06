# CUDA 13.0 W4A16 before/after

This campaign reruns the published pre-PR W4A16 comparison on C3 with
`nvcr.io/nvidia/pytorch:25.11-py3`. It does not optimize or change kernel math.

- Before: `002529e17b22567a071091053c6c4dc2a55e050e`, original 64-row gated layout,
  standalone preparation. Only its published benchmark adapter is overlaid:
  SHA256 `8078d09b8be9c5a992d8904ffc59fbcdb28fd2e34324a69e4fe250ed79477eab`.
- After: `a620ce7790b32f7f0ae524a811417d2c6cee1152`, swap-AB 16-row gated layout,
  in-kernel activation gather. N3U ReLU2 has no gate/up interleave.
- Shapes: V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8. Rank-local
  benchmark workloads, without distributed communication. W4A16 BF16 inputs,
  NVFP4 weights, public functional API, unfused finalize.
- Tokens: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384.
  Tokens 1/2 remain in raw results and are excluded from all aggregates.
- C-A-A-C order on the same GPU for each job; 10 warmups and 100 strict CUPTI
  cold-L2 CUDA-graph samples per cell per phase. 104 cells, 41,600 fresh samples;
  88 cells contribute to aggregates. Per-cell times are geometric means of the
  two phase medians. Speedup is `(before / after - 1) * 100`.
- Published source-specific winner choices are replayed without autotuning. The
  legacy JSON cache and current managed cache retain all original entry keys,
  tactics, and profiling policies; only environment metadata is explicitly
  rebound to the installed runtime. This is a fixed-choice comparison, not a
  claim that these choices are optimal on CUDA 13.0.
- Routing identities must match every fresh phase and arm. Historical identity
  equality is recorded separately because the image changes Torch 2.12 to 2.10.
- No CUDA 13.2 timings or compiled artifacts serve as the new before arm.
  Separate persistent C++/CuTe caches belong to this CUDA 13.0 campaign.

The image preserves Torch `2.10.0a0+b558c986e8.nv25.11`, CUDA 13.0, and system
nvcc/ptxas `13.0.88`. Both arms use CuTe DSL 4.8.0, whose cu13 library embeds
NVVM `13.4.59`; this compiler component is newer than the system toolkit.
Record generated PTX headers from the first smoke. The installed CUPTI bindings
are 13.0.1 and the loaded system CUPTI is `libcupti.so.2025.3.1`.

`prepare_local.py` created exact source archives with their pinned submodules
and copied frozen inputs. Observer copies under `harness/` are independently
adapted to each source's cache/API contract. The legacy observer adds the same
post-timing activity capture as the current observer and forbids profiling;
neither observer alters arguments, GPU work, or measured timing policy.

Deployment root is
`/data/ziangli/flashinfer-moe-gather-pipeline/cuda130-w4a16-20261102/payload`.
The isolated Python is the sibling `../venv/bin/python`. Extract `sources/before.tar.gz`
and `sources/after.tar.gz` into `sources/before/` and `sources/after/`, then:

```bash
../venv/bin/python harness/configure.py \
  --cache-root ../cache --output ../results

../venv/bin/python harness/run_pair.py --config harness/config.json \
  --job ep-v3-w4a16 --gpu 0 --tokens 4,4096 \
  --output ../smoke --dump-compiler
```

Configuration creates source-local `flashinfer/data` links for `csrc`, `include`,
`cutlass`, `cccl`, and `spdlog`, mirroring `pyproject.toml` package-directory
mappings. These generated links do not modify tracked source bytes. The first
smoke discovered their absence before any timed cell; its failure log is kept
separately, and the paired smoke restarts after the bootstrap correction.

After the smoke is independently checked, launch the eight `jobs.json` entries
on distinct GPUs with `run_pair.py --config harness/config.json --job JOB --gpu N`.
Full runs omit `--tokens`, `--output`, and `--dump-compiler`.
Keep native stdout, 100 raw timings, CUPTI activity records, NVML telemetry,
source/caches hashes, resource guards, and every repeat/negative result.
The independent report helper is under `audits/`.
