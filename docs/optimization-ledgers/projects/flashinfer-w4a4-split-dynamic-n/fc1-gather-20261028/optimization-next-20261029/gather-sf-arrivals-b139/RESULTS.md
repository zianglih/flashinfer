# Static SF arrival ownership qualification

The frozen b139 candidate passed39 exact cases and all76 matched code-generation/resource guards. It reduces the local SF completion arrival count to the number of threads that can issue SF work for the physical route tile. No timing has been run.

## Source and ownership

- Control: `b13963b0cc8409aeb92048b9ec7cf3be18f0a57c`, kernel `f41712327504ba6bc4c1c2c28aeb7d38536fa0d59400f9c977ddf2eb2f041e4a`.
- Frozen candidate: `a0328bf10796226afaa5c999aed86d0f531154ee2ef8c0f252f41bd3aae8c780`; archive `5039d08e6766444fb041fbc6f6f1dc1eac14168452c15da7b9a622d8d25d27a2` (400 verified files). The reused control capture is independently preserved under `../accumulator-tail-b139/evidence/exact/control`.
- The actual-source proof enumerates194,048 row-block cases. The thread-to-SF-row mapping is a bijection on0..127. An excluded thread has `sf_row >= route_tile`, so all its row-block indices are outside the rounded dynamic MMA rows and it issues no SF copy. Physical N16/32/64/128/256 therefore uses17/33/65/129/129 total arrivals, including the unchanged Gather4 byte-count arrival.
- Selected threads still arrive on empty/partial tiles even if every copy is predicated off. Gather4 payload work, expected bytes, relay, stage reuse, PDL and all operand counts are unchanged.

## Generated code

- Captures cover physical N16/N128/N256, both CTA group sizes, static/CLC, all four formats and partial-K/activation cases. N32/N64 have the exhaustive ownership proof but no capture in this39-case set.
- All37 FC2 PTX files and all29 wide FC1 PTX files are byte-identical. Two identical-PTX cases (32FC1,35FC2) differ only by uniform-register renaming in the normalized SASS instruction stream; do not claim universal binary identity.
- The10 N16 FC1 captures change the initialized SF-local count129→17 for every pipeline stage. MMA, TMA, SF copy and static SF arrival instruction site counts remain unchanged.
- Narrow SF arrivals lower to a conditional branch around `ARRIVES.LDGSTSBAR.64.ARVCNT`, with BSSY/BSYNC reconvergence. This adds4–13 non-NOP instructions and1–4 branch/reconvergence sites per captured kernel. The saved work is fewer participating lane arrivals; the branch overhead requires measurement before a performance claim.
- REG, shared memory, register quotas, STACK/LOCAL and local instruction-site guards pass. The two inherited synthetic MX FC1 STACK168 cases remain unchanged; this is a no-new-spill result, not a claim that every captured kernel is spill-free.

| Capture | CTA group | Physical N | Non-NOP delta | BRA delta | BSSY delta | BSYNC delta |
|---|---:|---:|---:|---:|---:|---:|
| 010-FC1 | 1 | 16 | +4 | +1 | +1 | +1 |
| 012-FC1 | 1 | 16 | +4 | +1 | +1 | +1 |
| 014-FC1 | 2 | 16 | +6 | +2 | +2 | +2 |
| 016-FC1 | 2 | 16 | +7 | +2 | +2 | +2 |
| 018-FC1 | 2 | 16 | +13 | +4 | +4 | +4 |
| 020-FC1 | 2 | 16 | +13 | +4 | +4 | +4 |
| 022-FC1 | 2 | 16 | +4 | +1 | +1 | +1 |
| 024-FC1 | 2 | 16 | +4 | +1 | +1 | +1 |
| 026-FC1 | 2 | 16 | +6 | +2 | +2 | +2 |
| 028-FC1 | 2 | 16 | +6 | +2 | +2 | +2 |

## Local composition boundary

The local review now has base `77391e28d12a01e371196e76e56d4b46ace122df` and kernel `abec6f9ba4cbb3a26f7e88f6cbcdccf7268815245f68a6e7c7211b0e47bc5fcd`. Only the SF arrival patch remains unstaged; all513 other guarded files match the retained commit. `composition-77391.json` binds the original and composed sources. The immutable remote b139 candidate is unchanged. The composed source still needs focused qualification before timing or retention.

Replay: `python3 analyze_codegen.py`; the ownership proof is `independent_owner_proof.py`. No sanitizer, performance, or public-report update was performed.
