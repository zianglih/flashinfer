# Terminal-ticket peeling qualification

Candidate kernel `0e9aaafcfb86d915f9782f9b1003466218467f74b9c7d370f038ad4c74ecafec`,
patch `4d335388df87561e264c329860f4e9339a3e2dbba34c434ee4581d03a2d62b2b`.
The independent local review remains based on `61c2c367`, with only this kernel
unstaged. Canonical source was not edited.

- **Exact outputs:** 256 paired graph replay records per source, across four
  scaled formats, one/two CTA, static/CLC, and PDL off/on. Sixteen changing-route
  patterns include empty, padded, skewed, reactivated, full and partial tiles.
  H512/I384 exercises a partial K stage. Final output and valid logical
  intermediates/scales match exactly; invalid padding contents are excluded.
- **Ordinary scheduler:** all 16 PTX, cubin, SASS and resource files are byte
  identical between source arms, including full instruction/control encodings.
- **CLC:** the smallest SASS backward-edge envelope containing the CLC request
  has 10–14 fewer static sites. Terminal publication is now outside that loop;
  total kernel non-NOP sites change by 0 to +7. These are static code counts,
  not dynamically executed instruction counts or latency results.
- **Resources:** all 32 register/shared/local/stack resource records match.
  Local-memory and uniform-register spill/fill counts are unchanged.
- **Protocol:** 20,470 abstract trace cases preserve ordered acquire/request/
  publish/wait/release events and pipeline advances. Valid padding tickets are
  canceled and drained, and each local metadata pipeline publishes one terminal
  ticket. This CPU proof does not substitute for hardware synchronization tests.
- **Checks:** scoped pre-commit and diff checks pass. Sanitizer was skipped per
  user instruction. No public API, tactic list, shared CLC flag, queue depth or
  synchronization quorum changes.

`GATE.json` binds all receipts. `evidence-verification.json` verifies 299 raw
files in archive `c705bcc32151cfa98de3d4958c66f9cc18a983b139ca080c6efb8a4bf3d9aa22`.
Control source retains actual remote Git HEAD `61249` plus the prior retained
patch; all 348 source hashes equal committed `61c2`. The candidate remote has
actual HEAD `61c2` plus this scheduler patch.

GPU5 on `fi-moe-descriptor-recover-1028` ran the two paired lanes serially and
was verified idle afterward. The initial controller had a quoting error before
any GPU work; its log remains preserved. The corrected controller and frozen
source ran all qualification cases without errors. All native cache links were
retained and compiler outputs used separate working directories.

Root launched a separate matched 15-job screen with frozen winners and four
token counts. `winner-classification.json` identifies 50 potentially affected
cells (49 with both GEMMs admitted to CLC, one FC2-only), 62 explicitly static
cells and 32 unchanged W4A16 controls. Admission is reconstructed from actual
frozen cache-key shapes and host predicates; the existing B300 148-SM count is
an explicitly recorded assumption. No new device-property probe was run during
timing. Performance and retention remain pending that screen.
