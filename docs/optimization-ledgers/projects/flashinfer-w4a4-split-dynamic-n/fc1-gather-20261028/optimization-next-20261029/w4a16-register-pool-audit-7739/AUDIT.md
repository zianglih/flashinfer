# Five-warpgroup W4 register pool

**Conclusion:** there is no supported way found to add the SM's remaining 4,096 registers to this 640-thread CTA while retaining its launch geometry. The current 96-register launch already reaches the maximum admissible uniform per-thread allocation. `setmaxnreg` can redistribute that CTA allocation, not borrow the unused SM remainder. No quota experiment or GPU workload was launched.

## Allocation proof

At retained `77391e28d12a01e371196e76e56d4b46ace122df`, Gather4 FC1 launches 640 threads and uses `--ptxas-options='-maxrregcount=96'`. Five warpgroup targets are epilogue144, control80, dequant96, dequant96 and gather64. Their sum is `128*(144+80+96+96+64) = 61,440`. The control/gather groups donate exactly 6,144 registers and epilogue receives 6,144; nothing remains in this CTA's pool.

The unmodified installed CUDA 13.2 header was fetched read-only from `/usr/local/cuda-13.2/targets/x86_64-linux/include/cuda_occupancy.h`, SHA256 `4c8d0f75a5bb1b266a77b50373b67b2959eb3bb4120a691c8a1a0e8d4e91b872`. Its register allocator uses 256-register units per warp and four SM subpartitions for compute major10. It rounds each warp before multiplying by the 20 CTA warps and checks the per-CTA/per-subpartition limits. See local header lines680–734 and1482–1597.

`occupancy_cpu.cpp` invokes the header's register-limit function with SM103, 65,536 registers per SM/block, warp32 and CTA640. It is a local CPU executable with no CUDA runtime/context or GPU launch. Full output is in `occupancy_cpu.txt`:

| Requested registers/thread | Registers/warp after rounding | CTA registers | Register-limited CTAs/SM |
|---:|---:|---:|---:|
| 96 | 3,072 | 61,440 | 1 |
| 97–104 | 3,328 | 66,560 | 0 |
| 112 | 3,584 | 71,680 | 0 |

The same boundary appears per SM subpartition: five resident warps need `5*3,072=15,360` of16,384 registers, leaving1,024. Raising the uniform allocation by eight registers/thread requires `5*256=1,280`, exceeding that remainder. Using an apparent average such as100 or102 does not bypass warp allocation rounding.

## Dynamic redistribution does not enlarge the pool

The [official PTX setmaxnreg contract](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#miscellaneous-instructions-setmaxnreg) places donated/requested registers in a CTA-local pool. An increase waits for that pool; it is not a request for additional SM capacity. Targets are multiples of eight and all warps of a warpgroup must execute the same redistribution instruction. An idle individual control warp therefore cannot independently donate registers without changing the current role/warpgroup contract.

The [Blackwell tuning guide](https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html#occupancy) documents the64K register file. These limits apply even when only one CTA is intended to occupy an SM. Two-CTA MMA does not pool general registers across CTAs/SMs.

Phase-specific donation could still redistribute the existing61,440 registers, but it would require a new demonstrated lifetime/overlap mechanism. It would not consume the4,096-register SM remainder. No such new mechanism is proposed here; previously rejected general quota redistributions remain closed.

## Current source and MegaMoE comparison

All source hashes are in `source-receipt.json`.

- Split W4 constructor/roles: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:353–371`; control donation near1507, epilogue acquisition near2147, gather donation near2755. The dequant groups keep the96 launch allocation.
- Split W4 compiler cap: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py:204`.
- Existing MegaMoE W4: `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1248–1250`,1461–1462,1485–1486,1535–1537 explicitly uses the same144/80/96/96/64 sum and640 threads.
- MegaMoE W4 compiler cap: `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py:374` also uses96.

This is a source/header allocation proof, not a fresh launch or performance result. The CPU calculation isolates the register limit; it does not assert overall occupancy after shared memory, barriers or cluster constraints. The failed first host build lacked `<initializer_list>` and was corrected before the successful run; production source was untouched.
