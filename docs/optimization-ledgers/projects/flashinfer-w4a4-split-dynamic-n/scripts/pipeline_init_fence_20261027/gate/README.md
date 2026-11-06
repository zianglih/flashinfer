# Initialization-fence focused gate

Frozen source `5112a25e` is independent of the TMEM candidates. Reuse the original clean9b CLC controls and the TMEM V2 clean9b static controls, including one-CTA overlap, on the same GPUs. The eight-case CLC probe remains byte-identical; the exact static probe and receipt paths will be bound after TMEM V2 freezes them.

No GPU launch until independent source review approves, the TMEM V2 gate completes, and GPUs 6/7 are idle. GPU 6 runs its CLC shard then static cases; GPU 7 runs the other CLC shard. Source-private DSL and retained native compilation caches remain separate. No timing runs belong to this gate.

`binding.json` intentionally blocks launch until the static controls and independent review hashes are known. The candidate-only driver checks unchanged source, same GPU, identical probe hashes, replay coverage and exact artifacts. The validator checks geometry, storage, pipeline stages, UMMA commits, resource use and exact output parity. No source edits or new tactic axes.
