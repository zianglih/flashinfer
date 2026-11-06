# Shared-empty API wording and caller audit

Suggested addition to the `PipelineCpAsyncUmma` class docstring (after its
existing description):

```python
    With ``empty_owner``, both pipelines must use matching stage indices/phases,
    UMMA consumer groups and empty-arrival masks. Call only the owner's
    ``consumer_release`` after all operands in the shared stage are consumed,
    and its ``producer_tail`` before teardown. This pipeline retains its own
    full-barrier commits and waits.
```

Suggested replacement for the existing parameter description:

```python
        :param empty_owner: Pipeline owning the shared empty ring. When supplied,
            barrier_storage holds only this pipeline's full barriers.
```

This documents the caller obligations rather than implying that `create`
validates consumer groups or masks. Existing checks validate stage count and
TCGen05Mma completion type. No new checks, source changes or public knobs are
proposed here.

## Caller audit at the frozen candidate

- The only Blackwell caller supplying `empty_owner` is the split blockscaled
  core at lines 1359–1383. Both pipelines receive `self.num_stages`, the same
  cluster layout and `CooperativeGroup(Agent.Thread)` (one arrival). The
  admitted layouts are `(1,1,1,1)` or `(2,1,1,1)`, so both computed empty masks
  are local/None for one CTA and `0b11` for two CTAs. Both use the same CTA group.
- The borrowed SF full ring remains independently allocated and initialized.
  All 128 SF producer threads still call `ab.producer_commit`; both CTA MMA
  warps still call `ab.consumer_wait` and the existing async-proxy fence.
  The two-CTA SF-ready join is unchanged. Payload transaction counts and the
  owner's full-barrier arrival are unchanged.
- Warp zero acquires the owner ring in `load_weight_stage` before issuing
  weights/weight scales. Startup prefetch uses a separate state with the same
  initial phase and at most `min(num_stages, k_tiles)` slots; the main loop
  skips reacquisition only for those prefetched slots. Other SF warps wait on
  the owner's empty phase before writing their SF bytes. This avoids duplicate
  TMA-full arrivals while preserving each writer's acquire.
- The original producer/consumer state index and phase advance once per K
  stage and persist across work tiles. No new state/reset or scheduler rule
  was introduced. Static/CLC and inline/overlap paths preserve the same operand
  lifetime.
- The sole `a_pipe.consumer_release(consumer)` remains in leader CTA's MMA
  warp at line 2070, after both channel MMA calls. There is no borrowed-pipeline
  consumer release. Both payloads and their scales are therefore protected
  until all native MMA reads complete.
- Warp zero alone calls `a_pipe.producer_tail(producer.clone())` at line 1789.
  The SDK tail waits all ring stages; the clone preserves caller state.
  There is no borrowed-pipeline tail. Every warp then joins the existing
  whole-CTA barrier at lines 2144–2146 before TMEM release/free.
- Wide TMA-SFB does not construct the borrowed pipeline, so it keeps its
  existing owner-only lifecycle. Its previously reserved unused full storage
  is unchanged by this experiment except for removal of the unused empty slab.
- No unrelated caller changes: Rubin uses its separate `.custom_pipeline`
  implementation; other Blackwell helper users omit `empty_owner` and retain
  the default allocation and lifecycle.

The original 114 replay gate and the additional 12 M512/two-channel replays
cover this contract with paired source outputs, PDL on/off, changing data and
routes (including no-local), one/two CTA, both SF transports, static/CLC and
inline/overlap. This is bounded coverage, not a sanitizer or exhaustive proof.
