# Focused scale UInt16/h trial

Ready for review, unexecuted. Source `a9b149c2` → `20ae8493dc0374efb67c6695fda4bb8f424b6be868bd27101fb2312238b1ad4f` changes only `moe_w4a16_utils.py` (`85808c54` → `35790888`). The public Uint32 ABI, numerical operations, shared transform, Mega kernel, static epilogue, graph scorer, five total WGs and exactly two decode WGs are unchanged. The accepted N128/N64 native review records a changed first-store schedule and fewer static instructions; it does not establish a performance gain.

The immediate native owner is the completed first16 full13: manifest `0f7305b5`, results `9fe07941`, exact final inventory `079f6f7a`. The frozen saved analyzer validates this owner in a separate process. Native roots remain their recorded paths, including every JIT-log byte. First validation requires that exact inventory; each later job requires the immediately preceding successful inventory. Each job gets fresh DSL/driver caches. Performance gets fresh DSL/driver/knob outputs and the completed five-job native lineage.

Five jobs use existing numerical definitions and unchanged tolerances:

1. All 14 `TestCuteDslMoeW4A16` tests on one GPU. The observer requires every node and setup/call/teardown phase to pass without skips, and records actual loaded shared/decoder files and alias identity before and after each call.
2. Existing `test_w4a16_mega_reference_schedule` at M256/N128/C2, EP1.
3. The same at EP2.
4. Existing reference schedule at M256/N64/C2, EP1.
5. The same at EP2.

Each reference job includes both return modes, explicit flag4 and four compiled layers per mode/rank: 12 rank-tests and 48 actual Mega objects overall. The original geometry observer and REG96/640-thread/two-decode/61440-register-pool prelaunch gate are unchanged. Its loaded shared-MRO observer changes only the exact decoder hash. The saved subset check retains the original geometry/resource assertions, replacing full-suite flag8 expectations with the exact two reference selectors and flag4. No new numerical tests, host/lifecycle/sampler rerun, C1/M128/clamp addition or exhaustive bit-equivalence claim is included.

The full13 phase loop is unchanged: fixed CONTROL then auto16, all global token counts 1–4096, 100 CUPTI iterations, three warmups, CUDA graph, cold L2, median of iteration-wise rank-MAX activity spans. Split uses the changed shared utility and retunes; keep both whole tables and split context.

Run only after source/native review approval, a fresh idle check, and exact new-only staging. Commands below are remote commands in `/workspace/flashinfer-w4a16-megamoe`; omit `--execute` for the existing dry modes.

```bash
export PATH=/usr/bin:/usr/local/cuda-13.2/bin:/usr/local/bin:$PATH
export PYTHONDONTWRITEBYTECODE=1 FLASHINFER_CUDA_ARCH_LIST=10.3a
unset MEGA_USE_NCU CUTE_DSL_LINEINFO CUTE_DSL_KEEP CUTE_DSL_DUMP_DIR
/usr/bin/python3 -B candidates/cuda132_recovery_0908c/scale_operand_u16/install.py --execute
CUDA_VISIBLE_DEVICES='' PYTHONPATH="$PWD/flashinfer" /usr/bin/python3 -B candidates/cuda132_recovery_0908c/scale_operand_u16/preflight.py --expect-system-cuda 13.2 --output logs/cu132-recovery0908c-scale-u16-preflight-001.json
/usr/bin/python3 -B candidates/cuda132_recovery_0908c/scale_operand_u16/run_validation_sequence.py --prefix cu132-recovery0908c-scale-u16 --preflight logs/cu132-recovery0908c-scale-u16-preflight-001.json --source-manifest candidates/cuda132_recovery_0908c/scale_operand_u16/prospective-source-manifest.json --native-predecessor /workspace/flashinfer-w4a16-megamoe/logs/cu132-recovery0908c-first16-full13-001/stack-manifest.json --focused-scalar --execute
```

After all five completed outputs and source/native guards pass review:

```bash
/usr/bin/python3 -B candidates/cuda132_recovery_0908c/scale_operand_u16/run_full13.py cu132-recovery0908c-scale-u16-full13-001 --preflight logs/cu132-recovery0908c-scale-u16-preflight-001.json --validation-summary logs/cu132-recovery0908c-scale-u16-validation-sequence-001/summary.json --source-manifest candidates/cuda132_recovery_0908c/scale_operand_u16/prospective-source-manifest.json --native-predecessor /workspace/flashinfer-w4a16-megamoe/logs/cu132-recovery0908c-first16-full13-001/stack-manifest.json --image nvcr.io/nvidia/pytorch:26.05-py3 --node-id hu-pdx-133 --execute
```

The installer backs up the single old file before writing and verifies the complete 1572-file source inventory before/after. It performs no native import, compilation, cache operation, GPU test or automatic performance launch. The validation and performance runners default to dry plans and reject old source/preflight, changed helper closure or mismatched native owner. Candidate preflight and all numerical/performance results are still prospective.
