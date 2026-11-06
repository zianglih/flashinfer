# Retained e780 full swap refresh

Fresh23 swap jobs /364 cells /46 AA passes /72,800 strict-CUPTI samples at e780f02c. Use GPUs0/4/5/6/7 with exact byte-identical retained6c-full engine/observers, frozen routes and native winners. No tuning or timing-method changes. Cold-L2 graphs,10 warmups/100 samples, input quantization enabled for NVFP4, unfused public API. Persistent CuTe/native caches and stable native-data symlink preserved.

Only swap kernel changes37+/147− from6c;104 W4A16 measurements remain from6c only after source/transitive dependency proof. All468 cells will remain in the final report; historical TRT/non-swap controls unchanged. No PR body edits yet.
