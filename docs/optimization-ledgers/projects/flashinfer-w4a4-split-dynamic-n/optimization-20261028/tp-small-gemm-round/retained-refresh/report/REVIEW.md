# Full refresh setup review

No blocker in the reviewed prepare, launch and runner templates. Exact file hashes are in `setup-review.json`.

- Clean retained source is fetched from the supplied bundle,348 tracked source files are checked, and only persistent native-cache symlinks are reused. Managed winner caches are copied per job. Each pass has a private compile directory.
- Fifteen jobs cover four models in EP/TP, with TP V41F MX omitted and K3 MXFP8 excluded. NV selects W4A4, W4A16 and per-token with input quantization enabled; MX selects supported same-dtype arms. Both passes use all13 tokens,10 warmups,100 strict-CUPTI samples and no autotuning.
- The runner binds source/helper/observer hashes, source before/after each pass, frozen winners/routes/cache manifests and raw medians. The independent report additionally checks exact backend sets/counts, policy partition, public command/environment, GPU UUIDs and nonoverlapping windows, printed native CSV, and unchanged external baseline fields.
- Root added immediate expected-backend set/count and postphase GPU UUID assertions; launcher timestamps are taken before Popen. The independent assembler rechecks these. No template changes were made by this reviewer.
- Source qualification is hash-bound by config. The collector and report also verify `complete` and `head` when present in the final qualification schema. Every input member is independently hashed after transfer; `archive-manifest.json` cannot overwrite source/local manifests.

The archive/fetch helpers only write collection artifacts. They preserve the source checkout, raw evidence, persistent caches and helpers remotely. No GPU launch, sanitizer, Git change or publication was performed.
