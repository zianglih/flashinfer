# Independent Nsight Systems review

Reviewed the four inference traces at source
`2079fa00c4a2a0fb2e95bb284978a703653a4830`, 20 replays each.
`verify_nsys_investigation.py` independently reconstructs activity ownership
and occupied GPU intervals; results are in `artifacts/nsys-independent-audit.json`.

Every captured device activity has exactly one owner: a synchronized `moe`
range or a synchronized `l2_flush` range. The 40 NVTX ranges alternate flush
and MoE without overlapping. Each MoE range contains exactly one
`cudaGraphLaunch` and one synchronization API, one repeated node sequence,
one process, one GPU and one stream. Each flush range contains one separate
kernel. CuTe has 8 target activities per replay (7 kernels and output memset),
TRTLLM BF16 has 5 kernels. Total activity counts are respectively 180=160+20
and 120=100+20; no activity is unassigned or double counted. Each target graph
node occurs once per replay. The excluded flush costs approximately 68 us.

All independent span/gap/overlap values agree with the existing breakdown
JSON for all 80 replays. Thus the reported graph spans contain one local MoE
call, with flushes, preparation and host launch time excluded.

Mean device timings in microseconds:

| Tokens | Backend | FC1 + SwiGLU | FC2 (CuTe includes fused finalize) | Separate finalize / output memset | All activity sum | GPU span | Uncovered GPU gap | Overlapping activity intervals |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | CuteDSL W4A16 | 67.812 | 36.946 | 0.906 memset | 118.386 | 118.522 | 0.668 | 0.531 |
| 32 | TRTLLM BF16 | 189.739 | 89.677 | 5.779 finalize | 291.712 | 285.562 | 0.000 | 6.150 |
| 4096 | CuteDSL W4A16 | 164.956 | 147.033 | 9.722 memset | 362.538 | 359.142 | 0.644 | 4.040 |
| 4096 | TRTLLM BF16 | 331.377 | 150.361 | 38.018 finalize | 535.309 | 527.871 | 0.000 | 7.439 |

FC1/FC2 mapping follows the verified source execution order and graph node
sequence. The native FC1 kernel name also includes `swiGlu`. CuTe's FC1 and
FC2 use the same generated name but different graph-node positions and grids;
they must not be merged when reporting the stages.

At 32 tokens, TRTLLM BF16 is 2.409x slower by mean GPU span. Its FC1 is
121.927 us slower and FC2 is 52.731 us slower, while the finalization difference
is only 4.873 us. At 4096 tokens it is 1.470x slower: FC1 costs 166.421 us more,
FC2 3.328 us more and separate finalize versus output memset 28.296 us more.
CuTe's separate routing/permute/setup costs more than native TRTLLM at both
sizes, partially offsetting the GEMM advantage.

These decompositions sum interval durations, which overlap. The correct
identity is `span = sum - overlap + uncovered_gap`, applied per replay.
Do not call `span - sum` a negative gap. Both APIs enable Programmatic
Dependent Launch, and NVIDIA documents that dependent kernels can overlap
even on the same stream and in CUDA graphs. The observed overlap is compatible
with this enabled feature; it is not by itself evidence of invalid timestamps.
[CUDA PDL documentation](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html)

Mean `cudaGraphLaunch` CPU durations are 7.4–9.9 us, including a slower first
profiled launch. The target spans begin at the first device activity, so those
CPU durations cannot explain a 167–169 us device-span difference. Native BF16
has no uncovered GPU gaps in these traces. The data locate the difference
inside GPU GEMMs, especially FC1, not preparation or host-side API overhead.

The trace does not measure DRAM bytes or establish that bandwidth alone causes
the GEMM difference. A minimal two-GEMM Nsight Compute probe is prepared in
`ncu-gemm-probe.md`; its replay changes node isolation/cache state and must be
reported as a hardware-counter diagnostic rather than replacement MoE timing.

## RL traces and NCU follow-up

The same independent verification subsequently passed all four RL traces,
bringing coverage to 160 replay ranges across eight reports. See
`artifacts/nsys-independent-audit-eight.json`. RL W4A16 mean spans are
114.262 us at n32 and 326.137 us at n4096; TRTLLM BF16 spans are 284.682 and
528.484 us. W4A16 uncovered gaps remain below 0.4 us; TRTLLM BF16 has none.
RL W4A16 uses eight kernels, replacing the inference output memset with a
separate unpermute kernel. Its interval overlaps are 16.211 and 23.639 us;
the same union-of-intervals calculation handles them correctly.

Two NCU probes at n32 subsequently completed, each capturing exactly two
GEMMs with the six requested metrics. The first parse attempt expected
long-form CSV, while this installed NCU's raw page uses wide CSV with a units
row. The parser was corrected and the existing successful capture was reused;
no profile was discarded or silently rerun for that parsing issue.

| Backend | Stage | DRAM read bytes | DRAM write bytes | DRAM throughput % | Duration ns | SM throughput % | Tensor-pipe active % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CuteDSL W4A16 | FC1 + SwiGLU | 366118400 | 3186944 | 66.32 | 72640 | 51.72 | 48.40 |
| CuteDSL W4A16 | FC2 | 179254784 | 3090432 | 38.08 | 62432 | 49.57 | 27.42 |
| TRTLLM BF16 | FC1 + SwiGLU | 1233753344 | 3744000 | 91.43 | 176448 | 25.41 | 2.42 |
| TRTLLM BF16 | FC2 | 616780544 | 3596288 | 87.31 | 92640 | 24.19 | 2.30 |

These counters strongly support a memory-bandwidth bottleneck for the
profiled native BF16 GEMMs: high DRAM throughput and very low tensor-pipe
activity. BF16 reads 1.851 GB across the two GEMMs versus W4A16's 0.545 GB,
about 3.39x more traffic. This is compatible with compression saving enough
weight traffic to overcome W4A16's online decoding work.

**Tactic caveat:** NCU instrumentation caused the independent tuning runs to
choose different launch configurations from the original Nsight traces. CuTe
uses the same generated function names but different grids (FC1 32x35 versus
32x60, FC2 1x1x148 versus 2x1x74). Native BF16 selected tile-8 kernels versus
the original trace's tile-16 pair. All four comparisons are explicitly marked
false in `artifacts/ncu-investigation/gemm-summary.json`; the complete names,
grids and block dimensions for both tools are preserved. Therefore the NCU
numbers are independent kernel diagnostics, not an exact-tactic decomposition
of the Nsight spans or replacement latency measurements. Node replay also
isolates the GEMMs and controls each node's cache; it does not preserve PDL
overlap. No permission or profiling-support failure occurred.
