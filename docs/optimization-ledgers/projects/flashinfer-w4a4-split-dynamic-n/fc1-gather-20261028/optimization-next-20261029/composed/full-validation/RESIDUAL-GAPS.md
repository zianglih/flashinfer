# Residual prefill gaps after control112 + scale-copy ordering

These comparisons use the complete measured kernel later committed as
`7106faf`. The fresh causal experiment is **fb66 → 7106 at identical tactics**.
The following d35, TRTLLM and non-swap numbers reuse historical controls;
they are not fresh same-GPU comparisons. Raw routing and quantization contracts
were reverified. Only 39/468 cells use the same physical GPU as the original
d35 campaign. `d35-residual-cells.csv` also includes a separately labeled chain
of the two paired ratios through fb66, for a drift check; the public table must
use the direct saved-latency comparison, not that chain.

## Highest-value source gaps

| Shape / format / tokens | d35 µs | 7106 µs | Speedup vs d35 | Paired-chain diagnostic |
|---|---:|---:|---:|---:|
| N3U EP8 W4A4 16384 | 514.722 | 718.593 | −28.37% | −28.25% |
| N3U EP8 MXFP4x8 16384 | 762.740 | 871.360 | −12.47% | −13.43% |
| N3U EP8 MXFP8 16384 | 828.645 | 939.769 | −11.82% | −12.51% |

N3U EP8 W4A4 at 4096/8192 is also −17.61%/−21.34% versus d35. The fresh fb66
controls differ by only +0.05%/+0.27%/+0.17% from the original fb66 medians at
4096/8192/16384, making this a much stronger residual than a marginal historical
comparison. At 16K MXFP4x8/MXFP8 the drift is −1.10%/−0.78%; the gap still
persists under both calculations.

These are identical frozen source-version tactics, all **static two-CTA**:

- W4A4: route N128; FC1 M256, FC2 M512, both Ksteps4.
- Both MX formats: route N256; FC1/FC2 M256, both Ksteps4.

Changed winner selection therefore cannot explain the source regression. The
old winner can nevertheless be a poor choice for gather reuse: the existing
M512 FC1 candidate halves channel-tile repetitions relative to M256. A clean
fb66 native retune already improved N3U EP W4A4 16K by 21.86%, without changing
source or expanding tactics. This remains separate evidence, not a measured
7106 improvement. Final-source native-cache replay is deferred while the new
metadata composition is validated.

## What the collected iKET trace establishes

The existing N3U EP8 W4A4 16K capture compares d35 with **fb66**, not 7106. It
uses the same routes and static two-CTA winner, FC1 only, first two clusters.
The table below uses the two cluster-leader CTAs; concurrent warp ranges
overlap and cannot be summed into an end-to-end latency breakdown.

| Marker mean | d35 | fb66 | Interpretation |
|---|---:|---:|---|
| Startup dependency wait | 28.8 ns | 5.3 ns | Not the main prefill issue in this capture |
| Weight stage empty wait | 209.7 ns | 349.3 ns | Mainloop progresses more slowly before storage reuse |
| Gather relay wait | — | 460.6 ns | Local payload/SF completion has material latency |
| MMA gather-ready wait | — | 57.0 ns | Separate consumer dependency remains visible |
| MMA weight-ready wait | 72.9 ns | 80.3 ns | Weight readiness changes much less than epilogue waits |
| Epilogue accumulator wait | 590.3 ns | 1982.7 ns | Consistent with slower accumulator production |
| Epilogue body | 1641.7 ns | 2106.3 ns | Also slower, but old fb66 spill/marker effects may contribute |

The gather issue range is 114.7 ns per warp/stage versus 44.7 ns for old
activation TMA, but there are four gather warp issuers and different instruction
counts. This is evidence to examine issue efficiency, not a directly additive
2.6× cost. There is no CLC work in this winner. The prior R6 K3 cluster-release
stall was already fixed before fb66 and must not be recycled as an unfixed
7106 diagnosis.

All 430 gathered-kernel observations in the new full run report zero local
bytes. Thus the old trace's epilogue-body increase cannot by itself justify
another register-budget change. A focused NCU comparison should distinguish:

1. **Gather issue/metadata pressure:** increased instruction/issue utilization,
   TMA issue counts and issue stalls without proportional DRAM growth. Prefer
   uniform route metadata, fewer pointer conversions, and reuse of one gathered
   activation stage across existing wider channel tiles.
2. **Repeated activation/SF traffic:** increased L2 sectors and DRAM reads,
   reduced tensor utilization, or long-scoreboard stalls. First replay existing
   native M512/K-step winners, then consider generally calculated stage budgets
   or wider reuse; do not add shape predicates or arbitrary fixed stage counts.
3. **Dependency publication:** low tensor activity with wait/short-scoreboard
   dominance and modest traffic. Revisit where payload and SF completion are
   published, while preserving local completion, proxy fences, consumer acquire
   and storage-release ordering.

No new iKET capture is needed for the same W4A4 case before this distinction.
MXFP4x8 at N3U EP16K is the useful second case: its activation payload is wider
and its K-stage behavior differs, while the residual and static scheduling
match the W4A4 signal.

## Separate historical backend gaps

At N3U EP16K, 7106 is −9.14%/−3.50%/−1.96% against same-dtype TRTLLM
W4A4/MXFP4x8/MXFP8. Against non-swap it is −29.99%/−18.26%/−13.16%; the MX
non-swap controls use fused finalization, marked † in the raw comparisons.
That fused-versus-unfused boundary is material.

TP V3 MXFP4x8 8192 remains −21.74% against fused non-swap and −7.52% against
TRTLLM, even though the gather design improves over d35. This is a separate
whole-pipeline issue: do not attribute all of that gap to the new gather path.
Likewise N3U TP per-token 16K is −16.93% against TRTLLM and −9.04% against
non-swap. Those TP cases merit a subsequent per-kernel breakdown before changing
FC1 alone; FC2/finalization and short per-expert GEMMs can matter.

Evidence: `d35-residual-{cells.csv,summary.json}`, `external-baseline-{cells.csv,audit.json}`,
and `../../iket-n3u-ep/evidence/{summary-table.md,summary.json}`. Historical
external audit verified 88 original raw files and 660 comparisons with zero
contract mismatches. All instrumented profile numbers remain diagnostic only.

## Fresh CUPTI decomposition follow-up

A same-GPU public CUPTI activity capture now compares d35 directly with the
frozen 7106 composition for N3U EP8 16K W4A4 and MXFP4x8. It is diagnostic
(one 100-sample control/candidate pair, not CAAC), with identical frozen winners
and routes. No GPU work was added; serialization occurs after measurement.

For W4A4, the stable mean total is 512.61→715.74 µs. Removing prepare saves 19.51 µs;
FC1 completion increment adds 222.97 µs. FC2 completion tail changes −0.29 µs
and combine −0.06 µs. FC2 duration 202.03→217.67 µs is explained by greater
FC1/FC2 overlap 15.45→31.37 µs, not an added end-to-end tail. The source gap
is therefore localized to FC1 under this tactic.

MXFP4x8 also shows FC1 completion-increment growth (+121.93 µs) and removed
prepare cost (−31.79 µs), but both captures drift substantially across their
100 samples. Its exact total/tail deltas are not reliable causal estimates.

Bounded NCU smokes hung at first CUDA allocation even for a native fixed binary
that succeeds unprofiled. No hardware counters were obtained. TMA issue pressure
versus repeated L2/DRAM traffic remains unresolved; do not assert either cause.
The existing native M512 tactic result and uniform metadata work remain the
most evidence-supported next directions. See
`../../ncu-n3u-prefill/RESULTS.md` and its source-bound raw activity evidence.
