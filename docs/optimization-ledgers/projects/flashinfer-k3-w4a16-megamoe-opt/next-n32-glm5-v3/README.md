# Optional GLM5 N32 follow-up: full32 FC1 and adjacent-pair FC2

Prepared locally only. The owner decides whether to run this after the v1-retry
FC1-N16 and FC2 results. This bundle replaces the unused v2 follow-up if selected;
never launch v2 and v3 for the same full32 arm. Existing sealed bundles, source,
and captures are unchanged. Preparation performs no GPU compilation, benchmark,
correctness run, sync, or dispatch.

The default runs exactly these two independent candidates serially, restoring
exact `866c80d0c70a90624b4c2056d12d1543d709609e` between them and at exit:

1. `glm5-n32-fc1-register32-v2r1`: unchanged frozen full32 shared-body patch,
   `bf16_nvfp4/epilogue.py` only (+57/−28, net29). Static N32 replaces the FC1
   scratch transpose with register shuffles, releasing after raw reads. All
   original arithmetic is shared. This arm has the same name and source bytes
   as the still-unused v2 bundle.
2. `glm5-n32-fc2-adjacent-mul-v3r1`: independent FC2 direct-pack plus early-release
   candidate, with FP32 multiplication paired inside each raw fragment. BF16
   conversion interleaves top/bottom values. Changes are confined to
   `epilogue.py` and `tmem_epilogue.py`. The candidate is applied to866c, not on
   top of the full32 FC1 arm. The frozen FC2 release sequence is unchanged.

Explicit `--arm` accepts either candidate only. The completed
`runs/glm5-n32-866c-control-v1r1` is strictly validated and reused, never replayed.
The owner must not dispatch an arm whose capture directory already exists.

- **Protocol:** native AUTO16, EP8 GLM5 D6144/E2048/N256/K8; global tokens
  **1,2,4,8,16,32,64,128,256,512,4096,8192,16384**; one sweep, 100 cold-L2 CUPTI
  samples and 3 warmups per point. Only T1/T2 are excluded from retention.
  Precomputed routing is untimed; routing weights remain in deterministic
  combine. PDL enabled, fused TMA/in-kernel FC2 reduction disabled, deterministic
  fused combine active. No decoder, scheduler, AUTO16 catalog, test, reference,
  benchmark, runtime, or persistent-cache-policy change.
- **Foundation:** copied from corrected `next-n32-glm5-v2-retry`, derived from
  `next-n32-glm5-v1-retry`. Preserve the five standard editable data links and
  checks on the actual `bf16_nvfp4/autotune.py` and shim autotune adapter.
  Native harness, strict reporter, comparer, control and test maps are unchanged.
- **Isolation:** project-owned `flashinfer-n32-glm5` checkout; existing successful
  K3 gate; held `.k3-perf.lock`; idle eight-B300 check; exact source, test and
  submodule validation; **45-minute timeout per arm**. Save before bytes and
  restore exact866c before the next arm and at exit. Surviving GPU processes
  defer restoration for owner inspection. No package installation, profiler,
  sanitizer, unrelated-process cleanup, or baseline replay.
- **Evidence boundary:** source mapping/AST proofs are copied under `evidence/`.
  Both candidates remain uncompiled and unmeasured at preparation. FC2 archived
  SASS is a historical N64 lowering precedent; it does not establish extra
  moves or a gain in the new N32 candidate.

## Local preparation and dry run

```bash
python3 -B next-n32-glm5-v3/prepare.py \
  --candidates next-n32-glm5-v3/candidates.json
python3 -B next-n32-glm5-v3/follow_on.py --check-only
python3 -B next-n32-glm5-v3/follow_on.py --check-only \
  --arm glm5-n32-fc2-adjacent-mul-v3r1
```

The manifest seals all inputs. Never rerun preparation over a sealed bundle.
Check-only verifies the seal and prints commands; it neither inspects GPUs nor
contacts the devbox. Default prints two commands in the order above, and an
explicit arm prints one. Control and unknown names are rejected. Compact runner
and preparation deltas against v2 are included under `evidence/`.

## Owner dispatch, only after review

Transfer this directory with the established managed HAI workflow. After v1-retry
has finished and restored control, the owner may select the default two-arm run:

```bash
python3 -B /data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/next-n32-glm5-v3/follow_on.py \
  --check-only
python3 -B /data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/next-n32-glm5-v3/follow_on.py
```

Default receipt: `queues/n32-glm5-v3`. An explicitly selected candidate uses
`queues/n32-glm5-v3--<arm>`. Captures retain the exact arm names in `runs/`.
Collector ownership stays separate; this bundle never downloads or publishes.

After collection, use a fresh output name:

```bash
python3 -B next-n32-glm5-v3/compare.py \
  --output evidence/n32-glm5-v3r1
```

Comparison retains historical GLM columns, fresh866c control, and every completed
candidate's full13 medians, raw samples, IQRs, selected tactics, and speedups.
Earlier N16/FC2 reports remain separate. No samples are pooled and no retention
conclusion is automatic.
