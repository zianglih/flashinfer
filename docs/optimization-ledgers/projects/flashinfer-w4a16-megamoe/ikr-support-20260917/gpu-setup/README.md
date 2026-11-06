# BF16 NVFP4 IKR validation environment

Dedicated devbox requested 2026-09-17 using the managed `/usr/local/bin/h` from the project-local HAI checkout. Live NGC catalog reported 26.08 as latest overall; the live 26.05–26.08 release notes confirmed 26.05 is newest CUDA 13.2 image. Selected `nvcr.io/nvidia/pytorch:26.05-py3` (26.06 uses CUDA 13.3.0, 26.07 uses 13.3.1, 26.08 uses 13.4.1).

```bash
cd /Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/hai
command -v h
/usr/local/bin/h devbox fi-mega-ikr-0917 -c c2 -n ziangli \
  --gpu-type b300 --gpus-per-pod 8 --bare \
  --image nvcr.io/nvidia/pytorch:26.05-py3 \
  --description 'PR5019 BF16 NVFP4 in-kernel FC2 reduce validation'
/usr/local/bin/h ssh fi-mega-ikr-0917 -c c2 -n ziangli
```

The initial ziangli namespace request was admitted on node `hu-pdx-129`; no fallback or unrelated devbox changes were needed. Managed h auto-update failed because its GitHub token lacks access; the installed managed executable continued normally.

Source `/workspace/mega-ikr/flashinfer` is pinned to `4bc278892b3ced0a8c81501f858de517931e2ae9`. Interpreter `/workspace/mega-ikr/venv/bin/python` inherits image PyTorch using a system-site-packages venv. CuTe DSL and cu13 native libraries are pinned to 4.7.1, CUPTI Python13.2.0 / runtime wheel13.2.86. `setup.sh` installs FlashInfer editable with dependency resolution and optional native EP builds disabled. `verify.py` checks eight GPUs, Torch CUDA13.2, CuTe4.7.1/compiler13.3, source identity and imports, and records complete environment evidence. No kernel tests are part of provisioning.

`transport.py:remote(code)` executes Python on the dedicated devbox through managed h. `upload_files.py` accepts repository-relative file paths, uploads only those explicitly named files, and verifies each SHA256 remotely:

```bash
python3 ikr-support-20260917/gpu-setup/upload_files.py \
  flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/tuner.py
```

Remote test launch example (once source patches are uploaded):

```bash
cd /workspace/mega-ikr/flashinfer
PYTHONPATH=$PWD /workspace/mega-ikr/venv/bin/python -m pytest <selected tests>
```

Sources: <https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch>, <https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html>, <https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-08.html>.

## Verified handoff

Setup and imports passed. Eight B300 SXM6 AC GPUs are idle with 0 MiB allocated and no compute processes. Host driver590.48.01, toolkit13.2.78, imageTorch2.12.0a0+5aff3928d8.nv26.05 remain unchanged. CuTe native library SHA256 `bb367e30bb24541faa974ed05ff201171f61c5b18b01df9e46a406bdde5edbba` matches the prior environment. Nsys2026.2.1.210 and NCU2026.1.1.0 are available. Evidence is in `verified.json`, `tool-versions.json`, and `setup.log`.

Environment ownership is handed to the implementation/test runner. Provisioning has no active process and makes no further environment changes.
