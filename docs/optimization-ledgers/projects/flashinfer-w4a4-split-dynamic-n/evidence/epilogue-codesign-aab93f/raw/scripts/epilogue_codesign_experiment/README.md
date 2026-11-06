# Epilogue/layout/pipeline co-design preparation

- Clean independent local source: `flashinfer-epilogue-codesign-review`.
- Corrected baseline: `aab93f854054de834447bdd8985b8bbd653fb3c8`.
- Remote control/candidate: `profile-aab93f`, `epilogue-codesign-review` under
  `/workspace/flashinfer-w4a4-split-dynamic-n`.
- Devbox: `fi-w4a4-narrow-1025`, c1/ziangli, managed `/usr/local/bin/h`.
- GPU2: B200, UUID `GPU-7e973000-5213-bf29-4ca1-25a6d947f8e3`, observed idle.
- Existing candidate442 native epoch/data resolution is retained; new private
  CuTe path `cache/epilogue-codesign-review/cute_dsl` is reserved.

No source changes, CUDA compilation or GPU kernel launch have been made.
`implementation_ready=false` makes prepared helpers refuse before CUDA imports.
The candidate's truthful expected dirty list is currently empty. Update/freeze
source hashes and explicit dirty files only after the mapping is agreed and
actual source changes are reviewable. Never inherit source changes mid-screen.

`REUSE.md` identifies the prior e14 direct-load epilogue without publisher code,
its remaining shuffle costs, numerical contracts and actual coverage limits.
The native helper preserves the reviewed input/timing/oracle body byte-for-byte;
only module names and explicit readiness/dirty-source guards differ. It retains
10warmups/100cold-L2 graph CUPTI timing, phase+full output checks, actual native
routing, preparation inside the fullchain and input quantization outside.
`helper-adaptation.json` records the exact restoration proof.

Future control calls must select `profile-aab93f`, never `profile-98fd`.
Prepare fresh corrected-aab exact receipts before new candidate validation;
no benchmark is launched during this preparation. Parent decides final geometry,
format coverage and candidate retention gate after the mapping review.
