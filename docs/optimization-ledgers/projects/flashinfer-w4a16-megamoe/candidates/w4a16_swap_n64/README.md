# Allocated routed N64 experiment

This is an **unapplied, CPU-validated candidate**, built from compute commit
`f952b398418932d52872a7ce13e6adebedbe33e2`. It does not include active raw3/raw5
or transform2 experiments. No CUDA kernel has been compiled or launched with
N64, and no performance claim is established.

`n64.patch` changes only the new W4A16 kernel, frontend and epilogue guard.
The default remains `(256,128,256)`. Select N64 through the existing knob:

```json
{"mma_tiler_mnk":[256,64,256]}
```

Keep every scheduling/return knob identical in an eventual N128/N64 comparison.
The frontend canonicalizes this JSON list to a tuple before validation, pool
keys and compilation. It sets token padding to the allocated N dimension.
There is no new public option or automatic selection policy.

## Existing patterns reused

All source line references below identify the fixed f952b398 source. Paths are
relative to the repository. The patch builder reads that commit with `git show`
and records base/proposed SHA256 hashes in `manifest.json`; it never reads the
active experimental kernel as its base.

- `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/tuner.py:42–47`
  already includes swapped Mega geometry `(256,64,256)`.
- `shim/w4a16/dynamic_mainloop.py:85–96` under the same directory already
  permits allocated N64. Both FC1 and FC2 use the shared activation task and
  existing non-leader TMA shift `align16(valid_tokens)/2 - allocated_N/2`.
  The dynamic BF16 MMA descriptor, K16 loop and clear-accumulator rule do not
  change.
- `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:323–331`
  locates decoded A after `num_acc_tmem_cols`. The Mega MMA path previously
  hardcoded `+256`; the patch uses the same computed reserve as its inherited
  transform. This is required when two N64 accumulator stages occupy only
  128 columns. The new assertion checks the epilogue and transform reserves
  agree. Packed/SF TMA layouts, online decoder, gate/up producer composition
  and direct TMEM MMA consumption are unchanged.
- `src/moe_nvfp4_swapab/megamoe_kernel.py:338–348` requires cluster token
  width to be divisible by token padding. N64 therefore uses padding64.
  `src/src/token_comm.py:885–891,1016,1126,1299–1321` derives its BF16
  transport/storage and completion boundaries from those dimensions.
  No activation SF planes are introduced.
- `src/moe_nvfp4_swapab/epilogue_refactor.py:1053–1105` already derives
  accumulator columns and stage stride from N, with `N/64` subtiles and
  two nonoverlapping accumulator stages. W4A16 FC1 at
  `shim/w4a16/epilogue.py:295–310,336–337,399` has one 64-token subtile
  at N64, split into two 32-token halves. Its feature offset
  `tile_m_idx * 64` remains unchanged because it describes M256, two CTAs
  and gate/up pairing rather than routed N.
- The current vendor FC2 helper at
  `src/moe_nvfp4_swapab/epilogue_refactor.py:2016–2018,2092–2109,2174–2195`
  uses the same N-dependent token base, stage view and subtile count. Its
  nonoverlapping path does not require a second 64-token subtile. Both FC2
  return modes, completion tracker and all device bodies are reused unchanged.

The `src/` and `shim/` paths above are under
`flashinfer/moe_ep/kernel_src/cutedsl_megamoe/`.

## Resource and ownership checks

| Quantity | N128 control | N64 candidate |
|---|---:|---:|
| Threads / launch register cap | 512 / 128 | 512 / 128 |
| Raw / activation / transform / accumulator stages | 2 / 2 / 2 / 2 | 2 / 2 / 2 / 2 |
| Allocated TMEM columns | 512 | 512 |
| Accumulator columns | 0–255 | 0–127 |
| Decoded BF16 A columns | 256–511 | 128–383 |
| Unused TMEM columns | none | 384–511 |
| Packed A SMEM bytes, both stages | 32,768 | 32,768 |
| Native SF SMEM bytes, both stages | 4,096 | 4,096 |
| BF16 B SMEM bytes, both stages | 65,536 | 32,768 |
| Token padding | 128 | 64 |

These are actual CPU CuTe layout sizes, not a compiled occupancy report.
TMEM allocation remains512. Transform warps remain12–15; every scheduler,
raw/transform pipeline, TMEM retrieval, dispatch and tail arrival count is
unchanged. The kernel still uses two-CTA M256 and K256. FP32 global alpha,
BF16 activation/intermediate/FC2 boundaries, post-FC2 FP32 routing and exact
clamp association are unchanged.

N64 may reduce activation storage and epilogue work for small route tiles.
For experts with more than64 routed tokens it creates more work tiles and
can repeat packed-weight work. This is a feasibility argument only; adjacent
same-schedule GPU measurements must decide whether to retain it.

## Validation and existing tests

- `logs/swap-n64-cpu-002.log`: **120** real kernel/workspace/epilogue
  constructor cases and **240** inherited mixed-input layouts, covering
  N64/N128, EP1/2/8, H32/I64 through H7168/I2048, static/atomic scheduling,
  both return modes, FC1/FC2 transform fragments, JSON/default/negative
  configurations and all valid-token TMA/epilogue coordinate bounds.
- The proposed sources pass Ruff, formatting, Python compilation and
  `git apply --check` against their saved f952 base.
- `logs/swap-n64-host-001.log`: **71 passed, 2 warnings in 2.36s**.
  `validate_host.py` selects the three proposed modules before imports in an
  isolated process and runs the existing host contract files against the
  separate `host-validation` tree. No active checkout files are changed.
- `tests/moe_ep/test_w4a16_shim_contract.py:198–203` requires N128 by default
  and rejects `(256,256,64)` with an error matching `mma_tiler_mnk`. Both
  remain valid. **No existing test rejects N64**, so none should be removed.
  If retained, add positive list/tuple N64 constructor and `apply_knobs`
  coverage to that test; keep the unsupported-geometry rejection.

CPU checks use `CUDA_VISIBLE_DEVICES=''` and assert CUDA is unavailable.
They do not establish TMA legality, generated register/spill behavior,
collective progress, numerical parity or graph replay for N64. Before timing,
run the unchanged EP1/EP2 numerical/empty-refill/graph/ring-wrap cases through
the public frontend with the N64 knob, then inspect fresh production-shape
PTX/SASS/resources. Keep the N128 source snapshot for adjacent controls.

```bash
python3 candidates/w4a16_swap_n64/build_patch.py
ruff check candidates/w4a16_swap_n64/proposed
ruff format --check candidates/w4a16_swap_n64/proposed
git -C candidates/w4a16_swap_n64/base apply --check ../n64.patch

# On the recorded remote environment, with the artifacts copied separately:
CUDA_VISIBLE_DEVICES='' FLASHINFER_CUDA_ARCH_LIST=10.3a python3 \
  candidates/w4a16_swap_n64/validate_cpu.py /workspace/flashinfer-w4a16-megamoe
CUDA_VISIBLE_DEVICES='' FLASHINFER_CUDA_ARCH_LIST=10.3a python3 \
  candidates/w4a16_swap_n64/validate_host.py /workspace/flashinfer-w4a16-megamoe
```
