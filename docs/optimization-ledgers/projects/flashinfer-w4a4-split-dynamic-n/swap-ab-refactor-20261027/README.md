# PR #7290 archive, squash and opt-in swap-AB refactor

## Published archive and squash

- Original upstream PR: https://github.com/flashinfer-ai/flashinfer/pull/7290
- Fork archive PR: https://github.com/zianglih/flashinfer/pull/7
- Archived head: `7ae6244de4ad60d92b6341f8f04dc73d2b1b0549` (27 commits).
- Archived base: `002529e17b22567a071091053c6c4dc2a55e050e`.
- Fork branches: `archive/pr7290-before-swap-ab-20261027` and its `-base` companion.
- Annotated tag: `archive-pr7290-before-swap-ab-20261027`; annotation includes the original PR metadata.
- Squashed/pushed head: `c20ee9e8bc295744f963cacdf87cfd6bdbb47aed`, with the same parent base and exact source tree `c78851906e978b25eb576e2615b5d9bf85bb0224`.

The archive refs were pushed atomically before the source branch was rewritten.
The source branch push used an explicit lease on the original head. GitHub
readback confirms one commit in #7290 and all 27 commits in fork #7. The original
body, metadata, commit list, source diff and squash receipt are stored here.
Upstream main advanced to `a3aae554a98ce4ab60b5976eccc255eb6b4e01ef` by the final
readback; this operation did not rebase onto that later commit.

## Published design refactor

The user requested publication after reviewing the design. Follow-up commit
`dd16512aba7a3948b6584b6552c8b6343057a4b6` was pushed to PR #7290. At the user's
subsequent request, both commits were squashed into
`c980f007d27cd8114a32a7b9da8066b1bdb0e1c4`, preserving tree
`f5a3200b177b792acd98e056b951645cb0b751b2` and parent `002529e1`. The push used
an explicit lease on `dd16512a`; GitHub confirms exactly one PR commit.
See `pre-final-squash.json` and `final-squash-readback.json`. Both
`../flashinfer-weight-layout-api-review` and canonical `../flashinfer` are clean
at the final squashed commit. The original archive remains unchanged. Files:

- `blackwell/moe_swap_ab_kernel.py`: optimized shared device implementation.
- `blackwell/moe_swap_ab.py`: host cache and FC1/FC2 launch adapters.
- `blackwell/moe_swap_ab_prepare.py`: shared preparation and routing-publication PDL contract, used by block-scaled swap-AB and W4A16.
- `blackwell/moe_swap_ab_tuner.py`: retained optimized tactic policy.

The two original Blackwell kernels and two architecture-dispatch launchers are
restored from the archived base. Public `swap_ab=False` preserves their default
dispatch, up64/gate64 layout, tactic policy and MX activation restrictions.
`swap_ab=True` selects the optimized SM100/SM103 path with up16/gate16 layout,
unfused MX finalize and SiTU support. It is fixed per API configuration, not an
autotune dimension, and unsupported architectures are rejected.

W4A16 already uses weights on A and activations on B. Its original 64-row
layout remains supported through the in-kernel transpose; True selects the
shared 16-row layout. It does not need a second device implementation.

The paired `interleave_cute_dsl_moe_weights` helper keeps quantized weights and
row-major scales in the same layout without requiring callers to query row
grouping. Unified preparation adds a `swap_ab=True` tag only for the new mode;
untagged views mean legacy False, and the runner rejects a mismatched view.
Raw wrapper calls select the mode at construction; the helper's tensor outputs
do not carry a tag, so their layout must match that selection.

DeepSeek and distributed benchmarks expose `--swap-ab`. Prior optimized timing
results correspond to True; no measurements were repeated and no new performance
claim is made. The public PR body was not refreshed during this push-only
request. SGLang's matching demo remains unstaged and unpublished.

Per the user's design-review instruction, no imports, tests, compilation,
formatting, linting or GPU benchmarks were run. Review was limited to reading
source/diffs and checking Git/archive state. Git hooks were disabled for this
commit/push to preserve that instruction. The follow-up commit contains the
reviewed refactor without further source changes.

## Additive-mode compatibility cleanup

The current one-commit PR head is `e25af36cea727cf473dfea72b6d9630c28f0b8d8`.
It retains universal shared/W4A16 optimizations, reuses one per-token quantizer,
and preserves the legacy/default behavior and original tactic policies.
Both FlashInfer source copies are clean at that head. See
`addon-cleanup.md`, `addon-cleanup-publication.json`, and
`refresh_addon_body.py` for the final design and publication evidence.

## Cleanup retained as a follow-up commit

At the user's request, restored original implementation commit `c980f007`
and moved its exact cleanup delta into follow-up `5ac452450f65c6cec179290a66503ae86143a13f`.
The two-commit branch has exactly the same source tree as `e25af36c`;
only history changed. Both FlashInfer copies are clean at the follow-up.
See `followup-split-local.json` and `pr-followup-split-readback.json`.
