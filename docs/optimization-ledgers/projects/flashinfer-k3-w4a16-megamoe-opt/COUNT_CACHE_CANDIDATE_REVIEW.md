# Next scheduler candidate: cache immutable expert counts

Source-only audit on retained native-tanh commit `03e1840c`. No kernel edit,
GPU run, profile, or benchmark bundle was made. This follows the SiTU transpose
candidate; it is an implementable hypothesis, not a diagnosed bottleneck.

## What changes, and why this differs from the rejected scan

The current W4A16 scheduler reloads `expert_token_sizes[expert_idx]` during both
greedy group construction and every expert-cursor advance. FC2 rewinds the
cursor to the group start; residual group traversal uses the same accessor.
K3 EP8 has 112 local experts. Cache these 112 immutable Int32 counts once across
the scheduler warp: four values per lane, with the last 16 lanes' fourth value
zero. Replace each later count load with a chunk selection and one full-warp
shuffle. Keep every existing loop, count-to-block calculation, greedy boundary,
claim, work ID, readiness peek, and publication unchanged.

This does not repeat the rejected cooperative **group-boundary** prefix scan.
That trial changed only group construction and added five prefix shuffles per
chunk. This proposal retains scalar traversal and amortizes the metadata reads
over group construction, per-claim seek, FC2 rewind, and residual traversal. It
also does not repeat dispatch idle-pull skipping: dispatch and transport are
untouched. The inherited dispatch already uses a comparable warp-distributed
count cache, providing a local implementation precedent.

Exact source points:

- `flashinfer/.../bf16_nvfp4/fc1_fc2_fuse_sched.py:680`: expert-cursor count load.
- Same file `:781`: group-boundary count load.
- Same file `:1015`: first `gen_next_work` trace site; suitable cache-init site.
- Same file `:1045`: `_mlir_fields` must carry the four cached values through
  DSL reconstruction and loop-carried scheduler state.
- `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:853–918`:
  existing count-cache load, chunk selection, and shuffle pattern.

## Exact proposed scope and guards

Keep the experiment in the owned scheduler file. Use a compile-time guard:

```
load_balance_mode == "atomic_counter"
and isinstance(params.expert_cnt, int)
and 32 < params.expert_cnt <= 128
```

The upper bound limits additional persistent state to four Int32 values per
lane. It covers K3 EP8 without changing the existing GLM/DeepSeek EP8 path
(32 local experts), dynamic expert-count configurations, larger expert shards,
or static scheduling. Retain their existing direct-load accessor. No public
knob or tactic catalog entry is required for the first measurement.

Initialize the fixed-length cache to zeros when creating scheduler state; load
its real values only in `gen_next_work` when the existing compile-time
`_first_advance_pending` flag is true. Under the atomic-only guard, early
`internal_init` merely preclaims an atomic tile ID and does not decode experts.
The first `gen_next_work` call occurs after the metadata wait, so this placement
avoids a second call-site edit or loading unpublished counts. Preserve the
existing timing of `_first_advance_pending = False` at the method tail.

The reader selects cached chunk `expert_idx // 32` and then broadcasts lane
`expert_idx % 32`; use the same full-mask `shuffle_sync` idiom as dispatch.
Register-slot initialization must use static/unrolled indexing, with the list
length established before any DSL control-flow merge. Include the cache in
`_mlir_fields`; otherwise reconstructed schedulers can use stale SSA values.
No value needs to persist across kernel launches.

## Publication, lifetime, and collective proof

1. **Read the bank-adjusted view.** `megamoe_kernel.py:567–576` exposes the low
   Int32 word of each Int64 received-count sum with stride two. The kernel binds
   the active bank to `sched_params.expert_token_sizes` at `:1099–1122` before
   scheduler creation. Reuse this exact tensor; do not reconstruct contiguous
   addresses or read the high word.
2. **Wait for publication.** Shared dispatch finishes peer count writes,
   system-scope fencing, and its NVLink/grid barrier at `token_comm.py:735–798`,
   then arrives at the dispatch-to-scheduler named barrier. Scheduler warp 7
   completes `sched_warp_pre_init_wait` before the first `gen_next_work`
   (`megamoe_kernel.py:1244–1252`). Cache loads belong after that wait, never in
   early atomic `internal_init` or generic scheduler `create`.
3. **Counts remain immutable for all scheduler reads.** Normal cleanup clears
   the previous bank (`megamoe_kernel.py:1111–1118,1501–1510`); the active bank
   selector changes only after producers retire (`:1705–1709`). Kernel-replay
   cleanup resets the active bank after the existing drain, after scheduler
   retirement. Caching does not require a new fence or alter bank lifetime.
4. **All 32 lanes participate.** The caller is the full `warp == 7` path. Work
   IDs are already shuffled/cluster-broadcast and scheduler branch conditions
   are warp-uniform. Only cache *loads* may predicate off the final 16 padding
   lanes. Reconverge before any shuffle; do not place a full-mask collective
   inside the per-lane valid-expert predicate. No cross-CTA or cross-warp cache
   sharing is proposed; each scheduler warp owns its copy.
5. **Zeros, tails, and replay are preserved.** Zero-token experts cache zero;
   legal lookups remain below `expert_cnt` by the unchanged cursor/group
   invariants. Dummy padded lanes remain zero. A fresh kernel invocation loads
   its current generation's counts again, so changed routing and graph replay
   cannot reuse prior counts. Arithmetic, sentinel handling and work order are
   unchanged; the source of a count value is the only semantic substitution.

## Costs and performance-first decision

The startup cost is four coalesced loads per lane (three full chunks plus one
partial chunk), replacing later repeated global loads with selection/shuffle
instructions. Four extra persistent registers can increase pressure in the
80-register scheduler/control role. The scheduler could already hide metadata
latency behind queued compute, and direct loads may hit cache; the rejected
group-scan result makes a large gain uncertain. Do not stack cooperative seek,
residual-scan elimination, or a second metadata representation into this probe.

If selected, measure the candidate once with native AUTO and the existing
baseline/intermediate results, on all **1,2,4,8,16,32,64,128,256,512,4096,8192,16384**
points. Only T1/T2 are reporting-only. Keep PDL, disabled fused TMA/FC2 reduction,
and fused deterministic combine. No repetitive control run and no IKET. Only a
useful measured gain justifies subsequent exact existing-test qualification and
checking generated register/local-memory effects.

## Geometry conclusion

The saved K3 and GLM W4A4 decode winners both use N128/G512 with F4/F8; the
tested W4A16 flag/group/depth/M128 axes provide no missing decode winner.
N32 does not reduce BF16 MMA work because dynamic N already uses
`align16(valid_tokens)`, and it requires a real epilogue/layout implementation.
N256/one-accumulator plus half-width activation TMA was fully tried and reverted
in the earlier ledger (`w4a16_optimization_experiments.md:8169–8362`), so it is
not proposed as a new low-scope tactic. A smaller persistent grid is mechanically
possible through the existing `max_active_clusters` argument, but needs a
separate experiment and would reduce compute/weight-load parallelism; it is
deferred rather than bundled with this metadata-cache change.
