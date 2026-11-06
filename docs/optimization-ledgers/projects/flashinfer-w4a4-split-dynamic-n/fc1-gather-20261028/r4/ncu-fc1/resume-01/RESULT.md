# Bounded NCU attempt did not complete

The replacement-box attempt stopped at its360-second limit while Nsight Compute initialized the retained/control process. The profiler used approximately one CPU core; the target Python process slept and GPU7 remained at4MiB/0% utilization. No benchmark table, selection receipt, `.ncu-rep` or counters were produced. R4 candidate profiling was skipped. This is not evidence of an FC1 barrier hang.

The timeout killed the launched process group. A fresh check found no remaining owned processes and GPU7 at0MiB/0%; GPU7 was explicitly released to the parent task. No automatic retry was made.

The original preemption-interrupted attempt remains unchanged one directory above. This retry's nine files are preserved in `evidence/` and SHA-verified `evidence.tar.gz` (`cafaab86a9854ad786428338d3d3ad53a90b7f1f9129f4b2ff0e8ba939f62037`). `failure-summary.json` records the boundary.

The retained and R4 source manifests, cache links and selected frozen winner/route inputs were verified before launch. Because capture never completed, no post-capture route/selection claim is made. R3 codegen and R4 end-to-end timing remain separate evidence.
