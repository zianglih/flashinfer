# Contemporary fixed-tactic R2/payload diagnostic

Prepared only; no GPU job launched. Use this if the full native payload sweep
leaves uncertainty about shared timing movement. This does not replace the
fresh AUTO sweep or establish retention by itself.

The existing payload uniform result is 330.659 us; the older R2 result is
324.642 us. Both selected N64/G512/epilogue, but they were measured at different
times. ABBA supplies contemporary controls without changing the tactic.

## Exact arms and timing

- A1 and A2: frozen `store16_no_raw_peek`, package SHA256
  `85f18dc5b772155571b21434184b1cef869cc2b0814039c6292943ab344171ff`.
- B1 and B2: frozen cumulative `store16_raw_payload`, package SHA256
  `1bc75d6fa090a747ed0e54e6924feba94039c4cdf4f6c0da4207e371738950db`.
- Sequence: A1, B1, B2, A2, each a new four-rank process group and cache directory.
- Exact `uniform256` fixture: 256 tokens per rank, EP4, GLM-5 dimensions,
  uniform top-8, public full forward, runtime alphas, top-k multiply in FC2.
- Fixed N64/G512/epi_warps, M256/K256, two-CTA cluster, atomic scheduling,
  deterministic reduction, flag batch 4, epilogue batch [2,4], two schedule stages.
- Three eager warmups and 100 cold-L2 CUDA-graph CUPTI samples per run, unchanged
  `benchmark_checked_v2.py` timer and independent reference after timing.
- All 100 samples are retained, including outliers. Each is the simultaneous
  rank maximum. Pool 200 samples per arm for the median; also inspect all four
  run medians, per-run quarters and A1/A2 drift in the existing summary.

The source snapshot remains experimental commit 002 metadata by design. This
comparison isolates the payload increment before ownership movement. It is not
final owned-source performance evidence. Native explicit-knob mode logs a null
AUTO winner: `fixed-knobs.json` attests the exact preserved command and driver,
which the existing summarizer requires instead of inferring a winner.

## Run only after the parent releases the exclusive GPU slot

Copy the new driver beside the existing frozen snapshots, benchmark wrapper
and summarizer at `/workspace/hashinfer-trace/optimization`. No source transfer
or source mutation is required. The driver defaults to a plan:

```bash
bash /workspace/hashinfer-trace/optimization/run-r2-payload-uniform-abba.sh \
  --plan r2-payload-fixed-1
```

When the exclusive GPU queue permits the diagnostic:

```bash
bash /workspace/hashinfer-trace/optimization/run-r2-payload-uniform-abba.sh \
  --run r2-payload-fixed-1
```

Choose a new label if that directory already exists. Each arm has a 20-minute
TERM timeout with 30 seconds before KILL; any failed command or incomplete source,
numerical or timing closure stops the sequence. The driver binds loopback port
29892 and devices 0–3, disables inherited IKET/NCU replay settings, verifies both
source hashes before launching and again before each arm, and checks completion
against the expected hash. Historical results are never overwritten.

Results appear under `optimization/results/r2-payload-fixed-1/`: four raw logs,
four unique cache directories, driver/source and fixed-knob provenance,
`comparison.json`, `comparison.md`, and `COMPLETE` only after all checks pass.
The report retains every sample and does not trim startup outliers. A1/A2 drift
can still limit causal interpretation; no retention threshold is embedded.

## CPU validation

Driver SHA256:
`86924baba676f471fe033b7aeb9346a41060813c96edd165c3e7b126010a532d`.
Benchmark wrapper SHA256:
`387172aa5de21c4030b265f7dac25dd888b75b6ed30a56bd9022f405ad1636c7`.
Summarizer SHA256:
`618935378e9b50df5c8dddc9f71cb9df09316c336732c1770594988585179861`.

`bash -n` and the real CPU-only plan pass. Eight local fixture cases cover
plan/default modes, bad/missing labels, an entirely intercepted synthetic ABBA,
existing-output refusal, failure at B1 stopping before B2/A2, and wrong source
rejection before reserving output. The synthetic ABBA pools 200+200 fixture
samples and checks all source/oracle/tactic closure through the existing
summarizer. Its numbers are replayed CPU fixtures, not new measurements.
See `r2-payload-abba-cpu-check/summary.json`; all six would-be GPU invocations
were intercepted. Frozen source trees and primary remain unchanged.
