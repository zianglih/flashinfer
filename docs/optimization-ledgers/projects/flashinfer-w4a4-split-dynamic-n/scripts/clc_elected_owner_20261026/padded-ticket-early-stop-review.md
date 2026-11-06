# Padded-ticket early-stop feasibility

**Recommendation: defer a standalone performance experiment.** Retiring the current cluster on a padded ticket can preserve coverage, but fewer cancellation queries can increase physical CTA launches and initialization work. First measure successful padded cancellations and physical launches, or design a safe cheap initial-padded exit. This is a source/history review only; no source changes or GPU runs.

The reviewed baseline is canonical `9b4721b08057d0a488c1f0236467acb75c48cd00`; the proposed owner protocol is separately frozen as patch `5da2bd3f6217a3b72d17fedadaf61214279e632c6f84135657070fbe1ccb2c5e`. Its first compile currently fails IR verification, so the source protocol review does not establish an executable candidate.

## Coverage and minimal protocol

The launch maps one cluster to each channel tile and allocated route-tile slot. Published `num_routed_tiles` bounds the live prefix; a valid hardware ticket outside that prefix has no payload. A successful cancellation transfers one not-yet-started cluster's ticket to the caller. Retiring after that ticket is safe only because its payload is empty; uncanceled live tickets remain launchable. This is a local retirement decision, never evidence that the grid has no live work. Cancellation order need not be monotonic. Both CTA ranks share the route coordinate, so the decision is cluster-uniform.

A minimal implementation would define current payload validity as `work.is_valid_tile and route < num_routed_tiles`, acquire a metadata slot, and publish either its current live item or the existing terminal sentinel. Only a payload-valid current item issues and consumes a new cancellation request. A padded response returned by the prior iteration has already been waited on, decoded, fenced, released and advanced before becoming the next current item. Do not issue a new request and then exit on padding: that could cancel a live ticket without processing it.

Keep the following invariants:

- Initial padded work still publishes a terminal item because worker warps await initial metadata. Existing startup weight prefetch already skips that work, leaving the operand ring unacquired.
- Terminal publication acquires and advances the metadata slot once. Response producer/consumer states advance exactly once per issued/completed query; no advance is needed for a padded current item that issues no query.
- Preserve response reuse fencing, the CTA0 response producer tail, the final all-thread CTA join, and TMEM teardown. Both CTA owners must drain the last multicast response and remain alive until the existing peer acknowledgement contract allows exit.
- Keep delayed PDL wait outside the owner branch. Published routing may be read before the payload wait only under the existing prerequisite release/signal contract; no broader early-read permission follows from this proposal.

These are generic runtime work-validity conditions, not model/dtype/dimension thresholds or a new tuning axis.

## Why query count is not the objective

The current scheduler keeps claiming padded tickets without publishing them. Every successful padded cancellation suppresses one otherwise launchable physical cluster. Early retirement leaves more padded tickets to start normally, each paying the current barrier setup, cluster rendezvous, TMEM allocation/retrieval, descriptor partitioning and teardown before it reaches the scheduler's padding check. It can also retire productive resident workers while live tickets remain, increasing startup cost and weakening load balance or the PDL tail.

The existing V41 mixed T16384 diagnostic records 235 live route tiles versus 863 allocated; FC2 has 4,700 live logical clusters versus 17,260 physical launch tickets, including 12,560 padded tickets. Those are mapping-capacity counts, **not measured successful cancellations or launched CTAs**. They cannot establish the sign or size of early-stop savings. See `../../perf-general-20261026/v41-mixed-prefill-diagnostic/README.md`.

A cheap initial-padded exit before initialization is a separate design. It needs a cluster-uniform decision after routing metadata is legally visible, must preserve prerequisite/dependent-grid obligations, and cannot let one CTA bypass initialization or teardown while its peer enters a collective. Without the existing startup routing publication contract it must wait for the prerequisite before reading the live count. Do not infer that an early kernel return is safe merely because the route has no payload.

Before implementation, a task-local diagnostic should distinguish physical initial clusters, successful live cancellations, successful padded cancellations, failed requests and published live items, plus startup versus scheduler-tail time. The existing `live > resident` replay gate does not measure cancellation success. A later exact gate would need all-empty and sparse-heavy-padding routes, padded initial and canceled tickets, changed/reactivated routes, persistent live work, one/two CTAs and PDL on/off. Exact output agreement alone cannot quantify launch amplification.

## Prior experiments

Searches for padded-ticket early stop/exit/terminal logic in project Markdown and the sibling `flashinfer-w4a16/w4a16_optimization_experiments.md` found no equivalent attempted variant. This is a scoped ledger search, not proof that no undocumented attempt exists.

- `../clc_current_experiment/README.md`: one-slot CLC filters padded metadata but continues cancellation. Different design.
- `../clc_metadata_single_owner_20261026/README.md`: publication cleanup explicitly preserves padded cancellation. Different design.
- `../../perf-general-20261026/clc-bounded-work/README.md`: rejected occupancy-bounded balanced intervals change ticket mapping and retain claiming. Its 96 exact replays passed, but fixed V41 mixed speedup was 0.9030x versus current CLC, and K3 cases also regressed. It cautions against coarser work distribution but does not test early stop.
- Request-before-metadata-acquire and metadata-depth experiments alter ordering/queue capacity; neither is equivalent.

The atomic cancellation/unique-ticket basis is specified in NVIDIA's [PTX CLC instruction contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-clusterlaunchcontrol-try-cancel). The local coverage and launch-amplification conclusions above are an inference from that contract and this kernel's mapping/startup sequence.
