# Composed full-matrix preparation

Status: **prepared, not launched**. The complete source is sealed; all13,245
tracked/submodule file hashes match the approved composition. Exactly two files
differ from82254e20: the swap kernel and W4A16 conversion utility. The original
R1, R2 and static-SF snapshots and measurements remain unchanged.

- Source record: `source-candidate-composed.json`.
- Full matrix:31nativejobs,36supported model/topology/mode arms ×13tokens =468
  cells; two candidate processes/job,100samples/cell =93,600samples.
- Config: `perf-config.json`, SHA
  `21b3fd524ccaa78fac9b31b801e59c24491dfcf6a22450460e8173a6614a889e`.
- Exact runtime/cache/tactic/route contracts are inherited from the audited
  compact harness. Native stdout uses the public benchmark’s `--output-format
  both`; preserve those tables verbatim. Ten recorded W4 defaults are intentional
  and must retain the native-config/library join. No retuning/event fallback.
- Tokens1/2 remain in raw output; exclude them from retention and heatmaps.
  NVFP4 includes the initial quantizer; W4A16 directly consumes BF16.
- Full source inventories are verified before/after the campaign; bounded
  launch dependencies and source-specific zero-LOCAL runtime guards remain on
  every process. Keep all samples, negative cells and clock exceptions.

Launch requires root’s explicit allocation after GLM5 releases the GPUs, review
of the K3 EP MXFP4x8 16K diagnosis, and acceptance of the composed source. The
independent compact ratios must not be multiplied or relabeled as composed
performance.

Prepared remote command (not yet run):

```sh
cd /data/ziangli/flashinfer-moe-gather-pipeline
python3 harness/campaign.py --config runs/composed-full/perf-config.json --gpus 0 1 2 3 4 5 6 7
```

After completion, retain all62 process outputs and assemble fresh two-pass
geometric candidate medians. Reuse the unchanged historical baseline fields in
`harness/historical/external/{ep,tp}/summary-cells.csv`, including unsupported and
legacy-fused markers. Historical measurements retain their original measured
revision and GPU/timing provenance; they are not fresh822 controls. Native script
stdout remains separate from any explicitly labeled historical formatter replay.
The eventual new-fork PR must use the retained commit plus exact measured source
hashes, concise environment/validation limits, and the measured full heatmaps.
