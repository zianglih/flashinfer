# Focused existing-test result

- **Result:** 11 passed, zero failures/errors/skips; pytest 20.35 s. Complete process including collection and source verification took 36.79 s.
- **Snapshot:** full-gate-02 frozen candidate, base HEAD `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`; exact candidate source hashes, environment, command, node list, GPU UUID and timings in `receipt.json`. Source hashes verified before and after testing.
- **Environment:** existing `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, C3 `fi-moe-sanitize-1028`, GPU1 B300; persistent candidate/native caches preserved.
- **Coverage:** six W4 scale-mapping combinations (row/K scales × one-CTA/two-CTA/cluster2); W4 route16 tail1 and route128 two-CTA half-plus-one boundaries; functional W4 weight-scale updates with original and swap-AB weight layouts; swap-AB FC1 N16/K192/17-token partial-K case. Existing bit-exact assertions ran unchanged apart from the previously authorized private-entry descriptor setup.
- **Boundary:** full-gate-03 froze after this run launched; W4 source is unchanged. The later FP32 FC2 pointer-swizzle correction is outside this test selection. This gate does not prove FP32 FC2, changed-routing graph replay, or performance. No autotuning or sanitizer ran.
- **Warnings:** upstream CuTe DSL deprecation warnings plus JIT-argument warnings for empty `output_ptrs`/`output_banks` tuples in the descriptor-free direct FC1 path. They did not prevent compilation or exact assertions; no warning cleanup was mixed into this frozen-source gate.

Raw output: `pytest.log`; JUnit: `junit.xml`; launch/process receipt: `launch.json`, `launch.log`; full source-bound receipt: `receipt.json`; exact helper: `run_pytest.py`.
