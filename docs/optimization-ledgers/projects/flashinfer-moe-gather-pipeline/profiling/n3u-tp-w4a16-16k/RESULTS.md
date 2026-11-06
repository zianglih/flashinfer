# N3U TP8 / 16384 W4A16 native pipeline profile

The retained W4 pipeline is substantially tensor active in this workload. This profile does not support reopening the TMA output late-acquire or generic barrier-removal experiments. It does identify an independent work-removal question: the MMA skips the unused half of a partial K stage, while dequantization still processes that entire stage.

Both bounded metrics and SourceCounters captures passed, using the actual frozen production default, public benchmark profiler mode, original compiler options, and original routing. Full retained02de source inventory passes before/after; the per-process subset, unchanged managed cache, native compiled-library default resolution, register donation, and zero-local checks pass for all18 compiled FC1/FC2 images across metrics/PC replays. All1,792 FC1 and1,632 FC2 NCU PCs match the exact loaded ELF after explicit printer/address canonicalization. Root's independent proof is `audits/w4-n3u-profile-peer.json`.

| Diagnostic | FC1 | FC2 |
|---|---:|---:|
| Tensor active, % peak sustained elapsed | 86.88 | 73.29 |
| DRAM throughput, % peak | 32.49 | 58.73 |
| L2 throughput, % peak | 50.25 | 51.44 |
| L2 read hit rate, % | 67.07 | 53.66 |
| Issue active, % sustained active | 57.62 | 56.63 |
| Barrier stall observations, % active warps | 0.82 | 2.19 |
| MIO throttle observations, % active warps | 0.43 | 0.63 |
| Initial registers/thread | 96 | 128 |
| Dynamic shared bytes | 222208 | 222208 |
| Accumulator / output-store stages | 2 / 2 | 2 / 2 |
| Actual CLC | Yes | No |
| DRAM read / write bytes | 1120207360 / 494577664 | 1617077504 / 1448654336 |
| NCU diagnostic duration, us | 647.872 | 680.416 |

NCU application replay alters inter-kernel overlap. Its647.9/680.4us durations are not replacements for the previously collected native cold-CUPTI825.5/817.6us kernel spans and1947.9us E2E. Different-precision TRTLLM W4A4 remains a performance target, not a causal W4A16 regression comparison.

## Output-acquire attribution

The existing post-commit output acquisition compiles to `DEPBAR.LE SB0,0x1`. It is almost absent from samples. The larger preceding synchronization is the shared-write visibility/join before TMA reads the freshly stored epilogue tile; moving the subsequent acquire cannot remove that dependency.

| Scope | FC1 samples / PC | FC2 samples / PC |
|---|---:|---:|
| Output acquire | 2 / 0x4720 | 6 / 0x4ec0 |
| Following epilogue join | 21 / 0x4730 | 75 / 0x4ed0 |
| Pre-store shared-write join | 307 / 0x4680 | 922 / 0x4e20 |
| All sampled PCs | 38637 | 37768 |

These are warp PC observations, not runtime fractions or removable latency. The prior isolated FC2 late-acquire was already neutral. This fresh nongated profile also supplies no reason to revisit it.

The larger sampled pipeline dependencies include epilogue accumulator publication (FC1 query/branch5324, FC21528), transform raw-input readiness (FC14412, FC24567), and gather/activation stage reuse (FC12645, FC21679). The source/SMEM barrier offsets distinguish these from TMA output acquisition. Their existence while tensor activity is high is not evidence that any necessary wait can simply be deleted. Existing raw-ready lookahead and stage-inventory experiments remain closed.

## Bounded next lead: unused K-tail dequantization

FC2 uses logical K640 with a K256 stage. The MMA's existing compile-time tail section issues16+16+8 BF16 K16 atoms, so it already avoids the final128 padded K values. `_transform_tile`, in contrast, runs three full transform stages and unconditionally loads/dequantizes/stores both transform warpgroups for all three stages. The current native transform group coordinate is `(warp_id-8)>>2`; its destination offset is64 TMEM columns per group (128 BF16 K elements). Thus the current specialization has a whole transform group's last-stage work that no MMA consumes.

A general solution must derive validity from the actual layout and compile-time remainder, not N3U/model gates; retain every raw-consumer release, transformed-producer arrival, phase advance, and ownership boundary even when a role has no valid tail elements; avoid reading invalid scale/payload fragments; and preserve full-K binaries. `_transform_tile` is shared with MegaMoE, so a split call-site-only solution is preferred if concise; any signature/shared behavior change needs its MegaMoE callers qualified. No source implementation or new GPU experiment is made for this lead here. The layout partition and historical closed-lead audit must precede a minimal prototype.

Reproducible private harness, raw reports, native artifacts, exact commands and hashes: `driver.py`, `run_ncu.py`, `profile_pc_entry.py`, `evidence/`, `fetch.json`, `summary.json`, and per-stage `pc-proof.json`. Persistent caches remain intact. No sanitizers or performance retuning ran. GPUs0/1 were released after capture.
