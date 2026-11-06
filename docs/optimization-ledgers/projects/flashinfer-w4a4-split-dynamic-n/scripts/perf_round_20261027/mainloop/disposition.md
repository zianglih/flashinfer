# Rejected: canonical two-CTA SFB multicast

Reject frozen patch `c9854f44` on `2995bfda`; no rerun or retention. The code correctly replaces two identical global SFB requests with one CTA0 multicast, but the whole-chain screen shows no useful gain and generated issue/ownership code grows.

Independent validation checks 267 timing artifact hashes, all 19,200 raw samples, 48 cells, source/routing/tactic/quantization parity and CAAC aggregation. Geomean control/candidate latency is **0.998345× overall**, **1.000234× decode**, **0.996460× prefill**. K3 per-token at 16384 tokens is 0.978977× with stable closing controls; larger drift affects some other prefill rows. These results do not justify the added code/issue overhead or another timing campaign. No speedup claim is retained.

Correctness/codegen evidence remains useful: 128 exact replay comparisons per source, 64 core pairs and 14 PrepareRouted pairs, unchanged resources and no local-memory spills. The base changed cores add 77 non-NOP instructions; the bounded short-K/tail cores add 546. The reduced duplicate TMA work is real, but it did not improve the representative whole pipeline.

The local review clone is released for removal. Remote sources are immutable and all required artifacts have been collected; no active job depends on this local copy. Keep the local proof, probe, patch and result artifacts. Canonical production source is unchanged by this rejected candidate.
