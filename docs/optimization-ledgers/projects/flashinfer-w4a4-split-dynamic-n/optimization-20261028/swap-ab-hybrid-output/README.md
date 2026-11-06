# Swap-AB output-store experiments

Local-only work from the padded R2 source at retained HEAD `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`. Existing W4A16 and descriptor experiments are untouched. All source edits remain unstaged.

## Arms

- **R2 control:** padded output rows; existing FC2 TMA slabs include partial tails, FC1 direct payload/scale stores.
- **fc2-01:** full FC2 slabs retain TMA; partial slabs use the existing SIMT epilogue and its TMEM transpose. Baseline TMA eligibility and memory sizing remain unchanged.
- **fc2-native-01:** identical full/partial policy, but both paths use the existing native bulk TMEM fragment. Partial stores consume the converted fragment directly, avoiding the tail TMEM transpose. This matches W4A16's shared-fragment principle without changing physical warp IDs or adding dequantization warps.
- **fc2-native-03:** native-fragment policy extended to N16/N32/N64, with slab extent and stage count clamped before computing storage; N128/N256 planning is unchanged.
- **fc1-02:** full slabs stage payload for TMA, partial slabs use direct stores, while scale stores and quantization math remain unchanged.

## Active review workspaces

- `../../flashinfer-swap-ab-hybrid-output-review`: FC2-01 plus FC1 payload work.
- `../../flashinfer-swap-ab-fc2-native-output-review`: FC2 native-fragment tail experiment.

## Validation and timing

Focused paired exact payload/scales/FC2/final comparisons precede timings. No sanitizer. Source snapshots contain hashes for all 348 relevant files and share the existing persistent native compilation cache. Timings use frozen saved tactics and strict CUPTI; no autotuning. Initial screen has eight affected prefill cells covering every model/topology and all four non-W4A16 modes, plus an unchanged decode control. Hardware: existing C3 eight-B300 allocation, CUDA13.2 NVIDIA PyTorch `26.05-py3`.

No PR or branch update is part of this experiment.

Compile bring-up: native01/02 had a CuTe DSL local-name join failure; native03 renames branch-local coordinates. FC1-01 had an IR dominance error; FC1-02 computes its distinct TMA channel coordinate outside elected-thread control. These snapshots are separate; no timings were taken on failed builds. FC2-01 valid outputs passed the initial exact gate, while writes to some owned inactive padding rows were observed and remain a diagnostic (no public untouched-padding contract).
