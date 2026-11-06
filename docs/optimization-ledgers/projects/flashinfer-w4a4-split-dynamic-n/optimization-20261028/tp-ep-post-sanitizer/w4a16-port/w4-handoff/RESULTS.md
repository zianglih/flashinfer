W4A16 logical-stage handoff cleanup passed. The mainloop now passes only the logical K extent; the issue helper derives native M/N/K and CTA count from the existing `tiled_mma`. The static fallback derives its own atom count. No atom count or N-alignment argument crosses that boundary.

- Candidate kernel: `cf503fe43234deac7f11aa855f26a01afffb65189ccfcefd955988ec5ce1854a`.
- Frozen combined control: `2caee0b467e9017bd53847a6401680810653eb4fdaff4573bc788cacb1a60126`, base `fd72759b15b8d417d6c791c0382f90d14262a8e4`.
- Only this W4 kernel differs across the 349 pinned sources. The other agent's blockscaled edits were excluded from the remote candidate.
- Primary C3 B300 GPU0, `nvcr.io/nvidia/pytorch:26.05-py3`; exact interpreter/dependencies are in `evidence/runtime.json`. Generated PTX retains the existing NVVM13.4.59 compiler header; the image CUDA runtime is a separate layer. Existing native compilation cache links remained intact.
- Existing main gate: **16 exact cases, 112 graph replays, 24 compiled kernels**; old64/new16 weight layouts, one/two CTA, ordinary/CLC scheduling, PDL on/off, aligned and partial-K reductions, zeros/cancellation/poisoned unused storage.
- Existing layout API test: **4 passed**, zero failures/errors/skips.
- N192 supplement: **2 exact cases and24 graph replays per source**, M128/CTA1 and M256/CTA2 with K128 stage geometry.
- All **26 paired raw PTX, cubins, SASS dumps, and resource reports are byte-identical**. Local and uniform-register spills/fills remain zero. Therefore no new timing campaign was run or claimed for this interface cleanup.

```text
candidate exact cases: 18
candidate graph replays: 136
layout API tests: 4 passed
paired compiled kernels: 26
raw identical PTX / cubin / SASS / resource reports: 26 / 26 / 26 / 26
source postflight: 349 verified
GPU0 processes after completion: none
```

The first supplementary N192/K256 attempt failed in the unchanged control before compilation: the existing resource planner allows only one transformed-A stage after its two accumulator stages, below its required minimum of two. That attempt's complete log/result/status remains in `evidence/n192-control` and the original `evidence/status.json`; no product policy was changed. The K128-stage supplement then passed both sources. Previously rejected forced-static helper cases were not retried or repaired.

`evidence/GATE.json` SHA256: `8b205a2a0575749902be9372e192e8573c793e122ccb6a81b024095842cb23fb`.
The local raw archive has **150 hash-verified files**; `evidence-verification.json` and `qualification.json` bind the archive, source, local re-audit, and final receipt. The original measured combined source, performance evidence, and earlier gate remain unchanged. Final sanitizer launch stays held for the eventual retained source binding.
