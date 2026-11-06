# Dispatch stateful second-pass audit

All three completed runs pass the independent CPU audit of their raw records:

| Frozen candidate | Profile | Actual CGAs/rank | Collective checks | Rank outputs | Elapsed |
|---|---|---|---:|---:|---:|
| counts_fence | partial33, heterogeneous | 1, 2, 3, 4 | 135 | 540 | 66.51 s |
| counts_fence | GLM5, full grid | 74, 74, 74, 74 | 135 | 540 | 63.60 s |
| parallel_payload | GLM5, full grid | 74, 74, 74, 74 | 135 | 540 | 56.94 s |

Each run uses EP4, O3, FC2 top-k placement and native tactics 2/6/1: N64/epi/G512, N64/epi/G1024 and N128/reused-dispatch/G512. All nine phases run on the same outer workspace: initial full input, owner-0 skew, owner-3 skew, half input, global empty input, one global token routed to rank 3, random refill, identical routes/hidden values with changed scores, and exact restoration of the initial input. Each phase checks the first graph replay after updating input buffers, three queued graph replays with cloned outputs, and a subsequent eager call. Five executions per phase also exercise alternating counter-bank generations.

The GLM5 profile is H6144/I2048/E256/K8 with capacity256 per rank; partial33 is H288/I448/E132/K8 with capacity32 per rank, 33 local experts, strided BF16 inputs and Int64 IDs. Partial33 compile records confirm that every rank uses its intended heterogeneous grid. The full profile records 74 CGAs on every rank. Every nonempty output is checked against the existing independent BF16-bit reference; globally empty output is checked against an empty tensor. All 1,620 rank outputs have zero mismatches/nonfinite values. This includes repeated checking of the same numerical elements, not 1,620 independent input fixtures.

The audit verifies exact tactic/phase/execution coverage; source hashes and closure on every rank; unchanged fixtures across tactics; changed score hashes without changed hidden/routing hashes; restoration parity; skew ownership; and identical GLM5 fixtures between the two candidates. Source identities match `source-manifest.json`. There is no `.git` in the executed tar snapshots, and the reported base commit is not claimed as their final source identity.

The exact executed harness is preserved as `results/dispatch-stateful-second-pass/qualify_dispatch_overlap.executed.py` (SHA256 `d4de02f8e1549fb7a0c0545bb39ee5592601e8cafa3c84e403077f35aca082d4`). Current local source differs only by adding `OSError` handling around optional Git lookup; that branch was inactive for these tar snapshots. Raw logs, summaries, and every check are under `results/dispatch-stateful-second-pass/`.

Reproduce the CPU audit:

```bash
python3 optimization/audit_dispatch_second_pass.py
```

The machine-readable result is `dispatch-second-pass-audit.json`. This is focused candidate qualification: it does not cover O2, top-k placement in FC1, EP8, every tactic, sanitizers, or a future ownership port. Passing it establishes correctness for these exercised paths, not a performance benefit or a retention decision. Any retained count-publication port needs validation on the actual owned implementation; any retained new payload barrier also requires the separately planned synchronization-sanitizer check.
