# W4A16 MegaMoE: native IKET register and pipeline tracing

Current HashInfer source `accf82dae0b703cb0276839dd53d3b17eb21f936`, package+fixture SHA `ef7dfe1c029f146a3051437446fb78655bc2cd4e30419869616638faf2819d9d`. Merged via PR13 [private repository link omitted] as `a4b2d9a690e302deb0feac8b7cc872ab0b31a766`; merged tree equals this tested source. [Deployment-integration reference omitted from this kernel archive.]

Three new ranges expose initial register donation/acquisition on every participating warp. Existing payloads are retained. Removing the six new marker lines restores the parent kernel bytes exactly; register policy, synchronization and computation are unchanged.

| Global tokens | Winner | Hot tuning score µs | Selected rank | Worst initial sync µs | Complete trace |
|---:|---|---:|---:|---:|---|
| 128 | N64/G512/epi_warps | 268.608004 | 1 | 8.160 | [Perfetto](optimization/register-reallocation-20260926/audit-v2-128/selected-min-sync-rank1.pftrace) |
| 4096 | N128/G1024/reuse_dispatch_warps | 585.856020 | 3 | 10.944 | [Perfetto](optimization/register-reallocation-20260926/audit-v2-4096/selected-min-sync-rank3.pftrace) |

Both fresh eight-candidate AUTO sweeps and all eight native rank captures pass independent-reference/baseline/capture finite BF16 bit checks, original source/config/PID/CUBIN/PMTRIG binding, dynamic event IDs, ranges/payload ordering, and own-Perfetto nanosecond agreement. Each rank has24 register ranges on WG0/1/2; WG3/4 retain96 registers without redistribution.

Selected ranks minimize the maximum initial count-exchange/sync duration across their eight recorded WG2 tracks. Complete traces are copied unchanged; no cropping or cross-GPU clock alignment. Full148CTA/74CGA launch; recording filters one two-CTA cluster. Scores are uninstrumented hot tactic-selection scores, not end-to-end speedups. Register ranges include profiler overhead.

- [Current runbook](optimization/register-reallocation-20260926/README.md)
- [128-token detailed results](optimization/register-reallocation-20260926/summary-128.md)
- [4096-token detailed results](optimization/register-reallocation-20260926/summary-4096.md)
- [Local experiment ledger](optimization/EXPERIMENTS.md)
- [Prior transport-phase capture records](optimization/transport-phases-20260927/README.md)

C2/infra devbox `fi-w4a16-align256-r2-0926` on `hu-pdx-43` remains allocated. Image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe/IKET4.8.0, four B300 GPUs. Traces and disassembly remain outside both source repositories. The six register-marker lines are synced to FlashInfer PR5019 at `acbc0b1f389d34dbeea6b33e64eebfdcc54a0119`; focused upstream validation passed (18 logical tests / 42 rank executions and four-rank native IKET smoke, with 24 register ranges per rank). Private transport changes remain HashInfer-only.
