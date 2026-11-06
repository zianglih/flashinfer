# FC2 K/depth diagnostic (not a retained source policy)

The previous rejected K256 trial coupled shorter MMA/TMA tiles with maximum buffering (NV nine stages). This diagnostic separately evaluates the shallowest real shared-memory allocation that prohibits two same-kernel CTAs per SM, one additional operand stage, and maximum capacity. It uses the existing explicit private `k_steps`/`num_stages` controls in a task-local precompile wrapper; no production source or API changes. The original narrow EVICT_FIRST policy is held fixed.

- Source: clean `0c1e00fc3e4f913c8c241796c70a29673737c542`, independent local `flashinfer-fc2-kstage-review/`, remote `fc2-kstage-r1/`. Production advanced independently to retained mixed-FC1 overlap; this diagnostic intentionally freezes the earlier identical FC2 baseline and makes no final retention claim.
- Hardware: C2 `fi-v41-gap-c2-1025`, B300 GPU5, CUDA13.2/PyTorch26.05, CuTe4.7.1, arch10.3a.
- Occupancy bound uses the actual queried physical SMEM (233472 bytes); the per-block architecture helper returns232448 bytes. Enumerate real CuTe operand/SharedStorage layouts and choose the first depth with `2 * actual_storage > physical_smem_per_sm`, then validate actual driver occupancy. No token, expert, model, or reduction-size threshold is introduced.
- Gate:48 exact cases across NVFP4/MXFP8/MXFP4×MXFP8, reductions2048/2304/384, valid/padded/zero routes. All compiled kernels report one active block/SM and zero local bytes. Three fullmodel dimension cases are also captured during native timing, so small exact-gate resource values are not substituted for measured specialization resources.
- Timing: unchanged native `bench_moe_deepseek.py`, fixed N16/M128 for both phases, native PDL, unfused finalize,10warmups/100cold-L2 CUDA-graph/CUPTI. V41 T32/128/512, same GPU, C/min/+1/max/max/+1/min/C. FreshB300 exact route identities and cache selections checked; original13 tactics retained. W4A16 output from the shared NV backend selector is preserved as an unaffected control and excluded from the changed-backend decision.
- Files: source receipt, actual layouts, gate source/pins, raw commands and resources in `evidence/fc2-kstage-r1/`; native timing in `evidence/fc2-kstage-r1-fixed/`.

## Actual N16 gate resources

| Activation/weight bits | Policy | K tile | Stages | SMEM bytes | Regs | Local bytes | Active blocks/SM |
|---|---|---:|---:|---:|---:|---:|---:|
| 4/4 | control | 512 | 4 | 197504 | 86 | 0 | 1 |
| 4/4 | min | 256 | 5 | 123776 | 84 | 0 | 1 |
| 4/4 | plus1 | 256 | 6 | 148352 | 84 | 0 | 1 |
| 4/4 | max | 256 | 9 | 222208 | 84 | 0 | 1 |
| 8/8 | control | 256 | 5 | 215936 | 86 | 0 | 1 |
| 8/8 | min | 128 | 6 | 129920 | 84 | 0 | 1 |
| 8/8 | plus1 | 128 | 7 | 151552 | 84 | 0 | 1 |
| 8/8 | max | 128 | 10 | 216064 | 84 | 0 | 1 |
| 8/4 | control | 256 | 5 | 215936 | 86 | 0 | 1 |
| 8/4 | min | 128 | 6 | 129920 | 84 | 0 | 1 |
| 8/4 | plus1 | 128 | 7 | 151552 | 84 | 0 | 1 |
| 8/4 | max | 128 | 10 | 216064 | 84 | 0 | 1 |

## Outcome: reject a general K/depth policy

The repeated V41 fixed-N16 screen is complete. Geometric means across T32/128/512:

| Backend | Minimum occupancy depth | One extra stage | Maximum capacity |
|---|---:|---:|---:|
| NVFP4 | 1.002574× | 1.002326× | 0.983074× |
| MXFP8 | 1.006763× | 1.001613× | 0.990904× |
| MXFP4×MXFP8 | 0.963959× | 0.982355× | 0.996646× |

Minimum buffering removes the prior maximum-depth penalty, but its homogeneous gains are too small to justify a new general policy; mixed precision consistently regresses. NV T32 improves0.89%, while NV T128/512 are neutral; MX8 minimum-depth gains0.48–0.87%; mixed minimum-depth loses3.34–3.77%. All route/source/tactic checks pass, C1/C2 changed-backend drift stays below0.07%, and full-specialization driver resources retain one CTA/SM with zero local bytes (NV90→86regs; MX/mixed90→86regs). Do not promote this diagnostic wrapper or hardcode its resulting counts. No full V3/AUTO sweep is warranted for this rejected universal change.

Complete paired medians and unaffected W4A16 controls are in `evidence/fc2-kstage-r1-fixed/summary.md`; raw results, exact commands, GPU snapshots and observed compile resources are preserved in `raw/`. The two generated compiler output files are moved with SHA verification into the evidence directory after completion, leaving the remote source clean. This is source0c diagnostic evidence; retained mixed-FC1 overlap and concurrent FC2 bulk-store/CLC work remain independent.
