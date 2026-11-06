# Candidate007 unchanged native controls

PASS: saved candidate007 controls match retained005. This is a local comparison of completed compile-only captures; no compiler, GPU launch, numerical test, or benchmark was run for this review.

Both captures use physical M=256, N=256, K=512, eight groups, tactic MMA M128/K256 with cluster(1,1), static scheduling, PDL disabled and 148 maximum active clusters. The directory `m256` denotes runtime feature M, not MMA tile M. Fused N64 uses top-k 2 / 65 source tokens; ordinary N16 uses top-k 0 / optional-finalize metadata absent. These input/call descriptors match within each pair.

| Control | SASS rows before → after | Exact code | Resources |
|---|---:|---|---|
| Fused N64 | 1568 → 1568 | Entire raw SASS byte-exact, including PC, encoding and scheduling; PTX exact after removing only `.loc` directives | REG128, STACK0, LOCAL0, static SHARED1024, CONST2=12, CONST0=1888; byte-exact resource dump |
| Ordinary N16 | 1640 → 1640 | Entire raw SASS byte-exact, including PC, encoding and scheduling; PTX exact after removing only `.loc` directives | REG128, STACK0, LOCAL0, static SHARED1024, CONST2=12, CONST0=1856; byte-exact resource dump |

The complete normalized PTX includes identical GPU parameter declarations and launch directives (sm_103a, 512 threads). Raw PTX differs in source line locations following the 13-line source insertion. Dynamic shared-memory launch bytes are not exported in these compile-only result/resource files and are not inferred from the static SHARED1024 figure. No cubin-byte identity claim is made because debug/source metadata can differ.

Actual source attribution is the saved source hash, not the unchanged remote checkout HEAD: retained005 kernel `1fe29f6f802508034c2fc5daaf7a24271e35bf98a0ca1b052548bfc955f5f97b`; candidate007 kernel `ae6ef44ce1aa0c64bdad284e8ecae69977709bd125f397683c012639f25b3e72`; wrapper `aa446d91adfd1335d59bf30acb8ed240f6b592bd78724d02f230cde7806fd90d` in all four captures.

This confirms no emitted runtime overhead for the excluded fused branch or the one-subtile ordinary N16 control. It does not establish correctness of the changed ordinary multi-subtile loop or private zero-route progress; those have separate review/execution ownership.

## Exact saved inputs and identities

- **Fused N64**: [before](candidate005-tma-prefix-fused2-m256-tile-n64/result.json), result SHA256 `2cc21d7cf8a842dd415cadad1d9b596c54c5e1fb462e67ac2b54ba800a92eadd`; [after](candidate007-useful-subtiles-fused2-m256-tile-n64/result.json), result SHA256 `055cf1bfb3578d58040f6bf69179dfcb82d7f8296e3635f49148ace4eb5f469f`.
  Whole SASS SHA256 `f83b7182fc53effcb21fd94a6cd14f9c47b6cf683d51f10c9832306e77382e1a`; PTX with only `.loc` lines removed SHA256 `217fd2cb047cef78074036894f762d718978af7c8b5d38ba3970a6827ead0289`.
- **Ordinary N16**: [before](candidate005-single-subtile-ordinary0-m256-tile-n16/result.json), result SHA256 `18d95c65a28df8a39089a150ab12f9a3f510afe488102ef2bdac72f1a16743de`; [after](candidate007-useful-subtiles-ordinary0-m256-tile-n16/result.json), result SHA256 `aef6532661a6e5e669f958eb51afca8119b682d32288ea877438434a1629130c`.
  Whole SASS SHA256 `7ff0bbc86b16c047d0ff7e21baf38015423434f3e38d45ffe2d511a0bd04455a`; PTX with only `.loc` lines removed SHA256 `a59ef667d2e90d6689c84d85004dcfd4c702978c59ab76c3d711520957ff5677`.
