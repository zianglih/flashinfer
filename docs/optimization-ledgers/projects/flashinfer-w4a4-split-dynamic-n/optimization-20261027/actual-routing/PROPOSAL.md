# Preserve the supplied workload in its matching tuning profile

This began as a source-traced proposal; the isolated experiment below is now
implemented and its initial three-cell comparison is complete. The
two crossed-winner results establish that tactic selection can leave performance
on the table; they do not yet establish that synthetic routing caused it.

## Current data flow

- `cute_dsl/fused_moe.py:1450–1524` and `1933–2074` pass the actual quantized
  activations, scale factors, expert IDs, routing weights, weights, optional row
  scales and output buffer into `AutoTuner.choose_one`.
- `cute_dsl/tuner.py:569–673` gives the shared blockscaled runner a dynamic
  token axis plus a `CuteDslMoEInputsHelper.inputs_pre_hook`. Swap-AB and
  legacy/Rubin use the same profiling-input construction; the dedicated
  `moe_swap_ab_tuner.py` only defines and filters tactics.
- `autotuner.py:2838–2854` first synthesizes dynamic tensors, then calls the
  pre-hook once per bucket, then profiles every candidate on the same prepared
  inputs. `_prepare_input_tensors` at4236–4256 synthesizes every dynamic tensor
  even when its requested shape already equals the caller's shape.
- `_inputs_helper.py:89–115,190–224` replaces the expert IDs with approximate
  maximum-rank load distributed almost perfectly evenly across local experts.
  Supplied route values do not affect the tuning workload. Routing scales and
  optional per-token scales are also synthesized; actual weight tensors remain.
- The helper's zero-quota loop at172–181 still assigns one route to an expert
  whose requested count is zero. Its source explicitly documents this behavior.

The saved actual N3U T4 routes contain10 local routes over10 local experts.
The helper's intended rank quota is16, but its per-expert quotas are16 ones and
48 zeros. Because the token capacity is88, the zero-quota loop assigns one to
each of all64 local experts:64 local routes,6.4× the actual active-expert work.
At N3U T4096 the actual local total is11,180 with counts117–252; the helper
uses11,418 total with counts178/179. Those are materially different scheduling,
padding and weight-reuse workloads.

## Surrounding architecture patterns

Hopper's `sm90_tuner.py:275–298` deliberately replaces balanced routing with a
seeded global uniform top-k draw. Its comment identifies artificial row-tile
padding as a cause of poor rankings in that implementation. It remains
synthetic, so it supports investigating the mismatch rather than proving our
winner changes have the same cause. Rubin inherits the shared balanced helper;
keep its existing behavior unchanged. No SM120 pattern was used.

The existing generic autotuner contract already supports a call-bound
`inputs_pre_hook`. It is invoked after profile allocation and before both
candidate admission and timing. No generic autotuner API change is needed.

## Smallest safe experiment

Add one private helper in `blackwell/moe_swap_ab_tuner.py` that derives a
call-scoped `TuningConfig` with `dataclasses.replace`. Its hook does the following:

1. If every synthesized tensor shape matches the corresponding actual tensor
   shape (including preserved `None`), return `list(actual_inputs)`.
2. Otherwise invoke the original pre-hook if present, or return the synthesized
   inputs unchanged.

Use this derived config at the wrapper and functional `choose_one` call sites
only for `swap_ab=True` while tuning is enabled. Do not store the actual input
references in a persistent runner. Legacy/Rubin and non-tuning calls continue
to use the existing config. This can apply uniformly to swap-AB modes, including
W4A16, without changing any tactic list. The authorized experiment is restricted
to the swap-AB blockscaled runner, leaving W4A16, legacy and Rubin unchanged.

Illustrative helper logic:

```python
def tuning_config_for_inputs(config, actual_inputs):
    def profile_inputs(tensors):
        same_shapes = all(
            candidate is None and actual is None
            or candidate is not None
            and actual is not None
            and candidate.shape == actual.shape
            for candidate, actual in zip(tensors, actual_inputs, strict=True)
        )
        if same_shapes:
            return list(actual_inputs)
        if config.inputs_pre_hook is not None:
            return config.inputs_pre_hook(tensors)
        return tensors

    return dataclasses.replace(config, inputs_pre_hook=profile_inputs)
```

The shape check is required to preserve profile correctness. Returning actual
inputs unconditionally would tune every generated bucket on the caller's token
count and save those scores under mismatched bucket keys. Removing the dynamic
specs would instead change cache/bucket semantics. Neither is proposed.

## Contract and limitations

- Hybrid bucket generation, nearest-profile mapping, cache keys,360 blockscaled
  tactics,23 W4A16 tactics, public arguments and default legacy behavior stay
  unchanged. The existing actual-size bucket is included by the hybrid generator
  at`fused_moe/utils.py:228–275`.
- Reuse all actual inputs together: expert IDs and routing weights, quantized
  values and their scale layout, per-token scales, output shape and aliases
  stay coherent. No data-dependent host read or routing re-run is required.
- The hook is used only on a tuning miss. `autotuner.py:2838–2842` already
  rejects profiling under an active outer capture; warm-cache calls skip input
  preparation. Returning tensor references does not add synchronization or
  mutate the caller's inputs. Tactic runs already write the supplied output.
- Call-scoped closure lifetime ends with `choose_one`; it cannot bind an earlier
  wrapper call's routes to a later graph. No runner-state mutation is needed.
- Other synthetic profile buckets retain the current fallback. A single warmup
  at maximum capacity still cannot provide real routing for every smaller
  bucket. Existing cached winners remain usable and are not distribution-aware;
  fresh cache files are required to evaluate this policy. Do not claim every
  future routing distribution is optimized without a new distribution key.
- The hook does not add upstream input quantization/top-k into native MoE tactic
  timing. The end-to-end benchmark includes those operations. NV profiling is
  currently eager while MX profiling opts into CUDA graphs in
  `bench_moe_deepseek.py:791–837`; that remains another possible ranking factor,
  separate from routing and outside this small experiment.

First evaluate on the two crossed-winner cells with fresh native AUTO and
recorded actual-vs-probe route hashes/counts, then frozen matched-route replay.
Check capture/cache hits and different-sized bucket fallback without modifying
the benchmark observer or forcing either former winner. Broaden only if this
isolates a useful ranking improvement.

## Isolated implementation and gate

- Base: retained `1e69d0a391fd926d21a35388cacf2df3c1c22baf`.
- Former review clone: `flashinfer-actual-routing-perf-review`; it held two
  unstaged Python files,38 added /2 removed lines, and was removed after
  rejection with ownership/patch proof. Source patch and SHA manifest are in
  `artifacts/candidate.patch` and `artifacts/static-gate.json`.
- CPU gate: shape/None fallback, original tensor identity and output alias,
  unchanged base config, weak-key derived-config lifetime, both public API
  guard truth tables, AST syntax and `git diff --check` passed.
- GPU gate passed on B300/CUDA13.2/CuTe4.8 in26s: `gpu_gate.py` bounds tuning to one admitted tactic for validation
  only, with matchingT4 and syntheticT2 buckets across all four blockscaled
  formats and both public APIs. It checks input byte immutability, unchanged
  cache identity, warm captured calls and config collection. This does not
  provide benchmark winner files. All8 format/API cases passed, including
  24cache-key equality checks and16cold-batch pointer checks. The retained
  configs were collected after each call and input bytes were unchanged.
  Hash-verified raw receipts are under `artifacts/runtime/`.
- `observe_actual_routing.py` delegates the original benchmark observer
  unchanged and only reads route hashes/counts during input preparation before
  tactic timing. It verifies both the exact-shape branch and prepared-pointer
  preservation through the cold-L2 batch setup in the real N3U workloads.
- Fresh independent native AUTO per arm; frozen100-sample CUPTI C-A-A-C.
  Initial cases: N3U EP8 per-token4096 and MXFP4x8 T4, GPUs0/1. NativeNV
  profiling remains eager and MX profiling remains CUDAgraph.
- Orchestration review corrected a validator-only mistake while control AUTO
  was running: pre-hook random route IDs must not be compared with the
  post-hook balanced routes. Fallback now compares candidate and control
  post-hook routes at the same full profile shape. Completed AUTO outputs
  are resumed only after matching source/config/observer/cache proofs and
  validating all100CUPTI samples; they are not regenerated for this correction.

## Initial results and disposition

| N3U EP8 case | Synthetic-profile winner (us) | Actual-profile winner (us) | Speedup | Control drift | Candidate spread |
|---|---:|---:|---:|---:|---:|
| MXFP4x8,4tokens | 37.888000 | 37.888250 | -0.00066% | 0.0000% | 0.0013% |
| PER-TOKEN,4096tokens | 320.210500 | 310.737998 | +3.04839% | +0.0100% | 0.0206% |
| W4A4,4096tokens | 236.609706 | 219.217679 | +7.93368% | -0.1214% | 0.1609% |

Both sources are retained1e69 plus only the candidate's38+/2− profiling-input
change. Native AUTO selections are independent; the table uses the geometric
mean of the two frozen100-sample CUPTI passes per arm in C-A-A-C order.
The source does not change GPU code during frozen replay.

MXFP4x8 picked the same routeN16 / channelM128 /1CTA / K4,K8 / CLC-on
tactic under both policies. Per-token changed from routeN128 / channelM256
and2CTA for both GEMMs / K4,K4 / CLC-off to routeN256 with the same channel
geometry/depths and CLC-on. W4A4 changed from routeN256 with a one-CTA
FC1 to routeN128 and two CTAs for both GEMMs. No winner was forced during AUTO.

The real matching profiles reused every actual input reference, including
SF/output shapes, and cold-L2 batches preserved those pointers. At4tokens,
the original helper produced64local routes across64experts versus the
actual10routes across10experts. At4096tokens it produced11,418balanced local
routes versus11,180actual routes. All other profile buckets retained exactly
the control's prepared routing hashes.

Independent audit passed18phases,1,800CUPTI samples and86native profile
records (43 paired shapes), with all raw medians, keys/tactics, hashes and
formulas checked. Every paired profile has an identical admitted-tactic count
and hash, so the input hook did not change the search space.
See `artifacts/independent-result-audit.json` and
`harness/evidence/runs/` for the unmodified native outputs.

The frozen outer wrapper's raw `complete=False` is preserved: the unchanged
observer calls `sys.exit(main())`, so `runpy` raises `SystemExit(0)` before the
wrapper's success assignment. Completion is independently established by
process exit0, native results.complete/exit_code0, all admitted profile records,
and source/observer/cache/sample hashes. `artifacts/system-exit-proof.json`
reproduces this bookkeeping behavior. No measurement was rerun for this issue.

**Rejected after serving-warmup holdout:** an independently selected zero-local
warmup winner took354.066247us on the real N3U PER-TOKEN4096 workload, versus
310.737999us for the real-trained winner: -12.237328% speedup / +13.943659%
latency. Control drift was0.010299% and candidate spread0.026976%. Both arms
used the same source, routes, recipe and CUPTI timing. Only the matching native
profile was retuned; the same320 tactics were admitted and all19 other entries
were unchanged. This is a concrete shape-cache generalization failure, despite
the seed-specific gains above. No concentrated or additional-seed run was needed.

See `holdout/RESULTS.md`, `holdout/independent-audit.json` and the raw38-file
archive. The successful AUTO was preserved when an import-path-only failure
occurred before the first replay; the corrected wrapper's four fresh frozen
passes have independent receipts. Experimental source copies are removed after
ownership/patch verification; scripts, patches, evidence and compilation caches
are retained. Production and the published PR remain unchanged by this rejected
policy.
