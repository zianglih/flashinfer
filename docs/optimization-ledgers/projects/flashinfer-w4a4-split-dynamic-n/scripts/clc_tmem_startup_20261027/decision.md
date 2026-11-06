# TMEM startup experiments: not retained

Both source-paired48-point screens are neutral. Neither variant reduces static instruction count, and both add initialization/ownership machinery. Keep the canonical `9b4721b0` kernel unchanged.

| Variant | Overall control/candidate GM | Decode GM | Prefill GM | Static CLC SASS delta |
|---|---:|---:|---:|---:|
| V1: scheduler bypass |1.000542×|1.000384×|1.000700×|+193 /32 cores|
| V2: only readers wait, allocator publishes |0.999715×|1.000810×|0.998620×|+209 /32 cores|

- V1 `be8a12bb`:64 exact CLC and16 static replays/source;32+8 core pairs; no spills.
- V2 `e1f42b2a`:64 exact CLC and24 static replays/source;32+12 core pairs; no spills. Added static1CTA overlap. Its initial helper rejected config8 before compilation; the repaired guard and all completed CLC work are explicitly recorded.
- Both retain clean9b native full-CLC selections and exact same-GPU/source closing controls as the next opening control. Candidate timings are never reused between versions. Each measured cell has100 cold-L2 CUPTI graph samples after10 warmups. NV includes input quantization. No TRTLLM, W4A16, fresh AUTO, sanitizer or full-publication sweep claim.
- V2 source uses explicit SDK unaligned named-barrier methods, but emitted PTX prints legacy `bar.sync` for reader waits. Independent review found no new blocker from the matching SASS/coverage; the exact compiler pass was not identified. Do not claim the emitted PTX preserves unaligned spelling.

Raw evidence and complete tables remain in [V1 screen](screen/screen-results.md), [V2 screen](screen-v2/screen-results.md), [V1 gate](gate/result.md), and [V2 gate](gate-v2/result.md). Exact metrics/source hashes are in [decision.json](decision.json).

After the reviewer finished reading, the completed local TMEM clone was removed with an exact `e1f42b2a` patch/file-hash check, clean index, no untracked files and only known generated tool caches. [Cleanup receipt](local-source-cleanup.json). No other source copy, remote frozen source, compilation cache, helper, or raw artifact was removed. Nothing was committed or pushed.
