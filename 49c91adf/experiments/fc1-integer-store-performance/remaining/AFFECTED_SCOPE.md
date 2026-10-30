# Integer-carried FC1 store scope

The full468-cell table contains104 affected N3U swap cells: EP8 andTP8 × W4A4,MXFP4x8,MXFP8,per-token ×13 token counts. W4A16 uses its independent unchanged implementation(104 cells). The remaining260 swap cells use gated SwiGLU/SiTU FC1 paths; their reuse requires source specialization proof plus representative native equivalence across FP4,FP8 andper-token, including SiTU. That qualification runs separately without unrelated timing. This does not claim individual compilation of all260 gated cells.

The complete32-cell screen is preserved. This extension measures only72 remaining cells at1,2,8,16,32,64,256,512,8192 tokens using identical frozen sources, winners,routes,cache entries and strictCAAC/CUPTI methods. The104-cell retention union excludes1/2tokens(88retentioncells), while keeping them in raw output. The measured per-tokenEP16K−0.54% loss remains unchanged; no dtype-specific policy is added to rescue it.

Every source/control/native-guard receipt stays bound to retainedbf072 plus the final482b swap overlay. Historicald2aaa andfailedcdb2 source evidence are separate. The two initial independent audits are required launch inputs. No source changes, new tactics, retuning, sanitizer or unrelated benchmark rerun are introduced.
