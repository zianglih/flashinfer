# Single operand-stage completion screen

Frozen7829fc00, native NVFP4 T16384, M256N256/cluster2 for both phases,
C1B200GPU3, image nvcr.io/nvidia/pytorch:26.05-py3.
10warmups/100 cold-L2 CUDAgraph/CUPTI samples, actual native route inputs.

The existing AB empty barrier already gates all operand storage reuse after
MMA completion. The variant skips the redundant A empty wait, A consumer release
and A producer tail; its leader-CTA TMA full-barrier arrival/transaction counts
and wait remain unchanged. Both CTAs retain the local SF completion relay.
The AB tail still drains every operand stage. This revisits the prior single-CTA
completion experiment on the current two-CTA implementation.

| Phase | Control us | Single completion us | Control/variant |
|---|---:|---:|---:|
| FC1 |324.7370|323.6170|1.0035|
| FC2 |180.8810|180.3520|1.0029|

Native output/SF bytes match. All24 paired FC1 cases pass across six formats,
N128oneCTA/N256twoCTA, quantized/per-token outputs, shortK and persistent reuse.
The gain remains below1%; rejected for retention, no production edits.
Raw artifacts are `logs/single-completion-*` in the project root and remotely.
