# Count publication with one prefix fence per publishing thread

This is an isolated experiment, **not a retained optimization**. `optimization/counts_fence` starts at `002ef1454cbacde09972ed5e2ec7dcfe37e55749` and applies the exact frozen `counts_overlap` diff, which already includes store16. It then changes only the vendor count publisher in `TokenInPullTokenBackPush.dispatch_barrier`. No primary-source, existing-candidate, remote, or GPU changes were made for this preparation.

The parent task measured `counts_overlap` at0.9675× relative to store16. This experiment tests whether publishing staged inputs with a single prefix system fence can remove repeated release ordering from each expert-count atomic without undoing early scheduler readiness. This ratio motivates the hypothesis; it does not predict the result. Compare performance to the immediately retained stack (`store16` currently), and use `counts_overlap` as the causal control for this fence substitution.

## Exact delta from counts_overlap

```python
software_grid_sync(...)              # unchanged, all local dispatch CTAs
if sm_idx == 0:
    cute.arch.fence_acq_rel_sys()     # new, once per publishing thread
    for ... in ...experts...:
        ...                         # original per-source count store
        rank_count = (Int64(1) << 32) | (status_u64 & Int64(0xFFFFFFFF))
        red_add_relaxed_sys_u64_raw(ercs_peer_addr, rank_count)
    cute.arch.fence_acq_rel_sys()     # existing trailing fence, unchanged
...                                 # original dispatch barrier + NVLink barrier
```

The previous inner update was `red_add_release_sys_u64_raw`. The existing relaxed helper is imported again; rank normalization and low32 token counts are unchanged. The prefix is inside `sm_idx == 0` and outside the compile-time expert loop, so it executes once for each CTA0 dispatch thread, **not once globally or once per expert**. For EP4/E256 and128 dispatch threads, each publisher handles two expert contributions. Other CTAs do not execute the new system fence.

No scheduler poll, sleep interval, marker, named-barrier participant, input-stage ownership, register redistribution, ring bank, or payload-ready condition changes. No copied barrier implementation or new helper is introduced. The existing trailing fence stays because per-source receive counts and subsequent global publication still require their original ordering.

## Source-level ordering proof

1. Input and routing-score staging and dispatch preparation precede the existing local `software_grid_sync`. That helper's NB10 sandwich gathers each dispatch thread's writes, uses a GPU-release atomic plus relaxed completion read/acquire-release fence on its leader, then transfers the acquired visibility to all local dispatch threads through the final NB10. This existing cumulative chain is unchanged.
2. Each CTA0 publishing thread now executes a system acquire-release fence after leaving that grid barrier. A prefix release/acquire-release fence followed by a strong relaxed write forms a PTX release pattern. The 64-bit system-scope RED update supplies that strong write. Each expert's update can use the same prior fence; publication covers work before the fence. The scheduler still issues an Int64 `ld.acquire.sys`, and the existing observation-order chain through peer atomic RMWs allows its completed packed count to observe every source-rank contribution. These are the [PTX release-pattern and synchronization rules](https://docs.nvidia.com/cuda/parallel-thread-execution/#release-and-acquire-patterns), with [observation order](https://docs.nvidia.com/cuda/parallel-thread-execution/#observation-order) handling intervening additions.
3. The scheduler sees high32 equal `world_size` only after all source ranks have added once. The final warp synchronization shares acquired visibility between lanes. Thus early schedule/DONE publication still carries this rank's staged routing-score visibility, including `_prepare_reduce_worker` on compute-idle CTAs. The scheduler's low-word expert-size reads follow completion of all atomic contributions.
4. A subtle boundary matters: the ordinary `stg_b64_raw` updates of **per-source `expert_recv_count` occur after the prefix fence**, so the new count release pattern does not publish those stores. This is safe only because early scheduler/weight-load/decode paths never consume them. Their consumers (`dispatch_pull` and standalone token-back) remain downstream of the unchanged trailing fence, dispatch rendezvous, and NVLink publication. Source input payload fetch and FC1 activation retain their existing global-publication and `fc1_ready_counter` gates. Consequently early weight work cannot use incomplete activation payloads.
5. Existing packed-counter overflow assumptions, one-rank contribution per expert (including zero-token experts), heterogeneous CTA-count support, snapshot bank selection, bank reset/drain, normal replay and NCU cleanup remain identical to `counts_overlap`. No early bank is cleared or reused.

The RED operation is used here as the **write half of a release pattern**; it is not used as an acquire operation. PTX's separate warning that `red; fence.acquire` is not an acquire pattern therefore does not apply. A relaxed count update without the preceding system fence would fail the staged-score proof; this experiment is not that weaker variant.

## What must be checked on device

- Compile and run the same independent-reference and dtype/stride checks as the earlier candidates, including repeated launches and supported NCU replay semantics.
- Confirm native PTX/SASS retains the prefix system fence before all relaxed64-bit count REDs, with the original trailing publication intact. The compiler may lower release REDs into repeated fences, but that instruction reduction remains a hypothesis until native artifacts are inspected.
- Use the same fixed winner, uniform256 EP4 GLM5 inputs, full-forward cold-L2 CUDA graph CUPTI/rank-MAX methodology and serialized comparisons. Report its incremental result against store16 separately from the fence-only comparison to counts_overlap.
- Only capture the regular native IKET trace after correctness/timing allow continuation. Compare scheduler/weight/decode start to the same rank's dispatch-count-sync completion. Poll overhead or late count arrival may still outweigh any saved fences.

## Frozen artifacts and CPU validation

- Worktree: `optimization/counts_fence` (detached002ef145; both Git directories resolve inside this effort).
- Complete patch from002: `counts-fence.patch`, SHA256 `21a06a535f1c9edb3b0349290de72241bf1f0ce9a0d7b5619dfb1caf6b20b438`.
- Incremental review patch: `counts-fence-vs-counts-overlap.patch`, SHA256 `9686e71d351b06a81a2a049d92b545ad87eeed1c9fb25240dc9149c69d8a78fb`.
- Source tree SHA256: `771d8c303c79f299980ce97b9ffff53a24d86afea4ab1383bd2bfdd942d75951`.
- Parent patch and tree remain exactly `41c713c152738698bf2e30fd3a11e362436a453785ad09040ea27b1389bdbada` and `9bd9b0611dc1a575cac507a1e8f185b59abe51b72310f16589d0f7014ef08858`.
- `counts-fence-manifest-addition.json` contains only the new entries for the parent to merge into the main manifest. The main manifest was not modified.
- `audit_counts_fence.py` validates exact source closure against the frozen parent, parses all Python source without importing CUDA, asserts fence placement/retained trailing fence, verifies project-local Git and HEAD, and runs `git diff --check`. Result: `counts-fence-source-audit.json`.

```bash
cd /Users/ziangli/playground/projects/hashinfer-w4a16-device-trace
python3 optimization/audit_counts_fence.py
```

CPU checks pass. Device compilation, correctness, timing and native fence lowering are pending. No ownership-port change is included before retention.
