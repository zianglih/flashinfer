# Bounded follow-up structural validation

Wait for the parent's final source freeze; deployment and launch assert its base,
patch hash and changed source hashes. The earlier `validation/relocation`
deployment captured an intermediate source and has no GPU validation; preserve it
as a source-only receipt and use a new experiment name for the final candidate.

Reuse completed phase1 candidate artifacts as the control, explicitly retaining
their original `ed67 + d7cb` identity and independently verified equivalence to
all 87 Git source blobs at `1fab0dc8`. Do not relabel them as freshly measured
clean-commit controls. `run_reused_candidate_gate.py` records the original role,
receipt/result hashes, same GPU UUID, unchanged probe hash, and exact filtered
result hash. Artifact files are symlinked from the immutable earlier capture.

GPU0 replays configs 0–3; GPU1 replays configs 4 and 7. These six cases compile
24 GEMM variants and compare 48 exact route replays, covering both FC phases,
PDL off/on, narrow/wide output, inline/dedicated epilogues, both CTA groups,
standard/per-token NVFP4 and both MX formats. PrepareRouted artifacts are also
compared where compiled. The original probe and timing-free public closures are
unchanged. No new AUTO search or performance run is performed.

`compare_codegen.py` is the phase1 comparator and checks normalized assembly,
actual instruction encodings/control words and resources, not raw cubin bytes.
The CPU import smoke checks existing W4A16/prepare dependencies, common utility
reexport object identity, restored helpers and the new epilogue ownership.
