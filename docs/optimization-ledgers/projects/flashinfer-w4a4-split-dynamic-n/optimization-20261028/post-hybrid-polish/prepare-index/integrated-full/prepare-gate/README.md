# Integrated33b7 + prepare R1 gate

Bounded exact-byte/codegen gate before the GPU7 full benchmark job. Source ownership and deployment belong to the producer agent; this folder contains only qualification helpers/receipts. It changes no source, tactics, aliases, or loop policy.

Four geometries: scaled V3 route256/H7168/top8, scaled K3 route128/H3584/top16, and the corresponding shared BF16 representatives. Each uses4096 routed rows, hardware-sized persistent grids, PDL off/on, six graph replays with changing routes/limits and empty/reactivated tiles. Payload/SF bytes, invalid/padding canaries, and poisoned invalid mapping checks are inherited unchanged from the prior gate.48 exact replays/source,8 compile pairs expected.

Sources must be the frozen producer manifest: control33b7 and candidate33b7 plus prepareSHA603dcdf. Gate completed:48 exact graph replays per source and8 compiled pairs passed; all348 source hashes and the prepare-only delta were verified. All variants have zero local-memory sites/stack bytes and at most32 registers/thread. The74-file archive is verified. GPU7 was explicitly released to the producer for its full refresh job. `../qualification.json` is the concise publication receipt; its generator and all exact/codegen/raw receipts are preserved here. No timing, sanitizer or new autotuning in this gate.
