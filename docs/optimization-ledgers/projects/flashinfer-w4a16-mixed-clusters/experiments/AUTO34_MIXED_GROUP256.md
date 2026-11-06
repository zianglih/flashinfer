# Product AUTO34: append mixed groups of 256

`auto34-mixed-group256.patch` is an **unapplied catalog experiment**. It changes only the W4A16 candidate generator and its existing host contract test. It does not change the kernel, scheduler, capability filter, fixed configuration defaults, or the existing candidate order. The remote checkout was not touched.

The default product catalog retains its first 28 entries exactly and appends six preferred4/fallback2 M256 choices: N32/N64/N128, each with `epi_warps` and `reuse_dispatch_warps`, using `group_hint=256`. With `enable_in_kernel_fc2_reduce=True`, the first 42 entries remain exact and nine are appended, giving 51. Three of those nine opt into reduction and use dispatch return. Filtering the 51 choices to non-reduced choices reproduces the default 34 in order. The user subsequently clarified that optimized benchmark sweeps must contain only the new mixed tactics: the project-only wrapper would therefore expose 18 choices after this patch, while production retains all 34.

| Catalog | Existing uniform | Existing mixed | Added mixed group256 | Total | Reduced choices |
| --- | ---: | ---: | ---: | ---: | ---: |
| Default | 16 | 12 | 6 | 34 | 0 |
| Reduction opt-in | 24 | 18 | 9 | 51 | 17 |

## Established source pattern

SM100 GenPhase already scales its grouped hint inversely with cluster size: [`default_sm100_genphase_knobs`](https://github.com/flashinfer-ai/flashinfer/blob/316faec37a4706a2ecc7d46265087f8190b40baa/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/shim/tuning.py#L84-L91) uses `4 * (sms // cluster)`, while its [candidate enumeration](https://github.com/flashinfer-ai/flashinfer/blob/316faec37a4706a2ecc7d46265087f8190b40baa/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/shim/tuning.py#L118-L132) includes two/four/eight-wave hints with that same division. The older [SM100 tuner](https://github.com/flashinfer-ai/flashinfer/blob/316faec37a4706a2ecc7d46265087f8190b40baa/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/shim/tuner.py#L54-L56) also includes 256 in its existing group-hint axis. These are experiment-selection precedents, not measured evidence for W4A16.

The maintained W4A16 scheduler computes logical channel-block counts with ceiling division in [`fc1_fc2_fuse_sched.py:444`](/Users/ziangli/playground/projects/flashinfer-w4a16-mixed-clusters/flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:444) and walks whole experts until cumulative FC1 logical tiles reach `base_fc1 + group_hint` at [line881](/Users/ziangli/playground/projects/flashinfer-w4a16-mixed-clusters/flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:881). Explicit hints count logical work IDs; they are not automatically rescaled for cluster size.

For GLM5 (`hidden=6144`, `intermediate=2048`, 256 experts, EP8), M256 uses 128 channel columns per CTA. Cluster2 covers 256 columns and preferred4 covers 512. A token block therefore has 16 versus eight FC1 logical channel tiles and 24 versus 12 FC2 tiles. For identical N and routing, mixed group256 has the same expert-group boundaries as uniform2 group512. Current mixed512/1024 correspond to uniform2 group1024/2048. This equality relies on the channel dimensions dividing evenly; ceiling division makes it approximate on channel tails.

Rubin's [default mixed inference candidate](https://github.com/flashinfer-ai/flashinfer/blob/316faec37a4706a2ecc7d46265087f8190b40baa/flashinfer/moe_ep/kernel_src/sm107/next_cutedsl_megamoe/shim/autotune.py#L74-L82) uses `phase_interleave`; its hint is a different scheduling contract. The directly applicable precedent here is GenPhase's grouped hint scaling.

## Measurement boundary

All performance comparisons remain AUTO sweeps, with the baseline retaining its original uniform AUTO16 and the optimized arm sweeping only the new mixed tactics. The current optimized benchmark is mixed-only AUTO12 on the B-TMA-hoist implementation. Applying this patch would expand that optimized benchmark to mixed-only AUTO18 through the existing project-only wrapper. The product catalog remains AUTO34; do not benchmark its original uniform entries in the optimized arm. A comparison of mixed-only AUTO12 versus mixed-only AUTO18 with the same retained kernel can isolate the catalog expansion, while the pristine baseline AUTO16 remains the external control. Use the same fixtures, environment, cache policy, and short GLM5 EP8 token grid32/4096. Keep raw samples and each rank's winning tactic; this is not a fixed-tactic kernel comparison.

At global T32, no expert has more than 32 rows and each rank owns 32 experts. Every N32/N64/N128 mixed configuration has at most `32 * 8 = 256` FC1 logical tiles, so group256/512/1024 all form one group. T4096 can change the grouping. Earlier FC2 work may improve overlap, while more FC1/FC2 transitions and expert-group traversal may cost time. The six additional default candidates also add tuning and possible compilation work. No performance gain is claimed.

## Validation and application

Local checks passed: forward/reverse patch application in a temporary project-local tree with byte-for-byte restoration, Python AST parse for both proposed files, Ruff check and format check with the repository configuration, and execution of both updated catalog-contract parameter cases using the actual pure candidate/test/geometry-validator functions isolated by AST. The latter imports neither FlashInfer nor Torch and is not a substitute for the full package pytest run. Prefix equality was also compared directly against the current generator for both reduction settings. No GPU work, remote writes, or live source edits were performed.

The detailed receipt and before/after source SHA256 values are in [`auto34-validation.json`](auto34-validation.json). Patch SHA256: `a8f66e021968cd0a88d61939c4c5187a07aef8ec7683adabdf3e717b8cf1fb3d`.

When the experiment is selected and the current run has released the checkout:

```bash
cd /Users/ziangli/playground/projects/flashinfer-w4a16-mixed-clusters/flashinfer
git apply --check ../experiments/auto34-mixed-group256.patch
git apply ../experiments/auto34-mixed-group256.patch
```

The patch is independent of the B-TMA kernel patches because its two files do not overlap them. Recheck the receipt hashes and patch context if the generator or host test changes before application.
