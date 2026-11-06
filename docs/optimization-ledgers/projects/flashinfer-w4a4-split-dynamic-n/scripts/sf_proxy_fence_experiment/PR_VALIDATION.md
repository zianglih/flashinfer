### SF proxy-ordering correction after the measured performance revision

- **Measured-source boundary:** existing full-grid and TRTLLM tables remain measurements of `98fd3566b5f945c100f48cddacf25deb2432cbc2`. A subsequent four-line correction adds the required async-shared proxy fence after one-CTA non-bulk SF completion, before TCGEN shared reads. Existing group-two fencing and TMA SFB paths are unchanged. No prior numerical failure was observed; this is an ordering repair, not a claimed optimization.
- **Focused validation:** 31 byte-exact cases pass: seven reused NVFP4 control-oracle cases (K64/384/1216, per-token BF16, partial/zero routes) plus 24 paired cases across six supported format combinations, FC1/FC2 and per-token/per-route scaling. Native outputs also match before/after each timing arm. PTX confirms completion wait → proxy fence → TCGEN copy. Resources are unchanged (64 registers, 197504 B dynamic shared, 288 threads, 128 TMEM columns, 0 local bytes).
- **Cost:** B200-92 GPU3, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.78, CuTe 4.7.1, CUPTI 13.4.0. Same native NVFP4 inputs, unfused finalization, fixed N16 tactic, ABA/BAB, 10 warmups/100 cold-L2 graph/CUPTI samples per arm. All 36 arms/3600 samples retained. Full-chain cost is +0.675% at T32 and +0.579% at T128; no statistical-significance or full-grid equivalence claim. No primary benchmark or broad sanitizer rerun for this correction.

| Tokens | Scope | 98fd medians (us) | Repair medians (us) | Repair cost |
|---:|---|---|---|---:|
|32|full_chain|107.4240 / 107.3120 / 107.7440|107.9840 / 108.0325 / 108.6405|+0.675%|
|32|fc1|66.1600 / 66.9760 / 66.9920|66.7840 / 66.8480 / 66.9600|+0.233%|
|32|fc2|35.3600 / 35.4240 / 35.3445|35.5200 / 35.5200 / 35.4720|+0.361%|
|128|full_chain|144.5605 / 144.7520 / 144.6090|145.1205 / 145.3930 / 145.9200|+0.579%|
|128|fc1|89.3120 / 90.1605 / 90.3525|89.9200 / 90.1600 / 89.6320|-0.041%|
|128|fc2|47.9360 / 47.8720 / 47.9520|48.3360 / 48.2560 / 48.1120|+0.656%|

Cost = `100 * (geomean(repair medians) / geomean(control medians) - 1)`.
Actual repair core SHA256 `7c0fe69faab5acecafdd3d67a157f016836e149fafdc29942542d44ef4852c66`;
raw archive SHA256 `1fceb4bc6c19af9e8f92838e880ad8d7df957e9aae3ceaa80382ea360d8d7f52`.
The project artifact `scripts/sf_proxy_fence_experiment/README.md` lists exact remote commands and all coverage boundaries; `logs/sf-proxy-fence/commands.json` in the archive records each executed argv and environment. These are task-local helpers, not newly added repository tests. The coordinator output is:

```text
SEVEN_REUSED_ORACLE_EXACT
24_FORMAT_CASES_EXACT
STEP native-T32 0
STEP native-T128 0
STEP resources 0
SF_PROXY_FENCE_GATE_COMPLETE
```
