# Full row-index hoist: register-budget screen

This is an **off-tree proposal**, not a retained change. Production mixed V6 is unchanged. The candidate patch is `full-hoist-uniform128.patch`; its complete source is under `full-hoist-proposal/`.

## Why per-warp 128/64/64/64 is excluded

Warps 4–7 form the control warpgroup: MMA, scheduler, weight TMA, activation TMA. [PTX setmaxnreg](https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg) requires the same register-adjustment instruction across a warpgroup and identifies divergent execution as undefined. An equal aggregate register count does not make different limits for these four warps supported.

The current source uses 176 registers for each epilogue thread, 80 for each control thread, and the 128-register launch default for each transform thread. There are 4, 4, and 8 warps respectively:

| Region | Current registers | Uniform128 candidate |
| --- | ---: | ---: |
| Epilogue, 128 threads | 22,528 | 16,384 |
| Control, 128 threads | 10,240 | 16,384 |
| Transform, 256 threads | 32,768 | 32,768 |
| Total per CTA | 65,536 | 65,536 |

Giving the entire control warpgroup 128 while keeping epilogue176 would require 71,680 registers. The proposal therefore lowers the FC1 epilogue target to128; FC2 keeps its current176/80 targets. This is an explicit performance tradeoff: spilling or slower epilogue code can outweigh producer savings. The saved V4 PTX launches512 threads with `.minnctapersm 1`; the compiled resource report must still confirm the proposed allocation.

## Candidate

- Cache up to96 invariant row IDs before the activation K loop. N192 fallback2 then needs no row-index shuffle inside K; larger supported partitions retain shuffles for rows beyond96.
- Retain the distributed four-index map load and one elected issuer. Only the location of invariant broadcasts and the FC1 role register targets change.
- Preserve Gather4 payloads, multicast, barriers, descriptor layout, top-k specialization, arithmetic, and all warp ownership.

This follows the useful part of [FlashMLA's issuer-owned index reuse](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/prefill/sparse/fwd_for_small_topk/head128/phase1.cuh#L420-L473) without adopting its four-producer-warp topology. It does **not** promise elimination of `R2UR`/`UMOV`: cached per-thread row registers can still require repacking into uniform operands each issue group. Actual SASS is the decision point.

## Screen before timing

After mixed V6 is archived and validated, apply the patch only to an experiment snapshot. Capture N128 and N192 for cluster2 and mixedcluster4, then compare:

1. ptxas resource output and local-memory spill instructions in the activation and epilogue regions;
2. actual K-loop `SHFL`, `R2UR`, `UMOV`, and total instructions;
3. unchanged real Gather4 transaction counts;
4. exact smoke results followed by the existing four-point performance screen only if code generation is useful.

Local syntax, Ruff, and `git apply --check` passed. No GPU compilation, SASS, correctness, or timing claim has been made for this proposal.
