# Public W4A16 source-correlated codegen review

`compare_public_codegen.py` reads retained PTX/SASS and existing `summary.json` or `resources.txt`. It never invokes CUDA, a compiler, a disassembler, or GPU queries. Source snapshots are explicitly mapped and SHA256 checked; capture provenance must establish that those snapshots were compiled. Unknown helper locations remain unresolved.

```bash
python3 compare_public_codegen.py profiles/codegen-comparison/raw3.config.json \
  --output profiles/codegen-comparison/raw3.json
```

The generated JSON and Markdown preserve each rank separately, including every SASS LDL/STL, PTX local operation and declaration, PTX/SASS register-control instruction, nearest label, preceding instructions, source path/line/text/function, lexical warp guard, and source ownership. Source attribution is not a reconstructed machine control-flow proof. Generic helpers may execute in several roles, and optimized instructions can retain adjacent source annotations.

## Matched raw2 control: primary comparison

The adjacent control `profiles/tmem-raw2-control-codegen-001` uses the same public dynamic-N kernel, flag4-epi settings and compiler as raw3. Both have eight completed rank artifacts. The recorded source hashes differ only for the raw-stage-depth kernel override; raw2 source snapshots were extracted from `git show c7713ba1` because the active working file subsequently changed to raw5.

Use `profiles/codegen-comparison/raw2-vs-raw3.config.json` with the helper. Complete output is in `raw2-vs-raw3.json` and `.md`; timing and provenance are summarized in `RAW_DEPTH_COMPARISON_001.md`.

- Both report REG128/STACK112/LOCAL0, 512 threads, 96-byte PTX depot, 40 PTX local operations and 21 SASS local operations. Role register targets and transform opcode counts are unchanged.
- Current raw2 contains 6000 static SASS instructions; raw3 contains 6016. This is the matched codegen comparison; the older 5808-instruction fixed-N artifact is historical context only.
- The raw2 F2FP at `0x68a0` reads R20 from `LDS.128 @0x6350`. Its raw3 counterpart is at `0x6960`, with `LDS.128 @0x6410`. In both, producer-to-consumer distance is 85 instruction slots, with no intervening textual branch and the same preceding STTM.x8 stores using R4.
- The helper retains each F2FP's nearest preceding textual producer, including wide LDS destinations, branches and TMEM-store context. This is a conservative audit aid, not a full control-flow/reaching-definition analysis or proof of a stall's cause. The PC samples remain evidence from their exact captured binary; shifted candidate PCs do not inherit earlier sample counts.

## Raw3 capture

- Input: `profiles/tmem-raw3-codegen-001`, all eight ranks. Global T4096, M256/N128/K256 dynamic N, `group_hint=512`, `epi_flag_batch=(2,4)`, atomic scheduling, `flag_batch=4`, `token_back_mode=epi_warps`.
- Declared source: `c7713ba1+raw3`; actual kernel SHA256 `95f2cc38823c9c7e09a9659f84a294ffa80a31f87f4d934450fd7913b7ec8be9`. Recorded kernel/epilogue/decoder/frontend hashes were checked before source snapshots were copied into `profiles/codegen-comparison/raw3-sources/`. Other vendor source snapshots are locally hash checked and marked separately in the config.
- All ranks: `REG128 STACK112 SHARED1024 LOCAL0`; `.reqntid 512,1,1`. SHARED here is the reported static allocation; dynamic shared memory is not included in that field.
- All ranks: 21 static SASS local instructions (`STL.64`×8, `STL`×8, `LDL.128`×1, `LDL.64`×4), 40 PTX `ld.local`/`st.local` instructions, and one 96-byte `.local` depot.
- Nineteen SASS local instructions map directly to the vendor `Fc2OutputRouter.prefetch/get_data_dst`; two are emitted inside the same address-array sequence but carry nearby helper/source-anchor annotations. The exact addresses and surrounding instructions remain in the report rather than being relabeled as transform spills. There are no source-attributed transform local instructions and no additional local opcode/footprint relative to the historical capture.
- Generated SASS explicitly decreases scheduler, weight TMA, activation TMA and MMA to 80 registers, increases epilogue to 176, and decreases dispatch to 64. Transform has no setmax change and retains the 128-register launch allocation. The compiler-reported launch allocation and generated per-role targets are distinct fields.
- The instrumented one-iteration CUDA-event result is excluded from performance evidence.

## Comparison boundary

The predecessor is `profiles/swap-tmem-codegen-t4096-001`: a historical fixed-N candidate using the earlier default scheduling settings. Its kernel snapshot is `candidates/w4a16_swap/controls/fixed_n_timed_002/kernel.py`, whose SHA256 matches that capture's provenance. It also reports REG128/STACK112/LOCAL0, 96-byte PTX local storage, the same six register-control operations/targets, 40 PTX local operations, and the same 21 SASS local operations on every rank.

Total static SASS instructions are 6016 for current raw3 versus 5808 for that predecessor. This 208-instruction difference includes dynamic-N, scheduling and promotion changes; it is not an isolated measurement of adding a third raw stage. Static instruction counts are not executed work or latency.

The two generic helper annotations make the precise defensible statement “unchanged explicit FC2-router local footprint; no additional transform local instructions observed.” Stack bytes alone do not prove register pressure spills, and source annotations alone do not prove whole-program liveness.

## Two-transform-group capture procedure

Add its capture to a new JSON config using the same schema as `raw3.config.json` and source snapshots that match its capture provenance. Expected source-level settings are 640 threads, launch cap96, epilogue176, control80, dispatch64, and two transform groups retaining96 each. These are expectations until the actual cubin and register-control instructions are read.

Compare all ranks and inspect:

1. `.reqntid`, cubin REG/STACK/LOCAL, PTX local-depot declarations, and generated PTX/SASS setmax targets.
2. Any new local instruction in transform, MMA/control, dispatch or return code; preserve PC, operand, source and neighboring instructions for every new site.
3. PTX local operations at the same source versus SASS-only local operations. A SASS-only site is a compiler-spill review candidate, not automatic proof, because optimization can change line attribution.
4. Register-control order and source warp guards. Named physical register maxima in attributed instructions are only a static audit hint; they do not measure register liveness, allocation or occupancy.
5. Existing explicit FC2 router arrays separately from any new local storage. Do not treat LOCAL0 or unchanged stack size alone as proof that no local traffic exists.

The ordinary matched CUPTI runs remain the performance evidence. Codegen captures provide implementation and resource evidence only.
