# Local readiness overlap trial

Candidatec2b93f50 relays the established all-rank FC2 readiness event through one rank-local GPU release/acquire flag. It removes the second whole-CTA tail wait and permits reduction during the dispatch grid broadcast. Source proof and code remain in this isolated effort; current production7dc is unchanged.

Bounded qualification passed before timing:32 finite exact capture outputs across4 tactics,128 compiled fused ABI artifacts, intentional one640-thread tail barrier and unchanged16 dispatch barriers, correct flag clear/publish/consume ordering, REG96/STACK0/LOCAL0. Two strict1024 random/skewed EP4 cases cover all4 tactics,O2/O3,eager/graph and2,113,929,216 element comparisons. Queued tests passed96 case/rank records and1536 graph snapshots. See qualification/BOUNDED_VALIDATION.json, with separate owner and independent review receipts. These are not full60 or sanitizer claims.

A single C1 sweep uses the frozen existing benchmark/worker/timer and today's retained7dc A1 from input-stage-prep-overlap/performance. Samehu-pdx-7 boot and environment are verified;1–8192,100 cold-L2 CUDA-graph CUPTI rank-MAX samples per row,AUTO4,EP8,H7168/I2048/E256/K8. Output/fixture equality and all samples are retained. Only8–8192 enters retention aggregate. The retained serial baseline does not cancel temporal drift.

Timing completed with all14 rows. The sealed table has GM8–8192 1.00129224×; the result is marginal and remains unpromoted. Full independent archive audit passed: `after-benchmark/independent-timing-audit.json`, SHA256 `beb957c27e06696abb67d445f123f67a82dd8a58d71c42be07f3c22d973bc7b7`; all14 selected tactics are unchanged. Supervisor/PGID102668. Exact bindings:after-benchmark/remote-command.json and benchmark-launch.json. Root authorized launching after runtime gates while CPU-only collector review completed; both authorization and independent wrapper review receipts are preserved under gpu-setup.

The complete archive is locally verified: `after-benchmark/collected-perf-c1/evidence.tar.gz`, SHA256 `bab1cda11f730b0631e035d41c1152e3e66ba982447d8aa25ba5b35696ebda90`,188707407 bytes,59 members. Collection checks same host/boot, all owned process groups absent, idle GPUs,208 source files and112 exact cross-arm output pairs. An SSH transfer interruption at88MB was recovered by validating all existing chunk hashes and resuming the immutable archive; no source, timing or seal changes.

Independent full archive audit passed. Microseconds; speedup is retained7dc /c2b.

| Tokens |7dc|c2b|7dc/c2b|
|---:|---:|---:|---:|
|1|64.1280|74.0485|0.8660×|
|2|90.3205|87.9845|1.0266×|
|4|101.5215|103.4405|0.9814×|
|8|125.7775|125.5530|1.0018×|
|16|138.0970|137.9855|1.0008×|
|32|164.6410|167.4895|0.9830×|
|64|188.0180|187.1700|1.0045×|
|128|194.8020|194.4330|1.0019×|
|256|194.5615|194.8655|0.9984×|
|512|199.0415|197.6330|1.0071×|
|1024|221.1215|218.7375|1.0109×|
|2048|307.1870|308.7690|0.9949×|
|4096|470.1170|466.8815|1.0069×|
|8192|775.5915|772.3420|1.0042×|

Geometric mean8–8192: 1.00129224×. Serial same-node controls; no drift claim.
