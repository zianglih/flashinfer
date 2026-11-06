# R1 direct-predication SF poison qualification

Both source-bound arms passed **16 cases / 80 exact checks per arm**. Every production output hash equals its poisoned counterpart and the analytical exact output. No timings or sanitizer run.

- Four input modes: NVFP4, per-token NVFP4, MXFP4x8 and MXFP8; one- and two-CTA MMA.
- Route extents include 128/129 and tiny N16; NVFP4 K192/704/832 exercise K96 and mixed native tails. MX cases use K640.
- Twelve static cases use exactly one physical persistent cluster and 32 route tiles. Recorded compiled stage counts and source scheduler order prove 242 narrow-to-wide and 264 wide-to-narrow transitions through the same ring slot across the initial inputs. Four further cases use actual CLC.
- Each case checks initial eager output, initial graph capture, and three graph replays with changed routing/valid counts (including truncated active tile count and restoring the original pattern). Each case has three distinct output hashes, preventing a vacuous routing replay check. Padding remains the supplied sentinel.

The diagnostic-only clone adds a second `_copy_gather_sf` call with the complementary `row >= rounded_mma_n` issue predicate. Its helper and original call remain unchanged, and exactly one copy per word executes. It issues the existing 4-byte cp.async from the first SF word, reserved by the harness as `0xffffffff` and never routed as real input. E4M3 and E8M0 interpret these bytes as NaN. This poison is tracked by the same noinc arrivals before the unchanged relay and S2T, so no untracked ordinary-store ordering is introduced. It does not modify the production candidate.

`diagnostic-source-proof.json` verifies that deleting this one diagnostic call reproduces the production source byte-for-byte and that barrier/arrival/release sites are unchanged. All 128 noinc arrivals and the single explicit arrival remain present. `summary.json`, `fetch-receipt.json` and `evidence/fetch-manifest.json` bind all source, output and codegen artifacts. Archive SHA256: `c6caa2f128eb726ec78edfabb639049d20ffbcf8c892a7c16ce6ed77860fded5` (141 files).

Production kernel: `0046a405ab15ffc2b520e873165273fb08892046510978ea9d627be7dc7337f0`.
Diagnostic kernel: `adfa803fe1a8eef9517890b42a1de5e08323e02a62ac81f38bd8d2224a85d52f`.

All R0 and R1 production outputs also match byte-for-byte. This validates the skipped-row consumption boundary for the final R1 source; it does not establish a performance gain. The separate unpoisoned24-cell C-A-A-C screen is running.
