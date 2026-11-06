# K3 EP8 MXFP4x8 4096: control vs R6 iKET

The FC1 Gather4 regression is localized to readiness publication on the gather
side. **Follow-up split markers confirm that the elected cluster arrival takes
about802 ns/K stage; the proxy fence itself takes only17 ns.** The MMA warp's weight wait falls from77.7 to49.0 ns, while its new gather
wait averages805.3 ns/K stage. SF-copy and MMA-issue ranges are essentially
unchanged. Epilogue body time is slightly lower, but accumulator wait rises
from3.50 to24.76 microseconds/tile.

A sharper lead is the relay warp: the gap after completing its local gather
wait and before starting the next wait averages849–948 ns/K stage across the
four sampled CTAs. Its local wait itself is only58–156 ns. That unmarked region
contains `fence_view_async_shared`, elected cluster `mbarrier_arrive`, pipeline
state advance and loop bookkeeping (`evidence/candidate/sampled/sampled-core.py`,
lines2994–3016). This points to publication/fence overhead as a targeted hypothesis,
not proof that the barrier or fence alone is responsible. The follow-up diagnostic below resolves this gap to cluster arrival, matching
the independently inspected SASS release sequence.

## Binding and scope

- Control: retained `d35fcfda03875077b3af8455575cc1d20e866a8c`, core SHA256
  `14044c6c674ede904f32b29f9d4223b313adfa39798034aecd3a42defea9ae8c`.
- Candidate: frozen R6 core SHA256
  `deba8b639fba89e6f76381e8c6bf8bc323ccaf850b973c836f476f8144c4cc0a`.
- Both: routeN128, MMA tile256x128, two CTAs, tileK128,9 stages, PDL on,
  static scheduler. Control256 threads; R6 dedicated-gather384 threads.
- Same saved winner, routing IDs and routing weights as the original benchmark.
  All513 source hashes checked before and after each probe; winner caches
  copied independently and unchanged. No tactic profiling or CUPTI timing call
  allowed by the probe. No source checkout or review file changed.
- Actual frozen public benchmark callback, `--profile-cuda --profile-iters 1`,
  through `run-iket` NativeDump. Instrument FC1 only, first two clusters,
  four CTAs; one captured launch per arm. Artifact-only marker modifications
  passed AST equivalence after marker removal.
- C3 `fi-fc1-gather-1028`, GPU7. Both profiles complete with return0;
  GPU7 idle at collection. No retention benchmark numbers are generated here.
- Instrumented ranges include marker perturbation and are not uninstrumented
  latency evidence. Concurrent warp ranges must not be added. The existing
  winner is static, so this capture says nothing directly about CLC overhead.
- iKET `warpLocIdxs` contains start/end endpoints. The analyzer deduplicates
  equal locations to avoid double-counting counts and accumulated durations.

## Files

- `evidence/summary-table.md`: control/R6 mean markers and sample counts.
- `evidence/relay-table.md`: same-tile relay gaps;28 K stages/tile.
- `evidence/{control,candidate}/trace/*.trace.json`: complete raw traces.
- `evidence/{control,candidate}/probe/*/receipt.json`: both tracker and profiler
  process receipts, source checks, compile config, routes and cache hits.
- `evidence/{control,candidate}/sampled/source-proof.json`: artifact source hashes
  and marker-only AST proof.
- `evidence/archive-manifest.json`, `collection.json`, `evidence.tar.gz`: verified
  collection hashes. Relay analysis is derived locally after collection.
- `build_sampled.py`, `probe_iket.py`, `run_pair.py`, `analyze.py`,
  `analyze_relay.py`: reproducible capture and analysis.


## Follow-up: separate proxy fence and cluster arrival

The second source-bound pair completed successfully with the same routes,
winner,9 stages and instrumentation boundaries. Marker-only AST proof again
passed. Each sampled CTA records1036 K stages (37 tiles ×28 stages).

| Relay region | CTA0 mean / median ns | CTA1 mean / median ns | CTA2 mean / median ns | CTA3 mean / median ns |
|---|---:|---:|---:|---:|
| Local completion wait | 63.9 /64 | 62.0 /64 |149.1 /64 |61.0 /64 |
| Proxy fence |16.4 /32 |16.9 /32 |17.1 /32 |17.1 /32 |
| Elected cluster arrival |823.9 /800 |820.6 /800 |779.6 /800 |872.8 /832 |

The release-arrival region accounts for almost all of the earlier unmarked gap.
It lowers to `MEMBAR.ALL.CTA`, `MEMBAR.ALL.GPU`, `ERRBAR`, `CGAERRBAR`,
`SYNCS.ARRIVE`; see `../codegen/RELAY_LOWERING.md`. The32ns timestamp granularity
limits interpretation of the tiny proxy-fence range.

**Do not remove the proxy fence based on the lack of generic `st.shared`.**
The [official CUDA guide](https://docs.nvidia.com/cuda/cuda-programming-guide/03-advanced/advanced-kernel-programming.html#async-thread-and-async-proxy)
classifies LDGSTS/nonbulk cp.async as generic-proxy operations, unlike TMA and
tcgen05. Therefore the SF path crosses proxies. Existing `PipelineCpAsyncUmma`
code is a useful implementation comparison but its missing fence is not a
memory-model proof. CUTLASS issue3721 reports the analogous concern for SM90;
it is an unconfirmed source audit, not a vendor-confirmed runtime failure.

A targeted candidate should retain the local acquire wait and proxy fence,
then narrow publication to shared memory. The [PTX fence documentation](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-membar)
provides this release-pattern example (PTX8.6+,SM90+):

```ptx
fence.release.sync_restrict::shared::cta.cluster;
mbarrier.arrive.relaxed.cluster.shared::cluster.b64 _, [bar];
```

Keep the MMA acquire wait. The relay publishes only local shared payload/SF
readiness; it has no global writes to publish. An independent ordering review
is checking the acquire-to-shared-release transitive chain before changing the
implementation. Relaxed arrival alone has no ordering guarantee and is not the
recommended experiment.

Follow-up raw traces, source proofs, tracker/profile receipts and complete mean
marker table are in `relay-evidence/`. `publication-distributions.json` records
the full per-CTA mean/median/p90 values. Archive SHA verification succeeded for
all22files. `relay-evidence.tar.gz` and `relay-collection.json` preserve the
collection. GPU7 was released to the parent after profiling; no further GPU
work is owned by this diagnostic task.
