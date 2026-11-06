# Held scheduler-depth tactics: 16 depth3 plus two depth2

Source-only candidate atop exact current `autotune.py` SHA `6d7de539867400cb2c845309224ac8d7916bd7782818707cef660b3cc8ba97a5`. No production, kernel, scorer, cache API or other precision catalog is changed. This folder is separate from the earlier `w4a16_group_hint256_curated18`; those two different catalog proposals are not combined.

`source.patch` changes only `w4a16_candidates()`. Its first16 entries keep their exact order and every previous knob value, adding explicit `num_sched_stages=3`. Two independent dictionaries append with the existing field set to2:

| Appended index (zero based) | Geometry | Flags | Return | Scheduler depth |
|---:|---|---:|---|---:|
| 16 | M256/N128/K256, cluster(2,1,1) | 4 | reuse_dispatch_warps | 2 |
| 17 | M256/N64/K256, cluster(2,1,1) | 8 | epi_warps | 2 |

The additions follow their existing catalog order. The right-hand list comprehension completes before appending and copies the dictionaries; it does not extend an iterator over a growing list. Both retain group_hint512, epi_flag_batch(2,4), atomic_counter scheduling, two-CTA instructions and in_kernel_fc2_reduce=False. The kernel's selected B preference remains untouched and is not bound until the B4 verdict.

Explicit3 is required, not cosmetic. `apply_knobs` applies `with_knobs` to the current dataclass, preserving omitted fields. The tuner reuses one frontend through the sweep and then reapplies its selected winner. An old dictionary without this field would therefore retain2 after either new candidate. `_compile_key` already includes the field; the existing capture guard, workspace release and compile invalidation handle the change. No new public knob is introduced.

## Portable checks completed

```bash
python3 -B candidates/w4a16_scheduler_curated18/prepare.py
ruff check candidates/w4a16_scheduler_curated18
ruff format --check candidates/w4a16_scheduler_curated18
python3 -B candidates/w4a16_scheduler_curated18/validate_cpu.py
git -C flashinfer apply --check ../candidates/w4a16_scheduler_curated18/source.patch
```

All checks pass. The actual-AST extraction pattern reuses `w4a16_c1_curated16/validate_helpers.py`; the lifecycle assertion follows existing `test_w4a16_autotune.py` capture/config-change tests. `cpu-proof.json` records:

- Only the factory AST changes; restoring it gives whole-module AST identity, including the scorer and all other catalogs.
- Exact ordered first16 plus explicit3, only the two requested extras, 18 unique independent dictionaries, repeated factory calls independent.
- Actual `MegaMoEW4A16Config`, `apply_knobs`, `_compile_key`, `is_valid` and `with_knobs` host code exercised without Torch/CuTe imports. Both extras are followed by every old winner:32 actual2→3 transitions, including compile-key change, workspace release, compile invalidation and preserved clamp/config fields.
- The32 omission controls reproduce stage2 sticking when old dictionaries lack the field. A blocked capture-stage change preserves config and compiled state before release.

Only capture checking and workspace release are mocked. These checks establish the host selection/reset contract; they do not execute a GPU graph, compile a kernel or validate mixed-catalog numerics/performance. Initial style-check issues were corrected before the final successful checks; no production file was edited.

## Held execution plan

B4's global activation-preference trial remains next. After its verdict, select the then-retained kernel/source and apply only this factory patch if `autotune.py` still matches6d7; otherwise rebase the function delta while preserving unrelated scorer changes. This is not a declared runtime owner or an installed candidate.

For a later selected trial, reuse the existing full13 Mega-only AUTO100 controller and original scorer, input/routing/weight preparation, resource gates and sample metric. Make only the necessary existing catalog/parser expectations agree with18 dictionaries and their explicit scheduler field. Each13-point ranking then contains18 candidates, with104 final selected objects/choices and1300 primary samples. The existing scalar observer must reconcile actual kernel/scheduler params and allocation with each selected dictionary's2 or3, not a uniform default. Keep fresh knob/ranking/tactic files and all source/closure checks; no baseline/split/fixed rerun, scorer change or additional large knob grid.

The completed uniform-S2 trial supplied promising same-choice rows atT32/T64 andT4096 but was rejected as a default (near-neutral GM andT2 regression). It motivates these two tactics; it does not prove mixed-catalog results or establish causal fixed-tactic gains. Any retained catalog needs its own complete AUTO versus the then-retained accepted baseline. Existing original reference/oracle and lifecycle checks should be reused for actual selected-stage coverage; no new oracle or broad all16 lifecycle rerun is proposed here.
