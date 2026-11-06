# FC1 all-thread early PDL trigger: residual prefill regression

Not retained yet: FC1 all-thread issue restores wide registers80 and removes the large isolated FC1 loss; T4full1.053221x, but T16384full0.954754x still fails prefill guard.

Actual-source `flashinfer-pdl-fc1-trigger-review` from corrected `aab93f854054de834447bdd8985b8bbd653fb3c8`, exactly two unstaged files. Old elected candidate and component archives are preserved; production unchanged.

|Tokens|Route N|Phase|Control medians (us)|Candidate medians (us)|Control/candidate|
|---:|---:|---|---|---|---:|
|4|16|full_chain|49.7760, 49.9200, 49.7605|47.1520, 47.3285, 47.4240|1.053221x|
|4|16|fc1|28.8635, 29.2000, 29.3920|28.2560, 28.2880, 28.2720|1.031091x|
|4|16|fc2|16.1600, 16.2240, 16.2240|16.2720, 16.2570, 16.2085|0.997343x|
|16384|256|full_chain|483.7605, 483.6175, 483.6490|512.6415, 503.2815, 503.9220|0.954754x|
|16384|256|fc1|220.7850, 225.9205, 225.4080|223.3450, 227.4890, 227.0410|0.991481x|
|16384|256|fc2|133.5200, 133.6320, 133.6165|138.2565, 138.3370, 138.3850|0.965757x|

Same actual native input/routing and fixed tactics, A/B/A/B/A/B pertoken,10warmups/100cold-L2 CUDAgraph/CUPTI perarm. All36phase/full arms and3600samples pass exact output/SF/final checks before and after timing. Fullchain/FC1includeactualprepare;inputquantizationexcluded. Observer-held intermediate references released before fullchaincapture. No primary/AUTO/TRT rerun.

Only numerical-phase specialization changes relative to bbb04823: activation-enabled FC1 signals with allthreads immediately after the unchanged prerequisitewait. Activation-none FC2 retains electedwarp0 release.gpu→soletrigger exactly; prepare remains a3b0042e earlytrigger. No token/geometry PDLdisable, no math/layout/roles/stages/grid change.

|FC1 resource|N16 control/elected/all-thread|N256 control/elected/all-thread|
|---|---|---|
|Registers|64 /64 /64|80 /88 /80|
|Dynamic SMEM|197504 /197504 /197504|195584 /195584 /195584|
|Localbytes|0 /0 /0|0 /0 /0|
|Threads|288 /288 /288|288 /288 /288|
|TMEMcolumns|128 /128 /128|512 /512 /512|
|Operandstages|4 /4 /4|5 /5 /5|
|Driver CTA/SM|1 /1 /1|1 /1 /1|

Regenerated compile-only artifacts use the same static native FC1 channels4096/K7168/experts32, N16M128 or N256M256 cluster2, three sourcearms in one invocation. They are not retroactively identified as cubins from earlier measured processes. Static runtime example route/token values do not create additional staticshape specializations. No kernel launch in codegen export. PTX/cubins/SASS/resource hashes are archived.

The wide FC1 phase returns close tocontrol, but isolated FC2 retains about3.4%loss and fullchain loses4.5%, exceeding the approximately7us isolatedphase difference. The original loss was therefore largely codegen-related; residual cross-kernel behavior remains unproven pending the separate timeline. Do not claim cache contention solely from these medians.

GPU2B200-92 UUID `GPU-7e973000-5213-bf29-4ca1-25a6d947f8e3`,NVIDIAPyTorch26.05-py3/CUDA13.2.78/CuTe4.7.1. Onlysame-nodeadjacentcontrols.

CoreSHA `ac1aef1e9ff52ee57a10841eb69a1ce2cf44790968f5283fa36533f9022358fa`; prepSHA `a3b0042ea0ae64f66cfc968768c85b96118ed750fa92a668cb1485f91866a67b`. RawarchiveSHA `a0235ec684b9ab73dc249139265fbebad12edd12458cd298c2d67d2b94a50a18`. Executed `run_codegen.sh` then `run_pairs.sh`; source/helper/codegen/raw/environment pinned in summary/files-sha256. No further GPUwork launched by this archive.
