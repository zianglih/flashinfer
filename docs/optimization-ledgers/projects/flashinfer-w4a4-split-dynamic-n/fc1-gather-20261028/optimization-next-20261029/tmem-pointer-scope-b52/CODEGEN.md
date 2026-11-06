# Role-local TMEM pointer: compile-only qualification

Source: b52 + `06c882e4` (3 added / 2 removed lines). All 514 source hashes and 117 fetched artifact hashes verified. GPU0, original strict resource guard; zero owned MoE launches.

The allocation result remains in its immutable shared slot after the unchanged allocation wait. MMA and epilogue retrieve it only inside their existing roles; allocator warp0 reloads it at the unchanged final free. Allocation, every wait/barrier/release, final join, and two-CTA deallocation are unchanged. This is distinct from the rejected allocator/rendezvous reduction.

| Capture | Phase | Static instructions delta | Branch delta | REG before/after | STACK before/after | LDL/STL before/after |
|---|---|---:|---:|---|---|---|
| matrix:0 | FC1 | -3 | +0 | 168/168 | 0/0 | 0,0/0,0 |
| matrix:1 | FC2 | -91 | +0 | 100/100 | 0/0 | 0,0/0,0 |
| matrix:2 | FC1 | -9 | +0 | 168/168 | 0/0 | 0,0/0,0 |
| matrix:3 | FC2 | +4 | +0 | 125/123 | 0/0 | 0,0/0,0 |
| matrix:4 | FC1 | +6 | +0 | 168/168 | 0/0 | 0,0/0,0 |
| matrix:5 | FC2 | -3 | +0 | 80/80 | 0/0 | 0,0/0,0 |
| matrix:6 | FC1 | +4 | +0 | 168/168 | 0/0 | 0,0/0,0 |
| matrix:7 | FC2 | -82 | +0 | 108/108 | 0/0 | 0,0/0,0 |
| matrix:8 | FC1 | +21 | +0 | 168/168 | 128/128 | 16,16/16,16 |
| matrix:9 | FC2 | -80 | +0 | 152/152 | 0/0 | 0,0/0,0 |
| matrix:10 | FC1 | +21 | +0 | 168/168 | 128/128 | 16,16/16,16 |
| matrix:11 | FC2 | -80 | +0 | 152/152 | 0/0 | 0,0/0,0 |
| native-0:0 | FC1 | -21 | +0 | 168/168 | 0/0 | 0,0/0,0 |
| native-0:1 | FC2 | +4 | +0 | 106/106 | 0/0 | 0,0/0,0 |
| native-1:0 | FC1 | -9 | +0 | 168/168 | 0/0 | 0,0/0,0 |
| native-1:1 | FC2 | +1 | +0 | 105/105 | 0/0 | 0,0/0,0 |

All 16 captured configurations preserve actual geometry, shared storage, role quotas and hardware synchronization/TMA/MMA instruction counts. Four matrix FC2 configurations remove 80–91 static instructions; other FC2 deltas are −3 to +4. These are code-size counts, not dynamic timing gains.

Native FC1 N3U EP MXFP8 removes 21 instructions and five uniform fill/spill pairs; K3 EP per-token removes nine and six pairs. The two inherited M512/K8 MX stress kernels keep 128B stack and 16 LDL / 16 STL sites, but add six uniform fill/spill pairs and 21 instructions. The candidate is therefore a mixed generated-code change, not a general spill fix. All previously clean captures remain zero-local.

Three role-local LDS replace one common LDS (+2 static sites). There is no new branch or synchronization operation. Retrieval is outside work-tile/K loops; normal memory/math/quantization and accumulators are unchanged by AST proof.

Numerical coverage completed as 40 original passes plus one whole final-case rerun. The original final FC2 capture failed REG82→83, while STACK/LOCAL/LDL/STL remained zero; CUDA13.2 occupancy calculation and current device attributes prove both reserve22528 physical registers/CTA and unchanged215936B dynamic shared limits occupancy to oneCTA/SM. The isolated rerun uses exact source/PTX/CUBIN and this physical-allocation expectation; original failure is preserved. It is not a single unbroken41-case run. No performance or retention claim yet.
