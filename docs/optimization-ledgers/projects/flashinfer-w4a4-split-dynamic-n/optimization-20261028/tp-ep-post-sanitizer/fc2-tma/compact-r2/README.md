# Compact FC2 ordinary TMA R2

Active unstaged review: `../../../../flashinfer-fc2-tma-review`, based on retained `2cfb06afd4a6e180af37615dd5f1cea1fc188691`. `local-source.json` binds the five-file candidate and patch. The prior R1 source, performance and traces remain immutable in the parent effort directory.

The candidate preserves control BF16 output capacity. A prepare CTA0 warp publishes per-tile compact offsets; the unique channel-zero FC2 owner publishes a separate dense inverse index. Combine reads that index only after its dependency wait and only for a valid local route. Complete slabs use ordinary 2D TMA; incomplete slabs retain the original row-major STMatrix and row bulk stores. No extra transpose, public knob, tactic axis, routing-capacity policy change or new alignment requirement is introduced. See `../COMPACT-DESIGN.md` and `ALLOCATION.md`.

Exact gate: source-paired short K384 and long K2304, plus natural 32-row/one-stage epilogue storage. Both sources use identical forced tactics, source-bound inputs, static/CLC, PDL off/on and mutable graph routing. The helper independently reconstructs local route sets, verifies reciprocal original sort mappings, prefix sums, dense index uniqueness/range, and output storage-bit equality. Full/partial slab mixes are recorded. PTX/cubin/SASS originate in a private per-process compiler directory; the gate checks identity, resource geometry, no spills and unchanged FC1 instruction sequences.

The gate does not qualify unsupported hidden sizes outside the existing multiple-of-128 boundary, exhaustive tactics, Rubin, or a candidate sanitizer. The existing full sanitizer qualification applies to the earlier retained source, not this experiment.

After all three gates pass, eight fixed-winner C–A–A–C jobs compare EP/TP for V3/K3, NVFP4 and MX formats at 4,64,4096,16384 tokens. NV includes input quantization and W4A16 as an unchanged-path sanity arm. Each accepted median contains 100 strict CUPTI cold-L2 graph samples after 10 warmups. Fresh source snapshots and independent caches bind both roles; the historical benchmark winners are reused without retuning. Host allocation and descriptor construction are outside the warmed graph timer.

Local transport commands (from project root):

```bash
python3 swap-ab-exact-20261027/remote.py optimization-20261028/tp-ep-post-sanitizer/fc2-tma/compact-r2/status_remote.py
python3 optimization-20261028/tp-ep-post-sanitizer/fc2-tma/compact-r2/fetch_evidence.py --name gate
```

Do not rerun deployment or launch helpers over an existing campaign. No source changes are retained until exact/codegen gates and matched EP/TP performance are reviewed.
