Held source-only rebase of the existing tight logical-row launch proposal. No primary source, runtime manifest, remote installation, compiler or GPU was changed. Original `balanced_launch/tight_rows/` artifacts remain unchanged, including patch `9294894362b35758e9a5a57175d05a974ef0c8e6bb638f7836a60c205fc74a59`.

The new base is the combined central kernel, including wrapper cleanup44f7. Its bytes match both the central proposal and frozen source `184b73863665d3485d6099dc1e8e935e893590c631b9f25f983ace17e722cbc6`, manifest `68fcd4838b83ebd5f6d1d8b1c7abdccd1976df2e8fd2d02f8b363e279e531c8b`. `base-binding.json` pins that provenance.

- Target: `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/megamoe_kernel.py`.
- Base kernel: `667dee07d04af11eb2f67596131b5d67c95132541868e60cb0ff5181c49ab3b7`.
- Candidate kernel: `72b3af7c5f7e9dba8feb9561b85216c57f7a82583204dd8fabce90b9295dc257`.
- Rebased patch: `101b7ccae44e81497c1c8b6eb1786bcdef88ba8f10593d2a736e33b57f3fcd0c`.

Only the original two constructor/launch hunks are transplanted. Added and removed source lines match the original patch exactly; paths and hunk positions now address the central package. Applying the inverse hunks restores every byte of the combined central base, including direct `token_comm` calls and current CLC source imports. No file from the old package replaces a central file.

The exact balanced-row bound remains `k + (R-k)//N`, where `R = max_tokens_per_rank * num_topk`, `k = min(num_experts_per_rank, R)`, and `N = cluster_tile_tokens`. Only the initial physical launch estimate changes. Full worst-rank workspace, bitmap/queue capacity, actual-count guard, software fallback through all real bundles, fixed transport grids and final reset ownership remain unchanged. Exactly two decode/five total warpgroups remain unchanged. The estimate is not a correctness bound on skew; complete software fallback still covers that work.

The original arithmetic/ownership checks and proof are reused, not rerun or relabeled as new tests: `balanced_launch/tight_rows/host-checks.json` SHA `8975a63f47583a6912a25ec0972fa151378c1f3715d8353696c42d22979ac129` and its `RATIONALE.md`. New checks are bounded to the rebase: original hunk content equality, complete inverse restoration/AST equality, syntax, repository Ruff lint/format, and `git apply --check` against the saved central base. See `rebase-checks.json`.

Wait for the central baseline validation. Then port only `source.patch` to the reviewed base and generate a fresh source/install declaration through the existing workflow. No native, numerical, graph-progress or latency outcome is claimed. Activation-SF cleanup and payload overlap are not included; any later combination needs a separate reviewed merge and source identity.
