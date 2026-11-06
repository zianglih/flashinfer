# Padded FC2 output experiment

Final review: [RESULTS.md](RESULTS.md). The active unstaged source is **r2** (`ec675177`): padded routed BF16 output, existing inverse map, and uniform nonempty-slab TMA. R1 below is the archived initial experiment and retained-head timing control.

Baseline: `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`. Candidate is an unstaged five-file patch in `flashinfer-padded-output-review`. Production sources are frozen per experiment; no sanitizer this iteration.

## Frozen r1

- `r1/source-local.json`: all348 benchmark/kernel/source hashes, exactly five changed paths, helper hashes.
- `r1/candidate.patch`: patch SHA `6ea21d4b2918b7b9c730969fd04b6f3421459f2116c0712b8b55b83d0a6152c2`.
- Kernel SHA `ff6993cbaf412222b15ac5bc27ae421fbbcc30c7b1520475c0e35b7d2033620f`.
- Remote root `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/padded-output/r1`.
- Runtime reused from the final61249 refresh: CUDA13.2/B300, `nvcr.io/nvidia/pytorch:26.05-py3`; persistent native C++ compile-cache links retained. Each compile process gets a private working directory for PTX/cubin artifacts.
- Initial deployment stopped before GPU launch because Git serialized patch index IDs at7 versus8 characters. All348 file hashes matched. `deployment-diagnostic.json` records the difference; resume verifies exact paths/content instead. No source modification.

## Exact qualification

`probe_pair.py` is a scoped adaptation of the existing source-paired replay/codegen harness, using the public wrapper and explicit existing tactics. It compares final output storage bits, not physically different FC2 buffers.

Main eight configs cover allfour scaled formats (NVFP4 W4A4, per-token, MXFP8, MXFP4x8), N128/M128 oneCTA and N256/M256 twoCTA, static/CLC, PDLoff/on, balanced/skewed/empty/reactivated routes.128 graph replay comparisons per source;64 paired GEMM specializations. Skewed257-token/top2 routes give both full slabs and partial tails. Every FC2 output buffer is NaN-poisoned before replay, while original routing-map reciprocity and local/nonlocal row ownership are checked. This does not require invalid padded rows to have defined values.

Separate `small/` probe covers N16/N64 nonbulk SIMT outer epilogues for allfour formats, same routing/PDL/scheduler checks;64 additional replay comparisons and32 GEMM pairs. No source/tactic policy is changed by the harness.

Eight existing pytest nodes cover legacy W4A4/per-token unfused/fused endpoints, old/new W4A16 layout accuracy, and old/new W4A16 graph capture. Fused legacy tests retain their existing non-exact assertion contract; new padded unfused paths are exact source-paired checks. `moe_unpermute` generic expanded/routed map smoke is included in each probe process.

Primary GPUs0–3 main paired gate, GPU4 pytest, GPUs5–6 small paired gate. The gate writes raw PTX, cubin, encoded SASS, resource reports and source-bound receipts.

## Performance screen

15 jobs on the two existing boxes: primary8 EP family/model jobs; secondary7 TP jobs.112 scaled cells plus32 unchanged W4A16 control cells, tokens4/64/4096/16384. V3/K3/N3U use EP8 or TP8; V41F EP4 or TP4. K3MXFP8 and V41FTP MX remain excluded as unsupported comparable cases.

C-A-A-C on the same GPU per job;10 warmups and100 strict CUPTI cold-L2 graph samples per phase.144 cells/576 medians/57,600 samples. Replay current61249 caches/winners/routes (the same retained83df selections), no AUTO and no TRTLLM/non-swap rerun. NV includes activation quantization; MX retains graph tuning policy. Source hashes, every native cache hit, winner identity, routing identity, raw sample median and managed cache immutability are checked per phase.

The observer adds only host shape metadata at existing FC2 launches: model/token context, output shape/bytes, route capacity, dtype and MMA/cluster geometry. No device reads, syncs or extra GPU work. Each measurement's `native_diagnostic.measurements[].fc2_outputs` supplies exact output-memory deltas for root analysis. No final report or publication is generated here.

## Commands

Run from the project root. Preparation/deployment commands are only used after root authorizes a frozen source:

```sh
python3 optimization-20261028/padded-output/harness/freeze.py \
  --candidate-repo "$PWD/flashinfer-padded-output-review" --name r1
python3 optimization-20261028/tp-ep-post-sanitizer/remote_box.py \
  --box fi-moe-nvfp4-port-1026 optimization-20261028/padded-output/r1/deploy.py
python3 optimization-20261028/tp-ep-post-sanitizer/remote_box.py \
  --box fi-moe-nvfp4-port-1026 optimization-20261028/padded-output/r1/invoke_gate.py
python3 optimization-20261028/tp-ep-post-sanitizer/remote_box.py \
  --box fi-moe-nvfp4-port-1026 optimization-20261028/padded-output/r1/deploy_launch_small.py
python3 optimization-20261028/tp-ep-post-sanitizer/remote_box.py \
  --box fi-moe-nvfp4-port-1026 optimization-20261028/padded-output/r1/status_remote.py
```

The common transport uses only `/usr/local/bin/h ssh <box> -c c3 -n infra -- ...` after verifying the managed CLI path. Do not recreate/deploy over an existing frozen root. Benchmark launch requires verified main+small+pytest receipts and source binding; root authorizes timing after those checks. All raw outcomes are retained, including infrastructure/harness failures.
