# CUDA 13.0 W4A16 evidence

All 104 cases and 41,600 samples are fresh CUDA 13.0 measurements. Tokens 1/2 remain in raw files; 88 cases contribute to plots and aggregates. Extract both raw archives into the same directory to replay the independent analyzer. Original native stdout is also linked from [the full absolute/CAAC tables](tables.md).

| Archive | Bytes | SHA256 |
|---|---:|---|
| [cuda130-w4a16-raw-ep.tar.xz](cuda130-w4a16-raw-ep.tar.xz) | 17,332,840 | `89333080b862eb42b14ad9e3c68381898aa3e81a51243f734f8fc6577c198b3b` |
| [cuda130-w4a16-raw-tp.tar.xz](cuda130-w4a16-raw-tp.tar.xz) | 16,297,252 | `6aeb26ed1d68c1c2175a362db589b3701d9f562382873a6eb86e47530fceb9b6` |
| [cuda130-w4a16-reproduction.tar.xz](cuda130-w4a16-reproduction.tar.xz) | 1,836,992 | `e0e393bbcba6dcb1328f29cc15d0b92645622267fdd6a358fa527eb9559cfa56` |

The reproduction archive includes source and runtime manifests, the benchmark adapter, exact cache choices, compact historical route/winner expectations, independent analysis and all table/plot source. Original historical timing arrays, full source tarballs and compiled caches are excluded. [Manifest](bundle-manifest.json) lists and hashes every member; [historical context dependencies](dependencies.json) remain immutable external references and are not needed for the fresh timing replay.
