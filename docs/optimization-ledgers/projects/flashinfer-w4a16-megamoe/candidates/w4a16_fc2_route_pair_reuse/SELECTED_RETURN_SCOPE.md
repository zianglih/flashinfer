# Selected return scope

Derived only from the completed whole-run comparison. No saved checker or runtime replay. All chosen dictionaries are unchanged.

| Selected return / tokens | Rows lower | Latency GM change | Geometric speedup |
|---|---:|---:|---:|
| changed_selected_direct_8_to_1024 | 5/8 | -0.164361% | 1.001646× |
| native_identical_selected_reuse_2048_to_8192 | 2/3 | -0.644723% | 1.006489× |

The selected direct rows use the changed N64/F4 direct-return native body. The selected N128/F4 reuse rows use the native-identical control specialization; their measured change does not attribute a benefit to this direct-only patch. Both groups remain single-sweep observations, with no causal/significance claim. Full before/after rows and all56 hot scores remain in [FINAL_COMPARISON.md](FINAL_COMPARISON.md) and its linked saved comparison.
