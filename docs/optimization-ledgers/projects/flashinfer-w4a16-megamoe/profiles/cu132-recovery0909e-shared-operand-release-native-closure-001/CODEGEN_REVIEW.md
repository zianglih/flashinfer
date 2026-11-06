# Shared operand-release native review

Both private captures completed with one `cute.compile`, zero callable launches,
device allocations or collective initializations. Actual source stayed retained
`af938d80`; native inventory stayed `d3cefec8`; closure found no GPU compute apps.
The proposed Mega kernel is `0afda8f8`, separate from the previous K128 trial.

Against the saved retained shared-layout native captures:

| Observation | N64 B3/D3 | N128 B3/D2 |
|---|---:|---:|
| Shared operand release | true | false |
| PTX mbarrier init | 34 → 31 | 30 → 30 |
| PTX tcgen05 completion commits | 3 → 2 | 3 → 3 |
| SASS non-NOP instructions | 5396 → 5380 | 5926 → 5926 |
| Registers / CTA threads | 96 / 640 | 96 / 640 |
| Stack / local bytes | 0 / 0 | 0 / 0 |

Neither PTX has local loads/stores; neither SASS has LDL/STL. N128's complete
6032-entry `(PC, instruction)` SASS sequence is identical to retained. Cubin
hashes differ, so binary identity is not claimed.

N64 decoded full barriers remain at 80/88/96 with arrival count 512. Decoded
empty barriers remain at 104/112/120 with arrival count 1. Activation full
barriers remain separate at 128/136/144, arrival count 1, with 32768-byte TMA
transaction accounting. Activation producer waits now use the decoded empty
base 104; both decoded producer loops also wait on that base. The former
activation empty barriers at 152/160/168 are absent, without duplicate init.
Both producer and operand readiness wait counts stay unchanged. The existing
universal pipeline initialization fence still follows all construction.

The common MMA K body now has one operand completion at SASS 0x8a50 following
the last MMA at 0x8a40, replacing the two retained commits at 0x8b80/0x8b90.
Accumulator completion remains separate at 0x8ac0. Later control offsets move
by 16 bytes after alignment, matching removal of 24 raw B3 barrier bytes and a
16-byte padded control saving. The resource report's static SHARED=1024 does
not measure the full dynamic shared-memory allocation.

Artifacts: sibling `shared-operand-release-m256n64c2-001` cubin
`84d114038843dcbd9c8450f3eb9585080922b09c2965830a5541050ba374a1a8`;
N128 cubin `0a065bdf4365d46b1d2fa0778692f9a3a3db06d9a824e3b432a20d43a9842ede`.
These compile-only results admit the authorized existing numerical cohort;
they do not yet establish numerical correctness or performance.
