# FC2 N128 early accumulator release

Task-local diagnostic against frozen13ca, with the retained static-dimension
specialization applied equally to control and candidate. The candidate releases
an N128 accumulator bank after its last TMEM load, before conversion and bulk
store drain. N256 overlapping-bank logic is unchanged. Inactive channels and
empty trailing slabs still release exactly once.

24 six-format, per-token and route-tail paired exact cases passed. Native
NVFP4 fixed-tactic FC2 medians improve64.384→64.080us at4K,
94.688→93.105us at8K,157.280→153.184us at16K; corresponding whole chains are
206.881→205.936,319.728→317.137,559.857→556.737us. MXFP8 evidence is noisy
and does not establish a repeatable benefit. Raw logs and all samples are in
this directory. Same C1 B200 GPUs3/5,26.05 PyTorch CUDA13.2,10 warmup/100
cold-L2 graph/CUPTI samples. Fixed tactics are diagnostic, not primary AUTO
retention evidence. Existing B1 data was not rerun.

Decision: defer integration. iKET reports only69ns accumulator-empty wait per
FC2 N128 tile, whereas FC1's single bank waits4.328us. Prioritize the latter
and removal of FC2 scale-factor loading/relay overhead first.
