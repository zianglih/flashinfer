# W4 cutoff publication reuse boundary

Retainedc1ac8ce7 is a direct child of2b8eb9d8 and changes only the qualifiedcbef W4 kernel. The benchmark, W4 launcher, swap kernels and shared external interfaces are unchanged.

The104 existing W4 rows are enumerated from their recorded cache hits, including10 recorded deterministic defaults. Model dimensions come from the unchanged benchmark AST; each resolved FC1/FC2 K stage and two-transform-group geometry is inspected. All frozen stages are K256/group128. The existing constexpr tail predicate is false for65 W4 cells and true only forFC2 in the39 V41F TP4/K3 TP8/N3U TP8 cells. FC1 is unaffected for every model-table row.

Therefore publication replaces exactly39 primary rows and reuses429 prior full-row dictionaries:65 W4 plus364 unchanged swap. JSON contains the complete104-cell tactic/extent inventory and canonical sorted compact-JSON SHA256 for every reused row. Fresh keys exactly equal the source-derived affected set. Tokens1/2 remain in raw tables; retention excludes them. SeparateACCA does not replace or pool with primary timing.

The representative native qualification has13 byte-identical split pairs and2 padded-Mega pairs. The source/constexpr proof supports graph reuse for the remaining signatures; this is not a claim that all429 were separately recompiled. Historical measured revisions, external baseline fields and prior row values must remain unchanged in the new publication.
