# BF16 NVFP4 MegaMoE reduction permission and interface audit

Work on public FlashInfer PR5019, based on `4bc278892b3ced0a8c81501f858de517931e2ae9`. HashInfer synchronization is deferred. No reviewer replies are posted.

## Implementation

- Follow existing BF16 MegaMoE permission/tactic separation: `enable_in_kernel_fc2_reduce=False` by default. Opt-in allows the two dispatch-return IKR tactics in addition to the original four external-combine tactics.
- Default device specialization retains external FP32 routing and fixed-order combine. Opt-in weights the BF16 FC2 terms in FP32, rounds to BF16 and uses the existing universal BF16 bulk-reduce transport. It neither changes FC1 routing nor adds a core pipeline.
- Reuse the symmetric combine allocation through a contiguous `(T,1,H)` prefix. Zero it on each eager or captured launch; retain the full `(T,K,H)` allocation for tuning back to external combine. Permission isolates pooled workspaces and cache lookup.
- Match shared tuner default-picker and config-aware validation patterns. Vendored `src/` remains unchanged.
- Follow-up scale audit: W4A4 already carries these same post-accumulation scalars through `fc1_alpha`/`fc2_alpha`. Refactor BF16×NVFP4 to that existing interface and prepared `(weight, scale)` pairs; then remove both new canonical global-scale fields and the capability guard. No alpha folding into E4M3 scales or BF16 decoded operands. Config alphas initialize workspace values; per-forward overrides follow W4A4 staging. Config tensor identities isolate pooled workspaces, while callers sharing across layers provide each layer’s alphas through `MoEEpTensors` on every forward.

## IKR implementation validation (`576904a8`)

- Scoped production pre-commit passes; isolated host API checks: 88 passed (see `../ikr-api-20260917/results.json`). These use extracted actual source and CPU Torch; they are not GPU evidence.
- Independent index/lifetime review exhaustively verifies 24,576 thread/subtile/element mappings for N64/N128. Scores follow accumulator readiness, valid-token guards prevent padded reads, and existing FC2 publication fences order weighted stores before dispatch TMA reads.
- Dedicated B300/CUDA13.2 environment and exact provisioning evidence: `gpu-setup/README.md`.
- Native validation: 26 host contracts, 20 single-GPU tests and 9 tests on each of two ranks pass. Includes fused/default paths, N64/N128, shape tails, graph replay/mutation/zeroing, static/atomic scheduling, skew/uneven/empty/refill routing. See `validation/README.md` for raw logs, commands and manifests.
- Documentation cleanup is separate commit `b546b4ee`; IKR implementation is `576904a8`. The subsequent alpha refactor is `1098a348`, described below. Historical PR performance rows remain tied to their original source commits.

## Final alpha interface (`1098a348`)

- The existing W4A4 config/workspace and `MoEEpTensors` alpha conventions now replace the bespoke weight-pack global-scale fields. Prepared weights use the same `(weight, scale)` pair contract. Scale placement in FP32 epilogues is unchanged.
- Four shared production files and the weight-pack union test are byte-identical to merged upstream `f17b7726`; no global-scale capability remains. Cleanup removes 57 net lines across the production/test/doc change. The full architecture-doc PR diff is five added lines.
- Native validation: 58 host passes / one optional DeepGEMM skip / three GPU-marked cache deselections; 30 single-GPU passes; 15 passes on each EP2 rank. Full logs, commands and tested/final hashes: `validation-alpha/README.md`.
- All 34 remaining PR paths pass scoped pre-commit. Five benchmark host checks pass (mocked profiler plumbing, no GPU timing).
- Paired default-path performance comparison completed against pre-change `4bc27889`: GM8–8192 baseline/final 0.999521×. Saved pre-merge `4d183b83`/final is1.005964× on different B300 nodes. Full14 rows,2800 new raw samples,112 paired output hashes and14 tactic matches passed independent audit; three retained CUBINs are byte-identical. Both arms use external FP32 reduction/static unit alphas; no runtime-alpha-copy or IKR performance claim. See `benchmark/README.md` and its three-way table.

## Publication

All three commits are pushed to `zianglih/flashinfer:feat/w4a16-megamoe`; the remote branch was verified at `1098a348a1b2a4457cafba4e5263609451914043`. The PR body is refreshed with the complete three-way table and current validation. The older correctness-fix experiment is preserved locally in `pr-before.json`/prior ledgers rather than repeated in the body; both historical final Split tables remain unchanged. `PR_BODY.reviewed.md` has an independent source/receipt audit, including sticky runtime-alpha semantics and explicit historical performance labels. No reviewer comment was posted.

The owned devbox was released after source/archive/GPU closure and independent results audit. See `gpu-setup/release-receipt.json`.
