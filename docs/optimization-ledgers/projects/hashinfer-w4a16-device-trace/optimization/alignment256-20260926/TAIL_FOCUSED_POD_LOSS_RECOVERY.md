# Focused campaign pod-loss recovery

The original C2 devbox pod `devbox-fi-w4a16-align256-0926-0` disappeared during phase C2. Its durable campaign directory survived at `/data/ziangli/hashinfer-w4a16-device-trace/alignment256-20260926/tail-variants-focused-v1`. A replacement pod on hu-pdx-43 was used only to observe and copy the old durable files. It does not supply measurements to this audit.

The existing failed-B1/SIGTERM recovery tools were deliberately not applied: they require a different schedule and finished nonzero-exit receipt and would reset campaign state. Frozen focused runner/auditor files remain unchanged. The original campaign was neither resumed, promoted nor relabeled as a kernel/CUPTI failure.

## Preserved evidence

- Remote snapshot: `/data/ziangli/hashinfer-w4a16-device-trace/alignment256-20260926/recovery-tail-focused-pod-loss-v1/snapshot.tgz`.
- Local snapshot: `tail-focused-pod-loss-v1.tgz` and extracted `tail-focused-pod-loss-v1/`.
- 473 immediate files were copied and individually checked by size/SHA256: original campaign, every present run receipt/log, rank closure, and winner PTX/CUBIN/SASS/resource/target artifact. Partial C2 files are included exactly as found.
- Snapshot archive SHA256: `45d6d938a3ad1022e3598c896113f87bb4e302131810b998cfadbf479afe30d6`.
- Recovery manifest SHA256: `9c97e55c89804e11313dbaced9431129b1eaa06a202b2ca7dfbc238bbd09ea5a`.
- Original campaign SHA256: `5f566f9c12c84ee11fc26c065d16d859899ef84cd3aa424df41adcaafda8aa27`, rechecked remotely after local audit with no change.
- Transfer proof: `tail-focused-pod-loss-v1-transfer.json`.
- Cache/compiler-dump trees remain untouched in the original durable directory. The snapshot contains their paths, types, sizes, modes and mtimes, not their bulk bytes or full content-hash closure. No deletion or full-cache preservation claim is made.

## Partial audit boundary

`audit_interrupted_tail_campaign.py` passed for recorded closed phases **A1/B1/C1/D1/D2**, using the existing immutable source/receipt/tuner/output verifier. Every completed trial is from original node hu-pdx-38, boot `1b51b917-b064-4570-afbb-5acd4c450cd9`, with matching GPU identities and fixture hashes. All 80 selected winner exports have STACK0,LOCAL0 and no native LDL/STL or PTX local loads/stores.

C2 is present but interrupted (`passed=false`, no completed exit); 42 immediate C2 files are preserved. No C2 timing row is admitted, even where a shape may have finished. B2 and A2 are absent. The partial report uses only A1 versus each first candidate sweep, 100 samples each. D2 is retained for candidate repeat-drift diagnostics; it is not pooled against the single 100-sample A1 control. No fabricated A2, unequal sample pooling, cross-node pooling, or positive retention claim occurs.

Results and all provenance are in `tail-focused-pod-loss-partial-audit-v1.{json,md}`. First-pair speedups at T128/4096/8192/16384 are:

| Candidate | T128 | T4096 | T8192 | T16384 |
|---|---:|---:|---:|---:|
|B late/no-prefetch|1.017591×|0.991769×|0.998685×|1.005876×|
|C participant96|1.011399×|0.988098×|0.990156×|0.991037×|
|D score-only|1.020429×|1.005987×|0.994409×|1.003350×|

D2/D1 median ratios are 0.999608/0.993575/0.986907/1.002647 respectively. These provisional differences do not qualify a retained optimization. Parent is starting a separate all-eight-phase campaign named `tail-variants-focused-r2-v1` on hu-pdx-43 with the unchanged frozen runner. Every source must receive fresh measurements on that node; no old phase is imported.

## Recovery helper commands

The collector is standalone standard-library Python and performs no GPU queries or launches. It writes only a new archive outside the original directory:

```bash
python3 snapshot_interrupted_campaign.py \
  --campaign /data/ziangli/hashinfer-w4a16-device-trace/alignment256-20260926/tail-variants-focused-v1 \
  --output /data/ziangli/hashinfer-w4a16-device-trace/alignment256-20260926/recovery-tail-focused-pod-loss-v1/snapshot.tgz \
  --incident 'Original pod lost during C2; preserve all original-node evidence without resuming.'
```

That exact output already exists; do not overwrite it. After verified extraction, the partial audit command is:

```bash
python3 -B audit_interrupted_tail_campaign.py \
  --snapshot tail-focused-pod-loss-v1 \
  --output-prefix tail-focused-pod-loss-partial-audit-v1
```

The shown report prefix also already exists. Use a new versioned prefix for any new audit.
