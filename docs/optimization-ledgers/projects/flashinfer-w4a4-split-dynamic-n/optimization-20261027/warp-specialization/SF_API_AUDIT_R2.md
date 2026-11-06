# R2 prepare / quantizer / SF integration audit

Read-only review against retained `1e69d0a391fd926d21a35388cacf2df3c1c22baf`. All five current production files still match `sf-source-freeze-r2.json` (kernel `e14519f9`, prepare `710d0471`, quantizer `0b901ae7`). No source edits or additional GPU work were performed for this audit.

**Result: no blocking source or API issue found.**

| Boundary | Finding |
|---|---|
| Public MoE APIs and tactics | Unchanged. AST comparison finds only `_moe_core_impl` changed in `fused_moe.py`; its signature and all other 14 top-level definitions are unchanged. The swap-AB tactic module is byte-identical to retained. |
| Public input quantization | `fp4_quantization.py` is byte-identical and does not pass the new option. Omitted/None `sf_rows_per_group` leaves the original layout, allocation, grid, row limits, PDL flow and quantization arithmetic in place. The optional argument is appended to the existing shared helper rather than introducing a second quantizer. |
| Default kernel naming | `sf_rows_per_group=0` adds no specialization-name suffix; an explicit pitch adds `_sfrows<P>`. Existing source-content cache invalidation still applies; unchanged naming is not a claim that old compiled objects bypass that invalidation. |
| W4A16 prepare | Its caller is byte-identical and passes `activation_sf=None`, `routed_sf=None`. The old unscaled traversal was already `count * route_tile` logical rows, and the grid was already based on payload capacity. The simplified loop performs the same limit test and valid-row copy; its PDL, alignment and copy-width selection are unchanged. |
| Legacy / Rubin paths | Neither receives the optional SF pitch. The per-token call supplies it only under `swap_ab`; the view conversion retains the original `intermediate.shape[0]` branch otherwise. The legacy gather/finalize files and shared layout utility are byte-identical. No weight layout or caller preparation workflow changes. |
| FC1 to FC2 | Both GEMMs are already required to use the same logical routing tile N. Prepare allocation, epilogue stores, standalone per-token stores, kernel SF extents and TMA row coordinates agree on `P=ceil_div(N,128)*128` and `r//N*P+r%N`. Payload and per-token scalar rows stay compact. The existing view-only conversion receives physical SF row count only for swap-AB. |
| Supplied FC1 scale storage | The private swap-AB launcher now checks exact SF element count before launch. A canonical compact buffer is rejected when the new narrow-N layout needs more storage; it cannot silently overrun that buffer. The public wrapper normally passes `None` and lets the launcher allocate it. |
| Physical padding | Allocation and TMA cover complete atoms, while work traverses only logical rows. Invalid logical rows retain zero SF; unused physical slots are explicitly unspecified. Existing poison and final direct-quantizer results qualify this distinction. |

`sf-api-audit-r2.json` records the source hashes, frontend AST comparison and six byte-identical integration dependencies. `quantizer-ast-audit-r2.json` additionally records 20 unchanged top-level quantizer definitions and unchanged per-token arithmetic helpers.

The already completed runtime evidence is in `final-evidence`: final quantizer six default comparisons and 110 routed graph replays; original physical-padding poison proof 64 public replays / 112 hooks. This audit adds source tracing, not new runtime coverage. It makes no performance or sanitizer claim.

## Diff conciseness and optional nits

- The `fused_moe.py` change remains the intended three-line diff. No unrelated formatting, license, public doc or surrounding legacy implementation rewrite remains.
- Prepare's header changed because its old physical-padding-zero promise is no longer true. Its original PDL, copy alignment and grid-policy comments remain. The wrapper's scale-layout comment was extended only to explain complete route atoms.
- Optional documentation-only clarification: the shared quantizer's `scale_output` Returns paragraph describes the default `sf_layout` padding but could add that explicit `sf_rows_per_group` uses `ceil_div(M, rows_per_group) * sf_rows_per_group` physical rows. The new argument description already states the mapping contract and unspecified physical holes, so this is not a correctness blocker.
- Optional wording-only cleanup: prepare's existing error says `canonical routed SF storage mismatch`; `routed SF storage mismatch` would avoid implying compact canonical row packing. Keeping it unchanged also avoids unnecessary message churn.
- No new general-purpose layout utility is needed for the few host/JIT pitch calculations: they are short, identical formulas in different execution domains, and extracting them would add indirection without removing a competing contract.
