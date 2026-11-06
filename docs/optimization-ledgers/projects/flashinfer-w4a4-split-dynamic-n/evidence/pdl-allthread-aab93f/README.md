# All-thread early PDL publication

Not broadly retained yet: all-thread publication restores isolated wideFC2 throughput, preserves T4full1.048780x, but T16384full0.985217x still has1.50%residual loss.

Actual-source `flashinfer-pdl-allthread-review` from corrected `aab93f854054de834447bdd8985b8bbd653fb3c8`, exactly two unstaged files. All previous sources and evidence remain frozen. Production unchanged.

|Tokens|Route N|Phase|Control medians (us)|Candidate medians (us)|Control/candidate|
|---:|---:|---|---|---|---:|
|4|16|full_chain|49.7280, 49.7925, 49.7920|47.3600, 47.4560, 47.5520|1.048780x|
|4|16|fc1|28.8960, 29.3125, 29.2800|28.1605, 28.2880, 28.2880|1.032458x|
|4|16|fc2|16.1920, 16.1280, 16.1600|16.3200, 16.2560, 16.2565|0.992782x|
|16384|256|full_chain|483.0900, 484.0175, 484.0655|492.3540, 490.1455, 490.4500|0.985217x|
|16384|256|fc1|220.8650, 226.7845, 225.2805|221.3610, 234.5130, 225.6970|0.987545x|
|16384|256|fc2|133.4720, 133.3445, 133.5680|133.3285, 133.3610, 133.3130|1.000955x|

Same actual native input/routing and fixed N16T4/N256T16384 tactics, A/B/A/B/A/B pertoken,10warmups/100cold-L2 CUDAgraph/CUPTI perarm. All36phase/full arms and3600samples pass exact output/SF/final checks before and after timing. No samples or medians filtered. Fullchain/FC1includeactualpreparation; inputquantizationoutside. No primary/AUTO/TRT rerun.

Only revision from ac1: every thread executes the common earlytrigger. Under the static nonfusedFC2&&PDLon contract, every triggering thread first performs its own device release after the existing prerequisitewait. This removes the elected-issuer controlflow without any bypass of metadata publication, addedCTAbarrier, or token/geometrydisable. FC1 trigger/preparation stay early; arithmetic/layout/roles/stages/grid unchanged. Source labels `publisher` and older observer text are legacy arm names, not SFpublisher changes.

|FC2 resource|N16 control/elected/all-thread|N256 control/elected/all-thread|
|---|---|---|
|Registers|94 /94 /94|120 /122 /120|
|Dynamic SMEM|197504 /197504 /197504|229888 /229888 /229888|
|Local bytes|0 /0 /0|0 /0 /0|
|Threads|288 /288 /288|288 /288 /288|
|TMEM columns|128 /128 /128|512 /512 /512|
|Driver CTA/SM|1 /1 /1|1 /1 /1|

Regenerated same-invocation FC2codegen pins correctedcontrol, ac1electedFC2, and adccallthread. N16PTXwait145→release147→trigger149; N256wait141→release143→trigger145, exactlyone site each. Compiler artifacts are explicitly regenerated, not timing-process cubins. Native N256 FC2 has channels7168/K2048/experts32; allstaticparameters andgeometry equal.

WideisolatedFC2 returns tocontrol; widefullchain remains about7us slower. The candidate FC1middle median234.513us is retained alongside221.361/225.697; no noise-based exclusions or causal cacheclaim. The original large regression was mostly an avoidable compiler controlflow expansion; remainingwholechain loss awaits independent timeline/cache evidence.

GPU2B200-92 UUID `GPU-7e973000-5213-bf29-4ca1-25a6d947f8e3`,NVIDIAPyTorch26.05-py3/CUDA13.2.78/CuTe4.7.1. Same-node adjacentcontrols only.

CoreSHA `adcc6506dd4ba28769cf7a5f65526e9dc927363847150de231eb850cc6c9b4b9`; prepSHA `a3b0042ea0ae64f66cfc968768c85b96118ed750fa92a668cb1485f91866a67b`. RawarchiveSHA `d3d3fbfe082b9b8af8862a57a2825675baeb2a142f78fe61d6830c1118d82ccd`. `run_codegen.sh`, owner-order-check, then `run_pairs.sh` executed. Fullsources/helpers/PTX/SASS/cubins/resources/rawsamples/environment and source-reviewreceipt archived.
