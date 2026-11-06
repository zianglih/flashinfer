# Native count-fence and parallel-payload audit

The uninstrumented N64/G512 exports confirm the intended count-fence reduction and payload barrier ordering. Neither candidate adds local-memory spills or changes the repeated weight-decoder instruction counts. These are generated-code findings; retention depends on the separate serialized runtime and stateful numerical checks.

## Artifact and ABI binding

All artifacts were already produced by the parent's GPU queue. This audit ran only local CPU parsing. `analyze_native_codegen.py` verifies each export against the frozen worktree's complete Python source inventory, source manifest, selected ABI, configuration, PTX hash and cubin hash. The selected timed ABI is Int32 routing IDs with contiguous BF16 input, uniquely artifact00 in these manifests. It is the uniform256/rank EP4 H6144/I2048/E256/top8 fixture; it is not the native H7168 token sweep.

`audit_native_overlap_codegen.py` also checks all four exported fused-input ABIs for each arm: Int32/Int64 IDs and contiguous/strided BF16 input. All 16 exports pass source/hash/resource checks and the applicable native synchronization checks. No PMTRIG instructions are present. The manifests contain no prestaged-input artifact; prestaged correctness must rely on the separate source/runtime coverage, not these exports. Runtime live-token counts are arguments, so this export is not itself a zero-token execution test.

| Arm | Source SHA256 | Whole static instructions | MOV family | FC1 / FC2 body | Entry REG / STACK / LOCAL |
|---|---|---:|---:|---:|---|
| store16 | See `comparison.json` | 5112 | 426 | 225 / 231 | 96 / 0 / 0 |
| counts_overlap | 9bd9b0611dc1a575cac507a1e8f185b59abe51b72310f16589d0f7014ef08858 | 5200 | 433 | 225 / 231 | 96 / 0 / 0 |
| counts_fence | 771d8c303c79f299980ce97b9ffff53a24d86afea4ab1383bd2bfdd942d75951 | 5192 | 433 | 225 / 231 | 96 / 0 / 0 |
| parallel_payload | 94a939ede3ca316d23cd6aa640a1b0a17035c18aaa54d521b100fdb858d8a49c | 5128 | 426 | 225 / 231 | 96 / 0 / 0 |

All four ABIs of each arm have entry REG96, STACK0, LOCAL0 and no LDL/STL. Static shared memory is 1024 bytes; this field is not total dynamic shared-memory usage. The body counts and exact opcode histograms for the timed ABI are in `native-codegen-overlap-analysis/comparison.json`; all ABI resource and synchronization checks, source/PTX/cubin/SASS fingerprints are in `synchronization-audit.json` in that directory.

## Count fence: one prefix replaces two release bundles

In counts_overlap, each of the two unrolled count contributions has a four-instruction native release bundle immediately before its RED64:

```text
MEMBAR.ALL.CTA
MEMBAR.ALL.SYS
ERRBAR
CGAERRBAR
REDG.E.ADD.64.STRONG.SYS ...
```

In counts_fence, the existing local-grid completion ends in NB10 at `a590`. The CTA0 publisher branch is followed by one prefix at `a5b0–a5f0`:

```text
a590 BAR.SYNC.DEFER_BLOCKING 0xa, 0x80
a5a0 @P1 BRA 0xa940
a5b0 MEMBAR.ALL.CTA
a5c0 MEMBAR.ALL.SYS
a5d0 ERRBAR
a5e0 CGAERRBAR
a5f0 CCTL.IVALL
```

The two `REDG.E.ADD.64.STRONG.SYS` sites at `a740` and `a8c0` directly follow their per-source `STG.E.64`, with no intervening per-RED release bundle. PTX confirms `red.relaxed.sys.global.add.u64` twice and the prefix `fence.acq_rel.sys`; the existing trailing `fence.acq_rel.sys` remains at PTX line3679, native `a8f0–a930`. Publication still adds rank-completion value1 in the high32 word and the unchanged token count in the low32 word. There is no change to the later dispatch/scheduler NB9 arrival count.

The complete whole-kernel delta versus counts_overlap is:

```text
MEMBAR.ALL.CTA -1
MEMBAR.ALL.SYS -1
ERRBAR         -1
CGAERRBAR      -1
CCTL.IVALL     +1
NOP            -5
```

Thus the code removes **three ordering instructions plus five padding NOPs**, not eight useful instructions per K-step. The prefix is acq_rel and includes an invalidate; the former per-RED release bundles do not. The dynamic change applies only to count-publishing threads in CTA0, once per dispatch initialization, and does not save repeated decoder work. The decoder bodies, moves and spill resources remain unchanged.

The scope of the source proof remains important: the prefix publishes writes preceding the local grid synchronization through the count release pattern. Per-source `expert_recv_count` stores occur **after** the prefix and are not published by that prefix; their consumers still use the unchanged later global dispatch-publication gate. Early scheduling/weight preparation uses the atomic count sum and weights, not those per-source counts or token-payload reads. See `counts-fence.md` for the source dependency argument.

### Scheduler acquire lowering

Both counts candidates retain the same two `ld.acquire.sys.global.b64` PTX polls, one for each 32-expert group, and a100-cycle sleep only after an unsuccessful predicate. The native compiler eliminates the unused low word: timed SASS loads the high32 word at `10d0` and `1240`, then invalidates at `10e0` and `1250`:

```text
LDG.E.STRONG.SYS R2, desc[UR4][R6.64+0x4]   // next group uses +0x104
CCTL.IVALL
ISETP.NE.U32.AND.EX P0, PT, R2, 0x4, PT, !PT
```

These are native high-word loads, not native64-bit loads. The source/PTX operation remains system-acquire64 and the observed lowering is identical between counts_overlap and counts_fence. This audit records the compiler's output; it does not independently specify undocumented native ordering semantics. The acquire/PTX contract is the source-level basis for the readiness proof. The native load width is not a new difference introduced by the fence candidate.

## Parallel payload: handoff before register growth and grid publication

The timed vector-copy body moves from dispatch `93d0–9440` in store16 to epilogue `4c80–4cf0`. Both are the same eight-instruction copy loop, including one `LDG.E.128` and one `STG.E.128`; pointer-register assignments change but payload bytes and loop stride do not. In parallel_payload:

```text
4ca0 LDG.E.128 R4, desc[UR4][R4.64]
...
4ce0 STG.E.128 desc[UR4][R12.64], R4
4cf0 @P0 BRA 0x4c80
...
4d20 FENCE.VIEW.ASYNC.G
4d40 BSYNC.RECONVERGENT B1
4d50 BAR.ARV 0xb, 0x100
4d70 USETMAXREG.TRY_ALLOC.CTAPOOL UP0, 0x90
```

The bound branch for empty/no-assigned-chunk threads goes to `4d30`, then rejoins at `4d50`; it does not skip NB11 arrival. Actual writers execute the async-global proxy fence before arrival. All four exported ABIs preserve a single NB11 arrival, writer fence before it, and register increase after it; the strided cases use their scalar copy implementation.

Dispatch's register decrease to64 is at `94a0`, before routing staging/preparation. Its NB11 join is at `a130`, immediately before the original NB10 at `a140` and existing grid/publication sequence. Native code therefore matches the owned `dispatch_prep` override: inherited preparation finishes, dispatch joins the128 epilogue writers with128 dispatch threads, then publication begins. Count REDs remain relaxed as in store16, and the existing trailing fence/NVLink path is retained.

Control's register donation to80 appears at `f90`, before its original NB9 wait. Epilogue's NB11 arrival is nonblocking and precedes its possible wait for144-register allocation; dispatch donates to64 before its NB11 wait. This ordering matches the source deadlock argument: neither donation waits on successful epilogue allocation, and the epilogue arrival does not require its144-register grant. The original pool remains61440 registers: epilogue128×144, control128×80, dispatch128×64, transforms256×96.

Whole code grows by16 instructions versus store16, with MOV187→189 and IMAD.MOV239→237, so the total MOV family stays426. There is no native packing/spill penalty in the repeated decoder bodies. The added handoff and changed role/control-flow placement still have runtime cost; native resources alone do not establish a speedup.

## Reproduction

```bash
python3 optimization/analyze_native_codegen.py \
  --arms control store16 counts_overlap-uniform-n64-codegen \
    counts-fence-uniform-n64-codegen parallel_payload-uniform-n64-codegen \
  --output optimization/native-codegen-overlap-analysis
python3 optimization/audit_native_overlap_codegen.py
```

Synchronization excerpts are saved as `*-synchronization.sass.txt` beside the JSON. No GPU work or frozen/production source modifications were performed for this audit.
