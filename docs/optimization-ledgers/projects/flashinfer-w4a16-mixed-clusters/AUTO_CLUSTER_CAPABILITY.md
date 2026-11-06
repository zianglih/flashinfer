# W4A16 AUTO cluster capability boundary

Local source review and host-test additions, 2026-10-24. This note does not
represent GPU qualification or measured performance. No remote source was
changed for this follow-up; the running performance snapshot stays frozen.

## Current behavior

- The candidate catalog remains hardware independent. Its first 16 entries are
  the original uniform2 candidates, followed by 12 mixed4+2 candidates. With
  in-kernel reduction permission those counts are 24 and 18.
- Fresh backend AUTO now passes an explicit `{}` to the frontend allocator.
  This uses the existing cache-bypass contract and starts from uniform2 config
  defaults. The change is implemented locally and awaits final source sync;
  non-AUTO cached lookup and explicit-dict behavior are unchanged.
- After the existing session-validity and graph-capture guards, AUTO queries
  four-CTA cluster occupancy through the frontend's cached HardwareInfo helper.
  One EP-group MIN reduction combines both query success and capability. If any
  rank reports zero occupancy, all ranks drop every effective cluster4 candidate
  in the same order. A query error fails the sweep collectively; it is not
  interpreted as a capability miss. Uniform-only candidate lists make no query
  and add no collective.
- Explicit uniform4 or mixed4+2 configurations still fail with a clear error
  when preferred occupancy is zero. They do not silently change geometry.
- Supported full B300 sessions keep all 28 candidates (42 with in-kernel
  reduction permission). This filter does not alter their tactic ordering.

Implementation: `flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py`,
private `_cluster_candidates`, called before the first `apply_knobs`/compile.
Coverage: seven new parameterized host cases in
`flashinfer/tests/moe_ep/test_w4a16_mixed_cluster_config.py`:

- `test_auto_zero_preferred_capacity_keeps_uniform_order` (two cases).
- `test_auto_cluster_capability_agrees_across_ep_group` (three cases).
- `test_auto_inherited_cluster4_is_filtered_and_uniform_needs_no_probe`.
- `test_auto_cluster_query_failure_is_not_a_zero_occupancy_result`.

The backend startup change is in
`flashinfer/flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py`.
The existing `flashinfer/tests/moe_ep/test_mega_workspace_knobs.py` now includes
`test_w4a16_auto_workspace_bypasses_persistent_winner` with three modes: AUTO
passes `{}` without calling the cache, `None` preserves the cached mixed winner,
and an explicit dict preserves that same object without calling the cache.

Validation completed locally:

```text
ruff check <autotune.py> <test_w4a16_mixed_cluster_config.py>
All checks passed!
ruff format --check <autotune.py> <test_w4a16_mixed_cluster_config.py>
2 files already formatted
python3 -m py_compile <autotune.py> <test_w4a16_mixed_cluster_config.py>
git diff --check
```

The same Ruff check/format, syntax, and diff checks also pass for `backend.py`
and `test_mega_workspace_knobs.py` above.

The local macOS Python lacks PyTorch; these new pytest cases have not yet run
against the imported package. No GPU or remote validation was attempted for
this follow-up. Existing earlier GPU/scheduler results predate this filter.

## Cached-winner boundary retained for this PR

The shared SM100 knob cache keys on the CUDA device name, dtype, world size,
geometry and other existing math/session fields. It does not key on measured
four-CTA occupancy. Device names commonly distinguish MIG profiles, so this is
specifically a same-name capability change or a transferred cache whose device
identity does not capture the active resource restriction (for example MPS
restrictions). MIG/MPS changes and heterogeneous partition configurations have
not been qualified here.

There are two non-AUTO cache-consumption paths:

1. Standalone `get_symm_buffer_for_bf16_nvfp4_mega_moe(knobs=None)` calls the shared
   `resolve_knobs` directly in `bf16_nvfp4/frontend.py`.
2. The W4A16 backend points `_knob_cache_module` at the shared cache. Base
   `_workspace_knobs` resolves a live-token profile and passes its resulting dict
   to the frontend as explicit knobs. A guard only in the frontend's
   `knobs=None` branch would miss this path.

Backend `knobs="auto"` now bypasses both paths during initial workspace
allocation. This avoids inheriting a persisted tactic before a fresh exhaustive
AUTO sweep; it does not change how cached or explicit non-AUTO sessions resolve.

If a cached cluster4 winner is selected after a same-name device becomes P0,
the frontend occupancy guard rejects it before launching a zero-grid kernel.
The new AUTO filter does not reinterpret that cache hit or automatically choose
an unmeasured replacement. AUTO remains supported for the capabilities of the
active per-device session; explicit/cache-selected cluster4 still requires P>0.

Possible later changes, deliberately outside this PR:

- Add a resource-capacity discriminator to cache recording and lookup. This
  centralizes protection for both callers, but requires a compatibility rule
  for existing entries. SM count alone is not the exact cluster-placement
  capability; occupancy capability is the stronger key and needs a hardware
  query when constructing the key. Arbitrary changed capacity can also affect
  performance without making a tactic invalid.
- Filter unsupported cluster4 cache entries before selecting a winner, treating
  them as misses so the established uniform heuristic applies. Filtering in the
  shared resolver/matching path covers both callers, but introduces W4A16 device
  capability work into otherwise shared cache lookup and needs explicit
  multi-rank consistency rules. A W4A16 adapter would avoid changing other
  dtypes but adds another resolution surface and still needs both callers wired.

Do not merely clear a cached winner's mixed geometry while retaining its cached
performance provenance: the resulting uniform tactic was not that measurement.
