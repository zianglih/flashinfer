# K3 preset and public API audit

K3 copies the existing distributed benchmark's routed latent core: H3584, I3072, E896, topK16, SiTU(4,25), EP8/112 local experts. CPU FP32 sigmoid scores plus bias determine stable topK selection; selected unbiased scores are normalized by their sum+1e-20. Routing is shared and excluded from timing. This single-GPU benchmark retains its existing seed42 input-generation methodology; it is not a distributed communication benchmark.

The public CuTe function/wrapper already supports all five benchmark arms. TRTLLM FP4 supports NVFP4, per-token NVFP4, and MXFP4x8 SiTU with explicit local-expert FP32 alpha4/beta25 tensors and activation enum10. TRTLLM homogeneous MXFP8 and BF16 do not support this SiTU contract. CUTLASS is outside this benchmark extension; the K3 explicit arm is skipped rather than changed. No production kernel/API edits are required.

- `check_old_model_reuse.py`: executes all52 old V3/V4.1 CPU dispatch cases with identical input/histogram/backend argument traces, checks exact timer forwarding, and proves10 full API/routing AST equivalences after explicit static model specialization. Actual input creation, timing, and other helpers remain AST-identical. The explicit EP8/EP4 calls preserve measured behavior even though the V3 CLI default changed earlier.
- `probe_routes_cpu.py`: real Torch CPU equality for all13 K3 route shapes against the distributed implementation and all13 V4.1 routes against measured c5; lower-ID ties/cache identity/no-op timed routing; V3 native router call-binding stub. No CUDA initialized.
- `probe_public_benchmark.py`: bounded K3 T4 default-family smoke with public API interception. Checks actual SiTU scalars, TRT per-expert tensors/routed FP32 weights, per-token recipe isolation, finite outputs, and supported arm sets. Its observed timings are not the final performance evidence.
- `launch_gpu_gate.py`, `fetch_gate.py`: exact clean-source GPU5 run and read-only result retrieval. Preserve all85 source hashes before/after and raw stdout/stderr.

Evidence lives under `evidence/k3-public-audit-r1` and `evidence/k3-public-gate-r1`. Full K3 table launchers/observers are separately owned under `scripts/k3_model_tables`; original V3/V4.1 table data are immutable and reused through the source-bound equivalence proof.
