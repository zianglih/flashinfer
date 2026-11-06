# Warp3 local completion: unretained

Unretained: full chain is1.20% slower atT32 and0.83% slower atT128; final bounded localwait refinement closes this experimental round.

Fresh-cache exact gate: seven saved-oracle cases, including K64/384/1216, persistent routes, per-token BF16 fallback and zero routes; nativeT32 FC1/SF, FC2 and final bytes exact. All36 timed arms and3600 samples passed exact pre/post outputs. Original oracle reused without rerun.

|Tokens|Phase|Control medians (us)|Candidate medians (us)|Control/candidate|
|---:|---|---|---|---:|
|32|full_chain|107.2645, 107.2645, 107.3285|108.1120, 108.5760, 109.0240|0.988172x|
|32|fc1|66.4000, 66.8800, 66.9445|66.8805, 67.1680, 66.6880|0.997447x|
|32|fc2|35.3605, 35.3280, 35.3120|35.2960, 35.4240, 35.3285|0.999548x|
|128|full_chain|144.3360, 144.0485, 144.2240|144.8805, 145.4405, 145.8725|0.991785x|
|128|fc1|89.3760, 90.3045, 90.2720|90.2885, 90.8650, 90.2405|0.994682x|
|128|fc2|48.0165, 47.8885, 47.9520|47.9200, 47.9525, 48.0320|0.999670x|

Method: same native inputs/routing, fixedN16, ABA thenBAB,10warmups/100cold-L2 CUDA-graph CUPTI samples perarm. Input quantization excluded; regular preparation included in fullchain/FC1. GPU2 on replacement B200-92; same-node adjacent98fd controls only, no primary/AUTO or oldTRT comparison.

Control→candidate resources:197504→173056B dynamic SMEM,64→50 registers,0 local bytes/noLDL orSTL in both;4 operand/source stages,288 threads,128 TMEM columns,one driver-reported active CTA/SM. Static SASS instruction counts (not executed work): control 1135 / candidate 1583 excluding final padding; 1144 / 1592 including padding. Candidate keeps physicalB/C16,compactSFB2048B/stage and two TMEM SFslots.

The measured change replaces warp3 SFB full-barrier self-handoff with every lane executing commit_group→wait_group0→generic-to-async shared proxy fence→warp sync. Existing SFAfull/sharedsourceempty/TMEMfull-empty and TCGEN after_thread_sync fence remain. PTX contains all four intended completion instructions. All56 iKET calls remain by independent AST review. The unused ab.full initialization remains to isolate this hot-path change.

Pre-fence source dfcf99ba was preserved as unmeasured r1. Reviewed/measured core SHA `7f0fdbc4c53c9c0a7ac222e87d548269184b1fcce333d8a76f1af543bd880b4d`; utils unchanged e14d3300. Manifest SHA `4dcca16851e04055191a265dc94add47ed4deff1f1ae807555aaf1872c442797`.

Raw archive SHA `4dcaedbc193f7b4251eb7e73b9677afe32d908a1d219675c4c61a4fb19e8299f`. Source,helpers,100samples/arm,PTX,cubin,SASS,environment and unmeasured source receipt are preserved. Independent review is in local-evidence/review.json. No broader format campaign or rigorous sanitizer follows the negative performance gate. Historical inherited proxy-ordering audit is separate; no observed mismatch is claimed.

Production98fd remains clean; all experimental changes remain unstaged in independent source copies. GPU2 released; no further GPU axes in this round.

Static-count correction: Parse each address-bearing SASS instruction allowing mixed-case mnemonics; verify contiguous16-byte PCs. Report all instructions and a second count excluding only the final contiguous NOP suffix. Counts are static, not executed work. Corrected counts: control 1135 / candidate 1583 excluding final padding; 1144 / 1592 including padding. The earlier uppercase-only mnemonic parser omitted mixed-case TMEM operations; timings and immutable raw archives are unchanged.
