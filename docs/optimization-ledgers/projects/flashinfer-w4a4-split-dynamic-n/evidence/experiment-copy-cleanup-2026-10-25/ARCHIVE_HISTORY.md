# Experiment history and surviving baseline archives

The70-copy campaign was fully archived and verified before cleanup. The user subsequently requested that unretained experiments need not remain recoverable. Accordingly, the64 experiment archive snapshots are intentionally discarded; only six clean-baseline archives remain from this campaign. The separate16 retained-review archives remain under `../retained-copy-cleanup-2026-10-25/archive/`.

Performance notes, scripts, logs, raw measurements, validation receipts, historical source identifiers and PR drafts are preserved. Earlier `archive-receipt.json` and verification reports describe the pre-pruning audit; they are historical evidence, not a current archive-availability manifest. See [the completed disposition](archive-disposition.json) and [the exact discard selection](unretained-archive-discard-selection.json).

See the project [source-copy ledger](../../SOURCE_COPY_ARCHIVE_LEDGER.md) for all86 original names and links to optimization history.

## Recover one of the six baselines

Create a new independent project-local clone from canonical `flashinfer/`, check out the exact base HEAD in the linked receipt, and extract its `working-tree-files.tar.gz` if present. These baselines have empty tracked diffs and no untracked source. Their saved Git metadata and ignored files can be checked against `files.json`; canonical main contains the required base objects. Do not use the discarded-experiment table as a recovery promise.

| Baseline | Base HEAD | Complete patch SHA256 | Recovery receipt | Archive |
|---|---|---|---|---|
| `flashinfer-b300-original-a65` | `a65d5b09e7e4c4c5c160b0161c48becd100b3970` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](archive/flashinfer-b300-original-a65/receipt.json) | [files](archive/flashinfer-b300-original-a65/) |
| `flashinfer-b300-retained-853` | `853aaf69d706b291afee477f738956b997033f53` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](archive/flashinfer-b300-retained-853/receipt.json) | [files](archive/flashinfer-b300-retained-853/) |
| `flashinfer-fc2-kstage-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](archive/flashinfer-fc2-kstage-review/receipt.json) | [files](archive/flashinfer-fc2-kstage-review/) |
| `flashinfer-pdl-retention-frozen` | `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](archive/flashinfer-pdl-retention-frozen/receipt.json) | [files](archive/flashinfer-pdl-retention-frozen/) |
| `flashinfer-pr-scope-review` | `8b74eb6fa77651bb20dacb56b8e13872f3ad9885` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](archive/flashinfer-pr-scope-review/receipt.json) | [files](archive/flashinfer-pr-scope-review/) |
| `flashinfer-profile-98fd` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | [receipt](archive/flashinfer-profile-98fd/receipt.json) | [files](archive/flashinfer-profile-98fd/) |

## Discarded experiment snapshot identifiers (64)

Each snapshot below is intentionally discarded per user request; the existing experiment history is preserved.

| Experiment | Base HEAD | Historical complete patch SHA256 |
|---|---|---|
| `flashinfer-clc-scheduler-depth2-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `ee646b2c395a89a868e00311708495723fcb4b39089b7eda6a19c39ab4afa83c` |
| `flashinfer-clc-scheduler-reservation-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `eb431be438ba9ffabf0f160d283d9bcdb7106d37f0f63ed65255f6e0457f8d03` |
| `flashinfer-clc-scheduler-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `595eea40ee038fc61e24331748250703999cfbc7e127426ff817620d2a8f1ab0` |
| `flashinfer-clc-single-cta-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `6b3f1c4f532addca0a44a59c6b0b64207bff7a8c88819834f101e891773a1775` |
| `flashinfer-clc-static-control-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `d32be72863bf6f3496632a072d4d7ea81ab5d7d4f69c9f649e54b7dde2c74d97` |
| `flashinfer-compact-sf-broadcast-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `a130562c2da8314ce68c4f892a3e01fd10b6831746920b1a49e3c11ebe944ee7` |
| `flashinfer-compact-sf-publisher-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `ae4baacb9681eb1e2463cfd6a963e4902f2b58dcbcef753d27f8adaf3b13a718` |
| `flashinfer-dynamic-n8-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `ca83b907f588dfb728e9fc4820c294d4793a78335ebe87f237cce7acb5ec4da5` |
| `flashinfer-epilogue-codesign-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `1aad6df6daf5d89306b98aa0a310c95d8a467604324e0c9385d831a3773b72dd` |
| `flashinfer-fc1-tma-roles-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `a4ae50d117d21d0540b12b5524a8bf7b3103a20f67c0fde154eb204865745ae4` |
| `flashinfer-fc1-weight-prefetch-review` | `24c48b9fd5d7c38fdcea213376602f97635c4ef9` | `e05fcdc72c6c8e74df4cec6f8b31f94a74955cd29e5eca14103ec83a15649cd0` |
| `flashinfer-fc2-clc-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `382050d796e160f01d9a996a73b7fdb03f574c5542946b064f683ec35f8255ee` |
| `flashinfer-fc2-narrow-bulk-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `19b18874bd31c6654785bdffd862f74a7264f2851d701468119a53e429467399` |
| `flashinfer-fc2-narrow-bulk16-offset-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `3d09bce11b296e205a93ee538c1080d6cb949feeb3877fce75b7a215acc793e4` |
| `flashinfer-fc2-narrow-bulk16-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `f2bb5f50a6c8de22308e666995111389cd6b7857f38d58291c0954dfca17832c` |
| `flashinfer-fc2-physical-n16-bulk-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `61430be0fb7cf618cad64d7c4f8c63c02a7765b49dbb9bb8568be4d5f07e2fc2` |
| `flashinfer-merged-operand-ring-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `d5150b6531f2406341ab1b0c6f03db53b6607bd71e9b0ebe33d657f6f897dfe8` |
| `flashinfer-mma-k-tail-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `6ac943784ffa8d8a932da06540f3685bf453c5619c7a0de6da6117f52e652d5d` |
| `flashinfer-narrow-channel-reuse-review` | `0c1e00fc3e4f913c8c241796c70a29673737c542` | `ba51fa57b297abdbed523d4224a2b816661c74d98306fe372c2af9494fdd1d5a` |
| `flashinfer-narrow-epilogue-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `ef8c2d72d9eb9c8b7206dfaefce8e3bf3df2f8e738ae095c95c81507c4cf3f1a` |
| `flashinfer-narrow-ld256-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `e6fd4241aaa3b2b61c0038270ad751c374e578a6bf0d279fffd0df7fef20de02` |
| `flashinfer-packed-combine-review` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `6b992fa2596042eef1e7bd9d23360f962491876dc0ecc5c03d5d64a678bf8ace` |
| `flashinfer-pdl-allthread-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `56a6baea42e29a72eac77db47c44f820c6ee4c9038200a60bf8d4d6cce309f37` |
| `flashinfer-pdl-descriptor-prefetch-review` | `853aaf69d706b291afee477f738956b997033f53` | `50d44ac4085ac158b5d63767707054d6948895bc4797acccdba9f13ec66421e3` |
| `flashinfer-pdl-explicit-phase-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `a0f4519e163e38fb79960282602c224ecbafc0e2f0fc65d1d59afea1f846a37e` |
| `flashinfer-pdl-fc1-trigger-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `b6af5db71465fccd58ed9feab79df19765a62e45d5e085d456977168dcda3905` |
| `flashinfer-pdl-fc2-producer-wait-review` | `adf02fdd4a8fd2a5d4d2ca54b6969cd65572d93d` | `d631e9c0519d09bb07ba6b08fdcd62a390f17497cdbb0f2e8db4205bbed19ead` |
| `flashinfer-pdl-first-metadata-r2-review` | `853aaf69d706b291afee477f738956b997033f53` | `fb34e3e6ed0dfe871d7c1f34f513f3b7dfb0ec1b2159dc5f273acf3ceefea2eb` |
| `flashinfer-pdl-first-metadata-review` | `853aaf69d706b291afee477f738956b997033f53` | `37c9a0b2d9ac70837f51a1bc1db8b2b753c9e7b56ad416da6cad05715d9db7f5` |
| `flashinfer-pdl-handoff-cache-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `9b9aeb08ae5b312236dbc650008ee9f3ff5a1925da0d4c851902dc736019cf08` |
| `flashinfer-pdl-livecount-review` | `853aaf69d706b291afee477f738956b997033f53` | `d62db70d74fa96191f0defdf91bbca534bba0e3b0db3c6f12804da9ef58bc12f` |
| `flashinfer-pdl-producer-drain-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `da0efb6829624f1bfb2c4e8c3c9db39e6a943bf6f653f99ee6c5edc3814c6a54` |
| `flashinfer-pdl-producer-wait-review` | `24c48b9fd5d7c38fdcea213376602f97635c4ef9` | `8c0186207be4bf505d2f8a6a7f323798b7b09ece341c7b1c5b2aa2b456f08874` |
| `flashinfer-pdl-sfa-stream-review` | `853aaf69d706b291afee477f738956b997033f53` | `b73a9abeef6f3b6d23e5f6173b0cda2f68beeb56555e50f40d5c58164827bab3` |
| `flashinfer-pdl-startup-review` | `aab93f854054de834447bdd8985b8bbd653fb3c8` | `df6aa74e84c99f14becffa049adad8b60ab4b5aa22bbb92a48d2b0d4d3e0bf3a` |
| `flashinfer-pdl-weight-prefetch-multistage-review` | `853aaf69d706b291afee477f738956b997033f53` | `9cea43321866c8b08fa5b2371c436f78cbc1e46e6117838cbd960741e134dc07` |
| `flashinfer-pdl-weight-prefetch-review` | `853aaf69d706b291afee477f738956b997033f53` | `b4ac8987f5d221c579ea42f1a46b017a6591d59b23d854f4bdb35084e4126a44` |
| `flashinfer-pdl-weight-scale-producer-review` | `853aaf69d706b291afee477f738956b997033f53` | `908626d7f466b74b8d39751546853cba7fa1cedd524af09bfb53c94b608e926d` |
| `flashinfer-physical-n16-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `f3fb82f552db70f4db5325a2c3d8733f84075887dcedeb011937ed5f0cabe08a` |
| `flashinfer-pipeline-fence-review` | `8b74eb6fa77651bb20dacb56b8e13872f3ad9885` | `c9d17cc6f9a88761e8f19c3d6ab47922186443abf1db73350f05680f1e1d5f60` |
| `flashinfer-prep-linear-sf-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `d5f19eca814c25b2af598b3e139cf9cec84770d4e9656f0bcd241512939bb722` |
| `flashinfer-producer-distributed-tma-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `ed32a7009d6d5e88fbb7809da20d8f01c83c21e89398c5e87da715ba3ac5b120` |
| `flashinfer-producer-roles-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `2fe04cbd18375f4d4286a7e80566485278c970d33243fac1557d6929a92ced4e` |
| `flashinfer-producer-roles-shared-empty-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `a2ee5b7865afc242df4842c3a0e9b5a6aae831ecdcc4c491f48a0ea52fc29041` |
| `flashinfer-regular-tma` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `ab1b2c7023c5cb8f2e09d1f24d851436f16f3463b2a043f473b15ed598af27f9` |
| `flashinfer-regular-tma-ldg256` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `ab1b2c7023c5cb8f2e09d1f24d851436f16f3463b2a043f473b15ed598af27f9` |
| `flashinfer-regular-tma-pipeline` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `c11217a2d1d73078970cc38618140a82f7adbed3c4cd4c6e7869d93ce5f5f2b8` |
| `flashinfer-regular-tma-sf-tile` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `ab1b2c7023c5cb8f2e09d1f24d851436f16f3463b2a043f473b15ed598af27f9` |
| `flashinfer-regular-tma-sf-vector-review` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `64b0a11c56e25cdcea7aec95a6480c4ba92405eeb53bf2f53705aba44aa9d081` |
| `flashinfer-regular-tma-validcopy` | `442d2aa53f68b4640c3ab5118a76f1599ff60d34` | `ab1b2c7023c5cb8f2e09d1f24d851436f16f3463b2a043f473b15ed598af27f9` |
| `flashinfer-sf-publisher-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `cb75e4e21d9f9caaff1e2a961ab55a2503ef405fddada26ec7a13ee65af05714` |
| `flashinfer-sf-readiness-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `9ea59e95563bc3643301a30c1bc8bf0384c32c62cee87f909de6d11a0d461998` |
| `flashinfer-sf-readiness-stage5-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `592d493a8703f5e4c23119c01af62e7eadc1939bd24b6467695954044505067f` |
| `flashinfer-sf-warp-localwait-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `bd68f086bd387a67e1aef139f54bb50fbbe83b2fcb893831562af7b790128132` |
| `flashinfer-sf-warp-pairedrow-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `02c813f3c0d45d9e3ad7cc563ded2c379dc2dca4644da1bab2651594aee61338` |
| `flashinfer-sf-warp-reuse-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `a69e473914da09412391a0448bf36e411aa1adc243525a0468e15542ebc00986` |
| `flashinfer-small-b-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `4f3bd8281953945e56598439deb26d6bc7d9937ba9c17f623a9ce8db24c87fbf` |
| `flashinfer-small-n-k4-occupancy-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `e41406b60abbe7b6874bd95197e1089e19653843647c1f980ee0493769c91230` |
| `flashinfer-small-n-linear-sf-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `f4b39b569fd687a3f93ee33afab89b22b7e0c6ab9b81b29d8d09208e97c6833e` |
| `flashinfer-small-n-occupancy-review` | `98fd3566b5f945c100f48cddacf25deb2432cbc2` | `03cf86f03eb4187b42c0ada35ccadc54a3f5ef1d0f5077ee8603dd2ec1ccc7c8` |
| `flashinfer-stage-capacity-ktail-review` | `63d5fa0ea1c60e49242970e7721f0581e41c267a` | `0e356993ff79061743451ce3e9473f582264e23a8eb80be7025be3c334c3cc6a` |
| `flashinfer-stage-capacity-review` | `63d5fa0ea1c60e49242970e7721f0581e41c267a` | `06f6688c8136d1ad24214dadf84fc6885f98671aaa7e2915a1781bd11bebfcd6` |
| `flashinfer-static-tile-info-depth3-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `0a2df53f5be539ebc445d5cd61f209202e0873db41795b82f2139522474620a8` |
| `flashinfer-static-tile-info-review` | `fca8462cbd9096059d0019a206aa760fb34ca8c4` | `72fc49fd2d04d7c42cd09d4f44ac2d56d97caba87cfcc33f37b430d9a04f54eb` |
