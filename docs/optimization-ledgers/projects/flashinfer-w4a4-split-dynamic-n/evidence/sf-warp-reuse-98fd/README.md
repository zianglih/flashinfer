# Warp3 SF loading/publication: unretained

Unretained: full chain is 1.31% slower at T32 and 0.84% slower at T128; FC1 also has no repeatable gain.

Same-GPU adjacent control/candidate fixed-N16 screen on replacement B200-92. No AUTO or old-node/TRT retention claim. All36 arms (3600 samples) passed exact output checks. Seven saved-oracle cases and native T32 smoke passed in a fresh private cache.

|Tokens|Phase|Control medians (us)|Candidate medians (us)|Control/candidate|
|---:|---|---|---|---:|
|32|full_chain|107.3445, 107.2640, 107.1840|108.0165, 108.7040, 109.2810|0.987100x|
|32|fc1|66.4000, 67.0245, 66.9445|67.0560, 67.3760, 66.8640|0.995391x|
|32|fc2|35.3125, 35.4240, 35.3600|35.4080, 35.3920, 35.3920|0.999100x|
|128|full_chain|144.0645, 144.3685, 144.3200|145.1045, 145.4400, 145.8405|0.991679x|
|128|fc1|89.5840, 90.2725, 90.2250|90.6565, 90.9600, 90.5765|0.992238x|
|128|fc2|47.9680, 47.9680, 48.0000|47.9040, 47.8400, 47.8400|1.002452x|

Resource changes versus98fd:197504→173056B dynamic SMEM,64→50 registers,0 local bytes in both,288 threads,4 stages,128 TMEM columns,one driver-reported active CTA/SM in both. Static SASS instruction counts (not executed work): control 1135 / candidate 1599 excluding final padding; 1144 / 1608 including padding.

Initial source0669 failed per-token fallback compilation before launch because a mixed runtime/constexpr condition lowered the disabled publisher body. Final2c4fee74 adds an explicit constexpr body guard; supported operations are unchanged. Old source and failure are retained. An intermediate outer helper path error occurred after all7 cases completed; final exact-r3 reran from a fresh private cache and compared against the untouched saved oracle.

Core SHA: `2c4fee747528dc2bf6586b171c2757de5a3aaf4283867d0f233e7a3c7362319e`.
Archive SHA: `d8350ba7344a765d6b16c9fa87851babfa0ec36091cd9fedac1e6eeb9c871c59`.

Production98fd remains clean; candidate clone remains unstaged. Commands,source,PTX,cubin,SASS,100 timing samples perarm,environment,failures,and receipts are in the archive. No broader formats or sanitizer campaign follows this negative performance gate.

Static-count correction: Parse each address-bearing SASS instruction allowing mixed-case mnemonics; verify contiguous16-byte PCs. Report all instructions and a second count excluding only the final contiguous NOP suffix. Counts are static, not executed work. Corrected counts: control 1135 / candidate 1599 excluding final padding; 1144 / 1608 including padding. The earlier uppercase-only mnemonic parser omitted mixed-case TMEM operations; timings and immutable raw archives are unchanged.
