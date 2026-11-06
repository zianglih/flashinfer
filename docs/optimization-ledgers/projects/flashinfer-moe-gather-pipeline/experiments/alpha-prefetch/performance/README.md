# Held pre-wait alpha-prefetch screen

Prepared only; no timing or GPU work has started. The candidate must first pass the source/exact/native gate and receive the parent's performance release. This is the pre-wait expert-alpha reuse change, distinct from the rejected historical post-wait alpha-reuse candidate.

- Current retained `c1ac8ce7341039db65195b99445fcdeb193cf226` control versus swap SHA `2a6968117f2ab22bee751357667cc1dbb0edeb1f41f4a99c7112f588fc1310fd`.
- Both source snapshots are owned by qualification; this preparation created no source copy. Qualification source manifest hashes are control `efa5c55f2391ffc52098f15e016a29939c56529b850a60be4bdf3c61cf392a6c`, candidate `04ea1317919f4688ab99f299814664c5791620b463ead8d55cd6389b5b5e4927`.
- The completed interleave screen supplies the exact unchanged 23-job / 28-arm matrix at T32 and T16384, all 56 explicit recorded choices and 46 route rows, and all 12 byte-identical helpers. No W4, unsupported combinations, new policy, or autotuning.
- Held protocol: C–A–A–C, 100 strict CUPTI samples per phase, 10 warmups, cold-L2 graph replay; 22,400 total samples. Per-token input quantization remains included. Every negative, repeat spread and clock observation is retained.
- Config `screen/perf-config.json` SHA `9054f1221dec38fbbaaa2c34e8b1298f4b9acd0dac1472e5931d3abced1c6182`; remote `runs/alpha-prefetch-screen`. GPU allocation remains empty.
- Recovery runtime/native-cache receipts are bound, but fresh release ELF/Ninja/no-op and GPU-idle checks are still required at any authorized launch. No launch helper has been invoked.

The old interleave preparation/results are unchanged. `prepare_inputs.py` and `prepare.py` reuse the same workflow, replacing only the candidate/base bindings and experiment destination.

## Authorized launch

The final20-call/30-native-pair gate `c04d8b71` passed and the parent released the single screen. Controller94392 launched on recovery GPUs0/1/4/5; `screen/launch.json` and `screen/launch-preflight.json` bind the unchanged9054 config and current release cohort. The original held preparation above remains historical. One local null-occupancy metadata check failed before any remote execution and is preserved in `screen/launch-local-check-1.json`; numeric occupancy/resource gates are unchanged.
