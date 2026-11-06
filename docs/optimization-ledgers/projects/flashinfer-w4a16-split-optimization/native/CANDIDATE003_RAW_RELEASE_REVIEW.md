# Candidate003 raw-release native review

2026-09-13, read-only comparison of `candidate003-raw-release-{fused2,ordinary0}-m256` with corresponding `candidate002-full-m` captures. **PASS: the independent raw-stage lifetime is emitted exactly as intended.** No new compilation, GPU work or benchmark arithmetic was performed.

Actual kernel source is `e2da53cf8892143811bd69893456a7d79466e4a37d4e5a46d59a208bed649818`; wrapper remains `aa446d91adfd1335d59bf30acb8ed240f6b592bd78724d02f230cde7806fd90d`.

| Captured path | Last raw LDS | Final STTM.x8 | Raw arrival | TMEM completion fence | Decoded arrival |
| --- | --- | --- | --- | --- | --- |
| Fused top-k2 | `0x1ad0` | `0x2480` | `0x2490` | `0x24a0` | `0x24b0` |
| Ordinary top-k0 | `0x1ab0` | `0x2460` | `0x2480` | `0x2490` | `0x24a0` |

The complete raw SASS text differs only at those final three instruction slots in each kernel: raw arrival moves before the fence, and the fence dependency moves from raw arrival to decoded arrival. Every other instruction, operand, encoding and scheduling byte is exact to candidate002. Fused count remains1568 rows; ordinary remains1624.

Scheduling proof from the second64-bit encoding word:

- Raw arrival: `0x000fe20008100012` fused / `0x000fe20008100011` ordinary. Wait mask `(word >> 52) & 63` is0; it does not wait for TMEM completion.
- Fence: `0x000ea40000000200`. Write-dependency `(word >> 46) & 7` is2.
- Decoded arrival: `0x004fe2000810000f` fused / `0x004fe20008100010` ordinary. Wait mask is `0x4`, retaining the fence dependency.
- PTX independently shows last `tcgen05.st...x8` → raw `mbarrier.arrive` → `tcgen05.wait::st.sync.aligned` → decoded `mbarrier.arrive` (fused1836/1841/1846/1849; ordinary1826/1831/1836/1839).

Both decoder WGs share this emitted loop. The existing warp index minus8, divide4 and group-offset calculations select their disjoint partitions (fused SASS0x12e0–0x1400); there is no alternate WG path bypassing the moved sequence. All scale/raw loads and register decode precede store issue. The existing raw barrier still aggregates the required decoder-warp arrivals before a producer can reuse storage, so a faster WG cannot overwrite a slower WG's input. Decoded publication remains fenced separately. No later raw LDS occurs before the K-loop backedge. Source pipeline states, participants, stages and tails are unchanged.

Both results retain512 launch threads, REG128, STACK0, LOCAL0, static SHARED1024 and CONSTANT[2]12; CONSTANT[0]1888 fused/1856 ordinary. The static1024 figure excludes dynamic SMEM, which this compile-only helper does not export. Captures cover MMA128×64×256/C1, static, PDL disabled, N256/K512/M256/groups8, activation=None. SMEM-transform ordering is preserved by the source branch; this is not a native SMEM-transform or C2 capture. Root separately reports42 numerical tests and four long-K calls passed.

This establishes an earlier safe raw refill opportunity with zero instruction/resource growth. It does not establish a latency improvement. Root reports current full14 comparison +0.161942% latency GM8–8192 versus candidate002 repeat,7/11 lower; no timing result was independently regenerated here.

Result SHA256:

```text
fused2:    f98cb5f478b8af6e4dc561b3b7c6668be6d67e9a80f55b038ce800230380fda6
ordinary0: 293466cbe4d31b586fe2888e8c2800fcf88f80a4c2830ebf64cc735bc8af5d42
```
