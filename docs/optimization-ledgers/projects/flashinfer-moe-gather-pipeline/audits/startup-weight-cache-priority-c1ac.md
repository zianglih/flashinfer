# Startup-only weight cache priority: bounded read-only audit

Retained source c1ac8ce7; no source edit, compilation, GPU run or performance claim.

No tested first-fill-only FIRST→route-aware policy was found in the bounded cache-route/cache-scales/first-hint, warp-specialization/producer and gathered-kernel ledgers. [Constant FIRST/NORMAL screens](../experiments/cache-priorities/RESULTS.md) are distinct: universal FIRST lost4.450% prefill; universal NORMAL lost10.207% decode. The [old first-hint experiment](../../flashinfer-w4a4-split-dynamic-n/optimization-20261027/first-hint/README.md) reused the same route-aware hint across an earlier split startup/steady loop; it did not change cache priority. The similarly named `fc2-prefix-cache` experiment cached TMEM output fragments in registers, unrelated to weight L2 priority. The retained [Oct27 policy](../../flashinfer-w4a4-split-dynamic-n/optimization-20261027/RETENTION.md) explicitly applies route reuse to startup as well as steady-state weights/SFA.

Current `moe_swap_ab.py:247` enables pre-wait weight work only for PDL non-gather FC2. Kernel `:2755–2779` leaves weight/MMA/scheduler ahead of the payload wait; activation/epilogue wait, while routing has already been published. `weight_cache_hint:2531–2542` computes NORMAL for adjacent expert reuse and FIRST otherwise once per work tile. `load_weight_stage:2563–2620` acquires the shared operand slot and applies the same hint to weight payload and SFA. The weight loop `:2877–2923` carries one producer state across every work tile.

The smallest conceivable change is a stage-local hint selection in that existing K loop:

```python
stage_hint = weight_hint
if cutlass.const_expr(self.enable_pdl and self.prefetch_weights_before_wait):
    stage_hint = cutlass.select_(
        producer.count < self.num_stages,
        cutlass.Int64(0x12F0000000000000),
        weight_hint,
    )
```

Pass `stage_hint` to the existing call. No helper signature, routing query, public knob, model/dtype condition, barrier or wait needs to change. It must be called **initial operand-ring-fill priority**, not exact “before dependency completion” priority.

The first `num_stages` stages are the only ones that can issue without any operand slot being recycled. Subsequent acquire requires a prior MMA release (`:3295–3299`), after operand-full acquire (`:3202`) and activation/SFB arrival. The activation producer issues those only after its startup dependency wait. This holds across short-K tile boundaries, static/CLC work and one/two CTA. However, some first-fill loads can occur after payload readiness: the weight warp does not observe the activation warp's wait completion. `k_tile`, index or phase alone cannot distinguish first lifetime fill from later tiles/wraps. The installed CuTe4.8 `PipelineState.count` starts at0 and advances without resetting (saved `audits/barrier-init-installed.json`, `files/pipeline/helpers.py`; matching local helper at `flashinfer/3rdparty/cutlass/python/CuTeDSL/cutlass/pipeline/helpers.py:555–668`). Exact temporal classification would require another observation/publication protocol and is held.

Even this bounded proxy adds a comparison/select and may materialize a count/increment currently dead-code-eliminated. It discards some cross-CTA expert reuse for initial stages, including when the payload was already ready. FIRST changes cache retention priority; it does not reduce the bytes issued, limit FC2 occupancy or prove that L2 contention caused the paired-error loss. The measured earlier FC2 activity and quantizer extension are motivation only. A native gate would need to establish the actual extra instructions/register lifetime before any whole-chain timing; none is authorized or performed by this audit.
