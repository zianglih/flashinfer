# Candidate 3: mixed B-TMA producer lookahead

`mixed-b-tma-try-acquire.patch` is **unapplied** and depends on candidate 2, `hoist-b-tma.patch`. It changes only `_activation_task` in the maintained W4A16 kernel. The live checkout is now candidate 2; its kernel hash matches the candidate-2 entry below. Apply only the candidate-3 patch to that checkout.

The source pattern is Rubin `kernel_src/sm107/next_cutedsl_megamoe/src/sources/kernel_src/rubin/inference/mega/block_scaled_swap_ab_fc12_mainloop.py::run_tma_b`, lines 942–956: initial `producer_try_acquire`; acquire with the returned token; save barrier and stage index; advance the state; probe the next stage when one remains; then issue the current TMA. Candidate 3 applies that sequence only to the mixed activation pipeline. Uniform2/uniform4 retain their existing direct acquire/copy/commit/advance sequence.

The reused SM100 `custom_mix_cga_helpers.py::PipelineTmaUmmaMixedCga.producer_acquire`, lines 289–301, accepts the optional readiness token and still performs the full-barrier transaction-byte arrival. Its `producer_commit`, lines 303–305, is explicitly a no-op. Candidate 3 omits that no-op in the mixed branch because its state has already advanced. Current-copy K coordinate, barrier pointer, and destination stage are saved before advancing; every iteration advances once, and the final state handed to the next work tile or producer tail is unchanged. No descriptor, multicast mask, byte count, wait phase, MMA, arithmetic, scheduler, catalog, or return-path change is intended.

Risks: the installed CuTe 4.7 compiler must accept the loop-carried readiness token; stale-token/state-order mistakes can hang a pipeline. Probing can add instructions when slots are already ready, and the compiler/hardware may already hide the direct-acquire cost. This is not a claimed improvement. If selected, compare **mixed-only AUTO12 versus mixed-only AUTO12** at GLM5 T32/T4096 using the project wrapper; the product catalog remains unchanged. Native eager preparation before AUTO graph capture supplies the compile/liveness gate. Add a separate focused check only if a compilation or runtime problem requires it. Broader correctness and sanitizer qualification remain deferred until retained gains justify them. No fixed-tactic performance runs are proposed.

Historical preparation validation, performed without CUDA while the live checkout was candidate 1: AST parse and Ruff format/check of the complete proposed candidate-3 source passed. In a project-local temporary tree, candidate 2 applied to candidate 1, candidate 3 applied to candidate 2, and both reversed back to the exact candidate-1 bytes. That preparation did not patch the live checkout. Candidate 2 was subsequently applied by the GPU owner; candidate 3 remains unapplied.

| Artifact | SHA256 |
|---|---|
| Candidate-1 kernel | `cd947d453f3c9ebfc3df8e51feac190805e690a2462233e56dbb817e04b4efc6` |
| Candidate-2 kernel | `87839cd3b1c4d68bbaf83c44a3f9838f0d1c3875764187cbe3f2b45f99388fb4` |
| Candidate-3 kernel | `48c87b4f9e027c033ac7c2a34c9fd1f5b3d03f16e89e53891c6d7cd560574f98` |
| Candidate-3 patch | `79199f123cbb5fc284b4c12208a495b95fbc0c0f5a8da94ba24a0ffe47af17de` |

When the GPU owner chooses this experiment and no capture is active, apply only candidate 3 from the current candidate-2 checkout:

```sh
cd /Users/ziangli/playground/projects/flashinfer-w4a16-mixed-clusters/flashinfer
git apply --check ../experiments/mixed-b-tma-try-acquire.patch
git apply ../experiments/mixed-b-tma-try-acquire.patch
```

For candidate 2 versus candidate 3, reverse only `mixed-b-tma-try-acquire.patch`. Never apply either patch to a source being used by an active capture.
