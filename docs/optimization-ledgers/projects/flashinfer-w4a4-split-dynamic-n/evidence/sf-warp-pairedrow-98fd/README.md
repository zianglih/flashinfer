# Paired-row SFB copy mapping: unretained

Unretained: paired-row copy-site reduction compiles and remains exact, but full chain is1.27% slower atT32 and0.80% slower atT128 versus pinned98fd.

All seven saved-oracle cases, native T32 exact smoke, and36 timing arms/3600samples passed. The original baseline oracle was reused without rerun.

|Tokens|Phase|Control medians (us)|Candidate medians (us)|Control/candidate|
|---:|---|---|---|---:|
|32|full_chain|107.2165, 107.2640, 107.2320|108.0005, 108.6240, 109.1840|0.987438x|
|32|fc1|66.3040, 66.9125, 67.1040|67.3920, 66.9760, 67.1045|0.994272x|
|32|fc2|35.3280, 35.3920, 35.3920|35.4080, 35.3440, 35.4240|0.999397x|
|128|full_chain|143.9845, 144.4010, 144.0325|144.9125, 145.1365, 145.8085|0.992111x|
|128|fc1|89.5370, 90.3690, 90.0645|90.2245, 90.8160, 90.2400|0.995168x|
|128|fc2|47.9525, 48.0640, 47.9680|47.8715, 47.9360, 47.8400|1.002346x|

Same native inputs/routing; fixedN16 ABA thenBAB;10warmups/100cold-L2 graph CUPTI samples perarm. Input quantization excluded; regular prep included in fullchain/FC1. GPU2 on B200-92; adjacent controls only, no oldTRT or primary/AUTO comparison.

The intended compiler change occurred: publisher LDGSTS sites8→4 versus frozen localwait7f0fdbc4; new PCs0x2520,0x2550,0x2580,0x25a0. Startup scalar STS sites34→50 because upper-row even words become immutable zeros. Total static instructions1583→1591 excluding nine final padding NOPs (1592→1600 including padding). The98fd control has1135 excluding padding/1144 including. These are static sites, not executed counts or a causal performance attribution.

Resources unchanged from localwait:173056B dynamic SMEM,50registers,zero local bytes/noLDL orSTL,288threads,4source stages,2SFslots,128TMEMcols,one driver-reported activeCTA/SM. Control:197504B,64registers,otherwise same counts.

Coordinate ownership:128 refreshed words plus384 unique immutable padding words cover the2048-byte source stage. Both source-row and copy-valid predicates use row=lane%16; K64half=lane//16; invalid row/K groups zero-fill every reuse. All32 lanes keep commit/wait/proxyfence/warp-sync, and shared-source/TMEM completion stays byte-identical. Owner CPU model and independent full-byte oracle are archived separately from GPU evidence.

Control and nonpublisher fallbacks remain98fd. Parent separately retained minimal proxy fence aab93f854054de834447bdd8985b8bbd653fb3c8 during this screen; no source epoch change here. Negative gate gives no reason for another retention comparison.

Core SHA `72ce0c1159f23322677d45a3cfe486acb02ed3050003b2464a29e065874861ed`; unchanged utils `e14d3300a97fa508b0039065a6b29b876a0e14d20a5456ef18bf0a662c168274`; manifest SHA `5e72c63e2f62415f86eda51cb6edc46c7ba34feaa718d9ad891a8883b4c60d3b`.

Raw archive SHA `2a0b1481dc4d3cccafce42ac3a63acc9a719de6e029d6955b725484a4ccb6667`. Source,helpers,rawsamples,PTX,cubin,SASS,environment and checksums preserved. No broader formats/sanitizers follow this negative gate. Source changes remain unstaged in independent clone. GPU2 released; no additional axis launched.
