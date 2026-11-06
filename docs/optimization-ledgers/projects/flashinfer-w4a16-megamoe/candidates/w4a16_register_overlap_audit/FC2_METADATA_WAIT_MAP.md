# FC2 metadata publication versus activation completion

**The current kernel already permits FC2 metadata publication and FC2 weight loading/decode before FC1 activation completion.** It does not withhold FC2 work until the FC1 done counter is satisfied. This is a source-level capability; it does not assert that every measured work tile actually overlaps in time. No source change or additional lookahead pipeline is warranted for the proposed dependency relocation.

All paths below are under `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/` in the current C1 source overlay. The kernel SHA at this audit is `e00942e45f690e22258bb7f649b1be87b5a1cad72d61286251f6885ed10da42b`; vendor sources are unchanged.

| Step | Source | Actual dependency |
|---|---|---|
| Select FC1/FC2 phase | `src/moe_nvfp4_swapab/fc1_fc2_fuse_sched.py:1314–1346` | FC2 begins when the assigned cluster-linear tile index crosses `current_group_fc1_subphase_end`; no completion-counter condition. |
| Set phase | same file `:1032–1050` | `_switch_to_fc2()` changes phase and expert iteration state. No spin or barrier. |
| Enrich FC2 metadata | `src/moe_nvfp4_swapab/custom_ext.py:403–434` | Calls `spin_wait(..., peek_only=True)`, packs the returned hint, and returns valid work even if the hint is false. |
| Implement the peek | `src/moe_nvfp4_swapab/moe_utils.py:93–114` | One GPU-scope acquire load and condition check; the compile-time peek branch returns before the blocking loop. The actual implementation is acquire, despite an older nearby comment describing `ld.cg`. |
| Publish work | `shim/w4a16/kernel.py:1048–1057`; `src/moe_nvfp4_swapab/moe_persistent_scheduler.py:146–167,711–724` | Acquires a free metadata-ring slot, writes the work, commits it. No FC1 done check. Descriptor prefetch is a no-op (`custom_ext.py:532–535`). |
| Weight TMA | `shim/w4a16/kernel.py:1059–1101,762–832` | Consumes metadata, chooses FC2 tensors from phase, waits only for a free raw stage, then loads packed weights/scales. No `peek_ready`/FC1 done dependency. |
| Both decode groups | `shim/w4a16/kernel.py:1150–1229` | Consume the same phase metadata, then use raw-ready and free decoded-TMEM stages. No activation/completion-counter check. |
| Activation TMA | `shim/w4a16/kernel.py:1103–1147` | After reading FC2 metadata, warp6 blocks on the FC1 done threshold if `peek_ready` is false; only then `_activation_task` loads the BF16 FC1 output. This is already the requested owner of the dependency. |
| MMA | `shim/w4a16/kernel.py:1262–1276` | Waits for decoded weights and activation stages before tensor-core consumption; releases each input stage afterwards. |

The metadata consumer releases its SMEM ring slot immediately after copying work into registers (`moe_persistent_scheduler.py:170–193`), before the activation warp subsequently waits on FC1 completion. Thus a false readiness hint does not retain that particular metadata slot while activation waits. The scheduler can still be limited by the finite three-stage ring and the slowest consumer on later slots. That is bounded metadata backpressure, not a rule withholding FC2 until FC1 activation completion.

A particularly direct protocol check is `shim/w4a16/epilogue.py:209–223`: the epilogue consumes its next work tile **before** publishing the previous FC1 tile's done contribution. At an FC1-to-FC2 transition this requires next FC2 metadata to be available independently of that contribution. Turning scheduler readiness into a blocking prerequisite would risk a cycle with this ordering.

The group scheduler intentionally orders each expert group as its FC1 tile range followed by FC2, with `group_hint` selecting the cumulative FC1 tile grouping (`fc1_fc2_fuse_sched.py:1104–1150`). Changing that ordering or the metadata-ring depth would be a distinct scheduling experiment, not relocation of an activation wait that currently resides in the wrong warp. No such new experiment is proposed here. Existing raw/decode stage and consumer backpressure can limit realized overlap, and source-correlated profiling would be needed to identify a specific avoidable gap.
