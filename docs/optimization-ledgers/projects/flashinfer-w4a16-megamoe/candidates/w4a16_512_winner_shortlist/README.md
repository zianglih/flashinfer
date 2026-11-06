# Same-source final512 fixed-tactic shortlist

Purpose: test exact fresh C1 auto choices against exact fresh512 auto choices on final512 source `e2d88e6a564638efe464d5a586a2b0284e66cb0b14bb4b77c7743593a09a29e3`. This isolates tactic choice on the current implementation. It is not a 640-versus512 implementation A/B.

Three serial original benchmark processes, at global tokens32,128,4096. Each receives `--num-tokens=T,T,T`, so the original row loop runs split/Mega three times: A1=old C1 choice, B=new512 choice, A2=old C1 choice. Dictionaries are in `plan.json`, derived from the two complete independently audited sweeps whose hashes are retained there. Per-visit markers and actual compiled configs must agree with the exact dictionary; explicit dictionaries bypass automatic Mega cache selection. T64 evidence is a separate optional artifact, excluded from this run.

Original benchmark, shell wrapper, row methods, input/weight factory calls, tuner,100CUPTI iteration loop,3warmups,CUDA graph,coldL2,rank reduction and finalization remain unchanged. The setup adapter selects fixed knobs and resets only the diagnostic recorder's per-visit output dictionary/namespace. The split tuner cache persists across repeated same-shape rows; actual returned split tactics and selection-call counts are preserved. This can reduce repeated tuning cost and is disclosed rather than called three independent split retunes.

The existing actual-resource gate runs on each newly compiled Mega object before any Mega launch; actual REG128/512threads/two decode groups/65536 launch registers are required with all-rank consensus. Existing cached checks preserve normal object lifetimes. The compiled observer after untimed warmup adds only visit/arm identity. No CUDA work or timer hook is added.

The runner requires the completed fresh512 full13 manifest/results plus its exact completed C1 native-cache owner. Source1573/required338 and every original helper must match. Only the owner's native Torch/FlashInfer build caches are reused; DSL/driver/knob/tactic paths are fresh. It records all helper hashes, source before/after each process, owner identities and native inventory. The post-run validator requires18 ordered raw values,72 actual split selections,72 actual compiled rank/visit records,24 begin/end records per process and eight complete worker files per process. Repeated rows cannot be silently collapsed; failed processes cannot contribute substitutes.

Run from `/workspace/flashinfer-w4a16-megamoe` with the verified132 interpreter and no competing GPU/cache writers:

```bash
/usr/bin/python3 -B candidates/w4a16_512_winner_shortlist/run_aba.py \
  zero-dest512-winner-shortlist-aba-001 \
  --stack-id cuda132-recovery0908b-zero-dest512-shortlist \
  --completed-manifest logs/cu132-recovery0908b-zero-dest512-full13-001/catalog16-manifest.json
# After reviewing the dry plan, add --execute to the identical command.
```

The four new runtime files are capture_aba.py,validate_aba.py,run_aba.py,plan.json. `upload-manifest.json` records their full dependency closure and CPU evidence. Existing remote files must match exactly and are skipped; new files are created exclusively. Tests use the unchanged recorder with fake CPU-only frontend/tuner modules and verify original callback ordering; the actual remote Python3.12 dry plan is still required before GPU execution.

Results are kept separately from full13 tables. B versus both A controls, A2/A1 movement and paired split changes are reported; no per-row minima or automatic promotion.
