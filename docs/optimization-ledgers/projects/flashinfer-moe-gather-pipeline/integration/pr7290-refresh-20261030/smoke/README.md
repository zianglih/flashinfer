Seven existing merged-head exact/native smoke calls

The plan uses the actual a620 merge source; no controls or historical exact results are reused. The W4 and swap numerical wrappers and artifact capture are byte-identical to their recorded parents. The two resource guards change only the pinned head assertion. All seven calls are independent, one per GPU 0–6, and owner deployment must supply the ordinary source/cache preflight and per-case environment.

W4 cases 1/2/5 cover the restored helper, partial K640 tail/cutoff, SwiGLU and gate-plus-linear SiTU, ReLU2, one/two CTAs, both weight layouts, static/CLC, and PDL off/on. Swap cases cover NVFP4, native-CLC per-token, MXFP4x8 and MXFP8 at recorded K4/K8 choices. The existing small-SM scheduler fixtures apply to smoke only; the per-token case explicitly retains the native scheduler. They never enter AA performance.

`plan.json` contains helper paths, exact argument arrays, original case records, per-family guard policies and source hashes. `helper-proof.json` records unchanged helper identities and the two reversible head-only edits. No remote or GPU work was performed to prepare this leaf. The integration owner supplies the already-existing deployment/controller.
