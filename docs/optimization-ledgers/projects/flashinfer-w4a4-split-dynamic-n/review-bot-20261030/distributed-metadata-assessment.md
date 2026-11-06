# Distributed model metadata assessment

Reviewed retained head `f173414b5b256f78a5356f611366a0b092944a1d`; repository unchanged.

**Confirmed: misleading JSON metadata, no observed execution change.**

`ModelConfig(DeepSeekConfig)` at distributed benchmark lines112–117 inherits four newly added fields. Presets at120–147 do not override them, and `DISTRIBUTED_MODEL_JSON` at2278–2281 expands every field. CPU-only execution of the two dataclass definitions and preset assignment reproduces this:

| Preset | Inherited name | Inherited routing | Actual routing backend | Actual activation/clamp |
|---|---|---|---|---|
| deepseek-v3 | DeepSeek-V3 | deepseek_v3 | fused_deepseek | SwiGLU, no clamp |
| glm5 | DeepSeek-V3 | deepseek_v3 | fused_deepseek | SwiGLU, no clamp |
| deepseek-v41-flash | DeepSeek-V3 | deepseek_v3 | cpu_sqrtsoftplus_topk | SwiGLU, clamp10 |
| kimi-k3 | DeepSeek-V3 | deepseek_v3 | cpu_sigmoid_topk | SiTU(4,25) |

All presets also emit `swiglu_limit=3.4028234663852886e+38` and `default_ep=8`. The actual distributed CLI defaults to eight processes (line2104), so `default_ep` is unused/redundant rather than evidence of an incorrect EP default. Setting V41F's inherited default_ep to4 would be misleading unless the CLI also changed; that is outside this fix.

Runtime trace:

- `_route_tokens` at889–929 selects `routing_backend` and the preset top-k/scaling fields.
- `_distributed_moe_config` at701–708 selects `activation`, `situ_beta`, `situ_linear_beta`, and `gate_up_clamp`.
- MegaMoE config at1322–1325 uses those same activation fields.
- EP/TP dimension partitioning uses actual `args.num_gpus`/world_size at1527–1532 and1632–1637.
- AST scan finds no distributed runtime `CFG.name`, `CFG.routing`, `CFG.swiglu_limit`, or `CFG.default_ep` access. The only serialization is `asdict(CFG)` at2281.

Minimal fix recommendation: filter these four unused fields only at JSON emission:

```python
**{
    key: value
    for key, value in asdict(CFG).items()
    if key not in ("name", "routing", "swiglu_limit", "default_ep")
},
```

Keep the existing `model` identifier, `routing_backend`, and `gate_up_clamp` fields as the authoritative metadata. This avoids duplicating preset configuration or changing routing, activation, CLI defaults, inheritance, or model selection. The CPU audit proves that this filtered dictionary is equal in keys and values to the complete pre-PR `002529e` distributed dataclass metadata for all four presets.

Evidence: `audit_distributed_metadata.py` and `distributed-metadata-audit.json`. Existing GLM5 `logs/C1.log` in `upstream-integration-20261029/megamoe-glm5` independently shows the misleading inherited `name` while retaining correct `model=glm5` and D6144 dimensions. No GPU validation or benchmark rerun is needed for this serialization-only correction.
