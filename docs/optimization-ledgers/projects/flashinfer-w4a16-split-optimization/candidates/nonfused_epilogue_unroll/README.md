# Ordinary epilogue loop unrolling (held candidate006)

Source-only proposal against retained `b90b34744491c36d0039f44cba664191f7bb0eb0`; no live source changes, new tests, helper framework, native compilation, or GPU execution.

The only change adds `unroll_full=not self.use_fused_finalize` to the existing nongated epilogue `cutlass.range(subtile_cnt)` loop at `moe_w4a16_kernel.py:2119`. The field comes directly from the Python host's finalize-mode argument, is included in the existing compile-cache key, and is stored unchanged by the private constructor. It is a trace-time Python boolean, not a tensor or GPU predicate. The same kernel already uses `unroll_full=True` on its MMA fragment loop at line1702; sibling Blackwell GEMM loops use that keyword too. Independent source/API review passes. The pinned CUTLASS reference checkout accepts `unroll_full=False` in `base_dsl/ast_helpers.py:327–368`; `cutlass_dsl/cutlass_ast_decorators.py:280–328` requires a pure Python bool and attaches a full-unroll loop attribute only when true. This reference is not an exact saved copy of the installed4.7.1 AST implementation. Actual native lowering remains separate evidence; see [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md).

- [source.patch](source.patch): `cbb4e1ceb8d63619d8e8c4a098f6c927c676959c63558e406e7203f01f5e2b17`.
- Proposed kernel: `9b3b153ecefe6c5bbdf410071b3f94d3d70713d33a884db8f0a4d8232706c96e`.
- Baseline kernel: `22fefac2a21e2efb5f9b5e0f2b402202dddf8f7136c1c50585105466ae2794a0`.
- [source-review.json](source-review.json): removing this one keyword makes the entire module AST identical. Syntax, Ruff lint and formatting pass.

For the public M128/M256 tactics, the physical CTA and nongated epilogue each cover128 features; the static subtile count is route N divided by epi N. The current ordinary selected N16/N32 families have one subtile and may already lower identically. N64 has two; N128 has four; supported N192 has six. The intended opportunity is constant subtile offsets for TMEM loads, SIMT partitions and TMA destination coordinates, plus folding `subtile_idx == subtile_cnt - 1`. The existing accumulator fence/release/advance at lines2123–2127 remains after the last load and before that fragment's conversion/store, exactly once per tile.

Unrolling preserves ascending output-subtile order and every body statement. It does not parallelize or reassociate the top-k FP32 reduction, change accumulator types, or introduce TMA reduction. The fused branch requests `unroll_full=False`; no fused code expansion is requested. Gated FC1 still has zero iterations in this nongated loop. ReLU2 FC1 uses the ordinary path and therefore also receives the hint. Runtime C-buffer indexing can remain dynamic because it persists across work tiles and advances only for selected TMA stores.

## Two independent interpretations

1. **006 on b90:** unroll the original full-route-TMA versus SIMT decision. The saved patch and proposed source represent this case.
2. **005 + 006:** use the exact same one-loop hint with005's per-subtile TMA-prefix condition. Constant subtile endpoints may additionally simplify that condition.005's separate condition edit and enhanced tail tests remain independent artifacts; no combined source is presented as measured here.

Parent will select the actual immediate source/control after005. No historical benchmark rows should be relabeled as a new combination. If005 is retained, its existing enhanced tail tests can be reused; if rejected, parent may retain only that test extension for006's mixed boundary coverage. No new numerical oracle is needed.

Potential cost is increased instruction footprint at N64/N128/N192. This is an unroll hint rather than a guarantee that the emitted code becomes smaller or faster. Native review should compare actual ordinary loop/address/control instructions, the single final accumulator release, C-buffer lifetime, register/spill resources, and fused/one-subtile controls. The two project ledgers contain no identified prior epilogue-subtile unrolling trial; earlier rejected launch-width, reducer-cache and raw-release changes are not revived.
