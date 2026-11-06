# NVFP4 MMA exact-reference review

Review: https://github.com/flashinfer-ai/flashinfer/pull/7290#discussion_r4452342895

Source under review: `2b4732791a3ce48bc3ae6c030a283fab73854e0e`.

The unified typed-activation test directly imports the swap-AB reference and does not pass the selected MMA plans. Its default K64 reference is correct for SM100 but does not model SM103's K96 updates and K64 stage tails. The existing specialized accuracy module observes compilation and cache hits, but patches only its own reference binding.

The local, unstaged fix moves that observer into an opt-in shared MoE fixture. The specialized module calls the reference through its module, and the unified test opts into the same fixture before its local import. The observer still captures the selected FC1/FC2 stage widths, including automatic k_steps and cache hits. Kernel dispatch, numerical oracle arithmetic, tolerances, and benchmark results are unchanged.

For NVFP4, a 256-element stage uses `(96,96,64)`; a 512-element stage uses `(96,96,96,96,64,64)`. A final 128-element stage uses `(64,64)`. An architecture-only uniform K96 plan would not be correct.

On B300/SM103 (C3), all four unmodified unified NVFP4 cases passed at zero tolerance in 29.63 seconds. A passive compile observer confirmed native K96 with FC1 tile_k=512 and FC2 tile_k=256. The plan mismatch is therefore confirmed, but the predicted output-bit failure was not reproduced by the current small fixture. After the fix, all eight cases passed: four unified activations, two functional cases, and two wrapper cases, including per-token NVFP4. Tested file hashes match the canonical working copy; production sources and native artifacts are unchanged.

B200/SM100 validation initially encountered an OIDC browser-login timeout. The user completed Google SSO, and C1 access was restored. Bare devbox `fi-nvfp4-exact-b200-1103` uses eight B200 GPUs and `nvcr.io/nvidia/pytorch:26.05-py3`, with architecture 10.0a. All four original unified controls and all eight patched cases passed with no failures or skips. Native K64 and 256/512-element stages were observed. Tested files match the canonical patch, and the new compilation cache remains in persistent storage. No credentials were edited or deleted.

Existing zero-tolerance tests are reused; no new standalone test file or reference-arithmetic test is added. Targeted pre-commit and AST checks passed for all three changed files.

After both architecture validations passed, the three-file fix was committed and pushed as `14a338579eb8acddcc5cfd1cc58871fc0788de22` on the upstream PR branch. The canonical checkout is clean. A concise reply was posted to the review thread and read back exactly; its text and GitHub response are saved in `reviewer-reply.md` and `reviewer-reply-published.json`. The connector denied writes, so the authorized reply used the authenticated zianglih CLI.

Per-device logs and runtime details are under `c3/` and `c1/`. Combined validation covers 24 test executions: four original controls and eight patched cases on each architecture. Existing benchmark evidence remains valid because production sources are unchanged.
