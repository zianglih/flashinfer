# Ternary absmax reduction (R1)

Retained source: b13963b0, only `Sm100BlockScaledMoeEpilogue._absmax` changes. R0 binary-tree evidence remains frozen in the sibling directory. No fallback, new tactics, runtime policy, data-layout or API changes.

Sixteen absolute magnitudes compact to six (five triples and a carried leaf), then two triples, then `max(0, max(left, right))`. This permits eight ternary max instructions at depth three. Actual SASS is the gate: the compiler may choose a different lowering. Compaction in ascending group order never overwrites an unread input of a later group. The final positive zero preserves the retained maxnum behavior for all-NaN/zero fragments. Values remain unmodified for quantization/stores.

CPU proof executes the extracted source AST under maxnum semantics (55,184 edge/random vectors). Paired compile-only gate covers 15 FC1/FC2 geometries including both wide M512/K8 mixed-format baseline-spill cases; no kernel launches or performance before resource/instruction review. Existing exact cases and the predeclared 44-cell screen remain subsequent gates, not completed validation.
