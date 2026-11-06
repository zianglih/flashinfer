# Independent target correctness and qualification review

Reviewed 2026-09-25 from the local `results/*-cumulative-target.log` files, `benchmark_checked_v2.py`, the frozen candidate diffs, and `qualify_dispatch_overlap.py`. This review did not launch GPUs or alter candidate source.

## Target evidence

All three arms ran EP4 on B300, H6144/I2048/E256/K8, with 256 input tokens per rank and uniform routing. The environment records PyTorch 26.05, CUDA 13.2, and `nvcr.io/nvidia/pytorch:26.05-py3`. Every arm's input and weight fixture hashes match, as do all four final output hashes.

| Arm | Independent-reference rank checks | BF16 elements checked | Mismatch / nonfinite | Repeated output | Source unchanged | Target median |
|---|---:|---:|---:|---|---|---:|
| store16 | 4 | 6,291,456 | 0 / 0 | Bit equal | Yes | 329.827 us |
| counts_overlap | 4 | 6,291,456 | 0 / 0 | Bit equal | Yes | 340.899 us |
| parallel_payload | 4 | 6,291,456 | 0 / 0 | Bit equal | Yes | 327.491 us |

Executed source SHA256 values:

```text
store16          7a48709ed07bc8496908625b921927b04dbcca495d7a3b1ced9a7bd28d072234
counts_overlap   9bd9b0611dc1a575cac507a1e8f185b59abe51b72310f16589d0f7014ef08858
parallel_payload 94a939ede3ca316d23cd6aa640a1b0a17035c18aaa54d521b100fdb858d8a49c
```

The benchmark wrapper performs two untimed forwards after CUPTI collection, checks their finite BF16 bits agree, and compares the first against the existing independent numerical reference. This establishes winner-specific target correctness after substantial repeated execution. It does **not** independently check every timed graph replay or all eight candidates that autotuning timed. The source closure check is rank 0's digest of the shared source snapshot, not a per-rank generated-code audit.

All medians use 100 untrimmed, cold-L2 CUDA-graph CUPTI samples with per-iteration rank maximum. Counts selected N64/G1024/epilogue return (catalog index 6), whereas store16 and payload selected N64/G512/epilogue return (index 2). Counts is 0.9675x its immediate control; payload is 1.0071x. These are one sweep per arm in one direction. Counts has no demonstrated performance win; payload's small difference is insufficient to retain without a matched repeat. Timing and numerical correctness are separate conclusions.

## What the queued qualification adds

The first pass uses the same public layer/workspace on each frozen source, EP4, H288/I448/E132/K8, strided BF16/int64 inputs, and rank-specific 1/2/3/4 two-CTA clusters. Its 33 local experts stress a partial scheduler polling warp. It tests both epilogue return (index 6) and dispatch return (index 1).

For each tactic, nine routing/size phases include ownership migration, half input, wholly empty input, a single global token whose source owns no compute work, refill, score-only change, and restoration. Each phase checks the first updated graph replay, three queued graph outputs, then eager output. Ninety collective checks / 360 rank outputs per source must complete with finite bit equality and a passing terminal summary. The reference handles zero-local-input ranks by padded collection; wholly empty output is trivial, with refill providing the meaningful state check. Hot routing retains eight distinct experts per token.

The first local qualification log stopped before rank initialization because `torchrun --standalone` could not resolve the host name. That log is neither a candidate failure nor a qualification pass. The parent is preserving it and fixing the launcher to an explicit loopback rendezvous; this review does not modify that launcher. Do not count an absent `summary.json` or a start record as a pass.

Coverage limits that matter for retention:

- The first pass covers the counts target winner, but **not the payload/store16 target winner at index 2**. Add `glm5:full` with index 2 if payload remains under consideration; include index 6 for counts. Index 1 remains useful for the alternative return path.
- Run the full-grid GLM5 changing-routing/refill qualification on any retained arm. The small capped case deliberately changes scheduling pressure and cannot replace the native-grid case.
- Default routing weights apply after FC2. A retained staging/synchronization change also needs the existing FC1-weight-placement contract checked; `--apply-topk-in-fc1` is available for a separate focused run.
- Public forwards exercise live staging. Compilation of all four staging ABIs is not execution coverage of the raw prestaged path; payload adds a barrier even when `staging_inputs is None`, so that path needs a direct smoke/graph check if retained.
- Neither target checks nor this suite are sanitizer evidence. For payload's new NB11 handoff, use the existing EP4/O3 synccheck case after retention is plausible. Broader supported configurations should use the repository's existing numerical/sanitizer suite, without describing these focused checks as its replacement.

## Candidate-specific remaining risks

Counts releases the scheduler before full dispatch publication. Its risk boundary is counter generation, partial-warp acquisition, score visibility for compute-idle CTAs, and preserving activation/metadata gating. The candidate normalizes each rank contribution to high word 1, so heterogeneous source CTA counts are a necessary stress. Keep the one NB9 scheduler arrival, full-width system acquire polling, existing bank lifecycle, and original pull/FC1-ready gates. Native inspection should verify those exact operations; the separate pre-loop fence hypothesis remains conditional and is not part of this tested source.

Payload moves the unchanged BF16 copy to epilogue warps and adds NB11 with 256 participants. The risk boundary is one arrival from every epilogue thread and one arrive-and-wait from every dispatch thread, including empty/prestaged variants, plus each writer's existing async-global proxy fence. The source puts both participation sites outside the optional staging condition and retains the original global publication. Native inspection must still confirm barrier placement, copy-before-arrival, and the epilogue register increase after staging; a 96-register source declaration alone does not prove spill-free generated code.

## Ownership and promotion recommendation

Do not promote counts on these timings. A revised count candidate should remain a separate experiment with its own source hash, matched control, and repeated correctness qualification. Do not silently replace the frozen candidate while its queued tests are running.

If counts later earns retention, restore the experimental vendored `src/src/token_comm.py` change and move the changed publication behavior into the owned W4A16 adapter. The base publication method is monolithic: an owned `dispatch_barrier` override can reuse the existing grid-sync, NVLink, pointer-map and PTX helpers, with its copied baseline skeleton audited against the inherited method and only the packed contribution/order semantics changed. Avoid an upstream-style refactor or global monkeypatch. Re-run qualification on the actual owned port; movement between JIT methods can change generated code. Preserve the scheduler acquire override and update the owned source inventory/documented publication contract.

Payload already changes only the two owned W4A16 files; it needs no vendored-code port. If retained, transplant only its incremental delta relative to store16, keeping store16's independent decision separate. Re-run the exact winner target and focused stateful checks on the final integrated source. If both candidates are ever combined, qualify and time the combination independently: separate-arm passes do not establish combined barrier/latency behavior.
