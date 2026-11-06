# Padded routed FC2 host simplification

Base: `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`. Changes remain unstaged in `flashinfer-padded-output-review`; the kernel is owned separately by the producer agent. `host-source.json` records the four host-file hashes.

- Remove the compact workspace type/factory and `_output_workspace` parameters from the swap-AB launchers and deterministic finalizer. Remove prepare's prefix scan and its optional pointer/cache specialization. Remove the finalizer's optional dense-index load/pointer/cache specialization.
- Swap-AB unfused FC2 allocates and validates `(permuted_idx_to_expanded_idx.numel(), hidden)` output. This uses the existing host-known padded routing capacity, with no device readback or new capacity formula. The low-level launcher doc states the new row contract. Fused output remains `(num_tokens, hidden)` and zero-initialized.
- High-level deterministic combine selects `input_is_expanded=False` for swap-AB and reads the original inverse routing map. Legacy non-swap retains its expanded allocation and `input_is_expanded=True`. W4A16 code and call configuration are unchanged.
- The routed finalizer therefore uses its existing W4-style geometry. In particular, the expanded-only exact-divisor 5/7-vector choice no longer applies to swap-AB; the existing ordinary routed policy is intentionally retained rather than adding a new knob. Measure the complete simplified contract.
- Original routing arrays are neither changed nor replaced. Prepare still publishes routing ancestors before its existing signal; combine may preload the original inverse map/scales before its FC2 dependency wait, then reads FC2 output afterward.
- The host pointer tuple removes only `compact_offsets_ptr` and `dense_indices_ptr`, previously after `per_token_scale_ptr`. Constructor `output_is_routed` is removed; the kernel's existing unfused FC2 mode always selects padded routed output.

Source checks: four-file AST parsing and `git diff --check` pass. Repository searches found no caller of removed host metadata interfaces outside the corresponding kernel being edited in parallel. No imports, tests, GPU runs, staging, commits or pushes were performed for this host patch. Existing project-only probe observers must be adapted; the scheduler agent owns that work.
