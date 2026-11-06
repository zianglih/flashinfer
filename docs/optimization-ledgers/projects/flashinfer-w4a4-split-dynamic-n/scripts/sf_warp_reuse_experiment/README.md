# Reuse existing warp3 for compact SF loading and publication

Fresh independent actual-source clone at98fd, exactly two unstaged files.
Parent is frozen readiness core0f570a27; its source/artifacts are unchanged.
No API, weight layout, math, preparation, operand-stage or TMEM-slot changes.
The narrow gate remains generated-FP4 gated NVFP4 FC1 N16; other contracts
use98fd fallback code. GPU2 on replacement C1 B200-92, adjacent controls only.

Warp0 issues A, warp1 SFA, warp2 B; these keep independent persistent producer
states. Only warp1 waits shared SF-source empty. Warp3 alone loads SFB with32
cp.async participants, waits its completion plus SFA-full, then publishes both
scales into the existing two TMEM slots. It signals both published-full and
source-empty via TCGEN05 CP completion. MMA8 waits payload plus scales and
releases payload/TMEM slots after MMA; epilogue4–7 is unchanged. Total288
threads instead of320; four operand/source stages and128 TMEM columns remain.

Each lane owns one compact SFB row0..31. Per stage it writes both even words
of each512B atom with4B cp.async; invalid route rows and K64 groups beyond K
are explicitly zero-filled. Odd words are initialized once for every source
stage by warp3, followed by per-thread async-shared fence and warp sync.
Only this warp reads SFB SMEM for CP, so no additional CTA barrier is needed.
Even words always receive fresh data/zero before publication. Shared SF
source lifetime remains separate from payload lifetime; no padding is assumed
initialized by allocation.

The source loader/consumer states are four-stage rings; published SF uses a
separate two-stage state. All persist across channel/route tiles and advance
exactly once per K iteration. Source tails clone their state. The original
128-thread TMEM retrieval/deallocation protocol and288-thread final barrier
remain. This deliberately couples SFB load and SF publication in one warp;
reduced lookahead is a performance tradeoff, not a claim of free concurrency.

Before GPU launch: source hashes, Python syntax, diff check, CPU full-word
coverage, and independent barrier review. Focused exact GPU gate reuses the
frozen seven-case98fd oracle (K64/384/1216, quantized/per-token fallback, zero
routes); native T32 exact checks FC1/SF, FC2 and final full-chain bytes. Then
T32/T128 native fixedN16 ABA/BAB,10warmups/100cold-L2 CUDA-graph CUPTI samples
for every arm, same common inputs. Initial activation quantization is outside;
regular preparation is inside full chain and FC1 phase. No primary/AUTO rerun,
no old TRT ratio, no rigorous sanitizer before demonstrated performance gain.

Commands are in run_smoke.sh and run_pairs.sh. The current native helper is a
mechanical copy of the independently reviewed readiness helper with only
module/experiment names and assignedGPU changed; timing/input/oracle code is
unchanged. Each arm has separate actual-source classes and compile caches.

## Result

Unretained. Full-chain control/candidate ratios: T32 **0.987100x**, T128 **0.991679x**. FC1 ratios0.995391x/0.992238x; all36 arms exact. Fresh-cache seven-case fallback/tail/zero-route and native T32 smoke passed. Finalcore2c4fee74 repairs only static fallback lowering; earlier failedsource/compile receipts remain archived. Full evidence: `evidence/sf-warp-reuse-98fd/README.md`; raw archive SHA `d8350ba7344a765d6b16c9fa87851babfa0ec36091cd9fedac1e6eeb9c871c59`.

Static-count correction: Parse each address-bearing SASS instruction allowing mixed-case mnemonics; verify contiguous16-byte PCs. Report all instructions and a second count excluding only the final contiguous NOP suffix. Counts are static, not executed work. Corrected counts: control 1135 / candidate 1599 excluding final padding; 1144 / 1608 including padding. The earlier uppercase-only mnemonic parser omitted mixed-case TMEM operations; timings and immutable raw archives are unchanged.
