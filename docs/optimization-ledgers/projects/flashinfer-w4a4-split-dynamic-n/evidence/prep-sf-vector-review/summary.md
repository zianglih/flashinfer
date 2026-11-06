# SF source vectorization: rejected

All three actual-routing preparation phases regress in both orders. No primary
campaign or production integration is warranted. The actual experimental copy
remains unstaged; the regular-TMA control, native cache and previous evidence
remain unchanged.

| Case | Control medians, µs | Vector medians, µs | Control/vector |
|---|---|---|---:|
| NVFP4 8K, N128 | 15.968 / 15.9675 / 15.984 | 16.544 / 16.5285 / 16.544 | 0.965798× |
| NVFP4 16K, N256 | 29.616 / 29.632 / 29.744 | 30.816 / 30.864 / 30.800 | 0.962282× |
| MXFP8 16K, N256 | 42.528 / 42.3845 / 42.3685 | 43.248 / 43.312 / 43.1365 | 0.981376× |

Each case runs ABA then BAB, with10 warmups and100 cold-L2 CUDA-graph CUPTI
samples per arm. All18 arms/1800 individual samples are retained and their
medians recomputed. Ratios divide the geometric means of the three control and
three vector medians. These are preparation-only timings, not whole-MoE results.

The generic static policy chooses complete Uint32 widths1/2/4/8 by estimated
warp memory-instruction count. CPU checks cover512 block extents with exact
destination partitioning. GPU checks pass75 byte/canary graph cases and32
alignment cases. Whole prepared payload and SF allocations also match the
control for all three timed native-routing cases.

SASS confirms actual SF instructions:

- NVFP4 measured paths use `LDG.E.128`, followed by four32-bit scattered stores.
- MXFP8 measured path uses `LDG.E.64`, followed by two32-bit scattered stores.
- The compile-only width8 example uses `LDG.E.ENL2.256` at0x05e0, followed by
  eight scattered stores at0x0630–0x06a0. Its kernel was not timed or launched
  by the inspection helper; the width8 byte path is covered by the exact probe.
- Payload LDG/STG256 is unchanged. Resource counts are30 registers/thread for
  NV8K and32 for the other timed cases, identical to controls;16 resident
  128-thread CTAs/SM, zero static SMEM and zero local-memory bytes. No LDL/STL
  spill instructions appear in the saved SASS.

The store layout and total memory traffic are unchanged. The new SF mapping
uses fewer active warps and more serial stores per thread. This is consistent
with the regression despite fewer estimated warp instructions, but no NCU
causal claim is made. The stronger8/16/32-byte source alignment checks would
also narrow the cleaned prep API's previous4-byte allowance; that contract
delta is not justified by these negative results.

Candidate prep SHA256:
`19d29ab7dd421064c5de3d4d0858f8a9dd831cf07c91811fb6b32f0980ebe0f0`.
Control prep SHA256:
`ec2c70b178f828b769ab7d63128996bed8535f23f099591e1a5c046392bc292c`.
Archive SHA256:
`d3cbf935c61b3a44d8bcab2eec8ff97b268b40dead59bb6011716c7d5daa96d7`.

The archive includes source snapshots, all samples, native routing metadata,
exact checks, PTX/SASS/cubins, resources, commands and hash manifests.
