# Uniform v9 candidate

Baseline: `36740c36a32a6c6d1c7d8162823fe823912de741`.

`uniform-v9.patch` applies to that baseline and changes only the split W4A16 launcher, its kernel, and the existing MoE test's low-level FC2 call (`top_k=0`). Complete files and SHA-256 values are under `uniform-v9/`, including `METADATA.json`.

- The original 23 tactics and cluster ownership remain unchanged. There is no tuner delta, mixed-cluster helper, mixed launch attribute, fallback argument, runtime physical-width query, or mixed test case.
- FC1 gathers original activation rows and removes standalone permutation. Top-k remains a compile-time specialization. FC2 retains its prior path and passes zero for unused top-k specialization.
- The activation producer caches a prefix of up to 48 route indices with the existing 80-register target. `_load_gather_tile` issues static row groups and returns the producer state. The 176-register epilogue and 128-register transform targets remain unchanged.
- No skipped Gather4 requests or manual transaction completion from rejected v10 are included.

`build_uniform_candidates.py` reconstructs the uniform launcher/test from archived v5 and projects complete v9 onto every original uniform branch. It checks the resulting kernel AST against an independent structural projection. Compared with v5, the only changed existing method is `kernel`; `_load_gather_tile` is the only added method. All transform, MMA-issue, setup, wrapper, and geometry methods are AST-identical to v5. The launcher/test are AST-identical to archived v5.

Local checks passed: Python compilation, Ruff, and patch application against clean baseline file copies. The final campaign ran this exact snapshot: 24 existing bit-exact cases passed in 22.08s, followed by two full-grid candidate benchmark sweeps. Changed-file pre-commit checks also passed. See [results](results/split-v3/RESULTS.md): 1.007745× overall, 1.030856× decode, 0.948616× prefill against the reused baseline. The prefill regression prevents recommending retention; the candidate remains unstaged for review.

The builder also saves `uniform-v10-rejected/` and its patch as an unexecuted projection for possible future isolation. They are not candidates for the current retention campaign.
