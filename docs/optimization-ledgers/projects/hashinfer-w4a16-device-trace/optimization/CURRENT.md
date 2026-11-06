# Current W4A16 trace with complete dispatch-warp coverage

Draft HashInfer PR13 [private repository link omitted] is pushed at `cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7`. This follow-up expands markers only; the five changed package files across the full PR still match PR base computational AST after narrow instrumentation stripping. Original probes/waits, x8 stores and pipeline policy remain. No performance optimization is retained.

Fresh C2 capture: EP4, H6144/I2048/E256/top8, **128 global tokens (32/rank)** with uniform routing. All eight native tactics were freshly tuned; winner **N64/G1024/epi_warps**, score **274.111986µs** (maximum rank-median hot graph-event timing, not an end-to-end speedup). Independent reference and capture/baseline bit checks pass on all four ranks,196,608 BF16 elements/rank. Native full launch148CTA/74CGA; recorded cluster2CTA/40warp tracks per rank. Current-head pre-commit CI passes.

Each rank has eight dispatch prep/exchange/pull ranges, eight local-count waits, four actual CTA0 publisher ranges and eight input-publication waits. New per-K loader ranges distinguish free-SMEM waits from async TMA issue. Epilogue ranges distinguish readiness checks, compute/store and store-warp rendezvous. Final peer-return drain appears on eight WG2 tracks; actual reduction on sixteen transform tracks for this fixture. All133 native instrumentation points bind to original SM103a CUBIN sites, and all nativeJSON endpoints match their own Perfetto nanosecond timestamps.

- [Full audit and all8 candidate scores](marker-coverage-20260925/audit-2/audit.md)
- [Fresh rank2 trace](marker-coverage-20260925/cd7cc07-ep4-global128-rank2.pftrace)
- [Fresh trace observations](marker-coverage-20260925/PR-trace-snippet-v2.md)
- [Chronological ledger](EXPERIMENTS.md)
- [Architecture selection study at40d0ceb](arch-target-20260925/DECISION.md)

**Upstream sync is deferred:** earlier four-file tracing port74ba96d remains in [FlashInfer PR5019](https://github.com/flashinfer-ai/flashinfer/pull/5019), but this marker-coverage follow-up has not been synced. Neither PR is merged. Trace files, disassembly and external audit helpers remain outside both repositories/PRs.

C2/infra devbox **fi-w4a16-trace-0925** remains allocated on **hu-pdx-38**,8B300, image `nvcr.io/nvidia/pytorch:26.05-py3` with the recorded digest. GPU work is complete; keep the devbox for iteration. Prior40d0trace, failedcaa6189compile attempt, and all historical optimization/architecture evidence remain preserved and must not be relabeled as current-head measurements. Perfetto UI opening is currently blocked by the locked Mac; the new traces are ready locally.
