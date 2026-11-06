# SGLang CUDA 13 W4A16 dequantization receipt

Checked live on 2026-11-02. The newest timestamped CUDA 13 development image uses the **direct BF16 conversion/multiply path** on a CUDA 13-capable driver. Its CuTe compiler reports CUDA 13.4, despite its base CUDA toolkit and PyTorch build being CUDA 13.0. The user's conditional request to rerun the full fallback benchmark therefore does not trigger.

## Image identity

| Item | Value |
|---|---|
| Explicit image | `lmsysorg/sglang:nightly-dev-cu13-20261102-38d9e4a3` |
| Published | `2026-11-02T00:50:07.265214Z` |
| Index digest | `sha256:77ff63ee69fd7ebef20df3a6d036ee4b8a4ffe0734efb0028c3b7643386e3ccf` |
| amd64 manifest digest | `sha256:c6da252c6837bb062184b01c7aa2df7a2aadb1ed4944f236d7027174c73c45fa` |
| SGLang revision | `38d9e4a3fe4a493b0ae468477a274e83defda81a` |
| Base `CUDA_VERSION` | `13.0.3` |
| Installed PyTorch | `2.14.1+cu130` |
| Installed FlashInfer | `0.7.2` |
| Installed CuTe DSL and cu13 libraries | `4.8.0` |
| Installed `nvidia-cuda-nvcc` Python package | `13.4.92` |
| CuTe compiler `cutlass.CUDA_VERSION` | `DSLCudaVersion(major=13, minor=4)` |

The index bytes were fetched from the registry and their SHA256 was checked against the registry's `Docker-Content-Digest`. Versions above come from actual image config, package `METADATA`, and the image's `uv pip freeze` output in `constraints.txt`.

## Compiler and branch proof

- Extracted the actual amd64 compiler file from dependency layer 30 (`sha256:7f7e4ed3d0e6962cfedc8c370a7a579f12abbede2d8cff7862eaa9fca58f1c93`):
  `/opt/sglang/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/_mlir/_mlir_libs/_cutlass_ir.cu13.cpython-312-x86_64-linux-gnu.so`.
- File size: **193,177,432 bytes**. Actual SHA256: **`f325e99ecfd4e49411d694bf7b08f3d9aa4f3e8fa1f0da9d3b456038fa4c0d32`**. The installed wheel's `RECORD` contains this same content hash.
- This is byte-for-byte identical to the compiler imported by the existing NGC 25.11 experiment environment, where the runtime query returns `cutlass.CUDA_VERSION = DSLCudaVersion(major=13, minor=4)`. See `runtime-library-identity.log` and `binary-scan.log`.
- The image includes both cu12 and cu13 compiler flavors. Its actual loader chooses the highest installed flavor compatible with the CUDA driver **major** version; a CUDA 13-capable driver selects cu13. With no driver it also selects the newest installed flavor. A driver advertising only CUDA 12 would select cu12 and is outside this CUDA 13 deployment conclusion.
- The actual image's `moe_w4a16_utils.py:13-15` checks `major > 13 or (major == 13 and minor >= 2)`. At **13.4**, `_HAS_DIRECT_FP4_TO_BF16_CVT = True`: `cvt.rn.bf16x2.e2m1x2`, `cvt.rn.bf16x2.e4m3x2`, then `mul.rn.bf16x2`. The FP16 multiply / FP32 widening / BF16 output branch is not selected.
- The build-generated compiler fingerprint `b1028f...` in `_cutlass_ir_version_cu13.py` is a compile-cache fingerprint; it differs from the actual installed binary hash and was not used as a file-identity claim.

Image history was inspected for later installs. The late unconstrained `ai-dynamo` layer 53 and gateway layer 67 were also streamed and checked: neither contains a replacement CuTe package, compiler, or relevant package metadata. Later SGLang and NVIDIA plugin source installs use `--no-deps`. This was an OCI file inspection and a matching-compiler runtime query, not a boot of the complete SGLang image or a full serving test.

The image helper and current experiment helper have the same gate. Their scale-byte replication differs (`mov` in FlashInfer 0.7.2 versus `prmt` in the experiment checkout), without changing branch selection.

## Stable alias comparison

`latest-cu130` currently resolves to `lmsysorg/sglang:v0.5.23-cu130`, index `sha256:f832b5c39559c9caa900b22ad37c76fcce66470676855c42052102c537812f1f`, amd64 manifest `sha256:f7876bef696ccf9cf75a2bf7ccb82970f5fac577f082fb8ca95c9a59d2160eb5`. Its actual image config says CUDA 13.0.3 / FlashInfer 0.7.2; its extracted dependency source pins CuTe DSL `[cu13]==4.8.0`, FlashInfer `[cu13]==0.7.2`, and Torch 2.14.1. **Only stable config and pins were checked; its compiler binary was not separately extracted.** The conclusion above uses the newest timestamped development image required by workspace instructions.

## Evidence

- `image-audit.json`: compact machine-readable receipt, hashes, conditions, limitations, and source URLs.
- `tags-nightly-dev-cu13.json`, `tags-cu13.json`, `index-dev.json`, `manifest-amd64.json`, `config-amd64.json`: live registry evidence.
- `layer-30/sgl-workspace/constraints.txt`: installed dependency versions.
- `layer-30/opt/sglang/lib/python3.12/site-packages/`: extracted compiler, wheel records/metadata, loader source, and FlashInfer helper.
- `layer-scan.log`, `binary-scan.log`, `upper-layer-scan.log`, `runtime-library-identity.log`: extraction and runtime evidence.
- Public source: [Docker Hub tags](https://hub.docker.com/r/lmsysorg/sglang/tags?name=nightly-dev-cu13), [exact tag metadata](https://hub.docker.com/v2/repositories/lmsysorg/sglang/tags/nightly-dev-cu13-20261102-38d9e4a3), [pinned SGLang dependencies](https://github.com/sgl-project/sglang/blob/38d9e4a3fe4a493b0ae468477a274e83defda81a/python/pyproject.toml).

No new devbox, full benchmark rerun, source modification, or public GitHub write was performed in this investigation.
