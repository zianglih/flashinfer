# Single SF/payload interleave performance screen

The held preparation was released after the complete 22-call / 33-native-pair gate (`../qualification-summary-combined.json`, SHA `d5f5e0cf38e854096cb605ae99242a2d5134f25442461ea0e5e51318306d8092`). Original preparation files remain unchanged; `screen/launch.json` and `screen/launch-preflight.json` record the actual release.

- 23 jobs / 28 supported swap and per-token arms; all four models, EP/TP, tokens 32 and 16384. No W4 or unsupported arms.
- One C–A–A–C screen, 100 strict CUPTI samples per cell/phase, 10 warmups, cold-L2 graph replay; 56 cells / 22,400 samples. Same recorded choices, routes and unchanged timing helpers. Per-token includes input quantization.
- Immutable retained `2b8eb9d8` control versus the sole qualification-owned `a014d6aa` swap overlay. The later retained `c1ac8ce7` is W4-only and is not relabeled as the measured base.
- Runtime: recovery node, GPUs 0/1/4/5, existing release C++ cache. Launch checks unchanged native ELF/Ninja bytes, generated commands, no-op builds, source hashes and GPU idleness. Candidate occupancy and native resources match controls in qualification; performance resource guards remain active.
- Config SHA `14afee7c49e060c33e572a3dd4ac8c09d6f0fadbb1d15b68a74566e1be45e37d`; controller PID 81888. Remote `runs/sf-payload-interleave-screen`.

No repeat or source/tactic rescue is part of this screen. All negative values, repeat variation and clock observations will remain in the complete report. Finalization reuses `close.py`, the existing `experiments/w4-tail-cutoff/fetch_screen.py --node fi-gather-pipeline-recovery-1030 sf-payload-interleave-screen`, and `harness/report_evidence.py`.
