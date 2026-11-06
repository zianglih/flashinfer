# PDL startup overlap: bounded screen, unretained as unconditional policy

Not retained as unconditional policy: repeatable2.47–5.48% decode gains, but T16384 N256 is0.890570x (12.3% slower). Frozen-source component isolation requested.

Corrected control base `aab93f854054de834447bdd8985b8bbd653fb3c8`; candidate remains exactly two unstaged source files in independent `flashinfer-pdl-startup-review`. Production unchanged.

|Tokens|Route N|Phase|Control medians (us)|Candidate medians (us)|Control/candidate|
|---:|---:|---|---|---|---:|
|4|16|full_chain|49.7760, 49.8720, 49.7120|46.9760, 47.3280, 47.2970|1.054800x|
|4|16|fc1|28.8320, 29.3120, 29.3760|28.1920, 28.3045, 28.1925|1.033394x|
|4|16|fc2|16.2240, 16.1600, 16.2085|16.2560, 16.1280, 16.1600|1.001003x|
|16|16|full_chain|74.0640, 74.1285, 74.0645|71.8405, 72.0000, 72.1600|1.028967x|
|16|16|fc1|44.4000, 45.0240, 45.1040|44.0160, 44.3200, 43.9365|1.017034x|
|16|16|fc2|24.9440, 24.9920, 24.9920|24.9920, 24.9600, 24.9280|1.000641x|
|32|16|full_chain|108.0805, 107.9685, 107.8250|104.8490, 105.2005, 105.3440|1.026890x|
|32|16|fc1|66.4805, 66.9125, 66.9120|64.9920, 65.4400, 64.9120|1.025398x|
|32|16|fc2|35.4880, 35.5520, 35.4720|35.6000, 35.4720, 35.4560|0.999851x|
|128|16|full_chain|144.7045, 144.7690, 144.6720|141.0730, 141.3440, 141.2810|1.024658x|
|128|16|fc1|89.6330, 90.3360, 90.1600|88.8640, 89.0245, 88.8960|1.012531x|
|128|16|fc2|48.1445, 48.1605, 48.2400|48.2080, 48.1920, 48.1600|0.999896x|
|16384|256|full_chain|484.8650, 493.6175, 483.8735|548.0810, 549.0410, 544.8660|0.890570x|
|16384|256|fc1|220.6880, 224.5120, 224.6565|276.3210, 283.1850, 278.4485|0.799410x|
|16384|256|fc2|133.4245, 133.5200, 133.5525|138.2400, 138.3370, 138.2400|0.965479x|

Each row uses identical native inputs/routing and a fixed tactic, six arms ordered A/B/A/B/A/B (ABA then BAB),10warmups and100cold-L2 CUDA-graph CUPTI samples per arm. All90 arms/9000samples pass phase output+SF/full-final exact checks before and after timing. The ratio is geometric mean of three control medians divided by geometric mean of three candidate medians. Fullchain and FC1 include actual preparation; input quantization is outside timing. No primary/AUTO or TRT baseline was rerun.

N16 tactic: `[16,[[128,16],[1,1],false],[[128,16],[1,1],false]]`. Wide guard: `[256,[[256,256],[2,1],false],[[256,256],[2,1],false]]`. GPU2 on B200-92, UUID `GPU-7e973000-5213-bf29-4ca1-25a6d947f8e3`, NVIDIA PyTorch `26.05-py3`,CUDA13.2.78,CuTe4.7.1. Only adjacent controls on this node are paired.

Changes: prepare moves its dependent-grid trigger to immediately after its existing prerequisite wait. The GEMM moves its trigger to one elected warp0 issuer immediately after the existing all-thread wait. Nonfused FC2 inserts `fence.release.gpu` before that sole trigger to publish already-visible routing metadata for the finalizer preloads. No wait/read/layout/math/role/stage/grid change, and no baseline-bug claim.

Fresh PDL-on and PDL-off native T32 exact gates passed. V1 PDL-off helper incorrectly passed enable_pdl to run() and failed before off-mode kernels; that failure is preserved. V2 sets the constructor flag only for the exact-only off check; its default timed body is unchanged. Actual prep/core/finalizer paths and hashes are recorded per arm; canonical module rebinding selects real candidate preparation with independent caches.

Independent codegen review confirms FC1 wait141→trigger149→firstglobalread152; FC2 wait142→release149→trigger151→read157; prep wait43→trigger46→read48. FC2 SASS has elected issue and MEMBAR.ALL.CTA+GPU before PREEXIT. Resources unchanged for N16: FC1/FC2 64/94registers,197504B dynamicSMEM,zero local memory,288threads,148CTAs,128TMEMcolumns,four operand stages/two accumulator stages,one CTA/SM,no explicit register cap.

Core SHA `bbb0482387f0862f0e21fc27c93b08a76e825c38cbda1872184ccd20b7a6f1b2`; preparation SHA `a3b0042ea0ae64f66cfc968768c85b96118ed750fa92a668cb1485f91866a67b`. Raw archive SHA `57925f35e9170957aea1ad56bc57bc89ab061b9a2c52384c0e68bdfd4438027b`. Raw archive is immutable; local review/summary files are independently hashed in files-sha256.json.

Executed timing scripts: `run_pairs_decode.sh` then `run_prefill_guard.sh`, both using frozen `probe_native_v2.py`/manifest-v2. Prepared `run_trace.sh`/probe_trace.py were never launched: parent assigned the timeline to a separate agent. No causal claim is made from source code or aggregate timing alone. Next experiment separates candidate preparation from candidate GEMM triggers using the same frozen source components.
