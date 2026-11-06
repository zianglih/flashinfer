# Full gathered-FC1 comparison against retained PR7290 head

- Candidate: committed fork PR8, `fb66a27e6b40bdbbefd1b8bf0c0fc3f3ada8af90`.
- Control: retained upstream PR7290, `d35fcfda03875077b3af8455575cc1d20e866a8c`.
- C3 existing devbox `fi-fc1-gather-1028`, 8 B300 GPUs, explicit image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2. One independent benchmark lane per GPU; same GPU for all four phases of a workload.
- Full tokens: 1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Tokens1–2 are collected but excluded from displayed heatmaps and aggregate retention summaries.
- 15 jobs /468 measured cells /396 displayed cells /187200 raw CUPTI samples when complete. Existing unsupported comparator combinations remain N/A. W4A16 is an unchanged diagnostic and excluded from affected-path aggregates.
- Strict CUPTI cold-L2 CUDA graphs,10 warmups,100 samples/phase, control–candidate–candidate–control, identical frozen routes and tactics, no tuning. NVFP4 includes input activation quantization; unfused finalize only. EP/TP select rank-local shapes; no distributed communication.
- Reuses9 persistent native compilation-cache links. Runtime resource guard uses normal CuTe compilation/cache behavior; no compiler dump flags or cache bypass.
- Earlier44 existing accuracy tests remain applicable to exact committed source; no additional correctness or sanitizer run requested for this measurement-only follow-up.

`prepare_body.py`, `prepare_remote.py`, `launch_remote.py`, `status_remote.py` record setup/dispatch. Use the existing managed-CLI `remote_box.py` wrapper from a configured HAI checkout. `plotting/` contains full-matrix validation and visualization helpers. Source checkouts are unchanged locally.

## Completed results

All468cells/187200freshsamples verified. Affected displayed geometric speedup: EP -0.7799%, TP +3.9310%; prefill EP -5.8237%, TP +8.7008%. Published to forkPR8 with both heatmaps and396raw displayed phase rows; linked CSV retains all468cells. Full runtime guard:854compiled instances,430FC1;84FC1instances with8–16bytes localstorage,allresourcechecks passed. See report/ and publication/receipt.json.
