"""Root's independent overlay check; images inspected separately with view_image."""
from pathlib import Path
import csv
import hashlib
import json
import math

p = Path(__file__).resolve().parent
old = p.parent / 'publication-integer-store'
read = lambda q: list(csv.DictReader(q.open()))
key = lambda r: (r['model'], r['topology'], r['backend'], r['tokens'])
a = {key(r): r for r in read(old / 'report/cells.csv')}
b = {key(r): r for r in read(p / 'report/cells.csv')}
assert a.keys() == b.keys() and len(b) == 468
causal = {key(r): r for r in read(p.parent / 'evidence/w4-paired-situ-screen/1793379864881706000/report/cells.csv')}
fresh = set(causal)
assert len(fresh) == 26 and fresh <= a.keys()
for k in fresh:
    for field in ('a1_us', 'a2_us', 'candidate_us', 'candidate_spread_percent'):
        assert float(b[k][field]) == float(causal[k][field]), (k, field)
for k in a:
    if k not in fresh:
        assert b[k] == a[k], k
    for field in ('before1_us', 'before2_us', 'baseline_us', 'control_spread_percent', 'baseline_measured_head', 'baseline_production_equivalent_head', 'baseline_evidence'):
        assert a[k][field] == b[k][field], (k, field)
    assert math.isclose(float(b[k]['speedup_percent']), 100 * (float(b[k]['baseline_us']) / float(b[k]['candidate_us']) - 1), rel_tol=1e-10, abs_tol=1e-10)
for topology in ('ep', 'tp'):
    x = read(old / f'external/{topology}/summary-cells.csv')
    y = read(p / f'external/{topology}/summary-cells.csv')
    assert len(x) == len(y)
    for before, after in zip(x, y):
        assert all(before[field] == after[field] for field in ('model', 'tokens', 'column', 'baseline', 'status', 'baseline_ms', 'reason', 'baseline_evidence'))
        if not (before['model'] == 'kimi-k3' and before['column'] == 'w4a16'):
            assert before == after
sha = lambda q: hashlib.sha256(q.read_bytes()).hexdigest()
plots = {str(q.relative_to(p)): sha(q) for q in sorted((p / 'plots').glob('*.png'))}
assert len(plots) == 5
receipt = dict(passed=True, report_sha256=sha(p / 'report/cells.csv'), plots=plots, review='All five rendered PNGs inspected by root. No clipped text or overlapping labels; compact model names, red-green signs, unsupported N/A and 1/2 exclusion preserved.', numeric_checks=dict(rows=468, fresh=26, reused_exact=442, historical_baselines_unchanged=True, all_ratios_recalculated=True))
(p / 'visual-review.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
