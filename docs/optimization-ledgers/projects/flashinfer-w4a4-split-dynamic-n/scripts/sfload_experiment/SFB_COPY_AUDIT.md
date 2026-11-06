# Two-CTA SFB ownership audit

Source audit on 2026-10-24, followed by a parent-authorized profile of the frozen composed kernel. No kernel changes were made.

## Conclusion

Keep the full token extent of SFB in each CTA's shared memory. A group-2 `tcgen05.cp` transfers each CTA's own shared source into that CTA's tensor memory. Its `warpx2`/`warpx4` modifiers distribute data among tensor-memory warp groups; they do not select the leader CTA as a common shared-memory source. All `tcgen05` instructions with a CTA-group qualifier must use the same group, so a group-1 scale copy is not a supported substitute alongside group-2 MMA.

The existing CuTe `Cp4x32x128bOp(CtaGroup.TWO)` already selects `.32x128b.warpx4`. There is no omitted broadcast flag to enable. The official [PTX `tcgen05.cp` specification](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#tcgen05-instructions-tcgen05-cp) documents these source and broadcast semantics.

This does not require duplicated global reads. TMA multicast can populate both local SFB buffers before the unchanged S2T operation.

## MegaMoE source evidence

File: `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/kernel_fc12.py`.

- `_create_tiled_mmas` / `_setup_attributes`, lines 297–378: the data MMA uses group 2, while SFB gets a separate group-1 MMA partition. Its token dimension is rounded to 128; it is not divided like the B activation payload. The comment claiming SFB is not multicast across the pair is inconsistent with the actual TMA construction below.
- `_create_tma_atoms` / host TMA construction, lines 1069–1087: SFB uses `cluster_shape_to_tma_atom_SFB`, the separate SFB partition, and `internal_type=Uint16`.
- TMA-B warp, lines 1829–1847: SFB has its own multicast mask and CTA layout.
- Lines 1933–1944 and 1970–1977: `tma_partition` distributes the SFB request through that CTA layout and the copy uses `sfb_full_mcast_mask`.
- Lines 1146–1155: the same SFB TMA construction applies to the prepared FC1 output scales consumed by FC2.
- `mainloop_s2t_copy_and_partition`, lines 724–741: local SFB then uses `Cp4x32x128bOp(self.cta_group)`.

The installed CuTe DSL 4.7.1 helper `cutlass.utils.blackwell_helpers.cluster_shape_to_tma_atom_SFB` explicitly returns `CopyBulkTensorTileG2SMulticastOp(CtaGroup.TWO)` when the data MMA has two CTA participants. Its group-1 shape is therefore a partitioning choice, not an instruction disabling multicast. The installed `Cp4x32x128bOp` docstring explicitly identifies `.32x128b` with `.warpx4`.

## Applicability to this split kernel

The current split kernel's FC1 scale source is gathered, row-major input SF. FC2 reads already prepared blockscaled SF. Both currently use 4-byte cp.async copies into each CTA's full prepared SFB buffer.

- FC2 could use the Mega-style prepared-SF TMA partition and multicast. This would reduce duplicate global SF requests but retain both local buffers and their S2T operations. TMA expected-byte accounting and group-2 completion still need an isolated numerical/timing probe.
- FC1 cannot reuse the prepared-SF descriptor directly: row selection is arbitrary and the source layout differs. A 16-byte asynchronous row fetch into SF-only scratch followed by prepared-layout stores is a possible alternative. It adds scratch storage, shared loads/stores, and a transform-ready synchronization step. Transforming immediately in the producer after a blocking wait would lose the overlap being sought. No performance claim is made for this proposal.
- No change is needed to activation values, scale precision, route mapping, the MMA descriptor, or the epilogue arithmetic.

## Profile boundary

`sfload-ncu-twocta-fc1-01` profiles the earlier two-CTA overlap core with **cp.async B**, before the retained Gather4 composition. Its 60.614% LSU/L1 data throughput and 38.776% tensor activity are useful historical evidence, not proof that SF traffic dominates the composed core. The synchronous 16-byte SF register-load variants were slower and are archived in this directory. Read a current composed-core profile before implementing a further SF staging change.

## Composed Gather4 profile

The subsequent profile used immutable `two_cta_trial/combined_overlap_core.py` SHA256 `36bcef61277ad54957440d48d4cb5a89fe0d33d7add47c96f0bbdb96f5b2af82` with `integrated_utils.py` SHA256 `69dfd49f2e1bde42b93e1d2545e8d0e0d08bc60b2220885447b3dec9e82d2d5b`. C1 B200 GPU2, CUDA 13.2 image `nvcr.io/nvidia/pytorch:26.05-py3`, CuTe DSL 4.7.1; NVFP4 FC1, balanced 16,384 routes, 32 experts, M4096/K7168, N256, five stages, 148 CTAs. This is an NCU kernel profile, not a retention latency measurement.

| Counter | Value |
|---|---:|
| NCU kernel duration | 276.576 us |
| Tensor pipe active | 40.321% |
| TMEM active | 49.096% |
| LSU/L1 data pipe throughput | 68.974% |
| Tensor-core shared data pipe throughput | 23.941% |
| Registers per thread | 80 |
| Dynamic shared memory per CTA | 195,584 bytes |
| Local load/store sectors; explicit spill reads/writes | 0 / 0; 0 / 0 |

The eight SF `LDGSTS` PCs account for 58,720,256 of 61,263,156 source-attributed global L1 requests (95.8%) and 29,360,128 of 29,363,014 source-attributed shared wavefronts. These counters exclude TMA request traffic. Each SF copy instruction requests 32 distant 4-byte fragments per warp; NCU reports 16 shared wavefronts per active warp instruction and 51,380,224 excessive theoretical global sectors across the SF PCs. The source's destination-bank permutation remains unique across lanes, so this is **not** evidence of a new simple destination-bank collision. The fragmented global-to-shared requests remain expensive.

Long-scoreboard samples occur primarily at the epilogue accumulator-full wait (6,675) and producer empty-stage wait (3,570), which follow mainloop progress. The MMA-side local SF-completion wait has 536 samples, compared with 45 at peer relay-full and 23 at TMA-full. These support investigating SF transfer efficiency rather than treating cluster relay overhead as the primary cause. They do not establish a precise percentage of end-to-end time attributable to SF copies.

This profile supports a controlled asynchronous 16-byte SF-load experiment, with the original kernel as a same-GPU control. It does not yet justify production integration or added scratch/transform synchronization. No such experiment was launched during this audit.

Raw files: `../../logs/sfb-composed-nvfp4-n256-ncu-01-{raw,source}.csv`; remote `.ncu-rep` and `.log` share the same prefix. Reproduce from the remote `candidate` checkout:

```bash
CUDA_VISIBLE_DEVICES=2 PYTHONPATH=. TRTLLM_ENABLE_PDL=1 OMP_NUM_THREADS=1 \
timeout 180 ncu --target-processes all --profile-from-start off \
  --section LaunchStats --section Occupancy --section SourceCounters \
  --section SchedulerStats \
  --metrics sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed,sm__mem_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed,l1tex__data_pipe_tc_wavefronts.avg.pct_of_peak_sustained_elapsed,l1tex__data_pipe_lsu_wavefronts.avg.pct_of_peak_sustained_elapsed,l1tex__t_sectors_pipe_lsu_mem_local_op_ld.sum,l1tex__t_sectors_pipe_lsu_mem_local_op_st.sum \
  --csv -o ../logs/sfb-composed-nvfp4-n256-ncu-01 \
  ../.venv/bin/python ../transfer/two-cta-experiment/run_trial.py \
  --variant combined_overlap --script probe_perf.py --repo . \
  --mode nvfp4 --tokens 16384 --tiles 256 --factors 1 --stages 5 \
  --phases fc1 --profile
```
