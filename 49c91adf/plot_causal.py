"""Plot the 104-cell paired integer-store experiment, excluding tokens 1/2 visually."""
import csv
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import numpy as np

HERE = Path(__file__).resolve().parent
TOKENS = [4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384]
MODES = ['CuteDSL W4A4', 'CuteDSL PER-TOKEN', 'CuteDSL MXFP4x8', 'CuteDSL MXFP8']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    source = HERE / 'integer-store-causal/cells.csv'
    rows = list(csv.DictReader(source.open()))
    assert len(rows) == 104
    lookup = {(r['topology'], r['backend'], int(r['tokens'])): r for r in rows}
    ordered = [lookup[topology, mode, token] for topology in ('ep', 'tp') for mode in MODES for token in TOKENS]
    matrix = np.array([float(r['speedup_percent']) for r in ordered]).reshape(8, 11)
    cmap = LinearSegmentedColormap.from_list('red_white_green', ['#b2182b', '#ffffff', '#1a9850'])
    norm = TwoSlopeNorm(vmin=-5, vcenter=0, vmax=5)
    fig, ax = plt.subplots(figsize=(15.8, 5.6), facecolor='white')
    fig.subplots_adjust(left=.20, right=.98, top=.79, bottom=.25)
    im = ax.imshow(matrix, cmap=cmap, norm=norm, aspect='auto', interpolation='nearest')
    labels = [f'N3U {topology.upper()}8 · {mode.removeprefix("CuteDSL ")}' for topology in ('ep', 'tp') for mode in MODES]
    ax.set_xticks(range(11), [f'{token:,}' for token in TOKENS], fontsize=10)
    ax.set_yticks(range(8), labels, fontsize=10)
    ax.xaxis.tick_top()
    ax.tick_params(length=0, pad=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.axhline(3.5, color='#253447', linewidth=1.4)
    ax.axvline(7.5, color='#69778a', linewidth=.8, linestyle=(0, (3, 3)))
    for i in range(8):
        for j in range(11):
            row = ordered[i * 11 + j]
            value = matrix[i, j]
            noisy = max(float(row['control_spread_percent']), float(row['candidate_spread_percent'])) > 1
            ax.text(j, i, f'{value:+.2f}%' + ('*' if noisy else ''), ha='center', va='center', fontsize=9.8,
                    color='white' if abs(value) > 3.8 else '#17212d')
    fig.text(.025, .95, 'N3U FC1 integer stores · paired comparison vs retained bf072d26', fontsize=18, weight='bold', color='#18283c')
    fig.text(.025, .90, '49c91adf · B300 / strict CUPTI · fixed choices/routes · C/A/A/C · 100 samples per phase', fontsize=11, color='#526174')
    cax = fig.add_axes((.36, .14, .5, .022))
    colorbar = fig.colorbar(im, cax=cax, orientation='horizontal', extend='both')
    colorbar.set_ticks([-5, -2.5, 0, 2.5, 5], labels=['−5%', '−2.5%', '0%', '+2.5%', '+5%'])
    colorbar.outline.set_visible(False)
    fig.text(.025, .065, 'Positive: candidate faster. Colors saturate at ±5%; labels are unclipped. * Either arm repeat spread >1%.', fontsize=10, color='#37465a')
    fig.text(.025, .025, '100 × (√(C1 median × C2 median) / √(A1 median × A2 median) − 1). Tokens 1–2 remain in raw data and are excluded here.', fontsize=9.5, color='#37465a')
    outputs = {}
    for extension in ('png', 'svg'):
        path = HERE / 'plots' / f'integer-store-vs-retained.{extension}'
        fig.savefig(path, dpi=180, facecolor='white')
        outputs[path.name] = sha(path)
    plt.close(fig)
    manifest = dict(source_sha256=sha(source), script_sha256=sha(__file__), rows=8, columns=11, displayed_cells=88, raw_cells=104,
                    baseline='bf072d26b163e71458e7e4dfb12e615b19bd2c9a', candidate='49c91adf47d30fc2049c76cbaf34d0ccf3291434',
                    tokens=TOKENS, negative_cells=sum(float(r['speedup_percent']) < 0 for r in ordered),
                    cells=ordered, outputs=outputs, colormap='red_white_green', limits=[-5, 0, 5])
    (HERE/'plots/integer-store-causal-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
