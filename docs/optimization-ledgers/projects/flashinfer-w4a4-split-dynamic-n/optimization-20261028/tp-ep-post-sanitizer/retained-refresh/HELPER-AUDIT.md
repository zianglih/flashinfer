# Source-only refresh helper review

No measurement, source or scope blocker found in `prepare.py`,
`prepare_template.py`, and `benchmark-tools/run_job.py`.

- Preparation requires a clean exact requested head and binds source bytes to
  pinned Git blobs. The new remote snapshot has private DSL/Triton cache space;
  native compilation caches are reused only after verifying the native source
  paths are unchanged. No baseline source or timing file is edited.
- Each job uses native managed tuning once, then two frozen replays. Measured
  source and observers are checked around every phase. Winners, cache manifests,
  original routing hashes and GPU UUID are recorded. The observer verifies the
  expected backend set and preserves the public benchmark calls and native
  candidate admission order. It is byte-identical to the already qualified
  full-validation observer, including its timing guards.
- Public timing is CUDA graph + cold L2 + 10 warmups + 100 CUPTI samples, with
  event fallback forbidden. Native AUTO uses its existing profiling policy;
  tuning is forbidden while `_measure_or_profile` runs. NV retains its v1
  policy; MX uses the matching generic CUDA-graph policy for tune and replay.
- EP8/4/8/8 and TP8/4/8/8 with EP1 are explicit. NV times the initial quantizer
  where that arm consumes quantized input. K3 MX8 and TP V41 MX are omitted
  because no matching supported external comparison exists. The latter writes
  an explicit skip receipt. W4A16 is included without modifying its kernel.
- A complete fetched report must include per-token cache snapshots and frozen
  managed-cache files, not just `complete=true` receipts. The local report helper
  checks these, both before/after UUID records, raw medians and printed CSV.

This review is CPU/source-only. No deployment or GPU launch was performed, and
the future refreshed report cannot be marked complete until its raw evidence
passes the assembler. `helper-audit-receipt.json` identifies reviewed versions.
