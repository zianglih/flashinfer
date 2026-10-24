#!/usr/bin/env python3
"""Audit native AUTO scheduler-mode coverage and per-rank selected modes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--rankings', type=Path, required=True)
    parser.add_argument('--mode-counts', required=True, help='Expected mode:count entries separated by commas')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    expected = dict((mode, int(count)) for mode, count in (entry.split(':') for entry in args.mode_counts.split(',')))
    metadata = json.loads((args.capture / 'run.json').read_text())
    assert metadata['complete'] and metadata['source_unchanged_during_capture']
    rankings = json.loads(args.rankings.read_text())
    rows = json.loads((args.capture / 'raw-records.json').read_text())
    receipts = []
    assert sorted(group['global_tokens'] for group in rankings['groups']) == sorted(metadata['tokens'])
    for group in rankings['groups']:
        counts = dict(Counter(item['knobs']['load_balance_mode'] for item in group['rankings']))
        assert counts == expected, (counts, expected)
        assert group['candidate_count'] == sum(expected.values())
        token = group['global_tokens']
        winners = [row['value'] for row in rows if row['kind'] == 'MEGAMOE_TACTIC_JSON' and row['value']['global_tokens'] == token]
        assert sorted(winner['rank'] for winner in winners) == list(range(8))
        assert all(winner['knobs'] == winners[0]['knobs'] for winner in winners)
        assert winners[0]['knobs'] == group['winner_knobs']
        if metadata['tactic_policy'] == 'mixed-only':
            assert all(item['knobs']['cluster_shape_mnk'] == [4, 1, 1]
                       and item['knobs']['fallback_cluster_shape_mnk'] == [2, 1, 1]
                       for item in group['rankings'])
        receipts.append({'global_tokens': token, 'catalog_scheduler_modes': counts,
                         'winner_scheduler_mode': winners[0]['knobs']['load_balance_mode'],
                         'winner_knobs': winners[0]['knobs'], 'ranks': list(range(8))})
    report = {'capture': str(args.capture), 'commit': metadata['source_commit'], 'tactic_policy': metadata['tactic_policy'],
              'points': receipts, 'ranking_file_sha256': hashlib.sha256(args.rankings.read_bytes()).hexdigest(),
              'scope': 'Coverage and selected-mode evidence from native AUTO; internal ranking scores are not cold-L2 CUPTI timings.'}
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
