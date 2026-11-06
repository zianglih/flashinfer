# 04 integrated BEFORE vs53 convergent early-preparation AFTER

Full independent raw audit PASS. Observed8–8192 geometric BEFORE/AFTER ratio: **1.013773058×**;7/11 retained rows faster. All14 rows appear below;1/2/4 are excluded only from the aggregate.

| Tokens |04 BEFORE µs|53 AFTER µs|BEFORE/AFTER|BEFORE MAD µs|AFTER MAD µs|AUTO winner BEFORE→AFTER|
|---:|---:|---:|---:|---:|---:|---|
|1|75.729|78.624|0.963167×|0.848|0.864|N128 / epi_warps → N64 / epi_warps|
|2|96.017|99.441|0.965562×|0.720|0.880|N64 / epi_warps|
|4|106.416|108.913|0.977078×|0.879|0.928|N64 / epi_warps|
|8|130.529|119.969|1.088023×|1.185|1.136|N64 / epi_warps|
|16|144.450|142.657|1.012562×|1.168|0.720|N64 / epi_warps|
|32|170.177|170.642|0.997278×|1.040|0.913|N64 / epi_warps|
|64|205.394|193.842|1.059595×|1.152|1.136|N64 / epi_warps|
|128|196.434|195.537|1.004585×|0.752|0.720|N64 / epi_warps|
|256|197.537|196.945|1.003006×|0.896|0.911|N64 / epi_warps|
|512|200.866|202.482|0.992019×|0.784|1.104|N64 / epi_warps|
|1024|221.986|224.179|0.990220×|0.896|0.927|N64 / epi_warps|
|2048|301.732|301.651|1.000269×|2.272|1.824|N128 / reuse_dispatch_warps|
|4096|459.796|453.732|1.013364×|3.569|3.615|N128 / reuse_dispatch_warps|
|8192|749.254|752.870|0.995197×|13.232|11.151|N128 / reuse_dispatch_warps|

All112 rank/token outputs are finite BF16 and match bit-exactly across arms, with matching input/weight fixtures. All100 samples perrow are retained, including large first samples.13/14 rows retain identical tactics on all ranks; onlytoken1 changes N128→N64, with epi_warps unchanged. Full tactic dictionaries and sample trends are saved in the audit JSON.

Scope: EP8/H7168/I2048/E256/top-k8, O3, AUTO four deterministic tactics, three warmups and100 CUPTI cold-L2 CUDA-graph samples. Each sample is the rank maximum; table entries are medians of all100. Public forward includes staging, collective compute and integrated deterministic reduction; routing selection is precomputed/excluded. Historical external-finalize wording in the immutable comparator is not the current scope.

The largest retained ratios are1.088023× at8tokens and1.059595× at64tokens. Their within-arm quarter medians are stable, but the serial order does not isolate causality. At2048, the0.081µs difference is much smaller than either MAD. At8192, AFTER is3.616µs slower (0.995197×), smaller than MAD13.232/11.151µs.

|8192-token quarter medians|Q1 µs|Q2 µs|Q3 µs|Q4 µs|
|---|---:|---:|---:|---:|
|04 BEFORE|740.902|741.670|760.423|799.559|
|53 AFTER|747.174|746.278|763.334|797.191|

Late drift is present in both8192-token arms; Q4/Q1 is1.079170 and1.066942. MAD describes within-arm spread, not causal confidence. This one serial pair does not cancel time-dependent changes and does not establish an overall benefit independent of noise.

BEFORE source `04c51ad94738877e67045ece949ed16cd12c6f82`; manifest `ea0003b749bb72e483f2bdc3ab3cd4420620e81bafa9b210c1f9255e22f3bc69`. Timing 2026-09-18T19:18:33.271327+00:00–2026-09-18T19:25:58.113532+00:00; wall 444.842205s. Archive51files/235,304,003raw bytes/188,698,554compressed bytes, SHA256 `9b7e202ba9503f7f417ec84c80fe15a128aa09af89ef3ad86a8609a3464e0402`.

AFTER source `53caea384acd53cadce44d276d8a8a155b3c119d`; manifest `2eee96a867fa45a9a94afdb3e04c0971466d159fe512b0cfd2138025c2037450`. Timing 2026-09-18T19:50:11.357326+00:00–2026-09-18T19:57:38.196058+00:00; wall 446.838731s. Archive58files/235,484,733raw bytes/188,712,462compressed bytes, SHA256 `65ecaeb30ef09a18e7f06729dc272ee49d63acb3c80e72eeaaa09620c3c2ff56`.

Both106-file source trees, immutable helpers, setup/host/boot/GPU inventory, exact commands and full archives verified. Recorded codegen/native/queued intervals do not overlap either timing arm; GPU-idle endpoints and owned-group closure are retained. These are recorded-state checks, not continuous GPU monitoring. Transfers resumed against sealed archives without rerunning timing.

Independent audit: `independent-timing-audit.json`, SHA256 `7d417f709ea39aca2ba807d17b54eefc4e203cfebcc8ed1453e2253ce7b1a0ef`. Complete raw samples, output tensor hashes, median/MAD/trends and full selected tactics remain traceable through that report. This is53 versus04; it is not performance evidence for unmeasured364.
