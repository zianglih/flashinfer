# W4A16 MegaMoE preferred/fallback clusters

Refactor upstream FlashInfer W4A16 MegaMoE to support preferred `(4,1,1)` and
fallback `(2,1,1)` thread-block clusters, then qualify correctness and benchmark
against the unchanged current-main baseline. Preserve BF16 arithmetic and
transport contracts. Reuse established FlashInfer/CUTLASS protocols.

- Baseline: `316faec37a4706a2ecc7d46265087f8190b40baa` (2026-10-24 main).
- Candidate: `flashinfer/`, branch `feat/w4a16-mixed-clusters`.
- Prior effort: `/Users/ziangli/playground/projects/flashinfer-k3-w4a16-megamoe-opt`.
- Prior public optimization: https://github.com/flashinfer-ai/flashinfer/pull/6277.
- Benchmark contract and historical caveats: `BENCHMARK_PROTOCOL.md`.
- Current experiment status: `OPTIMIZATION_LEDGER.md`.
- Local `hai/` is an independent CLI working directory only; use the managed
  `/usr/local/bin/h`, never a checkout-local CLI or environment.

## Resources

Created C2 devbox `w4a16-mixed-cga-1024` in namespace `infra`, bare, 8 B300 GPUs.
The first `ziangli` namespace request had no quota and was deleted before the
`infra` retry. Existing user devboxes were not changed.

Image: `nvcr.io/nvidia/pytorch:26.05-py3`.
Live NVIDIA catalog/release notes checked on 2026-10-24: 26.05 includes CUDA
13.2.1, while 26.06 moves to CUDA 13.3.0. Runtime reports nvcc 13.2.78,
Torch `2.12.0a0+5aff3928d8.nv26.05`, driver 595.91.07, 8 NVIDIA B300 SXM6 AC.

Remote durable root: `/data/home/ziangli/flashinfer-w4a16-mixed-clusters`.

```sh
cd /Users/ziangli/playground/projects/flashinfer-w4a16-mixed-clusters/hai
/usr/local/bin/h ssh w4a16-mixed-cga-1024 -c c2 -n infra -- bash
```

## Design sources

- CUTLASS preferred/fallback cluster semantics, preserving complete 2-CTA MMA
  pairs and using actual runtime cluster geometry.
- FlashInfer SM107 generic inference mixed-CGA pipelines and scheduler.
- Byte-identical generic helpers in the SM100 GenPhase vendored snapshot,
  exposed through its public package/shim; vendored `src/` stays unchanged.
- Existing W4A16 scheduler, weight-dequantization pipeline, BF16 activation
  handoff, and epilogue semantics.

Candidate3r is committed and pushed as `3d047d3f8e7923118ffea8b8d36151504ab1fa3d`.
Upstream draft: https://github.com/flashinfer-ai/flashinfer/pull/7202.
The product catalog contains the original 16 tactics plus 18 new mixed choices;
the primary candidate comparison uses native AUTO over only those 18 new
choices. Baseline uses the original AUTO16. The completed fresh full13 comparison
uses per-source FlashInfer workspace caches and otherwise shared compiled caches;
earlier screens remain separate. Geometric-mean speedup is 0.992212x overall
(T4+), 0.991270x decode and 0.994731x prefill. No retained general gain is established.

All 2,600 untrimmed samples, all-rank winners, source manifests and reproduction
commands are frozen in `publication/final13-a1/` and published at
https://github.com/zianglih/flashinfer/tree/eb34175a2cc31befcc1e927db85c3628c5ae9e7f.

All 134 host-contract tests and scoped pre-commit checks on the 14 changed files
passed on matching source bytes. Earlier scheduler/smoke results do not qualify
the final revision. PC diagnostics confirmed physical preferred/fallback paths
but did not identify a diagnosed further pipeline bottleneck. Current numerical
and sanitizer qualification remains deferred.

The final bounded static-scheduler experiment at
`f14e4bae9379703fd5693d8ee993faae23e130d5` was rejected. Mixed-only AUTO36 swept
18 atomic and 18 static choices at T64/T128/T4096 against a fresh AUTO16 baseline;
all winners remained atomic, with ratios 0.980920x / 0.998785x / 1.007074x.
Both local and remote checkouts are restored to clean `3d047d3f`, with all 14
source hashes verified. The experiment branch and all helpers remain available.

The separate 600-sample trial, complete AUTO rankings, hardware audits, exact
source patch and restoration receipts are published at
https://github.com/zianglih/flashinfer/tree/623d698f45c2518243fdc11a849d2ed25e528b94.
PR7202 includes both independent experiments and remains draft; no performance
adoption or current numerical/sanitizer qualification is claimed. Upstream
pre-commit and documentation checks passed; GPU CI awaits maintainer authorization.
The C2 devbox remains available and idle. No further GPU jobs are running.

See `OPTIMIZATION_LEDGER.md`, `BENCHMARK_PROTOCOL.md`, and `evidence/`.
