# R0 SF live-row poison qualification

Both source-bound arms passed **16 cases / 80 exact checks per arm**. Every production output hash equals its poisoned counterpart and the analytical exact output. No timings or sanitizer run.

- Four input modes: NVFP4, per-token NVFP4, MXFP4x8 and MXFP8; one- and two-CTA MMA.
- Route extents include 128/129 and tiny N16; NVFP4 K192/704/832 exercise K96 and mixed native tails. MX cases use K640.
- Twelve static cases use exactly one physical persistent cluster and 32 route tiles. Recorded compiled stage counts and source scheduler order prove 242 narrow-to-wide and 264 wide-to-narrow transitions through the same ring slot across the initial inputs. Four further cases use actual CLC.
- Each case checks initial eager output, initial graph capture, and three graph replays with changed routing/valid counts (including truncated active tile count and restoring the original pattern). Each case has three distinct output hashes, preventing a vacuous routing replay check. Padding remains the supplied sentinel.

The diagnostic-only clone adds an else branch when `row >= rounded_mma_n`. It issues the existing 4-byte cp.async from the first SF word, reserved by the harness as `0xffffffff` and never routed as real input. E4M3 and E8M0 interpret these bytes as NaN. This poison is tracked by the same noinc arrivals before the unchanged relay and S2T, so no untracked ordinary-store ordering is introduced. It does not modify the production candidate.

`diagnostic-source-proof.json` verifies that deleting this one diagnostic else block reproduces the production source byte-for-byte and that barrier/arrival/release sites are unchanged. All 128 noinc arrivals and the single explicit arrival remain present. `summary.json`, `fetch-receipt.json` and `evidence/fetch-manifest.json` bind all source, output and codegen artifacts. Archive SHA256: `103f15c97a39eeb471257a98bfc57cef4d18bf19216298ab7787cffff7b031c0` (141 files).

Production kernel: `5a3e56cb036eadc9513208849c11a089a47f5dc0db01d44e532411b3b6ba01d6`.
Diagnostic kernel: `4b889ff08af9675f9398f0d2180d76b58f81e17b291b4b77995e73f1f40ba35e`.

This validates the skipped-row consumption boundary for R0. The direct-predication revision still requires the same qualification against its own source hashes.
