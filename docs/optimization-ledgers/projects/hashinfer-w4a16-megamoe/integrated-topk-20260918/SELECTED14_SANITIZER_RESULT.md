# Selected14 main6 sanitizer result

**PASS:** all 6 tool/EP/O3 batches, 36 rank reports and strict clean tool summaries, 216 workload-rank cases, 864 tactic-workload-rank completions.

Tested source `14a9e720d02472ae602ca3ed3ba121f273de4573` / manifest `cd9f745a3b9778084fec68590239ebad03951df9331d0664ab341b00e0198ebd`; all 104 local frozen files rehashed. Source publication with only README changes is not a separate GPU run. Workloads are global tokens 1/128/1024 × random/skew, four default deterministic tactics, eager and graph execution, at EP4/8 and O3.

| Tool | EP | Rank reports | JUnit wall seconds | Exact rank summary |
|---|---:|---:|---:|---|
| memcheck | 4 | 4 | 466.188 | `ERROR SUMMARY: 0 errors` |
| memcheck | 8 | 8 | 495.481 | `ERROR SUMMARY: 0 errors` |
| synccheck | 4 | 4 | 82.280 | `ERROR SUMMARY: 0 errors` |
| synccheck | 8 | 8 | 113.042 | `ERROR SUMMARY: 0 errors` |
| racecheck | 4 | 4 | 2464.396 | `RACECHECK SUMMARY: 0 hazards displayed (0 errors, 0 warnings)` |
| racecheck | 8 | 8 | 1620.409 | `RACECHECK SUMMARY: 0 hazards displayed (0 errors, 0 warnings)` |

Total driver wall: **5244.035s** (87.401min). These durations include compiler/tool/setup overhead and are not kernel timings; parallel rank times are not summed. All 36 raw logs contain only the Compute Sanitizer banner and exact zero summary, with no additional diagnostics.

- Archive: 126 files / 136,841 raw bytes / 22,931 compressed bytes, SHA `cf4415c3401693c9abc9df4c2e570c0577f690094ff64da25d920290d5e8d555`. All extracted and tar-member hashes passed.
- Recorded closure: exact secondary host/boot/inventory, selected source and finished hash; owned launcher PGID 81918 has no members and GPU process list is empty. The separately hashed owner closure sidecar is outside the archive. No live query or node release was performed by this auditor.
- Earlier `collected-sanitizer/verification.json` remains failed and unchanged: the old checker expected 12 command arguments and rejected the reviewed traceback-only 13th argument `--tb=native`. The previously prepared selected14 checker explicitly binds that exact launch and passed without modification.

Scope is the owned MegaMoE core and BF16 input-stage families; external Torch/reference/NCCL kernels and opt-in IKR are excluded. Memcheck retains compiler TMEM guards with the tensor-ops checker disabled; synccheck uses fatal uninitialized barriers; racecheck retains INFO/all/unlimited reporting and 16 workers without launch dumping. This is not a proof of arbitrary global/NVSHMEM/TMEM ordering. Generated-entry/options checks are bound to successful frozen test hooks; full PTX/launch dumps are not retained. Numerical equality is established separately by the completed strict 60 audit.

Independent audit: `selected14-main6-audit.json` SHA `4538c8620149af88c2a455bc42d215ad068d3fa921b780b049778bc179a160dd`. Source/archive/closure review: `selected14-main6-terminal-review.json` SHA `a3c5e3598a9cc35ecbb8c10ccf13d44f2ba4bfe000c558b7c3f72c2012e9c026`. Initial failed receipt SHA `768db4c8305c39995d9e01b3710da6b33c8ca50364e04be3ae15e78ec61516c9`. Closure SHA `d167da59ca7696bc1f53d67301cd1615333fbfe4f8f146042925aee2c1690101`.
