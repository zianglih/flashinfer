# Freeze a passing source for retention

Prepared CPU-only on 2026-10-25. **Procedure only:** no clone, commit, transfer, GPU execution, or campaign-config change was performed. The winner and five-case gate remain pending. Root owns winner selection, the freeze commit, launch approval, and later integration.

Use a new independent checkout at `/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-pdl-retention-frozen` locally and `/workspace/flashinfer-w4a4-split-dynamic-n/pdl-retention-frozen` remotely. Refuse either destination if it already exists. Keep manifests, bundles and receipts under `scripts/pdl_retention_campaign/`; do not add them to the source commit.

## 1. Pin the actual winner before copying

Root supplies the approved base commit, winning source directory, exact named-file SHA256 map, expected changed-file set, supporting-source pins, and the five passing T4/T32/T128/T4096/T16384 receipt paths/hashes. Do not take the latest contents of a mutable experimental directory as the winner. Verify its files against that frozen map before copying.

For a source with behavior knobs, record the effective knob values used by every gate and the values the unchanged canonical observers will exercise. Preserve those exact source bytes/defaults. A different default or a helper-only override is not established as equivalent merely by copying the same kernel body; root must resolve that before freezing. Do not substitute the currently pending explicit-phase manifest or an earlier adcc source for the eventual approved winner.

## 2. Create the independent local source checkout

Create from a **project-owned** seed containing the approved base, without copying the seed's dirty worktree:

```bash
git clone --no-local --no-checkout "$approved_seed" "$local_frozen"
git -C "$local_frozen" checkout --detach "$approved_base"
```

These are templates; root sets the quoted variables only after the freeze decision. Use a complete seed, not a shallow or partial clone with missing objects. Do not use `--shared`, `--reference`, worktrees, copied `.git` files, or repositories under the shared `playground/repos` tree. Require `.git` to be a directory, both `git rev-parse --absolute-git-dir` and `git rev-parse --path-format=absolute --git-common-dir` to resolve inside this new checkout, and no object-alternates dependency.

Copy **only** the regular source files named in the winning hash map, preserving the approved file modes. Resolve/check each path is inside the source and destination roots, and reject unexpected symlinks in either path before writing; do not recursively copy the experimental checkout, `.git`, logs, caches, or ignored files. Verify destination SHA256s equal the map and `git diff --name-only` equals the approved changed-file set. An unchanged file included in the hash map need not appear in that diff. Verify supporting source pins and unchanged native `csrc`, `include`, and `3rdparty` Git trees against the approved base.

Root reviews and creates the freeze commit in this checkout, staging only the named approved changes. Record its full SHA, parent and tree. After any hooks/formatting, hash both working files **and** `git show <freeze-sha>:<path>` blobs against the winning map. If either differs, stop: a commit with altered bytes is not the gated source. Production/benchmark changes must now be committed; existing observers reject tracked or untracked changes in those paths (`scripts/run_split_benchmark.py:70–79`). No push or integration is part of this freeze procedure.

## 3. Transfer the exact commit, without a remote recommit

Create a self-contained bundle of the committed HEAD, plus a receipt containing the approved base, freeze SHA/tree, winning source map, gate hashes, and bundle SHA256:

```bash
git -C "$local_frozen" bundle create "$bundle_path" HEAD
git -C "$local_frozen" bundle verify "$bundle_path"
git -C "$local_frozen" bundle list-heads "$bundle_path"
```

Using `HEAD` without exclusions includes its reachable history; do not make an incremental bundle with an unstated prerequisite. Check the advertised HEAD equals the approved freeze SHA. Transfer only this bundle and its receipt to a new project-owned remote staging directory. For HAI transfer, first verify `command -v h` resolves to `/usr/local/bin/h`, then use that managed executable; the existing named-file provisioner demonstrates `h sync --no-git-based` in `scripts/pdl_allthread_experiment/provision.py:30–32`. Do not execute that old provisioner: it pins a different source and destination.

Verify the uploaded bundle's SHA256 before creating the remote repository. Then import its commit objects directly:

```bash
git init "$remote_frozen"
git -C "$remote_frozen" bundle verify "$remote_bundle"
git -C "$remote_frozen" fetch "$remote_bundle" HEAD
git -C "$remote_frozen" checkout --detach FETCH_HEAD
```

Require remote `HEAD` and tree to equal the local freeze SHA/tree; recheck all named source blobs and working-file hashes. **Do not run `git commit` remotely.** A second commit from identical files can have a different SHA because metadata differs. Require the remote `.git` and common Git directory to be inside `pdl-retention-frozen`, with no alternates or linked-worktree dependency.

## 4. Preserve the actual native input roots and cache epoch

A Git bundle does not transport ignored data, generated metadata, or compiler caches. Remote discovery established that `profile-aab93f/3rdparty` directories are empty/uninitialized; native compilation uses the roots selected by `flashinfer/jit/env.py:398–411` through `flashinfer/data`. **Preserve that control layout.** The earlier blanket requirement to initialize or link every checkout gitlink is withdrawn.

The actual resolved inputs are recorded in `scripts/pdl_retention_campaign/provision-r2/native-header-discovery.json`: data `cutlass`, `cccl`, and `spdlog` resolve to `baseline/3rdparty/{name}`; data `csrc` and `include` resolve to `candidate/{name}`. Those directory names identify existing storage, not a request to switch source or native-cache epochs.

- Link `flashinfer/data` to the exact resolved native-data target used by remote `profile-aab93f`; record its resolved path and the existing native-data/build identity receipt. Verify the exact data-entry input roots selected by `jit/env.py`, rather than falling back to the frozen checkout's empty `3rdparty` directories. The discovered header HEADs match their pinned gitlinks: CUTLASS `b46b16d003484063bca4ed365e44095c4c6ed633`, CCCL `16bd510c9b712e82b0ab6cbb630d8e29ba1f7116`, spdlog `c3aed4b68373955e1cc94307683d44dca1515d2b`. Check those actual targets' HEAD/content identity and the native `csrc`/`include` tree equality against the approved control/freeze/build evidence; never modify or reset the targets.
- Leave unused `nixl` uninitialized: it is uninitialized even in the baseline and is not an input to this single-GPU campaign. Do not initialize/download it or require `git rev-parse` inside its empty directory to identify a vendor repository; Git can instead return the enclosing repository's HEAD. Do not add vendor links to the control or frozen checkout merely to satisfy a generic guard.
- Preserve the project's existing native files and host-local link targets; do not transport macOS absolute links to the devbox. Ignore only the known untracked `flashinfer/data` link in the new checkout's `.git/info/exclude`, as in `scripts/pdl_allthread_experiment/provision.py:15–16` and `scripts/regular_tma_review_cleanup/deploy_remote.py:19–23`. Never use broad ignore rules or assume-unchanged flags to hide source edits.
- If the environment requires ignored generated `flashinfer/_build_meta.py`, preserve the approved control's exact bytes and record its hash; do not overwrite a tracked version or silently generate new metadata. The existing setup precedent is `deploy_remote.py:24–26`.
- Source `scripts/recovery442/env_candidate.sh` in each remote shell. Retain `FLASHINFER_WORKSPACE_BASE=/workspace/flashinfer-w4a4-split-dynamic-n/cache/candidate-442` after verifying the unchanged actual native input roots and native `csrc`/`include` tree identity (`env_candidate.sh:1–8`). Do not switch to the a65 cache or rebuild unchanged native dependencies. Give this freeze SHA its own CuTe cache namespace, reused only for its repeats; a renamed checkout/module does not prove an old experimental CuTe cache hit. Keep AUTO-cache loading disabled as specified in the retention plan.

Do not create or commit `3rdparty` symlink replacements. Require no tracked diff or untracked file under `flashinfer`, `include`, `csrc`, or `benchmarks` after the exact ignored-data-link setup, and preserve full Git status. The outer guard must check the real pinned data/header roots and native source trees; an empty unused checkout vendor directory is not a failure and needs no fallback initialization.

## 5. Hand the frozen identity back to root

Deliver local/remote checkout paths, independent-Git-directory checks, freeze SHA/parent/tree, bundle digest, source/blob hashes, named diff, full Git status, actual resolved header/data input identities, generated-metadata hash if applicable, and the unchanged gate receipts plus effective knob settings. Link the new commit to the gated working-source hashes rather than relabeling an old receipt's commit field.

Root updates the campaign config to the clean frozen commit only after reviewing this evidence, and separately authorizes execution. Keep `launch_approved=false` while the winner/gates are pending. Do not alter `run_arm.py`, observer helpers, existing evidence, or the production checkout as part of this procedure. Later integration remains root-owned and distinct from the immutable measured freeze commit.
