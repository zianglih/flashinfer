# Precise-error one-warp retention qualification

Retain the existing one-warp bypass. The 24 source-paired precise-error cells all measured faster despite their additional local-memory traffic. Do not retain the conditional shared-buffer allocation: all nine captured binaries are identical to the simpler bypass. No additional policy, lifetime rewrite, or sanitizer run is warranted by this evidence.

## Measurement and exactness

- Eight BF16 cases reproduce the flagged K/SF-layout/error-recipe configurations; each uses rows 128, 4097, 131072. Main quantization fast math is enabled except strict K128; error estimation uses precise math in all cases. PDL remains enabled; retained default width is 32 threads. Initializers, output hashes, and source hashes match across all four phases.
- One exclusive B300 GPU3 (`GPU-828e523f-00a8-c70b-c818-2837a056cc49`), stock clocks. C-A-A-C, 10 warmups and 100 strict CUPTI samples per phase, cold-L2 CUDA graphs. All 96 phases/9,600 samples complete; all payload/SF/row-scale hashes agree.
- Measured source: control `2bb9ed15d2ba33520c6c8b015e43fe2d9d8a01fa08541dc7384c9163842ad0dc`, bypass `9960490f0d26786ab3c4491b9591cd126db944ec3e19a39bc3480e31ae2ab8f7`. Final formatted bypass is independently AST-equivalent (`format-equivalence.json`).
- Complete source/helper/telemetry/codegen evidence: `precise-stack-evidence-r1/`. Archive SHA256 `c5872b53a5216e64dfc46c2d9901c5a2055b32f068c2ceea52b7533b72e8ce83`, 131 hash-verified files. The first control diagnostic pass reused cached kernels; `codegen-control-r1` deliberately disables FlashInfer disk cache and captures all nine kernels. Timing runs are unchanged. The initial incomplete capture remains preserved.

Geometric mean **+1.685%**, range **+0.130% to +4.471%**. These are standalone quantizer results, not MoE end-to-end gains. The smallest changes are within sub-percent repeat variability; the evidence excludes a material regression in these cases, not every possible precise recipe.

| Case | K | SF layout | Error / FP8 max | Main strict | Rows | C1 µs | A1 µs | A2 µs | C2 µs | Change | C/A spread |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 64 | 1 | MAE / 256 | False | 128 | 3.9680 | 3.8720 | 3.8720 | 3.9680 | +2.479% | 0.000/0.000% |
| 0 | 64 | 1 | MAE / 256 | False | 4097 | 8.6400 | 8.5440 | 8.5440 | 8.6400 | +1.124% | 0.000/0.000% |
| 0 | 64 | 1 | MAE / 256 | False | 131072 | 227.7135 | 223.4900 | 223.4580 | 227.7130 | +1.897% | 0.000/0.014% |
| 1 | 64 | 2 | MAE / 448 | False | 128 | 3.9680 | 3.9200 | 3.9525 | 3.9680 | +0.807% | 0.000/0.829% |
| 1 | 64 | 2 | MAE / 448 | False | 4097 | 8.5920 | 8.4800 | 8.4645 | 8.6080 | +1.508% | 0.186/0.183% |
| 1 | 64 | 2 | MAE / 448 | False | 131072 | 225.9855 | 221.6980 | 221.7295 | 226.0170 | +1.934% | 0.014/0.014% |
| 2 | 128 | 0 | MSE / 448 | True | 128 | 4.0960 | 3.9360 | 3.9360 | 4.1280 | +4.471% | 0.781/0.000% |
| 2 | 128 | 0 | MSE / 448 | True | 4097 | 9.4080 | 9.1840 | 9.1840 | 9.4400 | +2.613% | 0.340/0.000% |
| 2 | 128 | 0 | MSE / 448 | True | 131072 | 253.9375 | 250.2415 | 250.0500 | 254.0015 | +1.529% | 0.025/0.077% |
| 3 | 64 | 2 | MAE / 256 | False | 128 | 3.9680 | 3.8720 | 3.9040 | 3.9680 | +2.058% | 0.000/0.826% |
| 3 | 64 | 2 | MAE / 256 | False | 4097 | 8.5760 | 8.4800 | 8.4480 | 8.5770 | +1.329% | 0.012/0.379% |
| 3 | 64 | 2 | MAE / 256 | False | 131072 | 225.8570 | 221.6490 | 221.7615 | 226.0010 | +1.905% | 0.064/0.051% |
| 4 | 64 | 0 | MAE / 448 | False | 128 | 4.0960 | 4.0000 | 4.0320 | 4.0960 | +1.993% | 0.000/0.800% |
| 4 | 64 | 0 | MAE / 448 | False | 4097 | 8.7040 | 8.6085 | 8.6080 | 8.7040 | +1.112% | 0.000/0.006% |
| 4 | 64 | 0 | MAE / 448 | False | 131072 | 230.6570 | 227.2810 | 227.0410 | 230.7370 | +1.557% | 0.035/0.106% |
| 5 | 64 | 0 | MSE / 256 | False | 128 | 3.9520 | 3.8720 | 3.8720 | 3.9680 | +2.273% | 0.405/0.000% |
| 5 | 64 | 0 | MSE / 256 | False | 4097 | 8.7680 | 8.7360 | 8.7515 | 8.7680 | +0.277% | 0.000/0.177% |
| 5 | 64 | 0 | MSE / 256 | False | 131072 | 235.3930 | 235.0090 | 235.1690 | 235.3940 | +0.130% | 0.000/0.068% |
| 6 | 512 | 0 | MAE / 448 | False | 128 | 4.2240 | 4.1280 | 4.1285 | 4.2405 | +2.519% | 0.391/0.012% |
| 6 | 512 | 0 | MAE / 448 | False | 4097 | 9.2160 | 9.1200 | 9.1520 | 9.2160 | +0.876% | 0.000/0.351% |
| 6 | 512 | 0 | MAE / 448 | False | 131072 | 237.7770 | 234.8485 | 234.8490 | 237.7620 | +1.244% | 0.006/0.000% |
| 7 | 512 | 0 | MAE / 256 | False | 128 | 4.0640 | 3.9680 | 3.9680 | 4.0640 | +2.419% | 0.000/0.000% |
| 7 | 512 | 0 | MAE / 256 | False | 4097 | 9.2160 | 9.0880 | 9.1200 | 9.2165 | +1.233% | 0.005/0.352% |
| 7 | 512 | 0 | MAE / 256 | False | 131072 | 237.8250 | 234.8650 | 234.9930 | 237.9060 | +1.250% | 0.034/0.054% |

Maximum control repeat spread 0.781%; candidate 0.829%. NVML samples fully within each timing window: SM 2032 MHz, memory 3996 MHz, event mask 0 in all windows. This is sampled telemetry, not an assertion about unsampled transients. No clock normalization or fixed clocks.

## Resources and simplification decision

- Fresh matched diagnostics confirm all eight precise cases increase stack 24→32 B; the two K512 cases differ from their earlier gate capture, so this report uses fresh source-paired resources rather than silently merging captures. These eight source-matched timing cases still improve. The K1024/64-thread multiwarp control remains byte-identical.
- Allocating the shared reduction buffer only when `warps>1` produces exactly the same nine cubins, including stack/local loads/stores. The compiler already eliminates the unused one-warp allocation. It cannot shorten the quantization arithmetic live ranges. The extra optional-buffer interface/branch is rejected; its patch/source/evidence is preserved and the local review clone is retired.
- `row_amax` is required by both row-scale calculation and precise 4over6 quantization, while the eight packed input words must survive for the single-load second pass. Renaming or explicitly deleting Python bindings does not shorten those data dependencies; no new branch, reload, or precision-specific policy is added in an attempt to rearrange registers.

## Published TRTLLM baseline reuse

The existing external baselines remain valid for this bypass. The shared Python per-token quantizer only sees full input H: V3=7168,V41F=5120,K3=3584,N3U=2048, in both EP and TP. All 52 model/token policies (39 supported TRTLLM policies) use at least 128 threads. Expanding the three introduced constexpr guards for multiwarp calls and normalizing the local `warp_amax`→`row_amax` SSA name reproduces the entire old module AST. This proves unchanged ordinary quantization and the full multiwarp kernel, supported by 36 matched byte-identical cubins. Eight dispatch/native source hashes are unchanged; TRTLLM intermediate per-token quantization is its own native 128-thread C++ path. K3 remains unsupported for TRTLLM. See `trtllm-bypass-impact.json`; no external baseline rerun is required.

GPU3 was released idle after all diagnostics: 0 MiB, no compute processes, SM 120 MHz. Broad-r1 end-to-end retention evidence remains separately owned by the parent task.
