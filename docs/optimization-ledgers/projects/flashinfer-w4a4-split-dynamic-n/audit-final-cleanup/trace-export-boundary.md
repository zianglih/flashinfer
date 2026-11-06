# CuTe trace export boundary

No additional source change proposed for this cleanup. The corrected in-process CuTe numerical reference reuses the preparation contract; standalone serialization remains a separate, pre-existing limitation.

The retained and cleanup versions both fail when defining the actual rendered source in a fresh namespace: `NameError: name 'ActivationType' is not defined`. The bounded renderer check and source hashes are in `trace-independent-review.json` (Torch import/decorator stub only; no tensor execution).

Completing standalone support would also require:

- Resolving the enum/default constants and registering the reference's numerical helper dependencies using the existing `_trace_reference_dependencies` mechanism.
- Resolving package-relative imports. The renderer emits imports for Python math and PyTorch but supplies no FlashInfer package context. The architecture-layout helper import and the shared expert helper's SiTU-validation import therefore cannot execute in `exec(source, {})`.
- Deciding the standalone architecture/layout contract. Retaining shared preparation/validation helpers requires an installed FlashInfer package and absolute imports. A PyTorch-only export would instead require self-contained architecture and validation logic, introducing duplication or a broader shared-helper refactor.

Root chose to preserve shared policy reuse and keep those changes outside the current tightening pass. The present validation must be described as an in-process numerical-reference correction, not standalone-export coverage. No other backend reference registration or shared expert validation was changed by this assessment.
