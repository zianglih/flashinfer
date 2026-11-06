# PR7290 C3 rebase qualification

Final tested source: `2b4732791a3ce48bc3ae6c030a283fab73854e0e`.

- Final targeted qualification: **98 successful test executions / 94 unique cases**, zero failures, errors or skips. The four additional executions are the existing same-process clamp → ReLU² → SiTU → clamp sequence.
- Broader qualification at `95a998233637b7cb471bcc8ee439497be841276d`: **224 successful executions / 220 unique cases**. Four MX clamp cases overlap its exact and clamp groups.
- Both successful epochs passed the complete 34,759-file tracked-source postflight. No scheduler fixtures, relaxed tolerances, test source edits, numerical substitutions or compiler-option alterations were used. Local pytest collection replay only repeats an existing test for state-isolation coverage.
- Final source supports all four swap-AB quantization modes in exact clamp tests, including non-power-of-two limits. Runtime tensor mutation and CUDA-graph replay are covered. W4A16 both layouts and shared PDL/cache-key interfaces pass.
- No performance benchmark or sanitizer run. Published performance retains its original measured-source attribution.

See `test-body.md` for the concise PR note and raw pytest group summaries. Complete original stdout, JUnit XML, launch commands/environment, JIT build records and postflight receipts are under `evidence/{final-tests,verified-tests}/`; `verified-summary.json` gives final counts.

## Runtime

- C3 `infra/fi-pr7290-rebase-1102`, node `hu-wtc-25`, 8×B300 SXM6 AC, driver 595.91.07.
- Image `nvcr.io/nvidia/pytorch:26.05-py3`, selected from the live NGC catalog as the newest CUDA13.2 image. CUDA13.2 / NVCC13.2.78; Torch `2.12.0a0+5aff3928d8.nv26.05`; CuTe DSL4.8.0, embedded compiler reports13.4; pytest8.4.2.
- Isolated system-site-packages environment and persistent caches: `/data/ziangli/flashinfer-moe-gather-pipeline/rebase-20261102/`.
- Python: `venv/bin/python`; native C++ cache: `cache/native-final`; strict CuTe source-key cache: `cache/cute-final`; cubins: `cache/cubin`.
- Bare devbox, no size override. First ziangli request had no quota and was deleted before retrying infra. The user's pre-existing CUDA13.0 box was untouched.
- Catalog/release-note URLs and exact pins are in `image-selection.json`, `runtime.json` and `bootstrap.py`.

## Test epochs and source provenance

1. Exact b17 git archive and all four pinned submodules were exported with SHA256 manifests. The first numerical launch raced setup of ordinary editable-install `flashinfer/data` symlinks and exited on missing native quantizer source paths; these infrastructure failures remain in `evidence/b17-tests`. The independent K-tail/legality98 and API23 cases passed.
2. Symlinks were validated before launching the full95 suite. Cold native compilation took most of its wall time. All224 executions passed. The final receipt certifies no tracked-source changes.
3. The017 epilogue-state cleanup failed CuTe compilation because calling a local object's bound method made the compiler treat that Python object as a runtime loop-carried value. It never reached failing GPU arithmetic; `evidence/cleanup-tests` preserves the failures. W4/interface controls passed.
4. The two explicit unbound-method calls at2b473 fixed that compiler issue. A fresh two-case probe passed before the final94-case suite and four-call state sequence. All98 final executions passed.

The remote source path `source-95a998233` was reused only **between completed test epochs** to preserve identical native C++ input paths and avoid redundant rebuilding. Each source transition is explicitly hashed in `prepare-cleanup.log`, `unbound-probe.log`, `bind-verified.log` and the corresponding manifests. The final full-tree manifest is `payload/source-verified.json` on the devbox and is bound to2b473. Earlier original source archives/patches remain available locally. No source mutation occurred during any successful test epoch.

## Reproduction

`run_verified.py` contains the seven independent pytest argument lists, GPU assignments and environment; `run_state_sequence_verified.py` contains the fourth-call replay. Each group's `receipt.json` contains its exact executed command. `run_final.py` preserves the broader95 suite. All harnesses are local to this task and are not repository changes.
