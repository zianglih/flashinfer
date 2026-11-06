# Source-copy history and retained archives

This ledger records 86 cleaned-up source copies: 16 retained review copies, 64 unretained experiments, and 6 clean baselines. Recovery archives remain only for the 16 retained copies and six baselines. The 64 unretained experiment archive snapshots are intentionally discarded at the user’s request; their names, base commits, patch hashes and optimization history remain. No recovery guarantee is made for those discarded snapshots. The canonical `flashinfer/` checkout remains the working repository.

## Optimization history

The existing notes, scripts, raw logs, evidence and drafts are preserved:

- [OPTIMIZATION_LEDGER_2026-10-24.md](OPTIMIZATION_LEDGER_2026-10-24.md)
- [DECODE_OPTIMIZATION_2026-10-25.md](DECODE_OPTIMIZATION_2026-10-25.md)
- [SCHEDULER_OPTIMIZATION_2026-10-25.md](SCHEDULER_OPTIMIZATION_2026-10-25.md)
- [V41_GAP_OPTIMIZATION_2026-10-25.md](V41_GAP_OPTIMIZATION_2026-10-25.md)
- [PDL_PIPELINE_AUDIT_2026-10-25.md](PDL_PIPELINE_AUDIT_2026-10-25.md)
- [TMEM-layout-audit.md](TMEM-layout-audit.md)
- [Task-local experiment scripts](scripts/)
- [Raw evidence and validation receipts](evidence/)

The notes retain the measured results and rationale. The identifiers below record exact historical source states without assigning new experiment outcomes. Older audit receipts describe what was verified before pruning; they do not imply that the 64 discarded archives still exist.

## Recovery of retained copies and baselines only

For a row with recovery links, create a new independent project-local clone of canonical `flashinfer/` using `git clone --local --no-hardlinks`, then check out its exact base HEAD. Apply nonempty `index.patch` with `git apply --index`, followed by nonempty `worktree.patch` with `git apply`. Extract `working-tree-files.tar.gz` into that clone. Verify file bytes and modes using `files.json`; deleted paths are recorded in the receipt and patches. `head.patch` captures the complete HEAD-to-working-tree delta.

The surviving archives also preserve Git index, HEAD/ref/reflog/remotes/config/status metadata and ignored files. All base/ref/reflog objects were checked against canonical main; no additional object pack was needed. Historical original paths are identifiers, not live dependencies.

- [Retained16 archive receipt](evidence/retained-copy-cleanup-2026-10-25/archive-receipt.json)
- [Six-baseline recovery and discarded-experiment history](evidence/experiment-copy-cleanup-2026-10-25/ARCHIVE_HISTORY.md)
- [Completed archive disposition](evidence/experiment-copy-cleanup-2026-10-25/archive-disposition.json)
- [Exact64 discard selection](evidence/experiment-copy-cleanup-2026-10-25/unretained-archive-discard-selection.json)
- [Historical70-copy audit before archive pruning](evidence/experiment-copy-cleanup-2026-10-25/archive-receipt.json)

## Retained review copies (16)

| Original copy | Base HEAD | Complete patch SHA256 | Recovery receipt | Archive |
|---|---|---|---|---|
| `flashinfer-api-cleanup-review` | `adf02fdd4a8fd2a5d4d2ca54b6969cd65572d93d` | `18dde9d0ed80619b2eaf2c5159b7efdef6d4b3ddbd01e46435b3a938c8cdb458` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-api-cleanup-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-api-cleanup-review/) |
| `flashinfer-clc-single-cta-grid-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `a5e9283a7021e563c991d125a140379bb7049135705fcc0e7608c727f832fd86` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-clc-single-cta-grid-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-clc-single-cta-grid-review/) |
| `flashinfer-k3-benchmark-review` | `6b6bf0cf9da684f8a7d60f77b6b0c135f4c54c8f` | `f1ae920db7937e88611f51a310c521a75bad52e4997c01fc4a566b401ec96158` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-k3-benchmark-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-k3-benchmark-review/) |
| `flashinfer-mixed-epilogue-overlap-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `4eae30d3cd181737b3a42ca5ac3bd1415c401d7b70109d75352a33abf6eeaff1` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-mixed-epilogue-overlap-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-mixed-epilogue-overlap-review/) |
| `flashinfer-mx-table-review` | `4ec7a29d60a8cc5d184f41ce860643d0a30dc4de` | `1b9c35fcbb3abbf941a37764d12d5a387aedf8d3d87991de7417ce499b201a94` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-mx-table-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-mx-table-review/) |
| `flashinfer-mxfp-situ-review` | `adf02fdd4a8fd2a5d4d2ca54b6969cd65572d93d` | `1c6801111f41d57ad16db4fc7aa58c5bce84a5aea669535c881ae5dc8bf2851a` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-mxfp-situ-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-mxfp-situ-review/) |
| `flashinfer-pdl-behavior-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `b77e107f1da32c31ce2e82e921a71ba91a2a80453966becbbb5ef76e72ae967c` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-pdl-behavior-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-pdl-behavior-review/) |
| `flashinfer-pdl-cache-tier-review` | `853aaf69d706b291afee477f738956b997033f53` | `dddd7db2146b2f6acbcdbf6868a9d6248052c49da6c89b5cf8937a1801ad611b` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-pdl-cache-tier-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-pdl-cache-tier-review/) |
| `flashinfer-pdl-weight-prefetch-integrated-review` | `853aaf69d706b291afee477f738956b997033f53` | `a92c766dfdfc1ca8051b0e5c93afe90b77225391c1203271137debcbb3d3d685` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-pdl-weight-prefetch-integrated-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-pdl-weight-prefetch-integrated-review/) |
| `flashinfer-per-token-bench-review` | `2b7fb10532dc3b5572a1cbff34bff41c2e8a2e01` | `e3f2821a7909685d0b3758fe65db2d658bae7262960320324efdc885ab427316` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-per-token-bench-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-per-token-bench-review/) |
| `flashinfer-public-mxfp-moe-review` | `8b74eb6fa77651bb20dacb56b8e13872f3ad9885` | `167e501598e18a4fe6225f715853bc486f691e80558e97e2d1ab00ffba36c0f6` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-public-mxfp-moe-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-public-mxfp-moe-review/) |
| `flashinfer-regular-tma-review` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `64b0a11c56e25cdcea7aec95a6480c4ba92405eeb53bf2f53705aba44aa9d081` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-regular-tma-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-regular-tma-review/) |
| `flashinfer-sf-proxy-fence-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `2228fac41ed9f0791e8f220f0703a4b9ae2c2e92a6a457b1d3b49fca0dbd9884` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-sf-proxy-fence-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-sf-proxy-fence-review/) |
| `flashinfer-stage-capacity-ghost-formatted-review` | `63d5fa0ea1c60e49242970e7721f0581e41c267a` | `aafc4ffd2d74e502bc6eb1f000837a04d9f0e044b4efbba483cd68bac70813d6` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-stage-capacity-ghost-formatted-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-stage-capacity-ghost-formatted-review/) |
| `flashinfer-stage-capacity-ghost-review` | `63d5fa0ea1c60e49242970e7721f0581e41c267a` | `c90bcb6559406b6142f237bb2ca3dc64148c6a839dcb87e46705afb152697aec` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-stage-capacity-ghost-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-stage-capacity-ghost-review/) |
| `flashinfer-v3-ep8-review` | `c5c79ef0dbfaa805f992cf5007d6376110876500` | `5ab7a691eeea36c7b9fcb0be09d72b7f24547d9e5e03c423dd258199f324681b` | [receipt](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-v3-ep8-review/receipt.json) | [files](evidence/retained-copy-cleanup-2026-10-25/archive/flashinfer-v3-ep8-review/) |

## Clean baselines (6)

These copies had no tracked delta or untracked source. Their exact HEAD, Git context and any ignored files remain archived.

| Original copy | Base HEAD | Complete patch SHA256 | Recovery receipt | Archive |
|---|---|---|---|---|
| `flashinfer-b300-original-a65` | `a65d5b09e7e4c4c5c160b0161c48becd100b3970` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-b300-original-a65/receipt.json) | [files](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-b300-original-a65/) |
| `flashinfer-b300-retained-853` | `853aaf69d706b291afee477f738956b997033f53` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-b300-retained-853/receipt.json) | [files](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-b300-retained-853/) |
| `flashinfer-fc2-kstage-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-fc2-kstage-review/receipt.json) | [files](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-fc2-kstage-review/) |
| `flashinfer-pdl-retention-frozen` | `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-pdl-retention-frozen/receipt.json) | [files](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-pdl-retention-frozen/) |
| `flashinfer-pr-scope-review` | `8b74eb6fa77651bb20dacb56b8e13872f3ad9885` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-pr-scope-review/receipt.json) | [files](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-pr-scope-review/) |
| `flashinfer-profile-98fd` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-profile-98fd/receipt.json) | [files](evidence/experiment-copy-cleanup-2026-10-25/archive/flashinfer-profile-98fd/) |

## Unretained experiment history (64)

Source snapshots intentionally discarded per user request. This table has no archive/recovery links. Existing notes, scripts, measurements, source hashes and other evidence remain unchanged; consult the optimization history above for the original findings.

| Original experiment | Base HEAD | Historical complete patch SHA256 | Snapshot disposition |
|---|---|---|---|
| `flashinfer-clc-scheduler-depth2-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `ee646b2c395a89a868e00311708495723fcb4b39089b7eda6a19c39ab4afa83c` | Intentionally discarded; history only |
| `flashinfer-clc-scheduler-reservation-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `eb431be438ba9ffabf0f160d283d9bcdb7106d37f0f63ed65255f6e0457f8d03` | Intentionally discarded; history only |
| `flashinfer-clc-scheduler-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `595eea40ee038fc61e24331748250703999cfbc7e127426ff817620d2a8f1ab0` | Intentionally discarded; history only |
| `flashinfer-clc-single-cta-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `6b3f1c4f532addca0a44a59c6b0b64207bff7a8c88819834f101e891773a1775` | Intentionally discarded; history only |
| `flashinfer-clc-static-control-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `d32be72863bf6f3496632a072d4d7ea81ab5d7d4f69c9f649e54b7dde2c74d97` | Intentionally discarded; history only |
| `flashinfer-compact-sf-broadcast-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `a130562c2da8314ce68c4f892a3e01fd10b6831746920b1a49e3c11ebe944ee7` | Intentionally discarded; history only |
| `flashinfer-compact-sf-publisher-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `ae4baacb9681eb1e2463cfd6a963e4902f2b58dcbcef753d27f8adaf3b13a718` | Intentionally discarded; history only |
| `flashinfer-dynamic-n8-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `ca83b907f588dfb728e9fc4820c294d4793a78335ebe87f237cce7acb5ec4da5` | Intentionally discarded; history only |
| `flashinfer-epilogue-codesign-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `1aad6df6daf5d89306b98aa0a310c95d8a467604324e0c9385d831a3773b72dd` | Intentionally discarded; history only |
| `flashinfer-fc1-tma-roles-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `a4ae50d117d21d0540b12b5524a8bf7b3103a20f67c0fde154eb204865745ae4` | Intentionally discarded; history only |
| `flashinfer-fc1-weight-prefetch-review` | `24c48b9fd5d7c38fdcea213376602f97635c4ef9` | `e05fcdc72c6c8e74df4cec6f8b31f94a74955cd29e5eca14103ec83a15649cd0` | Intentionally discarded; history only |
| `flashinfer-fc2-clc-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `382050d796e160f01d9a996a73b7fdb03f574c5542946b064f683ec35f8255ee` | Intentionally discarded; history only |
| `flashinfer-fc2-narrow-bulk-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `19b18874bd31c6654785bdffd862f74a7264f2851d701468119a53e429467399` | Intentionally discarded; history only |
| `flashinfer-fc2-narrow-bulk16-offset-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `3d09bce11b296e205a93ee538c1080d6cb949feeb3877fce75b7a215acc793e4` | Intentionally discarded; history only |
| `flashinfer-fc2-narrow-bulk16-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `f2bb5f50a6c8de22308e666995111389cd6b7857f38d58291c0954dfca17832c` | Intentionally discarded; history only |
| `flashinfer-fc2-physical-n16-bulk-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `61430be0fb7cf618cad64d7c4f8c63c02a7765b49dbb9bb8568be4d5f07e2fc2` | Intentionally discarded; history only |
| `flashinfer-merged-operand-ring-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `d5150b6531f2406341ab1b0c6f03db53b6607bd71e9b0ebe33d657f6f897dfe8` | Intentionally discarded; history only |
| `flashinfer-mma-k-tail-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `6ac943784ffa8d8a932da06540f3685bf453c5619c7a0de6da6117f52e652d5d` | Intentionally discarded; history only |
| `flashinfer-narrow-channel-reuse-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `ba51fa57b297abdbed523d4224a2b816661c74d98306fe372c2af9494fdd1d5a` | Intentionally discarded; history only |
| `flashinfer-narrow-epilogue-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `ef8c2d72d9eb9c8b7206dfaefce8e3bf3df2f8e738ae095c95c81507c4cf3f1a` | Intentionally discarded; history only |
| `flashinfer-narrow-ld256-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `e6fd4241aaa3b2b61c0038270ad751c374e578a6bf0d279fffd0df7fef20de02` | Intentionally discarded; history only |
| `flashinfer-packed-combine-review` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `6b992fa2596042eef1e7bd9d23360f962491876dc0ecc5c03d5d64a678bf8ace` | Intentionally discarded; history only |
| `flashinfer-pdl-allthread-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `56a6baea42e29a72eac77db47c44f820c6ee4c9038200a60bf8d4d6cce309f37` | Intentionally discarded; history only |
| `flashinfer-pdl-descriptor-prefetch-review` | `853aaf69d706b291afee477f738956b997033f53` | `50d44ac4085ac158b5d63767707054d6948895bc4797acccdba9f13ec66421e3` | Intentionally discarded; history only |
| `flashinfer-pdl-explicit-phase-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `a0f4519e163e38fb79960282602c224ecbafc0e2f0fc65d1d59afea1f846a37e` | Intentionally discarded; history only |
| `flashinfer-pdl-fc1-trigger-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `b6af5db71465fccd58ed9feab79df19765a62e45d5e085d456977168dcda3905` | Intentionally discarded; history only |
| `flashinfer-pdl-fc2-producer-wait-review` | `adf02fdd4a8fd2a5d4d2ca54b6969cd65572d93d` | `d631e9c0519d09bb07ba6b08fdcd62a390f17497cdbb0f2e8db4205bbed19ead` | Intentionally discarded; history only |
| `flashinfer-pdl-first-metadata-r2-review` | `853aaf69d706b291afee477f738956b997033f53` | `fb34e3e6ed0dfe871d7c1f34f513f3b7dfb0ec1b2159dc5f273acf3ceefea2eb` | Intentionally discarded; history only |
| `flashinfer-pdl-first-metadata-review` | `853aaf69d706b291afee477f738956b997033f53` | `37c9a0b2d9ac70837f51a1bc1db8b2b753c9e7b56ad416da6cad05715d9db7f5` | Intentionally discarded; history only |
| `flashinfer-pdl-handoff-cache-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `9b9aeb08ae5b312236dbc650008ee9f3ff5a1925da0d4c851902dc736019cf08` | Intentionally discarded; history only |
| `flashinfer-pdl-livecount-review` | `853aaf69d706b291afee477f738956b997033f53` | `d62db70d74fa96191f0defdf91bbca534bba0e3b0db3c6f12804da9ef58bc12f` | Intentionally discarded; history only |
| `flashinfer-pdl-producer-drain-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `da0efb6829624f1bfb2c4e8c3c9db39e6a943bf6f653f99ee6c5edc3814c6a54` | Intentionally discarded; history only |
| `flashinfer-pdl-producer-wait-review` | `24c48b9fd5d7c38fdcea213376602f97635c4ef9` | `8c0186207be4bf505d2f8a6a7f323798b7b09ece341c7b1c5b2aa2b456f08874` | Intentionally discarded; history only |
| `flashinfer-pdl-sfa-stream-review` | `853aaf69d706b291afee477f738956b997033f53` | `b73a9abeef6f3b6d23e5f6173b0cda2f68beeb56555e50f40d5c58164827bab3` | Intentionally discarded; history only |
| `flashinfer-pdl-startup-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `df6aa74e84c99f14becffa049adad8b60ab4b5aa22bbb92a48d2b0d4d3e0bf3a` | Intentionally discarded; history only |
| `flashinfer-pdl-weight-prefetch-multistage-review` | `853aaf69d706b291afee477f738956b997033f53` | `9cea43321866c8b08fa5b2371c436f78cbc1e46e6117838cbd960741e134dc07` | Intentionally discarded; history only |
| `flashinfer-pdl-weight-prefetch-review` | `853aaf69d706b291afee477f738956b997033f53` | `b4ac8987f5d221c579ea42f1a46b017a6591d59b23d854f4bdb35084e4126a44` | Intentionally discarded; history only |
| `flashinfer-pdl-weight-scale-producer-review` | `853aaf69d706b291afee477f738956b997033f53` | `908626d7f466b74b8d39751546853cba7fa1cedd524af09bfb53c94b608e926d` | Intentionally discarded; history only |
| `flashinfer-physical-n16-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `f3fb82f552db70f4db5325a2c3d8733f84075887dcedeb011937ed5f0cabe08a` | Intentionally discarded; history only |
| `flashinfer-pipeline-fence-review` | `8b74eb6fa77651bb20dacb56b8e13872f3ad9885` | `c9d17cc6f9a88761e8f19c3d6ab47922186443abf1db73350f05680f1e1d5f60` | Intentionally discarded; history only |
| `flashinfer-prep-linear-sf-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `d5f19eca814c25b2af598b3e139cf9cec84770d4e9656f0bcd241512939bb722` | Intentionally discarded; history only |
| `flashinfer-producer-distributed-tma-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `ed32a7009d6d5e88fbb7809da20d8f01c83c21e89398c5e87da715ba3ac5b120` | Intentionally discarded; history only |
| `flashinfer-producer-roles-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `2fe04cbd18375f4d4286a7e80566485278c970d33243fac1557d6929a92ced4e` | Intentionally discarded; history only |
| `flashinfer-producer-roles-shared-empty-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `a2ee5b7865afc242df4842c3a0e9b5a6aae831ecdcc4c491f48a0ea52fc29041` | Intentionally discarded; history only |
| `flashinfer-regular-tma` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `ab1b2c7023c5cb8f2e09d1f24d851436f16f3463b2a043f473b15ed598af27f9` | Intentionally discarded; history only |
| `flashinfer-regular-tma-ldg256` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `ab1b2c7023c5cb8f2e09d1f24d851436f16f3463b2a043f473b15ed598af27f9` | Intentionally discarded; history only |
| `flashinfer-regular-tma-pipeline` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `c11217a2d1d73078970cc38618140a82f7adbed3c4cd4c6e7869d93ce5f5f2b8` | Intentionally discarded; history only |
| `flashinfer-regular-tma-sf-tile` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `ab1b2c7023c5cb8f2e09d1f24d851436f16f3463b2a043f473b15ed598af27f9` | Intentionally discarded; history only |
| `flashinfer-regular-tma-sf-vector-review` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `64b0a11c56e25cdcea7aec95a6480c4ba92405eeb53bf2f53705aba44aa9d081` | Intentionally discarded; history only |
| `flashinfer-regular-tma-validcopy` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `ab1b2c7023c5cb8f2e09d1f24d851436f16f3463b2a043f473b15ed598af27f9` | Intentionally discarded; history only |
| `flashinfer-sf-publisher-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `cb75e4e21d9f9caaff1e2a961ab55a2503ef405fddada26ec7a13ee65af05714` | Intentionally discarded; history only |
| `flashinfer-sf-readiness-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `9ea59e95563bc3643301a30c1bc8bf0384c32c62cee87f909de6d11a0d461998` | Intentionally discarded; history only |
| `flashinfer-sf-readiness-stage5-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `592d493a8703f5e4c23119c01af62e7eadc1939bd24b6467695954044505067f` | Intentionally discarded; history only |
| `flashinfer-sf-warp-localwait-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `bd68f086bd387a67e1aef139f54bb50fbbe83b2fcb893831562af7b790128132` | Intentionally discarded; history only |
| `flashinfer-sf-warp-pairedrow-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `02c813f3c0d45d9e3ad7cc563ded2c379dc2dca4644da1bab2651594aee61338` | Intentionally discarded; history only |
| `flashinfer-sf-warp-reuse-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `a69e473914da09412391a0448bf36e411aa1adc243525a0468e15542ebc00986` | Intentionally discarded; history only |
| `flashinfer-small-b-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `4f3bd8281953945e56598439deb26d6bc7d9937ba9c17f623a9ce8db24c87fbf` | Intentionally discarded; history only |
| `flashinfer-small-n-k4-occupancy-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `e41406b60abbe7b6874bd95197e1089e19653843647c1f980ee0493769c91230` | Intentionally discarded; history only |
| `flashinfer-small-n-linear-sf-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `f4b39b569fd687a3f93ee33afab89b22b7e0c6ab9b81b29d8d09208e97c6833e` | Intentionally discarded; history only |
| `flashinfer-small-n-occupancy-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `03cf86f03eb4187b42c0ada35ccadc54a3f5ef1d0f5077ee8603dd2ec1ccc7c8` | Intentionally discarded; history only |
| `flashinfer-stage-capacity-ktail-review` | `63d5fa0ea1c60e49242970e7721f0581e41c267a` | `0e356993ff79061743451ce3e9473f582264e23a8eb80be7025be3c334c3cc6a` | Intentionally discarded; history only |
| `flashinfer-stage-capacity-review` | `63d5fa0ea1c60e49242970e7721f0581e41c267a` | `06f6688c8136d1ad24214dadf84fc6885f98671aaa7e2915a1781bd11bebfcd6` | Intentionally discarded; history only |
| `flashinfer-static-tile-info-depth3-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `0a2df53f5be539ebc445d5cd61f209202e0873db41795b82f2139522474620a8` | Intentionally discarded; history only |
| `flashinfer-static-tile-info-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `72fc49fd2d04d7c42cd09d4f44ac2d56d97caba87cfcc33f37b430d9a04f54eb` | Intentionally discarded; history only |

## 2026-10-27 UTC: retained cleanup and single-policy CLC round

Retained head9b4721b0 is clean in canonical and generality-review. The all-CLC diagnostic and four-field policy copies were bumped to that head; only pending policy work remains unstaged. The proposed metadata-depth tuning axis was never deployed or benchmarked and was removed. Seven redundant retained clones and eight rejected/superseded clones were deleted without new recovery archives. Helper docs, gates, raw evidence and persistent remote C++/DSL caches remain. Exact inventories/provenance: `scripts/terminal_wait_20261027/closed-source-cleanup.json`, `scripts/composed_clc_cleanup_20261027/closed-source-cleanup.json`, and `scripts/composed_clc_cleanup_20261027/rejected-source-cleanup.json`. All GPU jobs for this round are complete.

## 2026-10-26: stale review copy removed

Removed `flashinfer-generality-review` at user request after verifying clean tracked state and the same HEAD/tree as canonical `flashinfer` at `9b4721b0`. Only generated Python/linter caches were present. No experiment or helper artifacts removed. Receipt: `scripts/shared_clc_20261026/review-cleanup.json`.

## 2026-10-26: keep only active in-progress review source

Removed14remaining stale/superseded experiment clones at user request, without creating recovery archives. Only `flashinfer/` (canonical retained source) and `flashinfer-shared-clc-20261026/` (active unstaged shared-CLC experiment) remain. Helper scripts, ledgers and result evidence stay in place. Full removed-name/status receipt: `scripts/shared_clc_20261026/stale-source-cleanup.json`.

## Additional completed experiment cleanup — 2026-10-27

Removed `flashinfer-clc-elected-owner-20261026` after rejecting both tested owner-loop versions. Verified base9b4721b0, exact final patch96cfbfbe, only the two expected device files modified, clean index, no untracked files, and only generated mypy/Ruff caches ignored. No archive was created. Frozen patches, source receipts, raw tables, codegen evidence and helper scripts remain under [the experiment directory](scripts/clc_elected_owner_20261026/); all remote sources and persistent compilation caches remain untouched. [Removal receipt](scripts/clc_elected_owner_20261026/local-source-cleanup.json). Canonical and shared-flag review source contents were preserved.

## Retained fence cleanup and review-base update — 2026-10-27

Retained/pushed `9c9ed58a` and removed the completed `flashinfer-clc-init-fence-20261027` clone after exact5112a25e patch verification, clean index, no untracked files and byte-identical comparison to retained source. Only generated mypy/Ruff caches accompanied the source change; no archive was created. [Cleanup receipt](scripts/pipeline_init_fence_20261027/local-source-cleanup.json).

Fast-forwarded `flashinfer-shared-clc-20261026` from9b4721b0 to9c9ed58a. Its two-file unstaged patch remains byte-identical (76ded8f7), and its index is clean. Historical shared-flag timing/source receipts are unchanged. [Bump receipt](scripts/shared_clc_bench_20261026/workspace-bump-9c9ed58a.json). Canonical and this active shared-flag copy are the only local FlashInfer source clones; reference repositories, helper scripts, ledgers and raw artifacts remain.

## Oct28 stale layout review cleanup

Removed the inactive `flashinfer-weight-layout-api-review/` at e2728a29 with one superseded prepare-PDL edit, no untracked files and only generated Ruff cache files. No source recovery archive created. Receipt: `optimization-20261028/tp-small-gemm-round/stale-layout-review-cleanup.json`. Current active copies are listed at the top of README.md.
