# Compact SFB broadcast plus physical N16

Separate unstaged98fd sourcecopy. Narrow static gate: generated-FP4 gated NVFP4
FC1 N16; per-token BF16, FC2, SF32 and other route widths retain98fd code.
Numerical epilogue is the independently byte-exact physicalN16 source verbatim.
No operand stage changes:4stages;1CTA M128; trueB/C16;10warps320threads.

One publisher uses existing tcgen05.cp.32x128b.warpx4 broadcast. Four512B
shared atoms store native K64 word pairs at wordcolumns0/2; columns1/3and
rows16..31 are zero. Producer row=tidx//4, word=tidx%4; atom index0..3,
Kblock=2*atom+word//2. Global canonical scale source remains unchanged.
Half-K standardSFB copy layout makes four CPs and16TMEMcolumns; MMA explicitly
uses SFBbase+2*innerK, versus canonical+4*innerK. All four TMEM warpquarters
receive the same16-token scale vector, satisfying the hardware access contract.
The discarded four-publisher STTM draft remains separately preserved and unmeasured.

Ownership: Cpingpong[0,16)/[16,32); SFslot0 SFA[32,64),SFB[64,80);
SFslot1 SFA[80,112),SFB[112,128). Allocation128. Full CPcompletion and empty
MMAcompletion use the prior two-stage independentSFpipeline. OriginalA/ABshared
stages still release afterMMA; unlikeTRT this does not yet separateSFsource
lifetime from operandpayload lifetime. No claim that this fullymatchesTRTorchestration.

The broadcast reducesSFBsharedstage4096→2048B, not toTRT's512B four-warpSTTM
layout. With trueB16, expectedoperandstorage4*(32768+4096+4096+2048)=172032B
plusmetadata. All originalproducer/MMA/epilogue warp assignments remain.

Before timing: independent CPU per-lane/column mapping check and seven actual
source paired cases. Then adjacent NV T32/T128 N16 ABA/BAB fullchain+phases,
10warmup100coldL2graphCUPTI, complete100samples and exact pre/post. No oldnode
TRT ratio reuse; source/env/cache hash epoch distinct. Broadercoverage deferred.

## Measured result and remaining dependency

Seven actual-source cases are byte-exact against the previously saved98fd oracle
(no baseline exact rerun).36native timing arms/3600samples verify pre/post bytes.
Full-chain control/candidate geomean ratios: T32 0.994396, T128 0.995735;
FC1 0.995544/1.000531, unchangedFC2 1.000760/0.999555. Do not retain this schedule.

Actual compiled FC1 resources: SharedStorage172928B versus197504B;
registers46 versus64;320 versus288threads;128TMEMcolumns;0localbytes;1residentCTA.
PTX/SASS confirms12 `CP32x128b.warpx4` perKstage,8SFA+4SFB (control16).
Source geometry and packing worked; the remaining publication path still waits
for joint A+SFA+B payload completion. CPcompletion then adds a serialized
cross-warp dependency that the original same-warp pipelining does not require.
This result does not test separateSFreadiness or early SFsource lifetime release.

[Summary](../../evidence/compact-sf-broadcast-98fd/summary.json), raw archive
SHA256 `d2694fea36e1e4aef365cd7f3034be5ad239c47ec05b8a513c6701bd3152e5c9`.
Unmeasured four-warp STTM draft is preserved at
`flashinfer-compact-sf-publisher-review`; no results attributed to that draft.
