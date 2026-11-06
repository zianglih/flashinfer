# Exact B300 V4.1 TRT FC2 inspection

Clean CuTe control: `0c1e00fc3e4f913c8c241796c70a29673737c542`. Native TRT artifact revision is pinned in every copied cubin path and SHA256 receipt. All six selected TRT cases were read from completed Nsight graph-node traces; eleven unique FC1/FC2 cubins were copied without alteration. Disassembly and resource extraction use `cuobjdump` and perform no GPU work. `selected-cubins.json` binds every case/phase to the exact trace and binary hashes.

The separately archived PR2917 source export under `scripts/trtllm_gen_decode_audit/sources` is prior art, not source identity for these newer binaries. The findings below are from the selected binary and current CuTe source.

| Format | Tokens | TRT FC2 tile in selected name | Pipeline stages | CTA group |
|---|---:|---|---:|---:|
| NVFP4 | 32 | M128 N8 K256 | 6 | 1 |
| NVFP4 | 128 | M128 N8 K512 | 5 | 1 |
| NVFP4 | 512 | M128 N16 K256 | 6 | 1 |
| MXFP4×MXFP8 | 32 | M128 N8 K512 | 3 | 1 |
| MXFP4×MXFP8 | 128, 512 | M256 N16 K256 | 6 | 2 |

- All selected FC2 binaries use native `LDTM.16dp256bit` loads (`.x2` for the mixed two-CTA path) and `UTMASTG.4D` output stores. For example, NV T32 has loads at PC0x3860/0x3870 and stores at0x3be0/0x3c10; mixed T128 has loads at0x45a0/0x45b0 and stores at0x4880/0x48b0.
- Current CuTe `Sm100BlockScaledGroupedGemmKernel._configure_pipeline_storage` admits bulk output only when `route_tile >= 128`. The selected N16 FC2 therefore still executes the TMEM transpose/direct-store epilogue. A narrow bulk-output experiment directly tests a real implementation difference without reintroducing an activation-preparation stage. Root owns that experiment.
- The current TRT FC2 binaries use CLC (`UGETNEXTWORKID.SELFCAST` and `.BROADCAST`) with separate load/scale-copy/MMA/output roles. Current CuTe control FC2 uses static strided scheduling. Root/tests agent own the separate FC2 CLC experiment; its timing will decide whether the scheduling difference is useful.
- Actual SASS includes role-specific register repartition: NV control regions release to24 or72 registers and the epilogue allocates160; mixed control regions release to48 or72 and the epilogue allocates192. In the NV T32 binary, the warp-ID test at0x3130 selects warps0–3 for the allocation at0x3210; that region contains the native TMEM loads and TMA output stores. This is evidence of the binary's organization, not evidence that a full16-warp topology or register repartition would improve CuTe.
- CuTe narrow FC2 has288 threads and90 reported registers/thread with zero local bytes/thread in these traces. There is no measured spilling problem. Its197,504B NV /215,936B mixed shared-memory use excludes FC1/FC2 block co-residency on the233,472B SM, regardless of the lower register sum. TRT also fails adjacent FC1/FC2 SMEM co-residency for these cases; all measured inter-kernel overlaps can arise as different SMs drain.
- A universal K256 explanation is unsupported: TRT chooses K512 for NV T128 and mixed T32. Descriptor-only N8 and an earlier K512→K256 policy are already closed locally; the current evidence is not a reason to rerun those exact experiments.

Matched CuTe/TRT phase summaries are in `../v41-pipeline-profile-c2-{nv,mixed}-r1/summary.json`. Kernel lifetimes include PDL dependency waits; compare complete traces and separate native10/100 medians, not sums of kernel durations. The mixed overlap candidate T128 trace is in `../v41-pipeline-profile-c2-overlap-r1`: FC1 lifetime186.145→171.937µs, while inter-FC overlap9.024→6.976µs. The improvement is therefore consistent with reduced FC1 internal serialization, not merely more inter-kernel overlap.

The opcode inventories are static counts across the cubin's disassembled functions, including helper stubs; they are not executed instruction counts or occupancy measurements. All raw SASS/resource text is retained for narrower function-level inspection.
