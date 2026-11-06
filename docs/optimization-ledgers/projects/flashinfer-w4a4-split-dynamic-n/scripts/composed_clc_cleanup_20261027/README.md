# Composed cleanup gate preparation

Parent authorized the frozen source and candidate-only GPU0 execution. The candidate composes normalization hoist, scheduler PDL startup and local metadata-tail removal on the current canonical source without the all-CLC policy change.

Reuse the completed4e155 control from `clc_info_tail_20261027`:40 exact changing-route replays,20 core variants. The candidate uses the identical helper bytes and exact input/config/route recipe. Reuse requires the prior complete receipt, helper hash,40/20 counts, original control source pins and saved raw artifact hashes to match. Only candidate executes on verified-idleGPU0; no control rerun or timing.

The candidate freeze records the exact clean HEAD/tree,87 dependency/source hashes and hashes for every tracked regular file. Verify these before/after execution, compare all output/input/routing hashes, unchanged pipeline/storage geometry and zero spills, and report instruction/register differences from retained PTX/CUBIN/SASS. The low-level probe explicitly chooses CLC for both phases to exercise these changes, while the final public scheduler policy remains unchanged.

## Frozen candidate

HEAD `f5e7bdc8783718e225771c4e0c65c9692821beb1`, unstaged patch `4f41cc0cd8af244c7506cb017a44ba87b68309753845a935e7c3a5cb3c153edd`. All 12906 tracked regular files, 4 gitlink entries and 87 dependency files are recorded. Root authorized this freeze and candidate-only execution; no source mutation occurs during the gate.

## Completed result

The candidate passed40 source-paired exact changing-route graph replays against the saved control, with20 compiled FC1/FC2 pairs. The original control was not rerun. Every register count, storage/pipeline geometry and TMEM commit count is unchanged, with zero local-memory spill instructions. The composed candidate removes5–9 static SASS instructions per kernel (154 total across20 pairs); startup-PDL relocation adds an ACQBULK site in the enabled variants while the metadata-tail wait loop is removed. This is codegen evidence, not a timing claim. All12,906 source files and87 dependency hashes verified unchanged before/after execution. Raw179-file evidence lives under`results/`;`summary.json` and`validation.json` contain verified counts.

The final retained commit is `9b4721b08057d0a488c1f0236467acb75c48cd00`; its whole tree matches the tested composition. See `composition-review.md` for the dependency proof, including the scheduler's delayed `griddepcontrol_wait()` after the cluster response tail and before the final CTA barrier. Derived boundary wording now explicitly names all three changes; frozen raw evidence is unchanged.
