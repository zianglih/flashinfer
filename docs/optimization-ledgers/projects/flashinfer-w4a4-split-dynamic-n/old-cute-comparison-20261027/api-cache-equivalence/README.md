# Wrapper to functional cache reuse audit

Approved only for the **current 0b7fe901 nonlocalized, unfused comparison arms**. The old 002529e1 search remains independent; Nemo has no prior winner cache.

The public API operation name is different, so verbatim cache copying is insufficient. `mapped-current/` contains explicit derivatives of the completed current360 control caches. Only the first field in each persisted key changes from `CuteDslMoEWrapper::run::<mode>::<activation>` to `CuteDslFusedMoE::run_moe_<mode>::<activation>`. All 44 entries per model/family retain the exact runner class, input shape bucket, extras, winner tactic, cold-L2 profile provenance, and metadata. Originals are untouched. `mapping-manifest.json` pins input/output hashes, every old/new key hash, completed campaign receipt, and original source hashes.

## Current source proof

`prove.py` executes the source-extracted wrapper constructor/run method and functional entry point with tensor/resource metadata stubs, without importing Torch or launching a GPU. It covers 96 combinations: four model contracts, four formats, token counts 1/128/16384, and PDL off/on. It verifies identical runner-constructor kwargs excluding the callback, identical ordered input tensor specifications, identical recipe and tuning flags, and identical core forwarding arguments excluding inactive allocation/stream fields. This is a host contract proof, not a numerical GPU test.

Relevant current code:

- `fused_moe.py:1143–1181,1866–1886`: both create `CuteDslFusedMoERunner` with identical expert geometry, activation scalars, quant mode, per-token setting, PDL and `autotune_use_cuda_graph`. The benchmark uses false for NV and true for MX in both APIs.
- `fused_moe.py:1394–1416,1899–1922`: the same ordered inputs and output allocation shape enter tuning. Both outputs are newly allocated BF16 `[tokens,hidden]`; per-token scale is index11 and output index12 only for that arm.
- `tuner.py:514–695,713–755`: one common runner owns input synthesis, bucket policy, 360-tactic admission, cold-L2 timing and graph mode. `forward_impl` does not enter runner hash or extras. The hash-free file key in `autotuner.py:1353–1390` stores op name, class name, nearest shape profile and extras; its profiling-policy payload remains unchanged.
- `fused_moe.py:1249–1297,1562–1608`: both callbacks forward to `_moe_core_impl`. Wrapper-owned auxiliary stream/events and optional buffers differ from the functional defaults, but `_moe_core_impl:549–555,675–677,825–830` reads stream/events only for fused finalization. These comparison arms are explicitly unfused, and no localized parameters are used.
- `fused_moe.py:1454–1468,1979–1990`: both use the same runner during tactic timing, then pass `use_async_memset=not tuner.is_tuning_mode` on selected execution. `enable_pdl`, K-step settings and FC1/FC2 scheduler values pass through the shared runner and core unchanged.

The static mapping does not waive runtime checks: functional replays must still hit these mapped keys, keep the caches unchanged, admit no new tactics under `--no-autotune`, and bind source, shapes, route identities, quantization recipe and actual dispatches. The completed GPU packing proof separately establishes that changing the benchmark to public weight preparation preserves current NV payloads/SFs.

## Old source boundary

Old 002529e1's wrapper accepts W4A4/W4A8/W4A16 but has no MXFP8 wrapper initialization. Its functional API explicitly supports MXFP8 and builds the native old runner (`fused_moe.py:1795–1864`). Thus using the functional API for both sources avoids inventing an old wrapper implementation. The old wrapper/functional op namespaces also differ. No old cache is transformed from current winners: layout, tactic schema and kernel policy differ. Old MX uses native fused finalize, unlike current unfused; the inactive-resource equivalence argument above must not be generalized to fused timing without a separate audit.
