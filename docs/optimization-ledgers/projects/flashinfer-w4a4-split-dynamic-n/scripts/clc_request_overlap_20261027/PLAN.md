# Single-slot CLC request overlap

Frozen candidate base4e155c30 + patch3ed310c69ab5407c6551d5e70ec75dbd7c1b93f81ff2409623d056919359c331. The diagnostic six-field180-tactic policy is identical in both arms; the production policy candidate remains four-field180 with no scheduler/metadata axis.

Only move the existing CLC request before local metadata-slot acquisition. Current `work` is already in registers. The one-stage response and one-stage metadata rings use different storage and barriers. Keep leader response acquisition, both-CTA response wait/release, current metadata publication, terminal sentinel, PDL boundaries, pipeline depths, and math unchanged. No new capacity or runtime shape conditions.

Static review by port agent finds no dependency cycle: an early response can wait in its existing slot while consumers release the old metadata. Terminal invalid work still issues no request. Performance risk is reserving one ticket earlier; historical W4A16 acquire-before-cancel results are relevant but use dequantization warps and different pipelines, so they are not present-source measurements. Do not attribute deeper-queue decode losses solely to index overhead.

First gate:32 exact replays per source,16 paired core captures, four formats, N16/N128, one/two CTA, PDL on/off and empty/reactivated/skewed routes. Then only bounded same-tactic CAAC screens on V3 mixed decode and K3 NV prefill; reject early if decode materially loses. Use persistent verified native C++ cache and source-private DSL cache. No broad native search or TRT rerun until a useful result exists.
