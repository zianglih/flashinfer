# Held/authorized W4 output-ring performance screen

The immutable control is byte-identical to retained `2b8eb9d8`. The candidate changes only the W4 output ring index (`b4f80b0a`). Root reviewed the18 native pairs and104-cell setup before authorizing launch.

Eight original W4 jobs cover V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8 and N3U EP8/TP8. Each uses tokens1,2,4,8,16,32,64,128,256,512,4096,8192,16384. All94 explicit choices and10 recorded deterministic defaults retain original cache keys/routes. No autotuning, new tactics, default rewriting or event fallback is permitted.

Same-GPU C-A-A-C,100 strict CUPTI graph samples/10 warmups per cell, cold L2. All41,600 samples and four medians per cell are retained. The estimator is the ratio of geometric means of the two phase medians. Tokens1/2 are recorded but excluded from retention. The public NVFP4 input-quant option is unchanged; W4 itself consumes BF16.

Recovery node: `fi-gather-pipeline-recovery-1030`, C2, namespace ziangli. Assigned GPUs2/4/6/7 run disjoint jobs; GPU0 profile,1 clamp,3 available. Both arms reuse verified release CPP/Ninja modules and persistent strict-source-key CuTe caches. Full tracked source inventories are verified before/after the campaign; each phase checks the bounded imported-source manifest and native resource/default joins.

No sanitizer or new accuracy fixtures. Native qualification uses correctness-only small caps; performance uses untouched production geometry. No source modifications or publication until the complete performance evidence is independently audited.
