# Final focused existing-test validation

Frozen source: `flashinfer-quant-tail-guard-20261026`, HEAD `dd266b91fdf61dae2de45ee9192d36c81c56be23`, full unstaged patch SHA256 `f8ba9aeec6cd3f10925ca67712d7743468772145bcb71f70bef54de2386189ee`. This is B+C plus the per-token quantizer tail guard. Native/source cache identity and all selected test-file hashes were verified before and after both campaigns.

Environment: c3 devbox `fi-moe-nvfp4-port-1026`, host `hu-wtc-101`, B300 GPU7 for GPU selectors, NGC `nvcr.io/nvidia/pytorch:26.05-py3`. Runtime CUDA13.2, bundled CuTe NVVM13.3. Python path remains the original `control-0def601d/.venv/bin/python` without resolving its symlink. CPU cases ran with `CUDA_VISIBLE_DEVICES=''`; GPU cases had only GPU7 visible. Both used the candidate's source-private CuTe workspace and source-verified persistent native cache.

**197 unique existing cases passed, zero failures/errors/skips.** No new upstream tests, broad suite, or sanitizers were run.

| Group | Passed | Pytest seconds |
| --- | ---: | ---: |
| cache-names | 37 | 0.638 |
| tactics | 109 | 0.868 |
| large-m | 4 | 3.813 |
| quantizer-defaults | 36 | 14.306 |
| gated-moe | 5 | 15.405 |
| autotuner-integration | 6 | 1.079 |

The36 quantizer-default cases are18 wide-row cases (M130,K1536/18432/69632, both input dtypes/all SF layouts) and18 output-scale/padding cases. Large-M covers four default-caller/PDL/int32-addressing cases. The five gated MoE cases cover GeGLU, both SiTU clamp modes, wrapper accuracy and CUDA-graph replay. The115 tactic/config/blocklist cases are109 CPU-only cases plus six integration cases with a GPU visible, deduplicated against the other groups.

`validation.json` includes all197 exact node IDs, commands, source hashes and JUnit/stdout digests. `results/manifest.json` hashes every collected raw artifact. Raw command JSON, stdout, JUnit and source-before/after receipts are under `results/quant-tail-guard/existing-tests-{cpu,gpu}/`. GPU7 was explicitly released after all GPU subprocesses ended.

Two task-local reporting issues are kept in the record. The first CPU selection recorder ran before pytest applied `-k`, so its cache-name command passed37 cases but the recorder counted69 collected candidates. The CPU campaign was rerun with final-selection recording; the197-case count includes only the completed CPU campaign. The GPU driver raised an AttributeError in its last status print after all51 tests passed, its source-after check succeeded, and its completion receipt was written. The validated report checks those receipts and clean JUnit directly; no passed GPU tests were rerun.
