# Asynchronous retirement trial

Candidate `0190cce2ebf085f75d985c01f347a07617ba518e` builds on local readiness `c2b93f50`. Dispatch warps wait for the retirement rendezvous; the other roles arrive without blocking, prepare reduction metadata, and acquire the established rank-local readiness flag before reading FC2 partials. The inline wait includes a compiler memory clobber and adds no hardware fence. The earlier `d4b82885` freeze and helper package are preserved unexecuted because they lacked this compiler clobber.

Qualification uses `qualification-v2`, backed by `frozen-source-v2` (104 files, manifest `0bcf99ad394f972b9f798cff7270ef421864be953723ae330846616847e9b245`). Capture passed all four tactics and 32 ranks; finite BF16 outputs exactly match retained `7dc96269`. All 128 compiled fused ABI artifacts retain REG96/STACK0/LOCAL0/SHARED1024 and no spill instructions. PTX contains one nonaligned dispatch `barrier.cta.sync 8, 640` and one retiree `barrier.arrive 8, 640`; the 16 dispatch barrier sites and readiness ordering are unchanged. Owner gate and independent review are separate artifacts. Capture executes int32/vector; other ABIs are compiled and inspected.

Strict1024 random/skewed EP4 validation passed all four tactics, O2/O3, eager and CUDA graph. Queued validation passed before timing. These bounded gates do not replace full numerical and sanitizer qualification if retained.

Root authorized one full 1–8192 AFTER sweep once the independent generated gate and strict/queued gates pass. It uses today's retained `7dc` A1 control on the same hu-pdx-7 boot/environment, plus a comparison with the sealed `c2b` C1 table. Runtime helpers, 100 cold-L2 CUDA-graph CUPTI samples, EP8/H7168/I2048/E256/K8, AUTO4/O3 remain unchanged. Only 8–8192 contributes to the retention aggregate; all 14 rows remain visible. The serial control does not remove temporal drift. No promotion or PR changes are authorized from this trial alone.

Bounded qualification completed successfully: `qualification-v2/BOUNDED_VALIDATION.json` SHA256 `b7bbc4f3be16f33685c6b54c18ed9fd7264e9c04c0449d4818b77f18b3f750ac`; strict reference checks96, output-pair checks240, exact element comparisons2,113,929,216; queued case/rank records96, replay output checks1536. D1 full sweep completed after fresh same-host/boot/source/GPU-idle and port29975 checks. No archive transfer or export runs during timing.

## Decision: rejected, retained source remains7dc

The full independent timing audit passed: `after-benchmark-v2/independent-timing-audit.json`, SHA256 `10c4957c6b6f7fb1ee31d977055781108ee653aacc08ab19e4e34737f6115423`. The complete table, per-row MAD, ordered-quarter medians and selected tactics are in [the timing audit](after-benchmark-v2/independent-timing-audit.md). All112 cross-arm outputs are finite and bit-exact; all14 selected tactics match both controls. All2800 retained7dc/D1 samples,208 source hashes and fresh same-node/boot/process-group/GPU closure were verified.

8–8192 geometric speedup is **0.99218302× versus retained7dc** and **0.99090253× versus c2b**. Only3/11 retained rows improve versus7dc. This does not justify the additional orchestration; root rejected0190 with no repeat, promotion or PR changes. Both0190 and the earlier unexecuted d4 prototype remain available. GPU ownership is closed and the node is held for a separate authorized profiling-only diagnostic.

The immutable archive is `after-benchmark-v2/collected-perf-d1/evidence.tar.gz`, SHA256 `2f6f088b5e696303e8c8427e55d2ec28e5297d73be57fec53cd09721845210d0`,188707338 bytes,59 members. Full local transfer and member verification succeeded.

Full independent D1 archive audit passed. Latencies in microseconds. Serial same-node/boot arms; no drift cancellation.

|Tokens|Retained7dc|Local-readyc2b|Async-retirement0190|7dc/0190|c2b/0190|
|---:|---:|---:|---:|---:|---:|
|1|64.1280|74.0485|71.6490|0.8950×|1.0335×|
|2|90.3205|87.9845|81.8410|1.1036×|1.0751×|
|4|101.5215|103.4405|99.0880|1.0246×|1.0439×|
|8|125.7775|125.5530|126.3845|0.9952×|0.9934×|
|16|138.0970|137.9855|140.2405|0.9847×|0.9839×|
|32|164.6410|167.4895|167.0575|0.9855×|1.0026×|
|64|188.0180|187.1700|190.9605|0.9846×|0.9802×|
|128|194.8020|194.4330|196.1455|0.9932×|0.9913×|
|256|194.5615|194.8655|197.8885|0.9832×|0.9847×|
|512|199.0415|197.6330|198.6260|1.0021×|0.9950×|
|1024|221.1215|218.7375|222.5940|0.9934×|0.9827×|
|2048|307.1870|308.7690|306.9945|1.0006×|1.0058×|
|4096|470.1170|466.8815|464.3245|1.0125×|1.0055×|
|8192|775.5915|772.3420|791.7795|0.9796×|0.9755×|

GM8–8192: retained7dc/0190 0.99218302×; c2b/0190 0.99090253×. All14 selected tactics match7dc: True.
