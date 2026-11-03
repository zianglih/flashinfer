"""Local matched-CAAC diagnostic; never substitute historical external baselines."""
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
HEAD = "2b4732791a3ce48bc3ae6c030a283fab73854e0e"
CONTROL = "a620ce7790b32f7f0ae524a811417d2c6cee1152"
MODELS = [("v3", "V3", 8), ("v41-flash", "V41F", 4),
          ("kimi-k3", "K3", 8), ("nemo3-ultra", "N3U", 8)]
MODES = ["W4A4", "PER-TOKEN", "W4A16", "MXFP4x8", "MXFP8"]
TOKENS = [4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def group(values):
    return dict(cells=len(values), speedup_percent=100 * math.expm1(statistics.mean(
        math.log1p(r["speedup_percent"] / 100) for r in values)),
        negative=sum(r["speedup_percent"] < 0 for r in values),
        min_percent=min(r["speedup_percent"] for r in values),
        max_percent=max(r["speedup_percent"] for r in values),
        max_control_spread=max(r["control_spread_percent"] for r in values),
        max_candidate_spread=max(r["candidate_spread_percent"] for r in values))


def main():
    path = HERE / "report/cells.csv"
    rows = list(csv.DictReader(path.open()))
    rows = [dict(r, tokens=int(r["tokens"]), **{
        k: float(r[k]) for k in ("speedup_percent", "control_spread_percent", "candidate_spread_percent")
    }) for r in rows if int(r["tokens"]) >= 4]
    assert len(rows) == 396
    lookup = {(r["topology"], r["model"], r["tokens"], r["backend"].removeprefix("CuteDSL ")): r for r in rows}
    assert len(lookup) == len(rows)
    out = HERE / "retained"
    out.mkdir(exist_ok=True)
    cmap = colors.LinearSegmentedColormap.from_list("red_white_green", ["#b2182b", "#ffffff", "#1a9850"])
    cmap.set_bad("#eceff2")
    norm = colors.TwoSlopeNorm(vmin=-5, vcenter=0, vmax=5)
    plot_records = []
    for topology in ("ep", "tp"):
        keys = [(model, label, parallel, token) for model, label, parallel in MODELS for token in TOKENS]
        matrix = np.full((len(keys), len(MODES)), np.nan)
        for i, (model, _, _, token) in enumerate(keys):
            for j, mode in enumerate(MODES):
                if (topology, model, token, mode) in lookup:
                    matrix[i, j] = lookup[topology, model, token, mode]["speedup_percent"]
        fig, ax = plt.subplots(figsize=(10, 18), facecolor="white")
        fig.subplots_adjust(left=.25, right=.97, top=.94, bottom=.08)
        im = ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto", interpolation="nearest")
        ax.set_xticks(range(len(MODES)), MODES, fontsize=10)
        ax.xaxis.tick_top()
        ax.set_yticks(range(len(keys)), [f"{label} {topology.upper()}{parallel} · {token:,}" for _, label, parallel, token in keys], fontsize=9)
        ax.tick_params(length=0, pad=8)
        for spine in ax.spines.values():
            spine.set_visible(False)
        for i, (model, _, _, token) in enumerate(keys):
            if i and token == TOKENS[0]:
                ax.axhline(i - .5, color="#526174", linewidth=1)
            for j, mode in enumerate(MODES):
                row = lookup.get((topology, model, token, mode))
                if row is None:
                    label, ink = "N/A", "#64748b"
                else:
                    value = row["speedup_percent"]
                    label = f"{value:+.2f}%" + (" *" if max(row["control_spread_percent"], row["candidate_spread_percent"]) > 1 else "")
                    ink = "white" if abs(value) >= 3.5 else "#172a3a"
                ax.text(j, i, label, ha="center", va="center", color=ink, fontsize=9)
        fig.text(.03, .979, f"{HEAD[:8]} vs retained {CONTROL[:8]} · {topology.upper()}", fontsize=16, weight="bold")
        fig.text(.03, .959, "Matched C-A-A-C · CUPTI · fixed recorded tactics · all tokens ≥4; missing external-comparison configs not run", fontsize=9)
        bar_ax = fig.add_axes([.25, .048, .72, .008])
        bar = fig.colorbar(im, cax=bar_ax, orientation="horizontal", extend="both")
        bar.set_ticks([-5, -2.5, 0, 2.5, 5], labels=["−5%", "−2.5%", "0%", "+2.5%", "+5%"])
        bar.outline.set_visible(False)
        fig.text(.03, .023, "Positive = candidate faster. Colors saturate at ±5%; labels retain all values. * Either phase repeat spread >1%.", fontsize=9)
        outputs = {}
        for extension in ("png", "svg"):
            target = out / f"retained-{topology}.{extension}"
            fig.savefig(target, dpi=180, facecolor="white")
            outputs[target.name] = sha(target)
        plt.close(fig)
        plot_records.append(dict(topology=topology, cells=[r for r in rows if r["topology"] == topology], outputs=outputs))
    groups = {"all": group(rows)}
    selectors = {
        "topology": lambda r: r["topology"],
        "mode": lambda r: r["backend"],
        "implementation": lambda r: "w4a16" if r["backend"] == "CuteDSL W4A16" else "swap_ab",
        "band": lambda r: "decode" if r["tokens"] <= 64 else "middle" if r["tokens"] <= 512 else "prefill",
        "model_topology_mode": lambda r: f"{r['model']}/{r['topology']}/{r['backend']}",
    }
    for name, selector in selectors.items():
        for value in sorted({selector(r) for r in rows}):
            groups[f"{name}/{value}"] = group([r for r in rows if selector(r) == value])
    result = dict(passed=True, head=HEAD, control=CONTROL, cells=396, source_sha256=sha(path), groups=groups,
        negative_cells=sorted([r for r in rows if r["speedup_percent"] < 0], key=lambda r: r["speedup_percent"]),
        plots=plot_records, boundary="Matched CAAC diagnostics, no automatic retention threshold. All negatives and repeat/clock anomalies remain. Tokens 1/2 are raw-only. Source rebase/upstream changes accompany the candidate; this is not a single-optimization attribution.")
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["| Group | Cells | Speedup | Negative cells | Max control spread | Max candidate spread |", "|---|---:|---:|---:|---:|---:|"]
    for name, value in groups.items():
        lines.append(f"| {name} | {value['cells']} | {value['speedup_percent']:+.3f}% | {value['negative']} | {value['max_control_spread']:.3f}% | {value['max_candidate_spread']:.3f}% |")
    (out / "stats.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(groups["all"]))


if __name__ == "__main__":
    main()
