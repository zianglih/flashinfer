# Mixed W4A16 IKR qualification plan — deferred

This is planning only. No oracle, test, harness or production change has been made for this plan, and no qualification run is authorized here. The user deferred full-kernel numerical/sanitizer work until retained performance gains. The current product catalog exposes nine mixed IKR choices (N32/N64/N128 times groups256/512/1024), all opt-in and using dispatch return. The prepared static catalog would add nine more mixed IKR choices.

## Existing reference and exact comparison contract

Reuse the maintained [`_run_nvfp4_routing_rounds`](../flashinfer/tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py) public-layer helper (lines1436–1456). It already passes IKR permission and selection together (lines1544–1545), computes the independent reference with the IKR flag (lines1627–1637), and uses the matching comparator (lines1657–1663). Existing uniform W4A16 IKR cases exercise config/runtime scales at lines1821–1823; the new mixed geometry cases at lines1900–1963 currently do not enable IKR.

The [W4A16 oracle](../flashinfer/tests/moe_ep/w4a16_reference.py) computes on expert owners and transfers BF16 route bits back to sources. Its IKR branch returns the weighted BF16 route-term stack (lines245–248, 328–345). If routing weights are applied after FC2, it first rounds FC2 to BF16, multiplies the routing weight in FP32, then rounds the weighted term to BF16 (lines328–332). The separate before-FC2 placement remains governed by the same oracle flag.

For deterministic mode, the [comparison entry point](../flashinfer/tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py) requires BF16 bit equality (lines975–978). For IKR, it explicitly selects the established per-cell term-magnitude band (lines968–974), not bit equality. In [`mega_oracle_compare.py`](../flashinfer/tests/moe_ep/mega_oracle_compare.py), lines28–45:

```text
terms = oracle BF16 route terms converted to FP32
reference = sum(terms, topk)
tolerance = 1.0 + 0.05 * abs(reference) + 8 * 2**(-8) * sum(abs(terms), topk)
pass iff every abs(FP32(kernel_output) - reference) <= tolerance
```

The existing factor8 accommodates BF16 atomic accumulation order; this is the repository's established acceptance band, not a newly derived tight error bound. Require finite output/reference, preserve the reported worst margin and term magnitude, and do not describe an IKR pass as bit-exact. Do not widen the band for mixed clusters.

## Smallest useful deferred case

Start with EP2, M256/N32, preferred4/fallback2, atomic work IDs, dispatch return, H288/I448, T33, group6, two scheduler stages, four experts, top-k2, changing batches and boundary33. This reuses the current oracle and exercises partial channels/K, remote routes, empty source/all-empty/refill and more than one scheduler group. Pass `in_kernel_fc2_reduce=True` as the helper argument: putting it only inside `knobs` is insufficient because the helper overwrites that field from its argument. Keep `check_graph=False` and `graph_rounds=()` for this first case.

The project [`harness/correctness.py`](../harness/correctness.py) can reuse that reference without a new oracle. It needs a small explicit IKR option, dispatch-return validation and forwarding of the helper argument. Its current catalog hardcodes IKR off and its call omits that argument. The deferred assertion wrapper already calls the original comparator with all keyword arguments; receipts named `bit_mismatch` should instead identify IKR band failures when the option is added. Retain the existing synchronized first-compile safeguard and persistent runtime owner.

## Remaining boundary before final PR

A first smoke is not qualification of the exposed nine choices. After retained gains, cover N32/N64/N128, both physical preferred/fallback execution (including an explicit fallback-only diagnostic), partial channels, empty/refill state and both routing-weight placements. Group256/512/1024 affect FC1/FC2 transition boundaries; the small group6 case stresses transitions but does not enumerate the product catalog. If static copies are retained, qualify that existing scheduling mode too.

The routing helper fixes top-k2 (line1489); it does not stress higher-order BF16 atomic accumulation seen at production top-k8. The current helper explicitly prohibits IKR graph checks (line1665) and the graph comparator omits the IKR flag (line1686). Graph IKR coverage therefore needs a focused adaptation using the same term-stack oracle and comparator, with repeated replay/reset checks; do not merely remove the assertion. Full mixed IKR qualification has not yet run. Before an unrestricted merge claim, qualify these exposed paths or explicitly restrict their product exposure.
