# Same-source old/new native-winner holdout

Both arms use the identical retained `2b8eb9d8` source. The unchanged public managed-cache path selects the old FC2 M256 or newly selected FC2 M512. FC1 M512, route tile128, two-CTA clustering, both K-step4 choices and CLC-off remain identical. No private tactic override, source change, new tactic axis, cache rewrite, or PR table replacement.

Four ordered phases are control/candidate/candidate/control, each100 strict CUPTI samples with10 warmups, coldL2 CUDA Graph replay, functional unfused swap-AB W4A4, input quantization included. Actual sigmoid routing identity, model, topology, backend, compiler/source/resource guards are checked. The native search’s eager event selection and321 profiling calls are separate; every holdout phase must report zero profiling calls and zero admitted-tactic enumeration.

Only the orchestration helper’s expected-result and cache selection is role-specific. Original frozen and newly selected managed caches are copied to fresh role directories; originals and copies must remain byte-identical. The two source records intentionally share one repository, so the resource adapter sees identical source/policy under both roles. Register/resource values may differ because FC2 geometry intentionally differs; LOCAL0 and actual source/tactic resolution are mandatory.

The controller verifies all13,245 source hashes before/after, current recovery release ELF/Ninja identities and no-op builds, and idle GPU0 before running. Native/CUPTI results and all clocks remain authoritative. The preserved R0 outer-bucket error belongs to the separate search, not this holdout.
