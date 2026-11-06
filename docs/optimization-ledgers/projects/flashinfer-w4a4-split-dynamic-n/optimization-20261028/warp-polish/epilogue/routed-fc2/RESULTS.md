# Routed FC2 scratch: rejected

Control is retained `cb35c42f6143aa08546ee1c6c8d6e6913c6cf03f` (b45b kernel), measured remotely as original99f4 plus combined patch. Candidate is that same source plus `layout-only.patch`, kernel92f89b. Source receipts and complete raw evidence are retained alongside this note.

The public frozen-winner C-A-A-C screen covered all four model shapes, four quantization modes, and tokens4/64/4096/16384, with10 warmups and100 cold-L2 CUPTI graph samples per arm. NV includes input quantization. No external baseline was rerun. All64 cells completed with identical frozen winners, routing, source identity, sample counts, and timer checks.

The overall geometric speed change is−0.292%; token4 is−0.867%, token64−0.200%, token4096−0.047%, token16384−0.051%. Last50 samples are a diagnostic only (overall−0.319%); published timing remains all100-sample medians. Stable decode regressions and increased allocation outweigh the isolated N3U MX4096 improvements. Large16K MX medians are bimodal and do not justify retention.

| Model | Tokens | W4A4 | PER-TOKEN | MXFP4x8 | MXFP8 |
| --- | ---: | ---: | ---: | ---: | ---: |
| v3 | 4 | -0.238% | -0.394% | -0.188% | -0.186% |
| v3 | 64 | +0.037% | -0.159% | +0.024% | +0.091% |
| v3 | 4096 | -0.404% | +0.158% | -0.572% | -0.829% |
| v3 | 16384 | +0.140% | -0.948% | -2.759% | +0.421% |
| v41-flash | 4 | -0.743% | -1.196% | -1.129% | -0.494% |
| v41-flash | 64 | -0.150% | -0.139% | -0.144% | -0.087% |
| v41-flash | 4096 | +0.057% | -0.150% | -0.038% | +0.031% |
| v41-flash | 16384 | +0.498% | +0.268% | +0.473% | -0.116% |
| kimi-k3 | 4 | -1.646% | -1.686% | -1.598% | -0.896% |
| kimi-k3 | 64 | -0.165% | -0.173% | -0.227% | -0.033% |
| kimi-k3 | 4096 | +0.017% | -0.236% | -0.061% | -0.121% |
| kimi-k3 | 16384 | -0.025% | -1.007% | -0.054% | +0.713% |
| nemo3-ultra | 4 | -0.392% | -1.174% | -1.133% | -0.760% |
| nemo3-ultra | 64 | -0.411% | -0.218% | -1.098% | -0.349% |
| nemo3-ultra | 4096 | -0.144% | -0.103% | +1.004% | +0.652% |
| nemo3-ultra | 16384 | +0.224% | +0.128% | +3.066% | -1.727% |

The exact graph gate passed96 candidate plus96 control graph executions (96 cross-source comparisons) across static/CLC and PDLoff/on with changed routing.48 core kernel pairs had unchanged stage/launch geometry and no local/stack spills. FC1 codegen was identical; FC2 lost2–39 instructions and0–2 shuffles.

The combine penalty is intrinsic to dynamic per-slot row addresses: N3U H2048/topk22 adds139–143 static SASS instructions, despite unchanged payload loads/stores. PTX already calculates each slot row base once, with its second vector using the same base plus2048 bytes; an explicit source-level row-base hoist would not avoid repeated work across different slots. The expanded layout instead computes one token base and uses immediate slot offsets. V3 H7168/topk8 similarly adds21 instructions and6 registers.

Worst-case scratch allocation also increases: tokens*top_k <= local_experts uses tokens*top_k*route_tile capacity, yielding16–256x decode allocation growth. The T4/topk8/local32/N16/H7168 example is512 vs32 BF16 rows (7MiB vs0.44MiB). This does not change live bytes and is not a traffic-elimination optimization.

Standalone layout is rejected. Preserve expanded-layout addressing/allocation/combine and explore grouped TMA scatter stores separately.
