# Current PR8 experiment state — 2026-09-19

Canonical checkout: `integrated-topk-20260918/hashinfer`, branch
`perf/megamoe-integrated-topk`, clean HEAD `d01f074947d2cc754d6062c2b2ffe674e1577a34`.
No candidate from this batch has been promoted or pushed. PR8/9 remain draft;
no merge authorization. Failed and unpromoted experiments remain preserved in
separate project-local worktrees and frozen source bundles.

## Current work

- Hu15 (`hashinfer-combine-0919`, c2/ziangli, boot
  `0a0846f7-1ce1-4dcc-9876-1ca81df8001f`) is idle. All S2/W1/R1 GPU/process
  groups are closed; complete member evidence and independent audits are local.
  No further candidate is queued there.
- Hu115 (`hashinfer-startup-0919`, c2/infra, boot
  `b474cb00-f717-4583-a4b5-978d501455c6`) finished D2 linear-address timing.
  Full13 rows completed at epoch1789833571.5956037. Independent terminal audit
  1b64cd87 verifies166 member files,104 exact output pairs,13 same tactics and
  process/GPU closure. Node is idle, no further job or transfer is queued.
  No extra qualification, repeat or sanitizer is warranted by its mixed result.
- This batch is complete. All evidence and ledgers are updated; no candidate
  earned promotion. No new candidate is queued. Retained source stays d01.

## Completed and rejected/unpromoted

Ratios are same-node d01 baseline/candidate. Never multiply across nodes.

| Candidate | Decode4–512 GM | Prefill4K / 8K / 16K | Evidence |
|---|---:|---|---|
| Metadata-first3cd | .949920× | .978707 / .983742 / .994360× |104 exact outputs |
| Cheaper payload44b5 | .974916× | .975216 / .980820 / .989371× |104 exact outputs |
| Whole-row readiness4cd | .941059× | .954419 / .942848 / .991321× |104 exact outputs |
| Striped readinessca05, hu15 S2 | .944671× | .970046 / .984111 / 1.008488× |audit645db008;169 members;104 exact |
| Early scheduler2bb, hu115 B1 | .987321× | .999837 / .959524 / .987197× |audit757f42aa;436 members for3arms;104 exact pairs |
| Preinit stagingec742, hu115 C1 | 1.000089× | 1.004228 / .963794 / .989230× |same three-arm audit |
| Fifth combine WG2739, hu15 W1 | inactive decode path | 1.010541 / .960070 / .979782× |audita63435e1;169 members;104 exact |
| Coordinate recurrence63f49, hu15 R1 | inactive continuation | 1.007633 / .990740 / 1.008518× |auditb0f93d19;169 members;104 exact |
| Linear addresses3b42, hu115 D2 |1.005822× |1.008967 / .962814 / .971607× |audit1b64cd87;166 members;104 exact |

Fifth-WG and recurrence decode timing changes are not causal evidence for those
inactive paths. All13 selected tactics match their controls. Quarter samples
show substantial large-prefill drift. No additional native/sanitizer suite ran.

Fine-grained return notifications782bbf and finite prefix203fc5 were also mixed;
no promotion. Instrumented prefix08e measured only about0.5% of all combine work
before drain at4K and2.5–2.7% at16K. Detailed results are in the sibling
`final-combine-prefix-20260919` effort. The interrupted hu59 striped run has no
full retention verdict and is excluded; its interruption record remains local.

## D2 source and runtime

- Initial ce0 D1 failed at0/13 because flattened Int64 address arithmetic lost
  the source pointer's divisibility proof. Exact source/process/GPU closure
  and all rank errors are preserved; no performance claim from that attempt.
- Successor `3b42f0d1f3d0682cef1bca2ae51c2883259f11b7`, frozen-v2 under
  `linear-combine-address`, restores only stride-derived divisibility using
  `cute.assume(..., divby=gcd(8*sH,sT) or1)`. Existing H%32 ensures the proof;
  no new caller alignment or runtime guard. Source reviewa068a23b passed.
- Source archivedbde5e75, manifestd7feacc2. Runtime directory
  `linear-combine-address/decode13-benchmark-hu115-v2`, prepared3b7aad40,
  runtimed4e2d60c, reviewedf02ebfcb. D2 launch1789832979.761842,
  supervisor/PGID26774,port30110. Direct samehu115 startup A1 control.
- Full logged prefill is474.677/817.063/1565.341us versus
  A1478.933/786.6795/1520.8965us. Final table, MAD and quarters are in
  `linear-combine-address/decode13-benchmark-hu115-v2/RETENTION.md`.

## Method and durable references

CUDA13.2/B300, explicit `nvcr.io/nvidia/pytorch:26.05-py3`, EP8,
H7168/I2048/E256/K8, O3/AUTO4,100 cold-L2 graph CUPTI rank-MAX samples.
Shapes1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Retain mainly4–512 decode;
inspect each prefill; display1/2 but exclude retention. Unchanged worker0ff
retains all4 compiled staging ABI variants. No benchmark fast-mode change.

See `ROUND_SUMMARY_20260919.md`, `EXPERIMENTS.md`, `HU15_STAGING_REDUCER_BATCH.md`,
and per-experiment `RETENTION.md`. Complete member bytes/hashes are locally
verified; original compressed archives remain remote, a separate evidence scope.
Benchmark iteration-only ABI pruning is documented but not implemented.
