# Private HashInfer transport phase tracing

Status: both shapes pass fresh numerical and native qualification at `f4dc6e1b4990df3a783ab51b43f497a482811d5c`, source+fixture `50e19c04f93b952fdeac634f0fe36e7fb053fe37f1a31c4babb9674bdd767d69`. Publication receipt is tracked separately in `completion.json`.

The change adds six input-pull and two output-return phase ranges, with route/expert payloads, directly in the existing vendored `token_comm.py`. It remains private to HashInfer. No upstream code is touched, and no implementation is duplicated. Removing the16 marker lines restores the original source bytes. See `source-audit-v3-elected.json` and `peer-source-review-v2-elected.json`.

Both EP4 GLM-5 uniform128 and uniform4096 shapes are freshly tuned over the same eight candidates. Native IKET records cluster0 from the unmodified148-CTA launch. Capture output equality and original SASS/config/runtime event nesting must pass before reporting success. The cleanest rank is chosen by its minimum worst-track initial `dispatch_exchange_counts_sync` duration; duration comparisons do not align GPU clocks. Complete selected rank PF files are copied unchanged.

GPU box: retained C2/infra `fi-w4a16-align256-r2-0926`, node `hu-pdx-43`, B300, GPUs0-3. Image `nvcr.io/nvidia/pytorch:26.05-py3`; shared venv `/workspace/hashinfer-alignment256-20260926/venv`, CuTe/IKET4.8.0. Do not release the box.

Reproduction: `run-shape.sh COMMIT GLOBAL_TOKENS ATTEMPT` runs baseline/autotune followed by native capture using explicit localhost rendezvous. `download_capture.py` validates every archive chunk and the assembled archive SHA. `prepared-audit-v2-128.json` and `prepared-audit-v2-4096.json` contain exact audit commands and source-only plans. `render_audit_v2.py` summarizes accepted audits. Artifacts stay outside the source repository.

Accepted outputs: `remote-v2-128`, `remote-v2-4096`; strictaudits `audit-v2-128`, `audit-v2-4096`; summaries `summary-v2-128.md`, `summary-v2-4096.md`. Selectedrank2 files have startupgate maxima9.440us/11.552us. Both fullPF copies are byte-identical to their original rankPF. V1 remains rejected in `REJECTED-v1.md`. The4096 firsttar reported directory change; its original archive remains preserved remotely. Repack verified all input hashes unchanged; see `remote-archive-receipt-v2-4096.json`.
