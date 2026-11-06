# SF address cleanup disposition

Recommend retention as a small instruction/conciseness cleanup: +1/−4 source lines, one removed selector in each affected narrow kernel, unchanged storage/registers/copy counts and no spills. No end-to-end speedup claim.

The source-paired 48-point fixed screen measured 1.001574× overall, 0.999822× decode, and 1.003330× prefill. All 267 collected hashes, 19,200 raw samples, routes, fixed selections and quantization contracts passed independent validation. Selection data comes from historical shared360 winners; both executing sources are pinned to f718.

| Model | Format | Decode | Prefill |
|---|---|---:|---:|
| kimi-k3 | CuteDSL MXFP4x8 | 0.999610× | 1.025669× |
| kimi-k3 | CuteDSL MXFP8 | 0.999499× | 1.009669× |
| kimi-k3 | CuteDSL PER-TOKEN | 1.000758× | 1.002560× |
| kimi-k3 | CuteDSL W4A4 | 0.999458× | 0.988482× |
| v3 | CuteDSL MXFP4x8 | 1.000077× | 1.018913× |
| v3 | CuteDSL MXFP8 | 0.999941× | 1.003134× |
| v3 | CuteDSL PER-TOKEN | 0.998438× | 0.999736× |
| v3 | CuteDSL W4A4 | 0.999426× | 0.999439× |
| v41-flash | CuteDSL MXFP4x8 | 1.000650× | 0.989641× |
| v41-flash | CuteDSL MXFP8 | 1.000048× | 1.001365× |
| v41-flash | CuteDSL PER-TOKEN | 0.999987× | 1.000944× |
| v41-flash | CuteDSL W4A4 | 0.999971× | 1.001020× |

The root-requested repeat covers only the two initially slow prefill cells, on their original GPUs with identical sources/routes/tactics. It adds 800 samples without replacing the original matrix:

| Cell | Initial speedup | Repeat speedup | Repeat C/A/A/C medians (µs) |
|---|---:|---:|---|
| kimi-k3 CuteDSL W4A4 T16384 | 0.977200× | 1.015503× | 809.926 / 796.566 / 802.502 / 813.926 |
| v41-flash CuteDSL MXFP4x8 T16384 | 0.979894× | 0.989759× | 894.405 / 900.742 / 901.478 / 889.365 |

Both repeated cells have `tma_sfb=True` in actual FC1/FC2 compile observations, making the removed narrow-source branch inactive. K3 reverses direction; V41 retains a small loss. The cached compile IR did not expose a `gpu.binary` for optional extraction, so the report does not claim exact model-kernel encoding identity. No further timing rerun is recommended.

The installed `cute.add_offset` lowering uses a non-inbounds LLVM GEP. Together with the full kernel’s unchanged source-size-zero cp.async predicate, this resolves the masked past-allocation pointer question without an extra runtime test. See `pointer-lowering-review.json` and its exact IR artifacts.

The initial timing preflight used a stale expected HEAD and failed before measurements. Its isolated logs are preserved; only the f718-bound successful runs enter these summaries. The source patch remains frozen and unstaged for the parent to retain or discard.
