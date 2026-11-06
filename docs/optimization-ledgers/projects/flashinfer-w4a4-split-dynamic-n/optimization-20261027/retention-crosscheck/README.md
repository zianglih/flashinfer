# Causal retention checks

Both checks completed eight mirrored frozen phases: control(old winner), candidate(old winner), candidate(new winner), control(new winner), then reverse. All 16 phases passed exact source/cache identity, matched-route, saved winner, no-AUTO, and 100-sample cold-L2 CUDA-graph CUPTI checks. The public benchmark and full published campaign were unchanged. N3U uses EP8; per-token includes the initial activation quantizer and the existing 4over6 recipe. No sanitizer ran.

The 61-file raw archive is `evidence-transfer.tar.gz`, SHA256 `f9e3a0d1baec8633c144ca2609b6ef6d31b21f93d80553fe284e9eb698e90ee4`. Extracted receipts, native caches, commands, logs and 1,600 timing samples are under `evidence/runs/`. Original and new native winner files were copied byte-for-byte; no tactics were added or overridden.

| Case | Control / old winner (us) | Candidate / old winner (us) | Control / new winner (us) | Candidate / new winner (us) |
|---|---:|---:|---:|---:|
| N3U PER-TOKEN, 4096 tokens | 310.106 | 310.578 | 337.522 | 321.394 |
| N3U MXFP4x8, 4 tokens | 37.104 | 37.304 | 38.960 | 39.184 |

Values are geometric means of the two mirrored pass medians. Positive speedup means faster.

| Case | Source change, old winner | Source change, new winner | New winner on candidate | Native-winner before/after |
|---|---:|---:|---:|---:|
| N3U PER-TOKEN, 4096 tokens | −0.152% | +5.018% | −3.365% | −3.512% |
| N3U MXFP4x8, 4 tokens | −0.536% | −0.573% | −4.799% | −5.309% |

The large flags are primarily winner selection. PT changed from N256, both 2-CTA, CLC, K4/K4 to N128, mixed 1/2-CTA, static, K4/K4. MXFP4x8 changed only K8/K8 to K4/K4. The PT old-winner endpoint control drift was 0.046%, with 0.052% candidate spread; its 0.152% residual is small but not proven zero. The roughly 0.55% MX decode cost is consistent across both fixed tactics and should be acknowledged. It does not justify discarding the broader measured prefill improvements. Remaining old-CuTe gaps remain visible in the complete table.

Retention recommendation: retain the measured source separately from any subsequent autotuner experiment. Keep the full campaign's native winners and timing table unchanged. Any tuner-policy change needs its own causal evidence.

## Source audit

`source-retention-audit.json` verifies all 342 measured source-manifest files against canonical. Exactly two files differ through the known formatter changes (EOF blank line and existing error-message wrapping); both ASTs are identical. The measured review snapshot retains patch SHA256 `9b546843c47859284472540efe24ad1fa6ebea6d4c539f182d436ef66d371d18` and the original three file hashes. No canonical file was edited by this audit.

No blocking kernel issue found. Neighbor reads occur only for live routes with clamped indices and boundary predicates; hint calculation belongs to the TMA warp, including startup. Weight and scale loads share the hint without changing their barrier phase. The CLC consumer count follows the active producer/epilogue/MMA roles; inactive producers still participate in allocation and the final CTA join. Scale preload initializes every lane/iteration, guards all source loads, retains zero-fill for padding, and remains after the prerequisite wait. The no-scale W4A16 path excludes the new register preload at compile time.

The frozen combined candidate already passed 24 existing exact tests and 96 public-chain byte replays covering static/CLC, PDL off/on, one/two CTA, balanced/skewed/empty/reactivated routes and supported formats. The full campaign passed 54 phases with 44,200 AUTO plus 135,200 frozen samples. See `../retained-rerun/evidence/combined-gate/` and `../retained-rerun/assembled/`.

## Changed-file checks before commit

Read `CLAUDE.md`, `docs/code_review_guidance.md` and `.pre-commit-config.yaml`. Local read-only compile checks, Ruff 0.14.8 check and `git diff --check` passed. Root owns the repository-pinned pre-commit run (Ruff 0.12.8, mypy 1.17.1 and generic formatting/whitespace checks). The hooks may apply the two already documented formatting-only fixes; preserve the AST/source-equivalence receipt with the final commit.

```bash
pre-commit run --files \
  flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab.py \
  flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py \
  flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_prepare.py
git diff --check
```

No additional GPU rerun is needed for those two formatting-only changes. Any semantic change would invalidate the measured source identity and require appropriately scoped revalidation. Keep persistent compilation caches and the frozen remote source intact.
