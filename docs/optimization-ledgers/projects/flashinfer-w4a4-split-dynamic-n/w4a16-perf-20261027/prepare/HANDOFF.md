# Shared prepare handoff

Review copy: `flashinfer-w4a16-prepare-review` at1496b557; unstaged only. Full-index patch SHA256 `aa90f49c87e893664938ece40f1d0a04f941b9568e889a78714e914657a072fc`. Three production files,+113/−288(net−175). No test additions.

- `moe_prepare.py` handles byte-preserving payloads with optional SF buffers. BF16 selects zero SF columns at compile time; SF row padding/publication disappear.
- `moe_w4a16.py` calls the shared entry point directly; `moe_w4a16_prepare.py` is removed.
- Retains W4A16 caller workspace,256 payload threads,128/256-bit alignment capability, contiguous payload layout, and early PDL trigger. Blockscaled32-byte pointer promises and128-thread launch remain unchanged. No weight layout or Rubin behavior change.

Validation: scoped pre-commit+diff check passed;36 task-local exact preparation/alignment/padding cases and46 existing repository tests passed. Existing tests include32 W4A16 exact cases,12 MXFP public API cases,and2 NVFP4 recipe cases.

Performance: full13-token CAAC onGPU1,3 models,156 medians/15,600 samples.10 warmups,100cold-L2CUPTI CUDA-graph samples, fixed baseline native AUTO winners. Token1/2 run but excluded from retention. Every route identity and selected tactic verified equal across arms.

|Model|Decode4–512|Prefill4096–16384|All retained tokens|
|---|---:|---:|---:|
|v3|0.999043×|1.006677×|1.001119×|
|v41-flash|0.998612×|0.986474×|0.995287×|
|kimi-k3|0.999880×|0.985210×|0.995858×|

Keep as structural consolidation; do not claim a speedup. V41/K3 prefill show arm variance in raw data(e.g.K3T4096 C533.3/A533.9/A579.0/C536.2us). Parent composition retention will determine final performance.

Codegen: eight before/after cases(three model widths and16-byte fallback) pass exact copy. Register counts unchanged:28 V3/V41,26 K3,22 fallback. No spills/shared-memory allocation or CTA/mbarriers; LDG/STG256 and128-bit fallback preserved. Payload copy instructions match; common first-warp PDL policy adds two predicates,one branch,and the existing ancestor-release fence (`MEMBAR.ALL.GPU`, `ERRBAR`, `CGAERRBAR`) to W4A16. This was already the shared blockscaled publication contract.

Rejected diagnostic:128 payload threads regressed standalone decode copy by12–20% across all3 widths; prefill ranged0.99–1.03×. No production edit was made for this diagnostic.

Evidence: `gate-evidence/`, `perf-evidence/`, `retention.json`, `codegen-summary.json`.275 performance artifact hashes verified; archive SHA256 `86349d871d4ecd1abfbf97486df6bfff5027252b584a9ffed69a779c84fa922a`. GPUs0/1 released.

Reusable deployment helper: `../deploy.py NAME /absolute/review-copy`. It preserves remote1496 native source parity and reuses its persistent native cache while isolating DSL caches by exact source identity. No native C++ rebuild was needed.
