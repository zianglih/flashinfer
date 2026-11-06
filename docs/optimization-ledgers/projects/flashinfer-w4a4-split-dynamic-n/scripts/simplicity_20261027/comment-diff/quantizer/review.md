# Quantizer comment review

Restore the original register-copy pass description; it remains correct after guarding tail lanes. Keep the original launch-bounds wording with the necessary numeric correction (1024 threads, not 2048).

Retain the bounded-grid class description, dependency publication/valid-row padding notes, reduction-buffer reuse comment and new optional-argument contracts: the original descriptions would be inaccurate or omit new API behavior. Preserve the original 64-bit-address rationale verbatim under its changed indentation. No executable changes.
