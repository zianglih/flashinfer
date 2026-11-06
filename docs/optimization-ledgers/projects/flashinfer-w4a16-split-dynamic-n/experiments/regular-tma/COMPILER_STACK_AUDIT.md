# Compiler-stack fingerprint relocation audit

Independent read-only audit, 2026-10-25. **The complete historical compiler-stack fingerprint is reproduced exactly by accounting for three generated entrypoint shebang paths and their RECORD hash/size entries.** No installed package, source, cache metadata or benchmark result was changed. No compiler or GPU operation was run.

## Evidence

- Historical fingerprint: `experiments/gather4/results/split-v3/RESULTS.json`, `full_tactic_caches.before-r1["16"]._metadata.cutlass_dsl_version`.
- Current benchmark fingerprint: `experiments/regular-tma/probes/prep-v1/benchmark.t16.autotune.json`, `_metadata.cutlass_dsl_version`.
- Fingerprint definition: `flashinfer-regular-tma/flashinfer/jit/cute_dsl_core.py:45–86`. For each selected distribution it hashes JSON containing the complete installed `RECORD` text and `direct_url.json`; it also includes Python ABI identifiers and sorted package identities.
- Reproduction helper: `audit_compiler_record_relocation.py`, SHA256 `effa7636d4343a8cb3a6a6c48761aed8d57d34b28145656b9a013919b6e4d3d0`.
- Full raw receipt: `evidence/setup/compiler-record-relocation-audit.json`, SHA256 `20e561ef5b3e8f8fdde8fcfef981df986bd806c6e4054a2ab70499891fd00aa8`.

The current environment is `/workspace/flashinfer-w4a16-regular-tma/.venv`; the previous `/workspace/flashinfer-w4a16-gather4/.venv` is absent. The helper ran under the current benchmark Python using only standard-library metadata and file reads. For each differing distribution it checked every hashed installed file against the recorded digest and size, reconstructed only the interpreter path on the first line of generated scripts, updated only those scripts' RECORD hash/size fields in memory, and recomputed the original fingerprint algorithm without changing `direct_url`.

| Distribution | Current hashed files verified | Reconstructed entries | Historical digest matched |
|---|---:|---|---|
| `apache-tvm-ffi==0.1.15.post0` | 258 | `bin/tvm-ffi-config`, `bin/tvm-ffi-stubgen` | `c6512e315f49030a13f3729233b53ef4fcca526ea05be71fc03023e392908a5d` |
| `nvidia-cutlass-dsl-libs-base==4.7.1` | 103 | `bin/run-iket` | `c50ea58715fe2a2b310b365e98a5e95289f57956294a16a5749d9c128b25802a` |

Both current `direct_url.json` values are absent/null. All other selected package provenance digests and both Python ABI identifiers already match. The resulting full string matches the saved historical string exactly. The raw current fingerprint also matches the current benchmark's recorded string exactly, tying the inspected installation to that benchmark record.

Every other T16 cache metadata field matches: GPU, CUDA, cuBLAS, cuDNN, cuDNN frontend and FlashInfer version. Saved historical `nvidia-smi-before.txt` and current remote `logs/nvidia-smi-initial.txt` both report driver `595.91.07` and CUDA `13.2`. These are separate checks; driver identity is not part of this fingerprint.

## Scope and comparison limits

- Raw fingerprints remain different. The justified statement is **recorded compiler-package equivalence modulo generated interpreter paths**, supported by an exact reconstruction. It is not literal installation-byte equality.
- The old environment is unavailable. The receipt proves agreement of historical recorded file hashes, not that the historical installed files had no unrecorded modifications. Current files in the two differing packages were checked against those manifests; other packages' unchanged RECORD digests were compared without rehashing their full installed payloads.
- RECORD entries without hashes, principally generated `.pyc` files and RECORD itself, are listed in the receipt. Historical `.pyc` contents cannot be compared. RECORD text is covered by the aggregate provenance digest.
- The fingerprint does not capture which installed CUDA-family backend was selected, generated cubins, driver configuration, all environment variables, CPU scheduling, GPU thermal state or performance drift. Matching driver and package evidence removes the observed provenance mismatch but does not establish those other properties.
- Historical control measurements remain historical: no fresh bracketing baseline was run for these screens. Any speedup comparison must preserve that temporal limitation and the independent benchmark identity/routing/timing checks.

Do not rewrite saved cache metadata or broadly ignore `cutlass_dsl_version`. If a comparison accepts this relocation, require this explicit receipt, pin its hash and exact old/current fingerprint strings, and continue rejecting every other metadata difference. No comparison-validator relaxation was made by this audit.

The first transport attempt used Python stdin through `h ssh`, which returned no script output; its empty stdout/stderr artifacts are retained as `stdin-attempt-*`. The successful audited command passed the helper through Python `-c`; the receipt above comes only from that successful execution.
