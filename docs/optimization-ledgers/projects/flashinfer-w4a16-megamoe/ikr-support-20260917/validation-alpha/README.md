# W4A4-style alpha interface validation

Source: IKR commit `576904a8` plus the pair-weight/configuration/runtime-alpha API refactor. `remote-source-manifest.json` records the tested source hashes; `source-manifest.json` and `final-remote-source-manifest.json` record the final local/remote source, which match exactly. Three final edits were synced after validation: tuner docstring wording, removal of an unreachable empty-candidate check after shared filtering, and kernel combine-shape comments/docstring. The saved `*-tested.py` copies preserve the three tested versions. No device operations changed in those final edits; no numerical rerun was needed for them.

Environment: C2 / 8×B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA toolkit13.2.78, imageTorch2.12.0a0+5aff3928d8.nv26.05, CuTe4.7.1 cu13. Runtime NVSHMEM3.6.5. The numerical runs used one or two GPUs. Full inventory is `../gpu-setup/verified.json`.

- Host: **58 passed, 1 skipped, 3 deselected**, 4.64s. Complete affected weight-pack, layer-validation and knob-cache files; GPU-marked cache tests excluded. The skip is `test_deep_gemm_validate_transformed_weights_accepts_preprocess_output`: optional `deep_gemm` is not installed (verified with `importlib.util.find_spec`). An earlier launch hid all CUDA devices and failed one existing DeepGEMM bootstrap error-path expectation before its intended distributed guard; rerunning with CUDA visible passed without code changes.
- Single GPU: **30 passed**, 72.98s. Complete NVFP4 kernel/reference file: both weight-layout modes, BF16/FP32 input weights and canonical packed aliases, regular/tail/single-expert shapes, both IKR tiles, original default paths. The FP32 alpha/routing cancellation checks remain bit-exact for configuration and runtime alpha sources, including graph replays after mutating both alpha tensors and persistence when overrides are omitted. Wrong alpha shape, dtype and device are explicitly rejected on real CUDA inputs.
- EP2: **15 passed on each rank**, 93.85/93.86s. Configuration/runtime alphas with random/skew routing, unequal and empty source ranks, all-empty/refill, static/atomic scheduling, default/IKR combine, lockstep graph mutation and exact zero-output replay.
- No tolerance changes. IKR retains the existing repository BF16 accumulation band; the default exact checks remain exact.
- All owned validation processes exited and no GPU compute process remained at handoff (`gpu-cleanup.json`).

## Commands

Run from `/workspace/mega-ikr/flashinfer` with `PYTHONPATH` set to that path. Single-GPU command also uses `CUDA_VISIBLE_DEVICES=0 MEGA_NO_DIST=1`; EP2 uses `CUDA_VISIBLE_DEVICES=0,1 OMP_NUM_THREADS=1` and leaves `MEGA_NO_DIST` unset. Host checks keep CUDA visible but launch no GPU kernel.

```bash
/workspace/mega-ikr/venv/bin/python -m pytest tests/moe_ep/test_weight_pack_union.py tests/moe_ep/test_mega_layer_validation.py tests/moe_ep/test_knob_cache.py -m 'not arch_blackwell' -v -s --confcutdir=tests/moe_ep --disable-warnings
```

```bash
/workspace/mega-ikr/venv/bin/python -m pytest tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py -v -s --confcutdir=tests/moe_ep --disable-warnings
```

```bash
/workspace/mega-ikr/venv/bin/python -m torch.distributed.run --nnodes=1 --node-rank=0 --master-addr=127.0.0.1 --master-port=29760 --nproc-per-node=2 -m pytest tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py tests/moe_ep/test_mega_cuda_graph_multirank.py -k 'w4a16 and (uneven_sources or (graph_replay_lockstep and manual))' -v -s --confcutdir=tests/moe_ep --disable-warnings
```
