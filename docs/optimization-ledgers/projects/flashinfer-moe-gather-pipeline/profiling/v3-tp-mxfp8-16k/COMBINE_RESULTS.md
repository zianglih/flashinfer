# V3 TP8 MXFP8 T16384 combine profile

Native frozen winner/source822, unchanged finalizer bytes at retained02de.
Five NCU application replays, stock clocks, no cache controls, native source and
recorded routing/tactic verified. GPU6 is released; no production edits.

| Metric | Value |
|---|---:|
| Diagnostic duration |331.136us|
| DRAM read |1,877,658,624bytes|
| DRAM write |277,002,496bytes|
| DRAM throughput |84.82% peak|
| L2 hit |0.17%|
| L2 throughput |49.02% peak|
| Issue activity |22.67%|
| Long scoreboard |92.08%|
| MIO throttle |0.03%|
| Barrier stalls |0%|
| Registers |64/thread|
| Shared memory |0|

The prior native CUPTI phases exposed329.843/330.370us of combine work. The
profile strongly supports memory traffic as the main limitation, not a missing
CTA barrier optimization or memory-issue-throughput bottleneck. The expected
live input is1,879,048,192bytes plus234,881,024output bytes; diagnostic hardware
traffic includes cache behavior and overlap and is not assumed identical to
logical bytes. These counters do not prove an absolute bandwidth floor.

Do not reopen the already-rejected vector-outer/LDG256 combine variants on this
evidence. No code candidate is proposed. All receipts, raw counters and native
selection fingerprints remain incombine/. This stage does not alter the published
retention tables or mix NCU time into CUPTI comparisons.
