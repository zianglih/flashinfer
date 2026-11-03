"""Render the compact performance section from verified fresh publication reports."""
import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEAD = "2b4732791a3ce48bc3ae6c030a283fab73854e0e"
CONTROL = "a620ce7790b32f7f0ae524a811417d2c6cee1152"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(raw, metrics, runtime):
    return f'''**End-to-end performance.** All **468 benchmark cases** were freshly measured at `{HEAD[:8]}`; no older candidate rows are reused. Positive means faster: `100 × (baseline / candidate − 1)`, using the geometric mean of two candidate pass medians. Original TRTLLM, non-swap and pre-PR W4A16 denominators are reused; these external comparisons span different B300 instances. Tokens 1–2 remain in raw output but are excluded from plots and speedup aggregates.

![EP same-dtype end-to-end speedups]({raw}/plots/swap-ab-speedup-table-ep.png)

![TP same-dtype end-to-end speedups]({raw}/plots/swap-ab-speedup-table-tp.png)

† Non-swap MX uses fused finalize where required; candidates remain unfused. W4A16 compares the old pre-PR layout with the new layout. Gray means unsupported; BF16 is table-only.

**Matched regression check against `{CONTROL[:8]}`:** geomean **{metrics['overall']}** across 396 displayed cases; swap-AB **{metrics['swap_ab']}**, W4A16 **{metrics['w4a16']}**, prefill (4096–16384) **{metrics['prefill']}**. {metrics['negative']} cases are slower; worst **{metrics['worst']}**. All negatives remain. Maximum repeat spreads are {metrics['control_spread']} control / {metrics['candidate_spread']} candidate; small differences do not establish uniform non-regression. [Full matched diagnostics]({raw}/retained/stats.md).

**Isolated repeat:** {metrics['diagnostic_cells']} predeclared cases were rerun alone in A→C→C→A ({metrics['diagnostic_samples']} additional samples): geomean {metrics['diagnostic_speedup']}. V41F EP4 at 16,384 remains {metrics['diagnostic_v41_mxfp4']} MXFP4x8 / {metrics['diagnostic_v41_mxfp8']} MXFP8, with {metrics['diagnostic_v41_mxfp4_spread']} / {metrics['diagnostic_v41_mxfp8_spread']} control repeat spreads. These diagnostic values do not replace any full-matrix plot/table entries. [Selection, raw data and summary]({raw}/diagnostic-inputs.json).

- **Method:** same-GPU C→A→A→C per job, 10 warmups and 100 strict-CUPTI cold-L2 CUDA-graph samples per phase: **187,200 total / 93,600 candidate samples**. Rank-local EP/TP simulation; frozen recorded tactics, including ten W4A16 defaults; no retuning or event fallback. W4A4/per-token include initial quantization; W4A16 consumes BF16 directly. Candidate clock windows: {metrics['clock_exceptions']}/3,744 exceptional (median SM clock ≠2032 MHz or nonzero clock-event reason), {metrics['clock_missing']} missing; all are retained.
- **Runtime:** {runtime['gpus']} on C3 (`{runtime['devbox']}`); `{runtime['image']}`; driver {runtime['driver']}; NVCC {runtime['nvcc']}; PyTorch `{runtime['torch']}`; CuTe DSL {runtime['cute_dsl']} (embedded compiler CUDA {runtime['cute_compiler_cuda']}); CUPTI Python/runtime {runtime['cupti_python']}/{runtime['cupti_runtime']}. [Runtime and replay details]({raw}/runtime-notes.md).
- **Evidence:** [absolute latencies]({raw}/benchmark-comparisons.csv), [raw CUPTI data and original stdout]({raw}/bundle-manifest.json), [immutable historical baselines]({raw}/dependencies.json). K3 MXFP8 and V41F TP MX lack supported external comparisons and remain skipped.

Representative split-MoE command (use the archived role-specific frozen cache):

```bash
export FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1
export FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1
export FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0
export CUTE_DSL_CACHE_DIR=/path/to/persistent-cute-cache
python benchmarks/bench_moe_deepseek.py \\
  --functional-api --model v3 --ep 8 --tp 1 --quant-family nvfp4 \\
  --backends cutedsl --swap-ab --no-fused-finalize --include-activation-quant \\
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \\
  --cache /path/to/frozen-winners --warmup 10 --iters 100 --no-autotune --output-format both
```

Other presets: `v41-flash` EP/TP4; `kimi-k3` and `nemo3-ultra` EP/TP8. TP uses `--ep 1 --tp N`. MX uses `--quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8` without `--include-activation-quant`. Archived per-job commands and observation wrappers enforce frozen choices and CUPTI without event fallback.

**Benchmark table output:** the unchanged table printer uses all 468 fresh final-pass records plus original TRTLLM records; heatmaps use two-pass aggregates. Tables are included directly in the existing comments:

[V3 EP8 / V41F EP4](https://github.com/flashinfer-ai/flashinfer/pull/7290#issuecomment-6519314397) · [K3 EP8 / N3U EP8](https://github.com/flashinfer-ai/flashinfer/pull/7290#issuecomment-6519315021) · [V3 TP8 / V41F TP4](https://github.com/flashinfer-ai/flashinfer/pull/7290#issuecomment-6519315606) · [K3 TP8 / N3U TP8](https://github.com/flashinfer-ai/flashinfer/pull/7290#issuecomment-6519316131)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", action="store_true", help="Write a separate template with explicit unresolved statistics/asset placeholders.")
    args = parser.parse_args()
    runtime = read(HERE / "runtime-context.json")
    assert runtime["head"] == HEAD and runtime["control"] == CONTROL
    assert sha(HERE / "runtime-notes.md") == runtime["notes_sha256"]
    keys = ["overall", "swap_ab", "w4a16", "prefill", "negative", "worst", "control_spread", "candidate_spread", "clock_exceptions", "clock_missing", "diagnostic_cells", "diagnostic_samples", "diagnostic_speedup", "diagnostic_negative", "diagnostic_worst", "diagnostic_v41_mxfp4", "diagnostic_v41_mxfp8", "diagnostic_v41_mxfp4_spread", "diagnostic_v41_mxfp8_spread"]
    proofs = {"runtime_context_sha256": sha(HERE / "runtime-context.json")}
    if args.draft:
        metrics = {k: "{{" + k.upper() + "}}" for k in keys}
        raw = "{{RAW_BASE}}"
    else:
        summary = read(HERE / "report/summary.json")
        retained = read(HERE / "retained/manifest.json")
        numeric = read(HERE / "numeric-validation.json")
        assets = read(HERE / "assets-published.json")
        tables = read(HERE / "completed-tables/manifest.json")
        for value in (summary, retained, numeric, assets, tables):
            assert value["passed"] and value["head"] == HEAD
        assert retained["control"] == CONTROL and retained["cells"] == 396
        assert summary["fresh_candidate_cells"] == 468 and summary["reused_candidate_cells"] == 0
        assert summary["candidate_samples"] == numeric["candidate_samples"] == 93600
        assert summary["campaign_samples"] == numeric["samples"] == 187200
        assert summary["all_negative_rows_retained"]
        assert retained["source_sha256"] == numeric["cells_sha256"] == sha(HERE / "report/cells.csv")
        assert numeric["table_manifest_sha256"] == sha(HERE / "completed-tables/manifest.json")
        groups = retained["groups"]
        percent = lambda value: f"{value:+.2f}%"
        all_group = groups["all"]
        metrics = dict(overall=percent(all_group["speedup_percent"]),
            swap_ab=percent(groups["implementation/swap_ab"]["speedup_percent"]),
            w4a16=percent(groups["implementation/w4a16"]["speedup_percent"]),
            prefill=percent(groups["band/prefill"]["speedup_percent"]), negative=all_group["negative"],
            worst=percent(all_group["min_percent"]), control_spread=f"{all_group['max_control_spread']:.2f}%",
            candidate_spread=f"{all_group['max_candidate_spread']:.2f}%",
            clock_exceptions=summary["clock_exception_quartiles"], clock_missing=summary["missing_clock_quartiles"])
        diagnostic = read(HERE / "diagnostic-inputs.json")
        assert diagnostic["passed"] and diagnostic["head"] == HEAD and diagnostic["control"] == CONTROL
        assert diagnostic["main_cells_sha256"] == sha(HERE / "report/cells.csv")
        for name, digest in diagnostic["files"].items():
            assert sha(HERE.parents[2] / name) == digest, name
        summary_path = diagnostic["summary"]
        assert summary_path in diagnostic["files"]
        repeat = read(HERE.parents[2] / summary_path)
        assert repeat["passed"] and repeat["head"] == HEAD and repeat["control"] == CONTROL
        assert repeat["phases"] == ["candidate", "control", "control", "candidate"]
        metrics.update(diagnostic_cells=repeat["cells"], diagnostic_samples=f"{repeat['raw_samples']:,}",
            diagnostic_speedup=percent(repeat["speedup_percent"]), diagnostic_negative=repeat["negative_cells"],
            diagnostic_worst=percent(repeat["min_speedup_percent"]))
        for mode, suffix in (("CuteDSL MXFP4x8", "mxfp4"), ("CuteDSL MXFP8", "mxfp8")):
            matches = [r for r in repeat["rows"] if r["job"] == "ep-v41-flash-mxfp" and r["tokens"] == 16384 and r["backend"] == mode]
            assert len(matches) == 1
            metrics["diagnostic_v41_" + suffix] = percent(matches[0]["speedup_percent"])
            metrics["diagnostic_v41_" + suffix + "_spread"] = f"{matches[0]['repeat_spread_percent']['control']:.2f}%"
        proofs["diagnostic-inputs.json"] = sha(HERE / "diagnostic-inputs.json")
        raw = assets["raw_base"]
        assert re.fullmatch(r"https://raw\.githubusercontent\.com/zianglih/flashinfer/[0-9a-f]{40}/2b473279", raw)
        for name in ("report/summary.json", "retained/manifest.json", "numeric-validation.json", "assets-published.json", "completed-tables/manifest.json"):
            proofs[name] = sha(HERE / name)
    text = render(raw, metrics, runtime)
    assert text.count("![") == 2
    if not args.draft:
        assert "{{" not in text and "PLACEHOLDER" not in text
    name = "performance-section.draft.md" if args.draft else "performance-section.md"
    target = HERE / name
    target.write_text(text)
    proof = dict(passed=True, draft=args.draft, head=HEAD, control=CONTROL,
        output=name, output_sha256=sha(target), words=len(text.split()), bytes=len(text.encode()),
        inputs=proofs, metrics=metrics,
        boundary="Only the performance section is generated. Root patches a freshly fetched PR body, retaining tests, GLM5 and review text.")
    (HERE / ("performance-section.draft.json" if args.draft else "performance-section.json")).write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps({k: proof[k] for k in ("draft", "output", "words", "bytes")}))


if __name__ == "__main__":
    main()
