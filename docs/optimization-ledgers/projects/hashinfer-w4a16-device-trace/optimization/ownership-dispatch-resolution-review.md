# Final ownership dispatch-resolution review

No missed reachable legacy marker implementation was found. The prepared helper resolves the actual W4A16 paths to the intended owned methods with either retained R2 alone or the pending R2-plus-counts candidate. This is a source-only call-graph review of in-memory ports, not final CuTe compilation or trace qualification. No source was changed and no output worktree or GPU process was created.

Reviewed inputs:

| Source | Package SHA256 | Status during review |
| --- | --- | --- |
| `store16_no_raw_peek` | `85f18dc5b772155571b21434184b1cef869cc2b0814039c6292943ab344171ff` | Retained R2: Store16 plus raw-probe removal |
| `store16_raw_counts` | `3ec75add37d200d2c06d986436f3a87c61774706c0c79d0bfab0878b7baf99c1` | Pending counts-after-R2 candidate |

`ownership-dispatch-resolution-review.json` records both source hashes, the frozen helper hash, six-method port audits, the conservative union of transport call paths, and protected-file checks. All 28 Python files under the vendor subtree plus the shared grouped helper checked by this review are accounted for: three differ before porting, and none differs from PR base406bc0d after the virtual restoration. The count of28 includes the shared helper; it is not28 additional files besides it.

## Concrete call resolution

Source references below use the frozen candidate's unported paths under `hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/`; the helper changes definition ownership without changing these call sites.

| Caller / selector | Resolution after port | Why restoration does not bypass it |
| --- | --- | --- |
| `frontend.py:264–304`, then `:371` | `cute.compile(mega.kernel)` compiles a `Sm100W4A16MegaMoEKernel` instance | `_CompiledMega.kernel` stores the actual owned kernel object; this is not an inherited grouped-kernel entry point. |
| Kernel `_make_mixed`, `megamoe_kernel.py:312`; FC2 setup `:739` | Both mixed objects are `_MegaMixedInput` | FC1 and FC2 use the same subclass type even though their fragment sizes differ. The shared base supplies constructor/layout helpers, not their final transform method. |
| Kernel FC1/FC2 transform branches `:1553,1562` | Owned `_MegaMixedInput._transform_tile` | Calls use `self.mixed_fc1/2._transform_tile`, never `Sm100W4A16GroupedGemmKernel._transform_tile(...)`. The copied method retains zero raw lookahead probes and both TMEM probes. |
| Copied transform's stage completion | Existing owned `_MegaMixedInput._finish_transform_stage` | Its `self._finish_transform_stage(...)` resolves to the subclass override, preserving raw-SMEM release before TMEM store fence/commit. Layout partition helpers remain inherited and marker-free. |
| Kernel constructor `:258`; kernel dispatch `:1457` | Owned `W4A16TokenComm.dispatch_warp_body` | The constructor instantiates `W4A16TokenComm`; the kernel calls the instance. The copied orchestration calls `self.dispatch_prep`, `self.dispatch_barrier`, `self.dispatch_pull` and `self.token_back_by_push`. No explicit base-class dispatch bypass exists. |
| Dispatch route preparation | Inherited `dispatch_prep` in these two sources | Its body has no IKET markers. A future selected payload wrapper would override only this method and explicitly delegate the unchanged preparation before NB11. That feature is absent here. |
| Dispatch count/input publication | Owned `dispatch_barrier` | R2-only copies the original publication semantics plus three coarse ranges. R2-plus-counts copies the prefix-fence/rank-count publisher plus those ranges. The helper's marker-stripped AST check distinguishes them. |
| Dispatch pull | Owned `dispatch_pull` | The copied body contains no IKET calls, so the restored vendor's lane0-only `Pull.*` markers cannot reappear on this path. |
| Activation gate `:1302` | Owned `fc1_tma_b_predispatch_spin` | The instance call retains the explanatory FC1-input wait label and the original readiness check. |
| Scheduler gate `:1216` | R2-only inherits NB9 wait; R2-plus-counts uses owned count polling | Both are deliberate and marker-free internally; the owned kernel supplies the distinct surrounding wait label. The helper preserves any existing owned scheduler method verbatim. |
| Kernel retirement/cleanup `:1602,1658,1664` | Existing owned `kernel_tail_drain` / `kernel_tail_cleanup` | The original vendor `kernel_tail` is not called. Inherited NVLink, counter-reset and CTA-ID helpers have no markers. |

The conservative transport graph has17 resolved methods for each source, covering both possible return modes and all kernel entry calls. None of its inherited vendor methods contains a marker. Existing constructors do not rebind the copied methods on the instance.

## Return modes and staging variants

**Epilogue return:** the kernel permits only BF16, unquantized combine. With `token_back_mode="epi_warps"`, vendor constructor fields are `push_data=False` and `push_sf=False`; `enable_token_back` is false. The owned dispatch method's optional return branch is therefore omitted. `W4A16Epilogue` is an owned class rather than a subclass of a vendor FC1/FC2 epilogue. Its owned `Fc2OutputRouter` / BF16 STG functions route to local or peer combine storage (`epilogue.py:233–280,319`; `tmem_epilogue.py:356,586`). They do not call the vendor token-return method.

**Reused dispatch return:** `push_data=True`, `push_sf=False`. The copied dispatch method invokes the owned `token_back_by_push` after its pull phase. The optional in-kernel top-k reduction still follows the selected method's existing branch; ownership does not redirect it. The retained per-token `return_push_one_output_token` range is warp-uniform: its representative predicate is CTA0/dispatch-relative warp0, and it brackets the shared token index's copy outside `elect_one`. This is distinct from the removed lane-divergent nested pull markers. Both static and atomic return scheduling remain the selected implementation.

**Standalone return:** `frontend.py:101` rejects it and the kernel constructor explicitly passes `token_back_standalone=False` (`megamoe_kernel.py:269`). The kernel has no `token_back_warp_body` call. Consequently the one marker-bearing vendor method left inherited, `token_back_warp_body` with its old standalone label, is unreachable. Supporting standalone later would require extending the ownership review and likely copying that method.

**Prestaged inputs:** `staging_inputs is None` omits only the owned `stage_inputs` call. Dispatch preparation, owned publication/pull, activation readiness, both transforms and the selected return path still execute through the same objects. The prestaged variant does not use a separate vendor entry point. Fused Int32/Int64 IDs and contiguous/strided BF16 variants select descriptors in `frontend.py:350–410`; their methods and marker ownership are unchanged. Empty live inputs change route work and bounds, not method resolution.

## Tracing on/off and remaining inherited markers

`MegaMoEBf16Nvfp4Config` is frozen. `enable_iket` affects only the compiler option (`frontend.py:369–370`); it does not choose another kernel, transport class, transform implementation or return path. With it true, all active owned sites import `iket` through `hashinfer._compat`. With it false, the same calls compile without the explicit `iket` option. Existing uninstrumented candidate exports contain no PMTRIG, but that is not a substitute for checking the eventual owned cubin. Inherited `CUTE_DSL_COMPILER_OPT` can independently request instrumentation; the final native driver clears it.

Restoring the vendor compatibility module does not forward it to the owned adapter. On wheels with the dialect, both adapters import the same CUTLASS API. On wheels without it, each module can instantiate its own no-op shim and emit its own warning; two warning sites are a possible nonblocking consequence of complete restoration. `enable_iket=True` cannot supply a missing dialect, and such a fallback is not a validated capture path. There is no global rebinding or method-specific suppression of vendor markers.

A full vendor marker search also finds `sched_drain` / `helper_drain` in `MoEDynamicPersistentTileScheduler.drain_empty_tiles`. They are outside the W4A16 graph. Owned `MoEFusedFc12SchedulerParams.get_scheduler_type()` always returns owned `MoEFusedFc12PersistentTileScheduler`, which directly inherits marker-free `MoESchedulerBase`; it does not inherit the CLC dynamic scheduler. The kernel additionally rejects `force_static_sched=False`. No extra scheduler copy is needed.

The restored shared grouped helper contains no IKET calls. The only vendor token methods containing them are the four shadowed copies and the disabled standalone method described above. Thus no additional protected-file marker edit or extra copied method is required by the current supported W4A16 paths.

## Remaining validation boundary

The static dispatch graph and exact method/import checks are sufficient to identify the intended Python ownership; they cannot prove CuTe JIT lowering after the move. Keep the planned actual-owned-source compilation for tracing off/on, final native artifact audit, both return modes and prestaged/lifecycle suites. Re-audit new PMTRIG sites for the three dispatch subsections. In the final source guard, R2's **remaining** transform probe mode is `tmem`, not `raw` or `none`. The final parent source remains a retention decision outside this review.
