# Curated18 source review

**PASS for the source-only proposal.** The existing16 dictionaries remain equal in exact order; the two additions are fresh copies of indices0 and4, changing only group_hint512→256. The temporary comprehension is evaluated before `out +=`, so it does not iterate a growing list. Reversing only `w4a16_candidates` restores the complete baseline module AST. The graph scorer, other precision factories, public interface and fixed five-WG/two-decode kernel are unchanged. Independent checks used an AST-sliced factory with standard-library Python only; no Torch/native import, source install or GPU operation.

This is the bounded extension recommended in `../w4a16_group_hint_audit/README.md`, using the existing scheduler field and256 choice. It avoids multiplying all16 combinations. The comment about earlier FC2 describes the intended opportunity: smaller groups **can** reach an FC2 phase sooner when boundaries differ; this is not an established latency improvement. Grouping still consumes whole experts, preserves FC1 completion dependencies, and can add phase transitions or reduce independent FC1 work. No source blocker was found.

## Numerical coverage gap and minimal adaptation

Current `flashinfer/tests/moe_ep/test_cutedsl_w4a16_mega.py:26–30` has `_EXPERTS=4`, not8. `_check_numerical` at230–290 replaces its normal rounds with a **skewed** round whenever `num_tokens` is specified. `_inputs:165–189` then sends every token to experts0/1. Increasing token count alone therefore does not establish changed multi-expert group boundaries, especially with only two local experts atEP2.

Use one private E8 fixture, retain topK2, and change only the large numerical round to balanced routing (including its label). Reuse `_weights`, `_reference_terms`, `_layer`, the existing band comparison, synchronization and `finally` destruction unchanged. Avoid changing the public defaultE4 or creating a new oracle. Run the two new dictionaries against their existing512 controls at EP1/EP2. This is a fixture recommendation, not a prepared harness or a completed numerical gate.

A compact common fixture is **H64/I8192/E8/topK2**, with **1040 tokens per rank atEP1** or **520 per rank atEP2**. Both are divisible by8. Existing balanced ids `[row % 8, (row+2) % 8]` give exactly260 routed rows per expert across all ranks, including a four-row routed tail. The FC1 output-feature count is `ceil(2*8192/256)=64` cluster tiles per routed-token block. The scheduler (`src/moe_nvfp4_swapab/fc1_fc2_fuse_sched.py:651–666,1104–1155`) greedily takes whole experts until the group reaches its FC1 tile threshold.

| EP | N | FC1 tiles/expert | Total FC1 tiles/rank | Hint256: experts/group | Hint512: experts/group |
|---|---|---:|---:|---|---|
|1|128|192|1536|2+2+2+2|3+3+2|
|2|128|192|768|2+2|3+1|
|1|64|320|2560|1+1+1+1+1+1+1+1|2+2+2+2|
|2|64|320|1280|1+1+1+1|2+2|

Thus every rank exceeds512 FC1 cluster tiles, both hints form multiple groups, and boundaries differ for both geometries. `source-and-fixture-proof.json` records route-count arithmetic and exact local expert ranges. These are source-derived expectations, not observed scheduler telemetry. A future numerical run should save actual top-k expert counts and verify these cumulative-tile/group boundaries before claiming coverage; it must keep the existing numerical tolerances and record empty/refill lifecycle coverage separately. The fixture does not supply a performance claim or replace the existing general sweep.

Reviewed baseline scorer bytes6d7de539 and proposed factory bytes4013db77. Existing proposed files and production source were not edited.
