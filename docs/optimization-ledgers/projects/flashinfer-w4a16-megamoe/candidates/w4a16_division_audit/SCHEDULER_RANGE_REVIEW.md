# Scheduler fast-divmod range review

Source review PASS for the reachable valid-work domain. This is a source proof and candidate-diff review; it is not a new kernel execution or performance result.

Reviewed base: `083a9fd39e7ddda43a8b912ef50f7a13390287f9`; base scheduler SHA256 `30c35c2b3d3c0d1dc7050d8c19411702b8ad9dcace5388b5043df6e4127e68b8`. Final candidate scheduler SHA256 `9d26c662949e7d41f4fb1190e8ebbaebcdf98baef7df03fc97ce5a4396234d19`. The intermediate int-only candidate `aa6e8185` is superseded: the final candidate retains the positive-divisor guard.

Paths below are relative to the project `flashinfer/` checkout. Scheduler references mean `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/fc1_fc2_fuse_sched.py`; line numbers describe the final candidate unless stated otherwise.

## Reachable numerator range

Let `x` be the cluster-linear claim, `[a,b)` the current expert's interval within its current FC phase, `R=ceil(expert_tokens / routed_token_tile)`, and `d` the phase's feature-block count. The required invariant at `_decode_inside_expert` is:

```
0 <= a <= x < b = a + R*d
0 <= local_id = x-a < R*d
```

This follows from the actual state machine, not from a local lower-bound check:

1. **Claims are nonnegative and locally increasing.** Static initialization uses nonnegative `blockIdx.z` (361–378); `_advance_work_linear_tile_idx_static` returns that value and increments by the positive persistent-cluster count (550–563). Atomic initialization claims with `atomic_add(counter,1)` (495–525), consumes that cached first claim exactly once, then issues later `+1` claims (608–627). Other clusters may interleave claims but cannot make one cluster's sequence decrease. DSMEM publication and consumer wait distribute the same claim to the cluster's CTAs (629–658).
2. **Initialization and group changes preserve the lower bound.** Initial group/expert ends are zero. `_gen_work_from_cluster_idx` advances a group only while `x >= old_group_end` (938–954). `_advance_group` makes the old group end the new group's start and primes its first expert at that start (800–821). Thus even a claim that skips multiple groups enters each new group with `x >= its_start`.
3. **Phase changes preserve it.** FC1→FC2 occurs only when `x >= group_fc1_subphase_end` (956–967). `_switch_to_fc2` starts the FC2 expert scan exactly at that boundary, resets the per-expert caches and rewinds the data prefixes (713–730). It does not rewind `x`.
4. **Expert changes preserve it.** The inner scan advances only while `x >= old_expert_end` (969–976). `_advance_expert_within_phase` assigns `new_start = old_end`, then `new_end = new_start + R*d` (662–707). Once the scan stops, `x < new_end` and the lower bound still holds. If no transition is needed, the next locally increasing claim preserves the previous lower bound.
5. **Empty experts do not divide.** A zero token count gives `R=0` and a zero-width interval. The expert scan cannot stop there. All-empty groups have no work and are skipped by the outer group scan; exhaustion leaves the default DONE record. Zero-length FC phases likewise contain no valid decode.
6. **DONE is not a negative work ID.** The sentinel is `expert_idx=-1` in the default output record (927–936), not a negative `x`. The sole decoder call is inside `x < current_group_end` after the scans (956–980). Claims at or beyond the final end leave DONE and bypass division.

The proof applies to both static and atomic modes, all admitted C1/C2 geometries, partial feature dimensions, group skips and empty experts. It does not depend on token readiness or completion order: those affect execution waits, not the monotone work-ID mapper. The held ready-window experiment is absent from this retained scheduler.

## Exact arithmetic contract and limitations

The two divisors are computed from the static gate+up and hidden dimensions at scheduler creation (396–403). At every valid decode, `R*d > 0`, so `R>0` and the selected `d>0`. Therefore signed floor division, signed truncation and unsigned division agree for the required numerator domain. The original remainder is retained:

```
q = local_id // d     # 0 <= q < R
r = local_id - q*d    # 0 <= r < d
```

Since `q*d <= local_id`, the remainder multiplication itself does not overflow within the established representable range. A negative dividend is not a supported decoder input. The old signed shift/floor expression happened to define negative arithmetic, but no reachable valid scheduler call requires it.

The proof retains the scheduler's existing finite-Int32 assumptions. Token sizes must be stable nonnegative counts; claims, ceil numerators, `R*d`, group/phase/expert endpoints, cumulative counts and the `base_fc1 + group_hint` comparison must remain representable. There is no new range validation here and no existing complete overflow check in the owned frontend/scheduler. A wrapped counter, overflowing interval, negative count or arbitrary backward call to `_gen_work_from_cluster_idx` defeats the invariant; the method's upper-bound predicate alone would not reject all such inputs. Terminal claim increments also consume Int32 headroom beyond the last valid work ID. This audit does not extend the supported size domain.

The atomic counter is initially zero because the frontend allocates the local workspace with `torch.zeros` (`frontend.py:223`). The counter region precedes `l1_token_buffer` (`megamoe_kernel.py:1449–1460`), so it is covered by the existing local zero prefix (`megamoe_kernel.py:293–297,564–605`). Shared `src/src/token_comm.py:1783–1799,1862–1871` joins kernel roles and resets that prefix after the final transport barriers. Normal serialized launches therefore do not reuse the previous launch's terminal counter.

Static zero H/I are not explicitly rejected by the divisibility checks (`frontend.py:71–74`, `megamoe_kernel.py:174–178`), although successful zero-shape kernels are not established. The final **positive Python-int** guard avoids newly creating FastDivmod for zero/nonpositive extents during tracing: those and runtime-Int32 extents keep the original ordinary `//` fallback. This preserves the prior construction boundary without claiming zero-shape support or adding validation.

## Candidate and dependency review

The exact final diff changes only the two existing phase-arm division specializations and adds the two-line range comment. It removes the manual power-of-two test/shift, constructs `cute.fast_divmod_create_divisor` only for positive Python-int feature counts, and keeps the phase branch, scalar remainder, dynamic fallback, fields, serialization, claim/broadcast protocol and publication order unchanged. Net source change is −2 lines.

Installed CuTe 4.7.1 `cute/core.py` is preserved under `installed-4.7.1/`, SHA256 `035c764686c4e5a94c1f2432b55ba2e6cc572a27db4d857278ccd785a6f7f6f3`. `FastDivmodDivisor.__rfloordiv__` delegates to the fast-divmod compute operation (6383–6421); `fast_divmod_create_divisor` constructs that existing object (6538–6565). Python syntax alone does not establish signed-floor behavior. The executor's saved `probe001/result.json` reports all 42 required nonnegative cases passing for divisors 1/2/16/17/28/29/32, including `INT32_MAX`; only 5/35 negative diagnostics match signed floor. The range proof is therefore necessary. That finite probe is dependency evidence, not a substitute for the interval proof or full scheduler lowering.

Existing repository practice is compatible: split MoE `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:271–283,295–316` creates FastDivmod objects and uses them to decompose linear work IDs. Attention `flashinfer/attention/prims_ts/kernels/mla_decode/helpers/tile_scheduler.py:40–53,250–264` uses power-of-two specialization or FastDivmod on grid-derived linear indices. Neither example establishes correctness for arbitrary negative dividends, and neither requires copying extra state into this owned scheduler.

## Remaining validation boundary

Source admission is PASS for final `9d26c662`. The next native captures should establish that both mapper trace sites retain exact quotient/remainder semantics, static divisor setup folds away, partial `/17` and `/29` no longer merge into general signed division, and no register/spill/stage regression appears. Existing focused numerical coverage should still exercise static C1, atomic C2, partial H/I, empty/refill launches and group transitions. No new execution, validator, production edit or publication was performed by this review.
