#!/usr/bin/env python3
"""Plot the measured gathered-FC1 external-baseline table without rerunning benchmarks.

Uses a red/white/green palette and the NVFP4 quantizer benchmark's TwoSlopeNorm:
ratio 1 is neutral, with a range spanning at least 0.5 to 2.0. Cell labels
and colorbar ticks show the PR's signed percentage convention instead.

Usage:
    .venv-plot/bin/python plot_speedup_table.py
    python plot_speedup_table.py --csv assembled/summary-cells.csv --dpi 200

Dependencies: matplotlib, numpy. This script and its outputs are local
project artifacts, outside the FlashInfer source repository.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory
import numpy as np


ROOT = Path(__file__).resolve().parent
MODELS = (
    ("v3", "V3 EP8"),
    ("v41-flash", "V41F EP4"),
    ("kimi-k3", "K3 EP8"),
    ("nemo3-ultra", "N3U EP8"),
)
TOKENS = (4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384)
COLUMNS = (
    ("trtllm_w4a4", "W4A4"),
    ("trtllm_per_token", "PER-TOKEN"),
    ("trtllm_mxfp4x8", "MXFP4x8"),
    ("trtllm_mxfp8", "MXFP8"),
    ("legacy_w4a4", "W4A4"),
    ("legacy_per_token", "PER-TOKEN"),
    ("legacy_mxfp4x8", "MXFP4x8†"),
    ("legacy_mxfp8", "MXFP8†"),
    ("w4a16", "W4A16"),
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cells(path):
    with path.open(newline="") as stream:
        records = list(csv.DictReader(stream))
    cells = {}
    for record in records:
        token = int(record["tokens"])
        if token in (1, 2):
            continue
        key = (record["model"], token, record["column"])
        if key in cells:
            raise ValueError(f"Duplicate cell: {key}")
        if record["status"] == "measured":
            baseline, current = float(record["baseline_ms"]), float(record["current_ms"])
            if not all(math.isfinite(value) and value > 0 for value in (baseline, current)):
                raise ValueError(f"Invalid latency: {key}")
            ratio = baseline / current
            percent = 100 * (ratio - 1)
            if not math.isclose(percent, float(record["speed_percent"]), abs_tol=1e-10):
                raise ValueError(f"Speedup does not match latencies: {key}")
        elif record["status"] == "unsupported":
            ratio, percent = None, None
        else:
            raise ValueError(f"Unfinished cell: {key}, {record['status']}")
        cells[key] = dict(record, tokens=token, ratio=ratio, percent=percent)
    expected = {
        (model, token, column)
        for model, _ in MODELS
        for token in TOKENS
        for column, _ in COLUMNS
    }
    if set(cells) != expected:
        raise ValueError("Input must contain exactly the published 44 × 9 table")
    provenance_path = path.parent / "provenance.json"
    if provenance_path.exists():
        provenance = json.loads(provenance_path.read_text())
        if not provenance["complete"]:
            raise ValueError("Benchmark provenance is incomplete")
        if provenance["outputs"][path.name] != sha256(path):
            raise ValueError("CSV hash does not match benchmark provenance")
    return cells


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=ROOT / "assembled/summary-cells.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "plots")
    parser.add_argument("--commit-label", required=True)
    parser.add_argument("--topology", choices=("ep", "tp"), required=True)
    parser.add_argument("--dpi", type=int, default=200)
    args = parser.parse_args()
    global MODELS
    MODELS = tuple((model, label.replace("EP", args.topology.upper())) for model, label in MODELS)
    cells = load_cells(args.csv)
    ordered = [
        cells[model, token, column]
        for model, _ in MODELS
        for token in TOKENS
        for column, _ in COLUMNS
    ]
    matrix = np.array([
        np.nan if cell["ratio"] is None else cell["ratio"] for cell in ordered
    ]).reshape(44, 9)

    # Identical range/centering policy to bench_nvfp4_quantize_backend_comparison.py.
    vmin = min(0.5, float(np.nanmin(matrix)))
    vmax = max(2.0, float(np.nanmax(matrix)))
    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=1.0, vmax=vmax)
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "red_white_green", ["#b2182b", "#ffffff", "#1a9850"], N=257
    )
    cmap.set_bad("#e9edf2")
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "svg.fonttype": "none",
        "axes.unicode_minus": True,
    })
    fig = plt.figure(figsize=(15, 19), facecolor="white")
    ax = fig.add_axes((0.205, 0.125, 0.75, 0.775))
    im = ax.imshow(np.ma.masked_invalid(matrix), cmap=cmap, norm=norm,
                   aspect="auto", interpolation="nearest")
    ax.set_xticks(range(9), [label for _, label in COLUMNS])
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", length=0, pad=10, labelsize=10)
    ax.set_yticks(range(44), [f"{token:,}" for _ in MODELS for token in TOKENS])
    ax.tick_params(axis="y", length=0, pad=12, labelsize=10)
    ax.set_xticks(np.arange(-0.5, 9, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 44, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.65)
    ax.tick_params(which="minor", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    header_transform = blended_transform_factory(ax.transData, ax.transAxes)
    for start, width, label in ((0, 4, "TRTLLM"), (4, 4, "Non-swap"), (8, 1, "Before PR")):
        ax.add_patch(Rectangle((start - 0.5, 1.035), width, 0.025,
                               transform=header_transform, facecolor="#eef2f6",
                               edgecolor="white", clip_on=False))
        ax.text(start + (width - 1) / 2, 1.0475, label, transform=header_transform,
                ha="center", va="center", fontsize=12, fontweight="bold", color="#253447")
    ax.text(-0.19, 1.012, "MODEL", transform=ax.transAxes,
            ha="center", va="bottom", fontsize=10, color="#526174")
    ax.text(-0.027, 1.012, "TOKENS", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=10, color="#526174")
    model_transform = blended_transform_factory(ax.transAxes, ax.transData)
    for group, (_, label) in enumerate(MODELS):
        first = group * len(TOKENS)
        ax.add_patch(Rectangle((-0.255, first - 0.5), 0.135, len(TOKENS),
                               transform=model_transform, clip_on=False,
                               facecolor="#f0f3f7", edgecolor="white", linewidth=2))
        ax.text(-0.1875, first + 5, label, transform=model_transform,
                ha="center", va="center", fontsize=12, fontweight="bold", color="#253447")
        # Separate prefill rows without adding an axis or changing row spacing.
        ax.axhline(first + 7.5, color="#69778a", linewidth=0.8, linestyle=(0, (3, 3)))
        if group:
            ax.axhline(first - 0.5, color="#253447", linewidth=1.6)
    for boundary in (3.5, 7.5):
        ax.axvline(boundary, color="#253447", linewidth=1.4)

    for row in range(44):
        for col in range(9):
            value = matrix[row, col]
            if np.isnan(value):
                label, color = "N/A", "#768396"
            else:
                label = f"{100 * (value - 1):+.2f}%" + ("*" if float(ordered[row*9+col].get("candidate_spread_percent") or 0) > 1 else "")
                rgb = cmap(norm(value))[:3]
                linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in rgb]
                luminance = sum(weight * channel for weight, channel in zip((0.2126, 0.7152, 0.0722), linear))
                color = "white" if luminance < 0.179 else "#17212d"
            ax.text(col, row, label, ha="center", va="center", fontsize=10, color=color)

    fig.text(0.04, 0.974, f"CuTe DSL MoE · gathered FC1 · {args.topology.upper()} speedup", fontsize=21,
             fontweight="bold", color="#18283c", va="top")
    fig.text(0.04, 0.951, f"B300 / CUPTI · {args.commit_label} · same-dtype comparisons",
             fontsize=11, color="#526174", va="top")
    cax = fig.add_axes((0.34, 0.080, 0.50, 0.012))
    colorbar = fig.colorbar(im, cax=cax, orientation="horizontal")
    ticks = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    colorbar.set_ticks(ticks, labels=[f"{100 * (tick - 1):+.0f}%" if tick != 1 else "0%" for tick in ticks])
    colorbar.ax.tick_params(labelsize=10, length=3)
    colorbar.outline.set_visible(False)
    fig.text(0.34, 0.104, "Red: swap-AB slower     White: equal     Green: swap-AB faster",
             fontsize=10, color="#526174")
    fig.text(0.04, 0.049, "Speedup = 100 × (baseline latency / swap-AB latency − 1). All swap-AB paths use unfused finalize.",
             fontsize=10, color="#37465a")
    fig.text(0.04, 0.033, "† Non-swap MX uses fused finalize. W4A16: pre-PR old layout → swap-AB layout. Gray: unsupported. Tokens 1–2 omitted.",
             fontsize=10, color="#37465a")

    fig.text(0.04, 0.017, "39 fresh W4 cells / 429 reused; historical B300 baselines reused. * Candidate two-pass repeat spread >1%.",
             fontsize=10, color="#37465a")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for extension in ("png", "svg"):
        path = args.output_dir / f"swap-ab-speedup-table-{args.topology}.{extension}"
        fig.savefig(path, dpi=args.dpi, facecolor="white")
        outputs.append(path)
    plt.close(fig)
    manifest = {
        "source_csv": str(args.csv.resolve()), "source_sha256": sha256(args.csv),
        "script_sha256": sha256(Path(__file__)),
        "commit_label": args.commit_label,
        "topology": args.topology,
        "source_scope": "39 fresh W4-tail cells plus 429 source-equivalent reused cells. Historical baseline values/revisions retained; no fresh same-GPU causal comparison implied.",
        "rows": 44, "columns": 9,
        "measured_cells": int(np.isfinite(matrix).sum()),
        "unsupported_cells": int(np.isnan(matrix).sum()),
        "colormap": "red_white_green", "palette": ["#b2182b", "#ffffff", "#1a9850"],
        "ratio_limits": [vmin, 1.0, vmax],
        "normalization_reference": "benchmarks/bench_nvfp4_quantize_backend_comparison.py:create_heatmap",
        "models": dict(MODELS), "tokens": TOKENS, "column_keys": [key for key, _ in COLUMNS],
        "cells": [{key: cell[key] for key in ("model", "tokens", "column", "status", "ratio", "percent")} for cell in ordered],
        "outputs": {path.name: sha256(path) for path in outputs},
    }
    (args.output_dir / f"plot-manifest-{args.topology}.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"outputs": [str(path) for path in outputs], "rows": 44,
                      "measured_cells": manifest["measured_cells"], "unsupported_cells": manifest["unsupported_cells"]}))


if __name__ == "__main__":
    main()
