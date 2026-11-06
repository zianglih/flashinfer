# Shared FC1/FC2 CLC policy candidate

The independent, unstaged checkout is `../../flashinfer-shared-clc-20261026`, based on retained commit `9b4721b08057d0a488c1f0236467acb75c48cd00`. It changes the host tuner and existing tactic enumeration checks only. No kernel, benchmark, W4A16 runner, or Rubin geometry changes.

- AUTO emits 360 raw Blackwell tactics: 5 routed-token capacities × 3 FC1 geometries × 3 FC2 geometries × 4 K-depth pairs × 2 shared scheduler choices. The current full policy emits 720 by independently choosing the two scheduler booleans.
- New tuples are `(route_tile, gemm1, gemm2, k_steps, use_clc)`. The last boolean explicitly controls both FC1 and FC2. The existing lower-level launch flags remain separate implementation inputs, but the tuner resolves them from that one boolean.
- Legacy three-/four-field entries enable CLC for both phases. Three-field entries retain automatic K depth. Old six-field entries are rejected. The old experimental five-field meaning (FC1 choice with static FC2) is replaced by the shared choice; it is not silently retained as an independent default.
- Cache key `blockscaled_route_n_v5` prevents old v4 serialized choices from being loaded under the new format. v5 appeared only in an unretained local all-CLC experiment and has not been pushed/published. Benchmark workspaces must start without that experiment's cached v5 entries; production need not retain its local meaning.
- `verify_policy.py` evaluates the existing enumeration/extraction functions from their AST without importing CUDA modules. It verifies all 360 candidate tactics exactly match the corresponding equal-boolean subset of the full 720 launch parameters, and verifies unchanged extraction for all 8 Rubin tactics and unchanged enumeration of all 23 W4A16 tactics. This is a functional host-policy check, not GPU correctness or a performance result.
- Existing `TestTacticEnumeration` cases were updated in place. Scoped pre-commit passed (including mypy, ruff checks and format). The frozen remote candidate passed all 13 existing `TestTacticEnumeration` cases in 1.46 s with GPUs hidden; source hashes were unchanged. Full deployment/cache/CPU receipts are under `deployment-evidence/`. Native AUTO benchmark evaluation is a separate step.

Reproduce static proof from the project root:

```bash
python3 scripts/shared_clc_20261026/verify_policy.py
```

Focused existing CPU checks in the provisioned CUDA environment:

```bash
CUDA_VISIBLE_DEVICES='' python -m pytest -q -x \
  tests/moe/test_cute_dsl_fused_moe.py::TestTacticEnumeration \
  tests/autotuner/test_autotuner_configs.py \
  tests/autotuner/test_tactics_blocklist.py \
  -k 'not TestAutotunerIntegration'
```

## Frozen remote pair

Campaign: `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/shared-clc-20261026`. Arm A is clean retained 9b4721b0; arm B carries `policy-source.patch`. Each arm records its full `source.json` and verified `cache.json`. The paired source receipts hash 87 source paths; only the tuner and its existing test file differ. All device kernel source hashes and all 4,389 native dependency hashes match. Native C++ artifacts are reused from the persistent cache while each source receives a private DSL namespace. No AUTO cache was copied. `benchmark-config.json` supplies the immutable paths to the benchmark runner.
