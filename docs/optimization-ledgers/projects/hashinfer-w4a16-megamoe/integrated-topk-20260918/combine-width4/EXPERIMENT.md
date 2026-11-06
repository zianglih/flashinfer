# Width4 weighted combine O1

Source `54301c6000da5cdc1ce198e720b1a402a86651dc` is an isolated four-line
replacement on current PR8 `d01f074947d2cc754d6062c2b2ffe674e1577a34`.
Each worker handles four rather than eight hidden elements, with64-bit route
loads/output stores and8-byte derived alignment. First FP32 score multiply,
subsequent ordered packed FMAs, final BF16 rounding, barriers, oneCTA/SM,
fiveWGs, two dequant WGs and role register budgets remain unchanged.
No public knob or new tactic is introduced.

This is distinct from PR9 K1's score-free True mode and from adjacent/coalesced
width16 experiments. It targets decode worker coverage at the cost of more
repeated score/address work and prefill loop iterations. No benefit is assumed.

The104-file source freeze and independent source review are adjacent.
Scoped pre-commit hooks passed. No GPU pretest or sanitizer was requested.

O1 launched12:41:11.984UTC on2026-09-19, hu-pdx-15, boot
`0a0846f7-1ce1-4dcc-9876-1ca81df8001f`, PID/PGID149839,
startticks292011039, port30080. Namespace `decode13-benchmark` retains source,
launch, stage, progress, actual commands and all100 samples for each full13row.
It uses the unchanged six measurement helpers, AUTO4/O3/publicforward,
CUPTI CUDAgraphs/coldL2,3warmups and100samples at globaltokens
1,2,4,8,16,32,64,128,256,512,4096,8192,16384.

Primary controlA3 is retained3de on the same node/boot, with historicalA1
separately shown. Candidateparentd01 also includes534's benchmark documentation
and default-token-list changes; executed exportedbenchmark304a and explicit13
CLI remain unchanged. d01 removes the inner reducer guard that was already
constexprfalse at H7168. The control boundary is therefore explicit; it is not
an assertion of whole-repository source identity.

Retention waits the complete table plus104 finite bit-exact cross-arm outputs
against each control and source/process closure. Decode4–512 is the primary
summary; each4K/8K/16K guard remains visible. All samples and temporal-drift
limitations remain. No performance result or terminal qualification is claimed
by this preparation note.
