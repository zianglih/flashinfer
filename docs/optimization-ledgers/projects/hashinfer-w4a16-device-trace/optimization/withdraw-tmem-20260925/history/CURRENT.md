# Current optimization checkpoint

Completed 2026-09-25. Draft PR13 is updated, all selected validation has passed,
and no additional optimization or GPU process is active.

## Published source

- Draft PR: [private repository link omitted]
- Published head: `a1486e2fc63d5a54fe727b3123ee04b1e611c035`.
- Tested kernel/test/benchmark commit: `55cd345d57ccc56327966201bd0725767a11593a`.
  The later commits only correct one README ownership-table description.
- Current retained parent: `retained_owned_r2`, package SHA256
  `a7001bd59e04b03b372ba4315b3cad8cdcfd7e2db40a96006a5a987c08939e29`.
- Source checkout is clean and pushed. Final GitHub pre-commit check passed:
  [private repository link omitted]
- Published body exactly matches `FINAL-PR-BODY-DRAFT.md` and project `PR-body.md`.
  Receipt: `recovery-20260925/pr13-final-published.json`.

No upstream FlashInfer sync or merge was performed. No trace, disassembly,
local benchmark wrapper or experiment artifact was added to the repository.
The private GitHub operation used ziang-and; active account restored to zianglih.

## Retained stack and ownership

R1 widens decoded-weight TMEM stores from x8 to x16. R2 removes only raw-TMA
lookahead probes. Blocking raw waits, both TMEM readiness probes,
acquire-before-decode, raw release, store fence, decoded commit and pipeline
sizes remain. R2 was measured against retained R1, not the original baseline.

The transform and five modified transport methods are owned by W4A16. All
three protected shared/vendor files match base 406bc0d byte for byte. Six method
copies total 958 lines; source-origin comments and AST/codegen audits document
the maintenance boundary. Unchanged helpers remain inherited.

- R1 vs original 002: uniform fixed ABBA 1.0162x; native decode EP4 .9820x /
  EP8 1.0297x; fixed EP4T4 ABBA1.0857x. Per K, saves4STTM+4R2UR in each phase.
- R2 vs R1: uniform1.00557075x; native EP4decode1.01044581x /
  EP8 .99066792x. Further per-K savings5FC1/8FC2; whole5112→5096.
- Actual owned final vs original: FC1perK233→220, FC2perK239→223;
  REG96/STACK0/LOCAL0 and no spills. All four input-ABI cubins/native SASS
  are byte-identical to R2 at uniformN64/cap256 and nativeT1/cap1.

Counts-on-R2 is rejected (uniform.981613x, EP4decode.980290x). Its EP8 run is
incomplete and excluded; the separate post-export hostSIGSEGV is compilation
only, not execution success. Payload-on-R2 is also rejected (native EP4decode
1.001494x / EP8.979254x; fresh fixed uniform ABBA.996529x; whole+8instructions).
Both directions are closed for this iteration. Other rejected trials and
all negative rows remain in `EXPERIMENTS.md`; decisions are in `retention.json`.

## Final performance

All 27 final native/uniform rows have source, fixture, sample and paired-output
closure. The authorized original002 baseline is reused on the same node.

| Workload | Before / final owned |
| --- | ---: |
| Uniform EP4 H6144,256tokens/rank | 335.8745→324.915us =1.033730x |
| Native H7168 EP4 decode GM,globalT4–512 | .985787x |
| Native H7168 EP8 decode GM,globalT4–512 | 1.018346x |

Uniform pools both historical AUTO controls (200samples) against100 final
samples. Controls differ6.816us; this is not ABBA or drift-adjusted. Native
results retain all small-token regressions and tactic changes. Method:
3warmups,100untrimmed cold-L2 graphCUPTI samples, rankMAX each iteration then
median, full public-forward GPU span. Trace tuning is a separate hot metric.

The additional full fresh EP4 control was interrupted by old-pod loss and is
excluded. Bounded nativeT1 fixed ABBA completed on the replacement:
69.3765→69.729us=.994945x,200samples/arm. A1/B1/B2/A2 medians
64.5125/68.016/73.953/72.496us show substantial drift. This neither resolves
the older negative AUTO row nor establishes a precise causal penalty. T1
wrappers verify finite/repeated/paired bits, without an independentT1oracle.

Reports: `owned-r2-final-native-pr-evidence.md`,
`owned-r2-final-native-evidence-audit.json`, and
`native-t1-confirmation-analysis/audit.md`.

## Final correctness

All five suites passed and were collected into immutable
`results/owned-r2-correctness-snapshot-1` (191 files). Audit:
`results/owned-r2-final-correctness-1.{md,json}`.

- 26 outer cases / 58 rank pytest passes; zero failures, errors or skips.
- Four strict cases: 128 compiler/tactic/execution combinations,
  384 collective independent-reference comparisons and 1,984 collective pairs.
  Finite BF16 bits agree, including signed-zero handling.
- Three EP4 strict nodes cover randomGLM5T1024 with both routing placements
  and skewedT1FC2; one EP8 strict node covers randomT128FC1.
- Other suites: 10 tails, 6 lifecycle, 6 prestaged. Their own assertions remain
  distinct from the strict all-tactics matrix.
- Source/test/helper identity, rawlogs/JSONL, every rankJUnit/exit,
  unique strict combinations/phases/pairs and final source closure pass.
- No ComputeSanitizer, NCU, full test matrix or model-serving claim.

## Final winner trace

`results/owned-r2-final-winner-1/final`: fresh50sample native hot tuning chose
N64/G512/epilogue at322.272003us. Normal148CTA launch; native recording selects
one2CTA cluster. All4 independent baseline references and capture bitmatches
pass. Source/cubin/tracker/config binding,115native points/rank,maxspan128B,
full ranges/nesting/publication and nanosecond timestamps pass on all4ranks.

Rank2 is visibly open in Codex in-app Perfetto tab4 and marked deliverable;
old rank0 tab3 remains. The final rank2 pipeline/interpretation reports are
beside the final folder. The large explicit free-slot wait is at startup
(tile0/K3,22.146us mean over16transform warps); later marked free-slot waits
average~43ns. TMEM probes are outside these markers.470/472matched MMA weight
waits finish0–64ns after the latest corresponding producer-store marker.
This supports a same-GPU pipeline interpretation, not full-grid occupancy,
hardware utilization, cross-rank clock alignment or isolated issue throughput.

## Devbox kept available

Keep `hashinfer-trace-final-0925`, C2/ziangli, node hu-pdx-38, 8xB300.
Pod: `devbox-hashinfer-trace-final-0925-0`. Final outer PID4578 completed;
latest check shows Running/Ready, zero restarts and no GPU compute processes.
Receipt: `recovery-20260925/final-idle-devbox.json`.

Image: `nvcr.io/nvidia/pytorch:26.05-py3`, digest
`sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`.
Remote frozen source/helpers: `/workspace/hashinfer-trace/optimization`.
Results/codegen persist under
`/data/ziangli/hashinfer-w4a16-device-trace/recovery-20260925`.
Use real persistent roots and explicit pod with selective collectors.

The old `hashinfer-trace-labels-0924` disappeared unexpectedly; cause unknown.
This task did not delete it. Old PIDs152026/153509/164320 are obsolete and
must never be signaled on the replacement. Completed old-pod evidence was
already preserved; the interrupted extra control remains excluded.
