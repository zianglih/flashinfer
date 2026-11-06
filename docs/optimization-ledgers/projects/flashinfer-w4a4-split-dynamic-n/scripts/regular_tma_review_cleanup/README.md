# Regular-TMA review cleanup

`flashinfer-regular-tma-review` is a new independent clone at base442 with exactly the three experimental files unstaged. Frozen validcopy, LDG256 and primary sources remain unchanged. No remote deployment, GPU execution, stage, commit or push occurred.

The cleanup removes ten constexpr branches controlled only by `self.gather_activations=False`, two corresponding ternaries, the false attribute and its unreferenced Gather4 helper. All former helper imports remain used by regular SFB TMA or dynamic MMA. The live `gather_k` geometry name and empty `producer_gather4_issue` diagnostic range remain to preserve the trace contract. The transaction-count expression retains its mechanical division by one; no algebraic normalization was needed for the proof.

Core documentation now describes regular activation TMA in both phases, canonical SFB TMA at N128/N256 and cp.async at smaller route tiles, original per-token scale indexing and logical M512 reuse. Preparation documentation states that only valid payload rows are copied, invalid payload remains untouched and masked by downstream epilogues, complete required SF row padding is zeroed, and workspace allocation is per invocation. The new preparation file has the standard FlashInfer Apache-2.0 header. The repository-pinned Ruff0.12.8 formatter was applied to all three files through pre-commit.

`verify_ast.py` compares the complete Python AST for all three files against frozen validcopy. It removes docstrings and applies exactly the named false-branch/helper pruning to the frozen core, without changing names, arithmetic, markers, APIs or live expression/statement order. All three normalized module ASTs match. `ast-equivalence.json` records both source hashes and normalized AST hashes. `precommit.log` records successful changed-file checks including mypy, Ruff checks and formatting. `review-manifest.json` pins the final three source files; `cleanup-from-validcopy.patch` is the direct cleanup diff.

This is CPU evidence of live source equivalence. It does not assert identical CuTe generated code or replace GPU numerical, sanitizer or performance validation. Those boundaries remain explicit; no GPU work was authorized for this cleanup.

```bash
python3 scripts/regular_tma_review_cleanup/verify_ast.py
cd flashinfer-regular-tma-review
pre-commit run --files \
  flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py \
  flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_grouped_gemm_finalize_fusion.py \
  flashinfer/fused_moe/cute_dsl/blackwell/moe_prepare.py
```
