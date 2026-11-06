# Sole-announcer retention decision

Retained by the parent on 2026-10-28 as a simpler general operand protocol,
with no end-to-end speedup claim. The source remains unstaged and frozen in
`flashinfer-operand-announcer-review` pending final composition. No new GPU
work is scheduled from this experiment.

One elected weight producer announces all A/SFA/B/SFB transaction bytes for
the CTA group. Activation keeps its independent empty-stage wait and TMA
issuing. This removes one executed full-barrier arrival per K-stage without
adding an inter-producer rendezvous, tactic axis or shape-specific policy.
See [protocol and codegen audit](README.md) and the
[independent review](../../scheduler/sole-announcer-review/REVIEW.md).

The matched CAAC screen used fresh cb35-equivalent control and candidate
measurements on the same GPU per model, frozen tactics and exact routes,
10 warmups and 100 CUPTI cold-L2 samples. It covered all four models, all four
formats and tokens 4/64/4096/16384: 64 cells, 48 public benchmark processes and
25,600 samples. No external baseline was rerun. The standard all 100-sample
median is the primary statistic.

| Aggregation | Speed change |
|---|---:|
| All 64 cells | -0.022% |
| Decode 4/64 | +0.065% |
| Prefill 4096/16384 | -0.109% |
| V3 | +0.175% |
| V41F | -0.035% |
| K3 | -0.012% |
| N3U | -0.215% |
| MXFP4x8 | +0.196% |
| MXFP8 | -0.295% |
| PER-TOKEN | -0.065% |
| W4A4 | +0.077% |

V3 MXFP4x8 at 4096 tokens has a consistent **-1.057%** cost: control/candidate
pass spreads 0.071%/0.035%, first 25 diagnostic -0.949% and last 50 -1.015%.
This small prefill cost is accepted explicitly; no special-case workaround
or unroll-policy change is added. Larger 16K differences switch sign by
sample stratum or pass and do not support a source-specific causal claim.
Overall first 25/last 25/last 50 diagnostics are -0.068%/-0.391%/-0.119%; they
are never substituted for the standard median.

All 11 exact configurations passed 176 storage-bit replays against the control
and 88 matched kernel pairs, with no spills and unchanged shared/stack/local
memory. The barrier-byte and full-count codegen checks passed. One geometry's
activation loop fully unrolls after the simplification, emitting more static
wait sites while executing the same 18 waits per tile; the audit documents it.
Sanitizer and exhaustive cross-products were deliberately not run.

The [complete 64-cell table](../../scheduler/caac-audit/sole-announcer/verified/RESULTS.md),
[primary and diagnostic CSV](../../scheduler/caac-audit/sole-announcer/verified/cells.csv)
and [provenance audit](../../scheduler/caac-audit/sole-announcer/verified/audit.json)
retain all measurements. `retention-receipt.json` pins source and evidence
hashes; the gate archive verifies 724 files and the performance archive 1142.
