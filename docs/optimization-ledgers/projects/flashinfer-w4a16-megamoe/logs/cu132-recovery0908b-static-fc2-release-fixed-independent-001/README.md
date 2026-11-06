# Static FC2 plus safe release: fixed13 comparison

All 78 raw latencies below are independently matched to original stdout; 312 split selections and 312 compiled observations remain in the per-run JSONs. Latencies are milliseconds. The static candidate is source 28a, base512 is e2d88, and C1 is 250553. Negative change means faster.

| Tokens | C1 split | C1 Mega | Base512 split | Base512 Mega | Static512 split | Static512 Mega | Mega vs base512 | Split vs base512 | Changed split ranks | Mega vs C1 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 1 | 0.075681 | 0.081633 | 0.071072 | 0.092592 | 0.084256 | 0.091920 | -0.73% | +18.55% | [] | +12.60% |
| 2 | 0.101712 | 0.118193 | 0.100160 | 0.114081 | 0.116752 | 0.117217 | +2.75% | +16.57% | [] | -0.83% |
| 4 | 0.137649 | 0.137361 | 0.136753 | 0.136817 | 0.127202 | 0.130529 | -4.60% | -6.98% | [] | -4.97% |
| 8 | 0.160449 | 0.161793 | 0.162481 | 0.153680 | 0.147921 | 0.151761 | -1.25% | -8.96% | [] | -6.20% |
| 16 | 0.179874 | 0.181265 | 0.179600 | 0.177713 | 0.179538 | 0.174418 | -1.85% | -0.03% | [4] | -3.78% |
| 32 | 0.204978 | 0.210705 | 0.193681 | 0.206721 | 0.203538 | 0.199553 | -3.47% | +5.09% | [0, 6] | -5.29% |
| 64 | 0.222801 | 0.235954 | 0.224113 | 0.238049 | 0.222674 | 0.230210 | -3.29% | -0.64% | [0, 6] | -2.43% |
| 128 | 0.234961 | 0.242594 | 0.233298 | 0.241522 | 0.233505 | 0.240289 | -0.51% | +0.09% | [2, 6] | -0.95% |
| 256 | 0.241905 | 0.250626 | 0.243202 | 0.232289 | 0.243922 | 0.238305 | +2.59% | +0.30% | [5] | -4.92% |
| 512 | 0.241041 | 0.251922 | 0.240208 | 0.258113 | 0.239042 | 0.246434 | -4.52% | -0.49% | [3, 4, 5, 6] | -2.18% |
| 1024 | 0.262401 | 0.268962 | 0.262769 | 0.268786 | 0.261122 | 0.267985 | -0.30% | -0.63% | [0, 6] | -0.36% |
| 2048 | 0.355106 | 0.336435 | 0.350914 | 0.338337 | 0.351475 | 0.342035 | +1.09% | +0.16% | [0, 2, 5] | +1.66% |
| 4096 | 0.555268 | 0.522484 | 0.552515 | 0.526691 | 0.552262 | 0.531972 | +1.00% | -0.05% | [] | +1.82% |

Against base512, the static/release fixed arm is faster at 9/13 points (largest 4.60% at T4), and slower at 4/13 (largest 2.75% at T2). T32/64/512 improve 3.47%/3.29%/4.52%; T256/4096 slow 2.59%/1.00%. This is a mixed, modest shift in one sweep; it does not support a broad performance claim.

The high-token paired split is nearly unchanged at 4096 (-0.05%) while Mega is 1.00% slower. At tiny tokens, split movement is much larger (T1 +18.55%, T2 +16.57%, T4 -6.98%, T8 -8.96%), which argues for restraint when interpreting their unbracketed differences.

- Complete fixed CONTROL sweeps only. Current auto arm is excluded; no row minimum or cross-arm winner substitution.
- All three sweeps use the same explicit actual M256/N128/K256,C2,F4,epi_warps/group512/atomic/epi(2,4) configuration and original 100-iteration CUPTI graph/cold-L2 benchmark. Two transform groups remain fixed.
- The source difference e2d88 to 28a is exactly the private epilogue: static FC2 subtile specialization plus safe post-reorder last-subtile release. This sweep cannot attribute the combined effect to either change separately.
- Runs are sequential unbracketed sweeps on the replacement CUDA 13.2 stack. Recorded image/node/native identities match; matched metadata and source do not establish a causal noise-free A/B. Split retunes per process, and its variation is contextual, not a statistical error bar or a correction factor.
- Actual 512-thread resource records show 112 to 0 local bytes at all 104 fixed compiled observations; unchanged 128 registers/512 threads/2 groups/pool 65,536. This is resource evidence, not proof that removed local accesses caused a latency change. C1 historical compiled records did not include the actual CUDA resource query.
- Source/helper and imported native/preflight guards pass; this fixed-only audit does not claim a new contemporaneous loaded-library map for the static arm. Native-cache inventories are before-only, not immutability proof.
