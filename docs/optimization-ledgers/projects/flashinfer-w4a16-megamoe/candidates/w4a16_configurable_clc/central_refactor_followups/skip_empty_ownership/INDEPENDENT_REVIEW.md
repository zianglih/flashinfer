# Independent skip-empty ownership review

No concrete source-level correctness or progress defect found in patch
`eceefc318d7d2d1cc03b495799d6528dfc0a318ea7f2df2d1a8832bd70031484`.
The saved base and current primary `clc.py` both hash to `b2b7d6c3`; proposed
source hashes to `0dc79a78`. Review only: no source edits, tests, compilation,
GPU execution, or additional validation gate.

- **Uniform inputs.** In `run`, initial `x // cluster_x + z` is identical
  throughout each aligned supported C1/C2 cluster. `bundles` derives from
  immutable expert counts and common geometry. Software scan IDs pass through
  the existing cluster broadcast before reaching this helper. A failed scan
  leaves the same negative bundle and exhausted state on every participant.
- **Uniform hardware replies.** The saved installed `PipelineClcFetchAsync`
  (`candidates/cuda132_recovery_0909e/dsl_pipeline_source/cutlass/pipeline/sm100.py`,
  lines 796–1005) fans out full-barrier expectations to every cluster CTA;
  consumers wait for their local reply and release CTA0's empty barrier.
  Existing C1 PTX at `profiles/cu132-recovery0909e-central-clc-small-c1-001/`
  and C2 PTX at `profiles/cu132-recovery0909e-clc-m256n64c2-reuse-003/`
  both issue `try_cancel...multicast::cluster::all.b128`. The decoder returns
  the same ID on success and initializes the result to -1 on failure, without
  reading failed coordinates. The response read, CTA fence, consumer release,
  and state advance all still precede the helper call.
- **State and publication.** The new outer bounds branch is therefore uniform
  across every owner-warp lane and both C2 CTAs. Its false path returns the
  incoming `ds` and `claim_state` without advancing either broadcast state.
  The true path preserves the elected bitmap claim, ownership broadcast, and
  claim-pipe publications in their original order. A valid bundle whose bitmap
  bit was already claimed still broadcasts zero; that result cannot safely be
  inferred by other lanes or CTAs, and the patch does not attempt to do so.
- **Progress and tails.** Invalid initial helper IDs can proceed to the regular
  task/terminal loop. Hardware failure still permanently disables later queries;
  software exhaustion still permits ready-FC2 polling. The skipped broadcast had
  no claim or publication to carry. Prior broadcast reads retain their existing
  release fence/arrival, and future broadcasts acquire the unchanged state.
  The final producer tail drains the actual broadcasts issued. Claim-pipe drain,
  epilogue completion, DONE publication, final CTA barrier, and whole-grid finish
  remain unchanged, including for late initial CTAs.

The direct benefit is removal of a full ownership broadcast for invalid initial
or cancelled helper IDs and for repeated exhausted-loop `bundle == -1` calls.
Valid bundles pay the original protocol plus a uniform outer branch. There is
no new persistent state or buffer and `owned` has a narrower source lifetime.
The branch does introduce conditional merges of the existing returned pipeline
states; source inspection cannot establish native register pressure, instruction
count, or speedup. This is distinct from the held task-or-terminal change, which
is not present in this patch or its base.
