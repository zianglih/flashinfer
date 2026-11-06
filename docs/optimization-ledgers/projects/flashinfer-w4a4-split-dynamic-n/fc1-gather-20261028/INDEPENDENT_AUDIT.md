# Independent FC1 gather design audit

Scope: FC1 block-scaled swap-AB only. FC2 regular TMA and W4A16 are unchanged. Working source `flashinfer-fc1-gather-review`, base `d35fcfda03875077b3af8455575cc1d20e866a8c`. This audit owns no source edits. The later approved R3 qualification ran existing tests on GPUs4–7; all four GPUs have been released.

## Prior evidence and what it does not establish

`evidence/activation-loader-13ca1475/README.md` and its frozen `raw/scripts/loader_trial/cpasync128_core.py` preserve an exact direct-load comparison: 24 cases per loader, including six dtype/SF combinations, K/tokens tails and two-CTA physical layouts. Against Gather4, cp.async128 was about 5–6% slower in isolated NVFP4 FC1 at 8192/16384 tokens; LDG256 was considerably slower. Those are historical B200 results, not current B300 end-to-end retention evidence.

The former four-warp producer group also owned weight TMA in warp0; both MMA warps then waited on local SF/payload completion and relayed readiness to the leader (`cpasync128_core.py:870–918, 972–1192, 1326–1353`). A dedicated gather warpgroup separates that work and can keep relay overhead out of MMA. Thus the old result argues against replacing Gather4 with direct payload copies, not against the new Gather4 + SF-cp.async specialization.

## Minimal pipeline policy

1. Keep weight/SFA TMA on its existing warp, retain scheduler and MMA ownership, and add a dedicated gather warpgroup. The epilogue warpgroup remains separate. Gather4 payload and direct SF publication can share a stage index and the same operand-empty release because MMA consumes both before releasing it.
2. Cache source-token indices outside the K loop. Payload rows use `mapping[route_start + row] // top_k`, with invalid row coordinates mapped out of tensor bounds. Do not read invalid mapping entries. Split payload rows by the runtime rounded MMA N for two-CTA; do not shift the SFB logical row origin by CTA rank.
3. Every CTA needs its own complete local SFB row atom, even when payload rows are split between CTAs. Current S2T/group2 layout relies on this (`moe_swap_ab_kernel.py` base lines 1572–1575, 2950–2966). Invalid SF rows and final-K words must become zero rather than stale data. Preserve original row-major SF input indexing and four-scale-word packing.
4. Weight’s sole TMA announcement must continue counting all Gather4 payload bytes but omit SFB transaction bytes when SFB uses cp.async. Do not count only live rows: all issued physical copies, including zero-fill, complete transactions. New producer completion must represent both CTAs before group2 MMA can run.
5. SF completion should be owned by gather producers. A CTA-local cp.async completion followed by a producer relay to cluster readiness avoids putting a local wait/fence/relay into the MMA warp. Keep local completion and inter-CTA publication distinct. The consumer must not observe readiness before all four gather warps have completed their SF copies. A shared empty stage is sufficient for reuse after the existing MMA release; a second independent reuse counter is unnecessary.
6. Keep source-shared swizzle addressing tied to the real shared pointer. The old prototype failed when it assumed 1024-byte alignment; the actual base was only 128-byte aligned. Use existing CuTe pointer-swizzle machinery rather than reconstructing a relative-address XOR.
7. Update all thread-count contracts if FC1 becomes 384 threads: launch, TMEM retrieve, final block barrier and CLC metadata consumers. CLC metadata currently has 32 weight + 32 activation + 128 epilogue + leader32 MMA consumers; replacing activation32 with gather128 adds96 arrivals per CTA. Scheduler itself does not consume that queue.

## PDL boundary

Base prepare waits on routing ancestors and releases them before signalling dependent FC1 (`moe_swap_ab_prepare.py:99–107`). Removing prepare also removes that bridge. The launch change to disable FC1 weight-prefetch-before-wait is therefore appropriate for the first candidate: all source/metadata readers wait, while earlier initialization still runs ahead. FC2 retains its current completed-ancestor prefetch contract. Re-enabling FC1 metadata read-ahead requires a new explicit publication proof, not merely moe_sort’s early launch signal.

## Primary semantics checked

CUTLASS `cute/arch/mbar.py:466–484` lowers `cp_async_mbarrier_arrive_noinc` to CTA-local completion; `pipeline/sm90.py:394–465` configures thread-counted asynchronous producers. CUTLASS `pipeline/helpers.py` dispatches AsyncLoad arrivals through that helper. These are source references, not claims about a new implementation’s emitted machine code.

PTX states that cp.async mbarrier completion covers prior copies from the issuing thread; noinc arrivals must be included in initialization, and its address is local shared memory. A successful tracked wait makes the copies available to participants. This does not by itself publish the peer CTA’s scales. [PTX cp.async.mbarrier.arrive](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-cp-async-mbarrier-arrive), [completion mechanisms](https://docs.nvidia.com/cuda/parallel-thread-execution/#asynchronous-memory-operations).

## First runtime gate

`selection.json` is compatible with the root’s existing frozen-source runner: 32 existing cases, split by root into `nv` (8), `mx` (14), `tails` (6) and `wrapper` (4) for parallel execution. It covers six NVFP4/per-token exact cases, twelve fixed one/two-CTA MXFP8/MXFP4x8 public-API cases, six direct K/token tails, four eager/graph wrappers, two MXFP8 ReLU2 cases and two pinned per-token recipes. There are no W4A16, non-swap, sanitizer or reference-selftest cases.

The direct K-tail fixture already calls FC1 with original unpermuted rows, reversed mapping and poisoned extra SF storage, so it needs no adaptation. It is one-CTA and PDL-off by design. The fixed MX cases exercise route tails at 17 tokens and nontrivial top-k2. Default NV fixtures do not prove which tactic compiled.

After the first gate, `gather_test_modes.py` optionally forces public-call PDL on/off and a fixed N16/one-CTA or N128/two-CTA tactic for existing NV tests. `test-selection.json` separates groups. It leaves all assertions and the existing K96 reference-plan observer intact. Compilation output records actual CLC enablement; a requested CLC tactic folded to static by occupancy policy must not be counted as active CLC coverage. The plugin is intended only for the listed swap-AB public-call tests, not direct K-tail or pinned-recipe legacy-comparison nodes.

Example (environment/cache/source binding supplied by root):

```sh
PYTHONPATH="$PWD/../fc1-gather-20261028:$PYTHONPATH" python -m pytest -p gather_test_modes --gather-pdl off --gather-tactic n128-two-cta-static -s -q 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[True-w4a4-per-tensor]'
```

Static checks: plugin Ruff formatting and `python3 -m py_compile` pass. The subsequent source audit and source-bound runtime results are recorded below.

## CUTLASS dependency source hashes

- `references/cutlass/python/CuTeDSL/cutlass/cute/arch/mbar.py`: `ee85fc5a702e6225da0154506172e15c44c30ac7ba17006ad090693498beb46e`
- `references/cutlass/python/CuTeDSL/cutlass/pipeline/sm90.py`: `6e6f4c37958d818a2a17fe6f893c3c5271bf0087a3978211b6038e61a06ecfc0`
- `references/cutlass/python/CuTeDSL/cutlass/pipeline/sm100.py`: `4e7c4ce1f19f4d470adcbda7052740af36820a99fa74fcf9d01627fb52ff8def`
- `references/cutlass/python/CuTeDSL/cutlass/pipeline/helpers.py`: `da020a728733301cf679d118fca8092566c98fddcfcdc5b909f87b638ca6ac93`

## Frozen kernel R1 review

Reviewed `kernel-r1.json` / SHA `b0c061b797c15cf913c88eab9c1e9ab88a2c7e0442b1d2befcdad732cb80b9f2`. No source-level correctness blocker was identified. Subsequent constexpr-only compile fixes are being qualified separately; this receipt does not silently bind their source.

- Gather4 descriptor retains both dimensions as dynamic Int32, preserving rank2 when the original token count is one. Its single-row tile is 128 bytes: 256 FP4 values or 128 FP8 values. Its SW128 form matches the prior exact-qualified Gather4 descriptor. `source_rows` now uses original token count rather than routed capacity; invalid row coordinates equal that extent and therefore request zero fill.
- Physical B allocation remains at least N32, but issued rows use `route_tile / cta_group`. The raw offsets keep the actual allocation stride between K chunks and stages. Thus N16/2CTA issues eight rows per CTA while preserving the larger physical allocation stride. Issued bytes equal the existing `b_copy_rows * tile_k * element_bits / 8` expectation in every CTA.
- SF rows do not inherit the CTA payload offset. The four warp/lane mapping is a bijection over128 rows; each lane copies four contiguous SF bytes. Per-stage row blocks and 512-byte K-word blocks fully cover the SFB allocation. Source row offsets use Int64 multiplication. Predication excludes invalid row or K blocks.
- All128 gather threads wait for their own asynchronous SF group, fence to the shared async proxy, and release-arrive the leader’s SF-ready barrier. The installed SDK defaults even remote-address arrivals to CTA scope; the implementation correctly explicitly requests CLUSTER scope for two-CTA. Initial count is128 or256 and each participant arrives exactly once per stage. Only the leader MMA waits; the unused peer-local ready barrier need not complete.
- The ready barrier has no separate empty ring. Existing operand-empty release happens after SF S2T and all dependent MMAs, so it protects next-stage SF writes and ensures completed ready phases cannot be reused too early. The weight producer’s existing tail plus final full-block rendezvous protects shared storage at exit.
- CLC metadata arrivals are288/320 per CTA (peer/leader): weight32 + gather128 + epilogue128 + leader MMA32. The idle control warp1 remains the PDL publisher but is not a metadata consumer. Retrieve/exit barriers use the384-thread launch count; FC2 remains256 threads.

`check_gather_indices.py` / `gather-index-proof.json` pins R1 and checks12,024 row cases: all valid counts for N16/32/64/128/256, one/two CTA, FP4/FP8, Ksteps4/8, several stage indices, and SF16/SF32. It proves non-overlapping issued byte ranges, complete SF-word ownership, expected payload transaction counts and the rows actually consumed by runtime-N MMA. It does not emulate hardware swizzle, encode descriptors, prove CUDA memory ordering, or execute a numerical oracle.

Remaining runtime checks are predicated cp.async zero-fill in the current compiler, Gather4 rank/coordinates/swizzle lowering, K96 and short-K exactness, active CLC execution and graph replay with changing routing. Existing selected public fixtures cover the four benchmark arms; low-level E5M2/E5M2, MXFP4/MXFP4 and FP4/UE8M0-SF16 are not included in that first32-case gate.

## R2/R3 qualification update

Root's R2 gate passed all32 selected existing tests on B300. R3 `c259b6cb4b01037def6f1b8d4be09221f7abc36dd76e910660ced0179daebf75` changes payload issue ownership by flattening row-group/K-chunk tasks across four warps. The independent review verifies cached row coordinates indexed by `task_group % ceil(row_groups/4)` match the issued `task % row_groups` row in all40 allowed geometries, including the two-row-group N16/two-CTA case. SF completion, ready publication and stage advance remain outside the task loop. Producer `flatten-proof.json` is bound to that same hash and records5,952 live-row cases.

The approved broader12-case gate is artifact-only and runs existing tests with a public-call PDL/tactic plugin. Six cases demand actual compiled CLC (both FC1 and FC2) for NVFP4, per-token and large384-expert MXFP8 fixtures, with PDL both off and on. Four small MXFP4x8 SiTU cases cover static N16/one-CTA and N128/two-CTA with PDL both ways; two NVFP4/per-token cases add static N16/PDL-off. This does not claim active CLC coverage for MXFP4x8, whose existing small fixture is occupancy-folded to static.

Root authorized GPUs4–7 for this qualification. `broader-plan.json`, `run_broader_lane.py`, and `gather_test_modes.py` bind R3's513 source-file manifest and full unstaged patch before/after every job, assert actual compile roles/PDL/CLC/geometry, retain the nine persistent native-cache links, and impose600seconds per pytest process with whole-process-group termination on timeout. The gate completed **12/12 passed**, with no skipped cases, errors or timeouts. Ten cases use existing bit-exact assertions; the two large MXFP8 ReLU2 cases retain their existing tolerance/cosine assertions. All six CLC cases assert actual enabled CLC in both FC1 and FC2; every case verifies compiled PDL, CTA/N geometry, Gather4 FC1's384-thread role count and regular FC2's256-thread role count. No performance measurement or sanitizer was launched by this audit task. GPUs4–7 were released after completion.


## Collected R3 evidence

[`r3/BROADER_QUALIFICATION.md`](r3/BROADER_QUALIFICATION.md) lists all12 cases and their assertion/schedule boundaries. [`r3/broader-qualification.json`](r3/broader-qualification.json) binds their logs, JUnit XML and compile-mode receipts to the source manifest and archive.

- Source manifest SHA256: `cf70df603a7032c0d6f13b1e21bb92adc1fd5876db938ae93c921a7f3a8974d3`; all513 files verified before/after each case.
- Full unstaged patch SHA256: `1d430e76b0abf661c2b716b466ec439912776fa548daa39d941998205f952183`.
- Local50-file archive `r3/broader-evidence.tar.gz`: SHA256 `52b3815606a2f16401b049da7f74f6b5f19e434bdc6f0ff7a40a02ebac72ab0e`.
- Image `nvcr.io/nvidia/pytorch:26.05-py3`, B300/C3. Nine persistent native-cache links were retained and verified.

These results qualify selected existing public tests with the requested modes, not every low-level dtype combination or changing-route stress pattern. MXFP4x8 active CLC and direct E5M2/MXFP4-low-level variants remain outside this supplemental12-case matrix. Root owns the separate initial32-case R3 gate and performance runs.

## R4 relay qualification

R4 frozen kernel `6fae1558326e72aa8beab25520c9e7be1734e03b6ff39d190025f2445d09ed2a` moves scale completion to a CTA-local asynchronous barrier and one elected publication per CTA from warp1. [The relay audit](r4/RELAY_AUDIT.md) records the stage-reuse/lifetime chain and CLC consumer accounting.

The same supplemental12 cases passed again, with10 bit-exact cases,2 existing MXFP8 tolerance/cosine cases, and6 confirmed active-CLC cases. [R4 receipts](r4/BROADER_QUALIFICATION.md) bind all513 source files and full patch before/after each test. GPUs4–7 were released after a fresh idle check. No sanitizer or retention timing was run by this audit.

R3 [codegen evidence](r3/cache-codegen/CODEGEN_REPORT.md) remains separately pinned to its old kernel and frozen winner/route identities. It found no local-memory spill catastrophe; it does show the blocking per-thread SF wait/fence/publication sequence that R4 removes. Those instrumented public-call timings are excluded from retention.
