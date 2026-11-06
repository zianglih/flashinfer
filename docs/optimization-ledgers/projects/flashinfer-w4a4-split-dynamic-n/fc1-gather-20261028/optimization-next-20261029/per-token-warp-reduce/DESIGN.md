# One-warp per-token row reduction

Leave CTA selection and all arithmetic unchanged. A one-warp CTA already has the complete row maximum after warp_reduce; do not write/read shared scratch, repeat five shuffles, or execute CTA barriers. Multiwarp CTAs preserve block_reduce and the end-of-row scratch-reuse barrier. Compile-time self.warps controls the ownership boundary. Device live counts, routed holes, row scale stores and PDL stay unchanged.

Independent from the broad register-width diagnostic, whose large-row width policy regressed several wide rows. This candidate uses the retained f63 policy only. Existing exact quantizer and focused direct graph-replay tests gate source-paired micro/end-to-end measurement; no new repository tests or sanitizer.
