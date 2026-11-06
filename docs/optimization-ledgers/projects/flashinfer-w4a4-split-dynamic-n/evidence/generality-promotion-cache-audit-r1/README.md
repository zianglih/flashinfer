# Promotion compilation-cache audit

Keep final promotion on a fresh source-private compiled cache. Continue sharing only the native libraries, generated source root, cubins, and lock directory through the existing helper.

- The main split FC1/FC2 kernels, prepare/combine, and W4A16 call raw `cute.compile`. The current installed CuTe 4.7.1 compiler still forces `compile_only=True` and `no_cache=True`; namespace reuse cannot retain those compiled callables across processes.
- FlashInfer explicitly exports the NVFP4 quantizer. The active R3 namespace contained one such module, with 11 `.o` files totaling 443,656 bytes. Its metadata source key exactly matches the three source files **and the resolved physical checkout paths**. Rehashing the same bytes under another checkout produces a different key.
- A directory alias alone therefore fails the exported-module metadata check; rebuild/invalidation can then touch shared objects. Rewriting the metadata or the old namespace identity would weaken the existing source verification. No such alias is recommended.
- HEAD/patch-independent cache naming is not enough. A future improvement needs an independently reviewed content-normalized exported-kernel key, plus an explicit persistence path for the main raw-compile kernels. This is separate from AUTO timing caches.

`review.json` binds current runtime source, the prior SDK snapshot, helper files, and actual candidate metadata. No GPU/package import, compilation, cache mutation, source edit, or timing-cache operation was performed. The existing SDK compiler bytes match the previous audit; current runtime versions were queried again.
