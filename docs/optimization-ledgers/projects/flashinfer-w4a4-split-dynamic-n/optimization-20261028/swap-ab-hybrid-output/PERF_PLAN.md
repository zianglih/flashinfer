# Bounded output-store performance screen

The first useful screen compares padded R2, FC2 full-subtile TMA/partial SIMT, and the native-fragment FC2 variant. No source changes, PR updates, baseline TRTLLM reruns, autotuning, or sanitizer are part of this screen.

- Run each cell on one B300 using fresh interleaved phases: R2, FC2-only, native, native, FC2-only, R2. Report direct R2 ratios for both candidates and the native/FC2-only ratio from the same run.
- Use the saved public benchmark winner for each shape. Verify the cached key, runner, tactic, route identities, source hashes, and GPU UUID in every phase. Share existing persistent native compilation caches while copying immutable autotune winner caches per arm.
- Use `bench_moe_deepseek.py`, the functional API, swap-AB, and unfused finalize. NVFP4 includes input quantization; the existing per-token recipe remains unchanged. Timing requires 100 CUPTI samples after 10 warmups with CUDA Graph replay and cold L2. Event fallback and AUTO are errors.
- Record actual compiled `epilogue.bulk_tokens`, `bulk_stages`, operand stage count, logical tile, CTA count, and dtypes as passive host metadata. This confirms the measured code path rather than inferring it from routed N alone.
- Require exact valid FC1 payload/scales, FC2, and final output checks before timing. Owned padded rows were writable in R2; writes there are a documented internal-contract diagnostic, not proof of out-of-bounds corruption. Do not claim padding preservation for arms that write them.

`bounded-screen-02.json` contains 13 cells: eight original-bulk prefill cases covering every model/topology and all four non-W4A16 modes; five small-N decode cases cover the all-N native policy. The latter are unchanged only in the FC2-only arm. Keep the prefill and decode aggregates separate.

| Job | Tokens | Mode | GPU |
|---|---|---|---:|
| V3 EP8 | 64, 4096 | W4A4 | 0 |
| V3 TP8 | 4096 | MXFP4x8 | 1 |
| V41F EP4 | 64, 4096 | MXFP8 | 2 |
| V41F TP4 | 64, 16384 | W4A4 | 3 |
| K3 EP8 | 4096 | Per-token | 4 |
| K3 TP8 | 64, 4096 | MXFP4x8 | 5 |
| N3U EP8 | 4096 | MXFP8 | 6 |
| N3U TP8 | 64, 4096 | Per-token | 7 |

Current allocation: `fi-moe-descriptor-recover-1028`, C3 namespace `ziangli`, eight B300s, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, driver 595.91.07, CuTe DSL 4.8. Correctness initially owns GPUs 1–3; timing starts only on explicitly released, freshly idle-checked lanes.

Frozen `fc2-screen-01` and `fc2-screen-02` were prepared but never launched. Native01 failed a CuTe DSL local-variable join before a valid native timing result existed; native02 retained that naming issue and its timing config stayed inert. Use a new screen for the corrected native snapshot.
