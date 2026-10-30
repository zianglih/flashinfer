"""Plot the 39-cell paired W4 cutoff experiment, excluding tokens 1/2 visually."""
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
MODES = ['CuteDSL W4A16']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    source = HERE / 'tail-cutoff-causal/cells.csv'
    rows = list(csv.DictReader(source.open()))
    assert len(rows) == 39
    models = [('v41-flash', 'V41F TP4'), ('kimi-k3', 'K3 TP8'), ('nemo3-ultra', 'N3U TP8')]
    lookup = {(r['model'], r['backend'], int(r['tokens'])): r for r in rows}
    ordered = [lookup[model, mode, token] for model, _ in models for mode in MODES for token in TOKENS]
    matrix = np.array([float(r['speedup_percent']) for r in ordered]).reshape(3, 11)
    cmap = LinearSegmentedColormap.from_list('red_white_green', ['#b2182b', '#ffffff', '#1a9850'])
    norm = TwoSlopeNorm(vmin=-5, vcenter=0, vmax=5)
    fig, ax = plt.subplots(figsize=(15.8, 4.7), facecolor='white')
    fig.subplots_adjust(left=.20, right=.98, top=.70, bottom=.36)
    im = ax.imshow(matrix, cmap=cmap, norm=norm, aspect='auto', interpolation='nearest')
    labels = [label + " · W4A16" for _, label in models]
    ax.set_xticks(range(11), [f'{token:,}' for token in TOKENS], fontsize=10)
    ax.set_yticks(range(3), labels, fontsize=10)
    ax.xaxis.tick_top()
    ax.tick_params(length=0, pad=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.axhline(.5, color='#253447', linewidth=1.4)
    ax.axhline(1.5, color='#253447', linewidth=1.4)
    ax.axvline(7.5, color='#69778a', linewidth=.8, linestyle=(0, (3, 3)))
    for i in range(3):
        for j in range(11):
            row = ordered[i * 11 + j]
            value = matrix[i, j]
            noisy = max(float(row['control_spread_percent']), float(row['candidate_spread_percent'])) > 1
            ax.text(j, i, f'{value:+.2f}%' + ('*' if noisy else ''), ha='center', va='center', fontsize=9.8,
                    color='white' if abs(value) > 3.8 else '#17212d')
    fig.text(.025, .97, 'W4A16 transform cutoff · fresh paired comparison vs 2b8eb9d8', fontsize=18, weight='bold', color='#18283c', va='top')
    fig.text(.025, .90, 'c1ac8ce7 · B300 / strict CUPTI · fixed choices/routes · C/A/A/C · 100 samples per phase', fontsize=11, color='#526174', va='top')
    cax = fig.add_axes((.36, .21, .5, .030))
    colorbar = fig.colorbar(im, cax=cax, orientation='horizontal', extend='both')
    colorbar.set_ticks([-5, -2.5, 0, 2.5, 5], labels=['−5%', '−2.5%', '0%', '+2.5%', '+5%'])
    colorbar.outline.set_visible(False)
    fig.text(.025, .065, 'Positive: candidate faster. Colors saturate at ±5%; labels are unclipped. * Either arm repeat spread >1%.', fontsize=10, color='#37465a')
    fig.text(.025, .025, '100 × (√(C1 median × C2 median) / √(A1 median × A2 median) − 1). Tokens 1–2 remain in raw data and are excluded here.', fontsize=9.5, color='#37465a')
    outputs = {}
    for extension in ('png', 'svg'):
        path = HERE / 'plots' / f'tail-cutoff-vs-retained.{extension}'
        fig.savefig(path, dpi=180, facecolor='white')
        outputs[path.name] = sha(path)
    plt.close(fig)
    manifest = dict(source_sha256=sha(source), script_sha256=sha(__file__), rows=3, columns=11, displayed_cells=33, raw_cells=39,
                    baseline='2b8eb9d8f72ceda3952fbb05054fee97173fc9c7', candidate='c1ac8ce7341039db65195b99445fcdeb193cf226',
                    tokens=TOKENS, negative_cells=sum(float(r['speedup_percent']) < 0 for r in ordered),
                    cells=ordered, outputs=outputs, colormap='red_white_green', limits=[-5, 0, 5])
    (HERE/'plots/tail-cutoff-causal-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
