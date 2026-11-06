# FC2 TMA-only six-warp experiment

Frozen baseline: `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. Task-local files only. Production is unchanged. **Completed and rejected for retention:120 paired exact cases and36 native full-output comparisons pass; forward/reverse timings show no repeatable full-chain gain. GPU5 was verified idle and released.** Harnesses require `ROLES_GPU_RELEASED=1` to prevent accidental overlap with future benchmark holds.

## Mechanism and safe mapping

FC2 at N128/N256 already moves all activation data and scales through TMA. Its four-warp producer group only needs one warp for TMA issue. The compact arm uses 192 threads: physical epilogue warps0–3, TMA warp4, MMA warp5. Other kernels retain their existing 288/160-thread roles, geometry, stage counts, math, layout, cache hints, and markers.

The epilogue must stay on a complete physical warpgroup: TMEM load/store lane ownership follows the physical warp's position within its warpgroup, independently of a software `tidx` subtraction. Consequently the superficially simpler TMA0/epilogue1–4/MMA5 mapping would be wrong. [PTX13.2.2 TMEM access restrictions](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#tcgen05-tensor-memory-ld-st-access-restrictions).

The minimal isolated diff changes CTA size, three producer-warp guards, role dispatch, and the epilogue thread-index base. It preserves:

- Allocator warp0 and the first128-thread deallocation cohort. Allocation/retrieval happen before dispatch. CUTLASS internally restricts alloc/free/relinquish to allocator warp0, which is now an epilogue warp.
- Whole-CTA barriers1/3 use the new192-thread count. Teardown barrier2 and epilogue transpose barrier6 remain128. The group-2 deallocation peer protocol stays intact.
- Accumulator consumers remain128 threads per CTA; TMA producers remain one thread per CTA; transaction-byte accounting and pipeline tails are unchanged.
- PDL waits/dependent-launch signaling, opt-in iKET marker scopes, shared-memory/TMEM allocation, and output arithmetic.

Source anchors in frozen baseline: constructor362/385–390; allocation1012–1028; producer dispatch1061 and guards1178/1246/1383; epilogue dispatch1385 and thread indices1426/1462; teardown1666+. Utilities use a128-thread barrier6 and physical warp modulo4 for TMEM rows. Independent audit confirmed the same mapping.

This reduces launched warps from9 to6. At an unchanged register count R, nominal CTA register allocation would fall from288R to192R; emitted CUBIN resources must establish the real count and spills. Large shapes are already limited by shared memory, so no occupancy improvement is assumed. No `setmaxnreg` policy is introduced. Prior register redistribution experiments were exact but neutral/slower, and invalid CTA-pool assumptions caused hangs; see `../register_budget_experiment/README.md`.

## Preparation and structural validation

```bash
python3 scripts/fc2_roles_experiment/build_snapshot.py
python3 scripts/fc2_roles_experiment/check_source.py
```

The snapshot builder reads exact Git objects from442d rather than the mutable checkout. It freezes the core, utilities, common kernel helpers, custom pipelines, finalize, and host launch function. `snapshot_manifest.json` records source/snapshot SHA256 values. `check_source.py` checks parsing, source hashes, unchanged allocation/MMA/teardown regions, role coverage, physical TMEM ownership, all three issue guards, barrier counts, and marker counts. This is structural evidence only, not CuTe compilation or numerics.

## Bounded GPU screen, after concurrency release

Use the existing C1 image `nvcr.io/nvidia/pytorch:26.05-py3`, B200, CUDA13.2, CuTe DSL4.7.1. Synchronize only this task-local folder with `sync.py`. Do not change the candidate checkout or native JIT epoch. From `/workspace/flashinfer-w4a4-split-dynamic-n/candidate`, set the assigned device and an empty dump directory per run:

```bash
export CUDA_VISIBLE_DEVICES=5
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 PYTHONPATH=.
export ROLES_GPU_RELEASED=1
export CUTE_DSL_KEEP_PTX=1 CUTE_DSL_KEEP_CUBIN=1
export CUTE_DSL_DUMP_DIR=/workspace/flashinfer-w4a4-split-dynamic-n/logs/fc2-roles/smoke-dumps
../.venv/bin/python ../scripts/fc2_roles_experiment/run_paired.py --limit 1
```

First bound the smoke externally with `timeout 180` and inspect dumped PTX/CUBIN for192 threads, unchanged SMEM, zero local spills, expected allocator/producer guards, and unchanged pipeline barriers before extending. This first smoke is NVFP4,N128,twoCTA. Then run24 cases per invocation (six formats × N128/N256 × per-token off/on):

```bash
../.venv/bin/python ../scripts/fc2_roles_experiment/run_paired.py
SFB_SHORT=1 SFB_POISON=1 ../.venv/bin/python ../scripts/fc2_roles_experiment/run_paired.py
SFB_GROUP=1 SFB_SHORT=1 SFB_POISON=1 ../.venv/bin/python ../scripts/fc2_roles_experiment/run_paired.py
SFB_SHORT=1 SFB_POISON=1 ROLES_PDL=1 ../.venv/bin/python ../scripts/fc2_roles_experiment/run_paired.py --script probe_fc2_fused.py
SFB_GROUP=1 SFB_TILES=16,64 SFB_SHORT=1 ../.venv/bin/python ../scripts/fc2_roles_experiment/run_paired.py
```

The120-case screen covers both CTA groups, K tails and sub-stage K, M384 channel tails, poisoned invalid-route SFs, BF16/FP16 route-scale metadata, per-token scaling, fused top-k1 exact writes, PDL, and unchanged small-N controls. Every output byte and canary starts identically in each arm. Fused top-k1 avoids interpreting nondeterministic top-k atomic ordering as a role-map failure.

After numerics, run fixed-tactic actual-routing phase and full-chain diagnostics, first NVFP4,N128,T8192/16384, then reverse order. Use baseline/compact/baseline,10 warmups/100 samples,cold-L2 CUDA graph CUPTI; fallback to CUDA events is fatal. The same442d source and prepared input are used in both arms. N256 and MXFP8/mixed follow only if a plausible gain appears; smaller token counts bound regressions before any retention decision.

```bash
../.venv/bin/python ../scripts/fc2_roles_experiment/probe_modes.py \
  --repo . --expected-head 442d2aa53f68b4640c3ab5118a76f1599ff60d34 \
  --tokens 8192,16384 --mode nvfp4 --variants baseline,compact,baseline \
  --output ../logs/fc2-roles/native-n128-forward.json
../.venv/bin/python ../scripts/fc2_roles_experiment/probe_modes.py \
  --repo . --expected-head 442d2aa53f68b4640c3ab5118a76f1599ff60d34 \
  --tokens 16384,8192 --mode nvfp4 --variants compact,baseline,compact \
  --output ../logs/fc2-roles/native-n128-reverse.json
```

`probe_modes.py` also accepts `--mode mxfp8` or `mxfp4` (the latter is mixed MXFP4 weights/MXFP8 activations), and an explicit N256 tactic via `--tactic '[256,[[256,256],[2,1],false],[[256,256],[2,1],false]]'`. Full outputs must match exactly before timing. FC1 is recorded as an unchanged drift control; isolated phase medians are not additive full-pipeline evidence. No new primary benchmark run is part of this experiment.

## Initial GPU evidence

GPU5 NVFP4/N128/two-CTA smoke is byte-exact. Emitted CUBIN reports288→192 threads and106→102 registers/thread, zero stack/local memory and zero LDL/STL sites, with8 TMA instruction sites in both arms. Static `SHARED:1024` excludes the dynamic operand/epilogue allocation; do not treat it as total shared-memory usage. Full120-case matrix above passes. Native codegen reduces FC2 registers110→106 (NVFP4) and114→110 (MXFP8/mixed), with no spills. Native timings were neutral or inconsistent/slower; no production patch is retained. Complete samples and receipts are safely local in `../../evidence/fc2-roles-442d2aa5/`, whose README records all36 measured medians and the archive digest. The devbox became unavailable after successful collection; no evidence is missing.
