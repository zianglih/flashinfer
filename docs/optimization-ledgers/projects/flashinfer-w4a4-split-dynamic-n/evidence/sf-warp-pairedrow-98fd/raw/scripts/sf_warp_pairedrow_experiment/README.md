# Paired-row compact SFB loading

Independent actual-source clone `flashinfer-sf-warp-pairedrow-review`, base98fd,
with two unstaged files. Derived from frozen localwait core7f0fdbc4; prior
source/artifacts remain unchanged. The only new change maps each warp3 lane to
`row=lane%16`, `half=lane//16`, so each lane issues four4-byte cp.async copies,
one per512-byte atom. This is motivated by published TRT N16's four SFB copy
sites, not a claim that the historical generated source matches current cubins.

The same128 active-row even words are refreshed each K512. Existing odd-word
padding remains scalar-initialized once. The128 upper-row even words are now
also scalar-initialized once in all four source stages; no vector startup
optimization is combined. Thus384 immutable words plus128 refreshed words cover
every2048-byte stage. Low rows outside current validN and channel groups beyond
K still zero-fill on every reuse. Source addresses retain canonicalSF layout.

All32 lanes retain commit_group→wait_group0→async-shared proxy fence→warp sync;
SFAfull/sharedsourceempty/TMEMfull-empty and TCGEN fence/copies remain. No
role/stage/weight-layout/API/fallback change:288threads,4 source stages,2SFslots,
physicalN16,generatedFP4 gated NVFC1N16 only. All56 iKET calls unchanged.

CPU check `check_layout.py` proves unique whole-stage ownership and compares
5950 persistent-stage updates (3,046,400 words), valid counts0..16, K64 through
7168, repeated grow/shrink and canonical128-row boundaries. This is a coordinate
model; GPU exactness and performance remain separate gates. Published-source
and previous SASS evidence are preserved as `prior-*` files.

GPU2 on B200-92. Run `run_smoke.sh` then `run_pairs.sh`: seven saved-oracle cases
with no baseline oracle rerun; nativeT32 FC1/SF/FC2/full exact; then T32/T128
fixedN16 ABA/BAB,10warmups/100cold-L2 graph CUPTI samples perarm. Initial input
quantization outside; regular preparation inside fullchain/FC1. Same-node
adjacent98fd controls only; no oldTRT or primary/AUTO performance comparison.
No other optimization axes are combined.
