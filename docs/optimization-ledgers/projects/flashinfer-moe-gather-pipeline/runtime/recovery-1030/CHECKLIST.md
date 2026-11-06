# Recovery contract

The replacement is `fi-gather-pipeline-recovery-1030`, C2/ziangli, explicit
`nvcr.io/nvidia/pytorch:26.05-py3`. This is an environment recovery, not a new
source, tactic or timing policy. The interrupted run remains immutable at
`runs/mma-readiness-screen`; its config SHA is `89e7fa42`.

1. **Recorded packages:** install only `pins.txt` using
   `/usr/bin/python3 -m pip install --disable-pip-version-check -r pins.txt`.
   Use `nvidia-cutlass-dsl[cu13]==4.8.0`; do not explicitly name the transitive
   `libs-cu13` wheel because that changes its REQUESTED/RECORD fingerprint.
   Keep the image's torch `2.12.0a0+5aff3928d8.nv26.5.50603568` and torchvision.
   `install.json` preserves before/after versions and the exact command.
2. **Strict runtime identity:** compare the full `_collect_metadata()` result
   to `harness/cache-import.json`, not only package version strings. Confirm
   CUDA/ptxas 13.2.78, CUDA Python/bindings 13.2.0, core1.2.1, CUPTI Python13.2.0
   and library13.2.86. No winner-cache namespace rewrite or retuning.
3. **Persistent sources:** verify both13245-file inventories and every native
   data link. Control remains `candidate-fc1-integer-store-perf` (49-equivalent)
   and candidate remains `candidate-mma-readiness` (e908 overlay). The exact
   manifests and paths are in `expected.json`; `persistence.json` records the
   recovered bytes. No link replacement was necessary.
4. **Persistent native cache:** keep the original `workspace_base` at the old
   project's `upstream-integration-20261029/megamoe-glm5/cache/cpp`. Keep
   project `cache/cute-perf` and `cache/driver`. All four original ELF and Ninja
   fingerprints are preserved in `expected.json` and `persistence.json`.
   The generated Ninja descriptions must remain byte-identical in both arms.
5. **Release-only warmup:** ordinary workers clear all FlashInfer/CuTe/TRT/FI
   overrides and leave JIT DEBUG/VERBOSE unset (release defaults). The warmup
   explicitly sets both to0, never VERBOSE=1 (legacy debug fallback). Preserve
   architecture10.3a, FP4 fast-math flags0, strict cache key1, PDL1, distributed
   autotune0, MAX_JOBS4 and OMP_NUM_THREADS1. New TVM header mtimes require a
   normal routing/moe_utils rebuild; no force-clean/touch/rebuild of already
   no-op FP4/MX8. `warm.py` records Ninja dependency reasons, old/new library
   hashes, then requires all four normal build_and_load paths and dry-runs to
   become no-op. It performs no owned kernel launch or timing.
6. **Salvage:** copy all original raw/log/receipt files, including partial jobs,
   to a new local leaf using `salvage.py`. Analyze only complete four-phase
   CAAC jobs after every raw100-sample span, source, route, tactic, cache,
   resource, GPU UUID and clock record is checked. Do not finish an old partial
   phase or overwrite its receipt. The persistence inventory found11 complete
   jobs, but that count is not a substitute for the full raw audit.
7. **Recovery campaign:** use a new run/config directory for every missing or
   interrupted whole job, preserving all56 planned cells exactly once in the
   final job-level union. Both arms of each job run on one recorded physical
   GPU with all four fresh phases. Keep original sample count, warmups,
   compiler flags, frozen routes/choices and geometric phase-median estimator.
   Preserve source/runtime equivalence and campaign labels per row; no phase
   splicing across campaigns/devices. Parent reviews readiness and the recovery
   config before any timing launch.

Managed HAI is `/usr/local/bin/h`, invoked from the read-only
`/Users/ziangli/playground/repos/hai` working directory. No new allocation,
clock change, sanitizer, source edit or benchmark run is part of this checklist.
