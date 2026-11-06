# Retained adf V41 MXFP8 gap diagnostics

Frozen clean source `adf02fdd4a8fd2a5d4d2ca54b6969cd65572d93d`, all85 source pins. GPUs0/1 on the existing C2 B300; selected CuTe and TRT tactics and exact routing from final public A1 GPU7. T32/T128/T512 are traced using five cold-L2 graph replays of the unchanged public profiler path. No native timing is rerun: original A1 medians are only contextual labels, distinct from profiler spans.

`observe_profile.py` is byte-identical to the existing public-script observer. `run.py` removes its native-timing arm and retains only trace mode. `summarize.py` reads the archived native median from the source-bound plan rather than requiring a newly timed file. No production, source, quantization, cache metadata, routing, tactics, or kernel policy changes. Kernel lifetimes include PDL waits; summed lifetimes are not total latency.

Local immutable plan/helpers/caches and deployment hashes are in `evidence/v41-mxfp8-gap-adf-r1`. All profiler jobs run from artifact directories outside the frozen source. `CUTE_DSL_CACHE_DIR` is recorded as configured only; the current runtime does not consume it. Native compiled artifacts use the established `FLASHINFER_WORKSPACE_BASE`.

Next step: attribute phase differences before choosing targeted NCU counters. Cache-sensitive counter replays must state whether dependency and cache context are preserved; ordinary flushed kernel replay cannot establish cache/PDL causality.
