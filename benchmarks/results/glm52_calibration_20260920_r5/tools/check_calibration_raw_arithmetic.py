"""Parent-only direct raw-sample arithmetic audit; does not import the summarizer."""
import argparse
import collections
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics

p = argparse.ArgumentParser()
p.add_argument('--summary', required=True, type=Path)
p.add_argument('--output', required=True, type=Path)
a = p.parse_args()
s = json.loads(a.summary.read_text())
root = (a.summary.parent / s['evidence_root_relative']).resolve()
manifest = json.loads(a.summary.with_name('raw_manifest.json').read_text())['files']
logs, hashes, rows = {}, {}, []
samples = repeat_medians = pooled_medians = complete = 0
native = collections.Counter()
phase_groups = collections.Counter()
for g in s['performance_groups']:
    assert g['timer'] == 'cupti'
    pool = {'split': [], 'mega': []}
    repeats = [r['repeat'] for r in g['repeats']]
    assert len(set(repeats)) == len(repeats) and set(repeats) <= {1, 2}
    assert g['complete_repeats'] == (set(repeats) == {1, 2})
    changes = []
    for r in g['repeats']:
        e = r['evidence']
        path = e['log']
        if path not in logs:
            raw = (root / path).read_bytes()
            h = hashlib.sha256(raw).hexdigest()
            assert len(raw) == manifest[path]['size']
            assert h == manifest[path]['sha256'] == e['log_sha256']
            hashes[path] = h
            records = []
            for line in raw.decode().splitlines():
                if line.startswith('DISTRIBUTED_TIMING_SAMPLES_JSON,'):
                    records.append(json.loads(line.split(',', 1)[1]))
            logs[path] = records
        for arm, variant in (('split', 'w4a16'), ('mega', 'w4a16_megamoe')):
            matches = [v for v in logs[path] if v['global_tokens'] == g['tokens']
                       and v['profile_label'] == 'ep::' + variant]
            assert len(matches) == 1
            v = matches[0]
            assert v['world_size'] == g['ep'] and v['ep_communication'] == g['communication']
            assert v['megamoe_capacity_override'] == g['capacity']
            assert v['cuda_graph'] == g['graph']
            assert v['precomputed_routing'] == g['precomputed_routing']
            assert v['timer'] == 'cupti' and v['cold_l2_cache']
            assert v['sample_aggregation'] == 'per_iteration_rank_max'
            values = v['samples_ms']
            assert len(values) == v['sample_count'] == 100
            assert all(math.isfinite(x) and x > 0 for x in values)
            assert statistics.median(values) * 1000 == r[arm + '_us']
            repeat_medians += 1
            samples += len(values)
            pool[arm].extend(values)
        change = 100 * (r['mega_us'] / r['split_us'] - 1)
        assert change == r['mega_latency_change_percent']
        changes.append(change)
        native[r['cross_pair']['status']] += 1
    derived = None
    if g['complete_repeats']:
        assert all(len(v) == 200 for v in pool.values())
        split, mega = [statistics.median(pool[k]) * 1000 for k in ('split', 'mega')]
        derived = dict(split_us=split, mega_us=mega, sample_count_per_arm=200,
                       speedup_split_over_mega=split / mega,
                       mega_latency_change_percent=100 * (mega / split - 1))
        assert derived == g['pooled']
        complete += 1
        pooled_medians += 2
    else:
        assert g['pooled'] is None
    phase_groups[g['phase']] += 1
    rows.append({**{k: g[k] for k in ('phase', 'ep', 'communication', 'capacity', 'tokens',
                                     'knobs', 'graph', 'precomputed_routing')},
                 'pooled': derived, 'repeat_signed_changes': changes,
                 'repeat_sign_reversal': len(changes) == 2 and changes[0] * changes[1] < 0})

if s['status'] == 'FINAL':
    assert s['successful_jobs'] == 60 and len(rows) == complete == 110
    assert not s['failed_jobs'] and not s['missing_jobs']
    assert samples == 44000 and len(logs) == 52
    assert dict(phase_groups) == dict(core=84, auto=6, routing=12, prefill=8)

report = dict(checked_at=datetime.now(timezone.utc).isoformat(),
              status='parent_direct_raw_arithmetic_passed',
              summary_path=str(a.summary),
              summary_sha256=hashlib.sha256(a.summary.read_bytes()).hexdigest(),
              checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              raw_logs_rehashed=hashes, groups=len(rows), complete_groups=complete,
              raw_performance_samples=samples, repeat_medians=repeat_medians,
              pooled_medians=pooled_medians, native_comparison_counts=dict(native),
              phase_groups=dict(phase_groups), rows=rows,
              full_matrix_complete=s['status'] == 'FINAL', equivalence_claim=False,
              scope='Exact direct parsing of raw rank-MAX samples and repeat/pooled arithmetic. '
                    'Numerical/reference/lifecycle acceptance is independently reviewed.')
with a.output.open('x') as f:
    json.dump(report, f, indent=2)
    f.write('\n')
print(json.dumps({k: report[k] for k in ('status', 'groups', 'complete_groups',
                                      'raw_performance_samples', 'phase_groups')}))
