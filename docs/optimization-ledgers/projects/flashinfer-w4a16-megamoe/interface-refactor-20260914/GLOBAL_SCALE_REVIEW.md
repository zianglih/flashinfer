# Independent review: global weight scale capability

Verdict: PASS by source inspection; no blocking findings.

Reviewed the current uncommitted changes in `core/kernel/base.py`, `core/validation/common.py`, `modes/mega_layer.py`, `weights.py`, the W4A16 backend opt-in, and the six-case `test_layer_global_weight_scale_support` product in the existing `tests/moe_ep/test_mega_layer_validation.py`.

- Scope is centralized: one common validation argument defaults to false; Mega backends inherit false; only W4A16 opts in. No unrelated backend preprocessing or compute implementation was changed, and no validators were scattered into direct helpers.
- Normal unquantized and prequantized packs without separate global scales pass the new branch unchanged. W4A16 packs still reach their existing dtype/shape/device scale validation during preprocessing, and retain post-FP32-accumulation application. The capability does not weaken those checks.
- Public Mega construction passes the selected backend capability before consuming canonical weights. Split construction still invokes the same validator with three arguments, so the default false rejects either new scale field before fleet creation. Every registered Mega implementation derives from the base, so ordinary backends need no explicit new field.
- The existing transformed-weights branch intentionally skips validation of the unused source pack. This was already the layer contract and remains appropriate; the new canonical-scale rejection applies when source weights are consumed, not to ignored placeholder weights.
- Documentation identifies W4A16 as the sole supported consumer and directs standalone preparation to `preprocess_w4a16_cutedsl_mega_weights`. Unsupported direct helpers remain a documented caller precondition, as requested.
- The added test product covers each optional scale independently across W4A4, W4A16, and split. It imports the normal package and constructs real CPU `PrequantizedMoEWeights`; no fake package/module scaffolding is used. `auto_bootstrap=False`, `preprocess_weights=False`, and `torch.cuda.is_available=False` isolate the actual layer init gate without kernel launch or distributed setup. Fixture H=I=128/E=2/topk=2 satisfies both Mega geometry paths. The split rejection precedes its backend architecture and fleet validation. The successful W4A16 object is destroyed normally.

Validation boundary: all six reviewed files parse. The local system Python lacks pytest, so this reviewer did not execute the product and does not claim a normal-import pytest pass. No source changes, commits, pushes, or GPU work were performed for this review.
