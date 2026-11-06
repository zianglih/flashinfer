# Terminal PDL wait removal qualification

- Source: retained `02de7785` versus one three-line deletion; candidate kernel SHA256 `ec0f3685f42df89160ad1840ad561e728ec757623327bdb2ced29e51d74adb02`.
- Six paired exact numerical calls cover W4A4, per-token NVFP4, MXFP4x8 and MXFP8; one/two CTA, static/actual CLC, PDL on/off, route N16/N32/N128/N256, and partial K.
- Four graph cases per arm cover one/two CTA × static/CLC. Each captures once and replays changing routes: active → empty → partial → active → empty, with strict exact reference and zero-output checks for empty local routes.
- All 14 processes passed. All 27 paired native kernels have zero local and stack usage; no register increase. FC1, combine, and PDL-off cubins are byte-identical.
- Every affected FC2 capture removes exactly one native `ACQBULK`; remaining non-NOP count falls by 2–5. Full decoded operands and encoded control words remain in the comparison; this is not a claim that all other instructions are identical.

| Captured FC2 | Route tile | CTAs | CLC | Registers before → after | Non-NOP change |
|---|---:|---:|:---:|---:|---:|
| mxfp8-13-01 | 16 | 1 | True | 76 → 74 | -2 |
| per-token-10-01 | 256 | 1 | False | 144 → 144 | -4 |
| w4a4--1-01 | 16 | 1 | False | 82 → 82 | -5 |
| w4a4--1-04 | 16 | 1 | True | 76 → 74 | -2 |
| w4a4--1-06 | 32 | 2 | False | 70 → 68 | -4 |
| w4a4--1-08 | 32 | 2 | True | 72 → 70 | -3 |
| w4a4-14-01 | 32 | 2 | True | 72 → 72 | -4 |
| w4a4-9-01 | 128 | 1 | False | 98 → 98 | -4 |
| w4a8-2-01 | 32 | 2 | False | 82 → 80 | -4 |

Evidence: `summary.json`, `full-evidence/`, and `full-fetch.json`. Source safety peer review: `../../audits/terminal-pdl-peer.md`; full manifest inventories were verified before and after execution. Persistent native compilation cache and compiler options were preserved.

Boundary: this is bounded exact/codegen/resource qualification. It does not include sanitizer, a full accuracy suite, or performance timing. The separately prepared 56-cell same-GPU CAAC screen is responsible for performance assessment. GPU2 was released after these checks.
