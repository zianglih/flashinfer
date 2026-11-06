# Coordinate-cache bank placement: read-only verdict

**Hold; padding is not justified by current evidence.** `p|1` has a coherent address-spreading effect, but neither native instruction inspection nor the full56 timing screen establishes cross-warp bank contention. It does not remove coordinate loads, their dependent uniform-register transfers/TMA issue, or either required warp synchronization. No source, cache, compile or GPU change was made; candidate remains `15d6eb18`.

The source at `flashinfer-sf-coordinate-cache-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:3452` uses `p=ceil(b_copy_rows/16)` packets per warp and stride `4*p` Int32 words. Ignoring a common base-bank rotation, packet `j` touches banks `(4*(warp*p+j)+[0,1,2,3]) mod32`. The actual wide native capture has one elected lane loading each aligned packet with `LDS.128` inside K. Its four words use distinct banks; unique contiguous publication writers likewise do not create an intra-warp conflict. [CUDA's bank-conflict contract](https://docs.nvidia.com/cuda/archive/13.2.1/cuda-c-best-practices-guide/index.html#shared-memory-and-memory-banks) concerns addresses requested within a warp. Different warps targeting the same banks is a possible shared-service issue, not an established four-way conflict in each instruction.

Normalized first-packet start banks for the four warps are:

| p | Current | With p\|1 |
|---:|---|---|
| 1 | 0,4,8,12 | unchanged |
| 2 | 0,8,16,24 | 0,12,24,4 |
| 4 | 0,16,0,16 | 0,20,8,28 |
| 8 or16 | 0,0,0,0 | 0,4,8,12 |

Only the p≥4 cases remove repeated packet-bank sets at the same logical issue position. Actual warp progress need not be synchronized there, and successive packets already rotate the bank set. Padding preserves16-byte alignment, but adds no per-request bank-conflict improvement. It leaves the wide32 packet loads/warp/K stage (2KiB logical shared reads/CTA/stage) unchanged. The warp-base multiplier also becomes odd; native address-generation cost is unmeasured. [Nsight's guidance](https://docs.nvidia.com/nsight-compute/ComputeTriage/) distinguishes source-instruction conflicts from cross-client shared/L1 contention and warns that scoreboard stalls alone do not establish bank conflicts. No candidate coordinate-PC wavefront/service measurement exists here; old retained-kernel profiles predate this scratch.

The CPU-only [planner replay](sf-coordinate-bank-padding.json), using actual candidate planner methods and all364 frozen FC1 records, predicts:

- p=1:241 cells,64→64B; p=2:40 cells,128→192B; p=4:43 cells,256→320B; p=8:36 cells,512→576B; p=16:4 cells,1024→1088B.
- Raw growth0B for241 cells and64B for123. Rounded metadata growth0B for300 and128B for64.
- No frozen stage/accumulator-overlap changes or automatic-K changes; minimum prospective planner slack640B. These are planner predictions, not new compiled struct sizes or a guarantee for arbitrary explicit depths.

Bounded searches of both CLOSED_LEADS indices found no exact odd-packet warp-stride trial. Library precedents address different access contracts: CUTLASS `examples/python/CuTeDSL/ampere/sgemm.py:127` pads matrix rows for conflict avoidance; FlashInfer `include/flashinfer/mamba/kernel_checkpointing_ssu_8bit.cuh:87` uses a16B row pad to separate several lanes' transpose stores while preserving LDS128 alignment. Neither demonstrates throughput improvement for four independent single-lane packet requests. The new56 screen remains the primary composition result; padding is not a basis for a rescue variant without distinct native service evidence.

The independently replayed primary56 screen has opposite normal-clock N3U W4A4 T16384 outcomes: EP p4 gains4.7487%, while TP p16 loses4.6876%. Both use SF_G4, but their topology/work geometry and new coordinate dependency volume differ. This supports the held paired FC1 diagnosis; it does not isolate a bank-placement cause or justify padding as a rescue. The rejected source and all caches remain unchanged for that diagnostic.
