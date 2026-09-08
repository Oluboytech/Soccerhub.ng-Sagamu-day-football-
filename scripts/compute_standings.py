#!/usr/bin/env python3
"""
Compute group standings from match results.

Reads:  data/v1/<competition>/matches.json, groups.json, teams.json
Writes: data/v1/<competition>/standings.json

Tie-break order (standard football convention, adjust in TIEBREAK_KEYS if the
organizer's rules differ):
    1. points
    2. goal difference
    3. goals for
    4. head-to-head points among tied teams
    5. team id (stable fallback so ordering never flaps arbitrarily)

Safe to run at any point in the season: unplayed matches (score.home is null)
are simply skipped, so this produces the same all-zero table pre-tournament
and updates automatically as results are added.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

def load(path):
    with open(path) as f:
        return json.load(f)

def save(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')

def compute_standings(competition_dir: Path):
    matches_data = load(competition_dir / 'matches.json')
    groups_data = load(competition_dir / 'groups.json')

    competition_id = groups_data['competition_id']
    groups = groups_data['groups']
    matches = matches_data['matches']

    # per-group, per-team running totals
    stats = {
        g['id']: {
            team_id: {
                'team_id': team_id,
                'played': 0, 'won': 0, 'drawn': 0, 'lost': 0,
                'goals_for': 0, 'goals_against': 0,
                'goal_difference': 0, 'points': 0,
            }
            for team_id in g['teams']
        }
        for g in groups
    }

    # head-to-head points, keyed by (group_id, frozenset({team_a, team_b}))
    h2h_points = defaultdict(lambda: defaultdict(int))

    for m in matches:
        score = m.get('score') or {}
        home_goals = score.get('home')
        away_goals = score.get('away')

        # Only count matches with a completed regulation/normal-time score.
        # Penalty shootout results (knockouts) do not affect group tables.
        if home_goals is None or away_goals is None:
            continue

        group_id = m.get('group_id')
        if group_id not in stats:
            continue  # knockout / non-group match

        home_id, away_id = m['home_team_id'], m['away_team_id']
        home = stats[group_id].get(home_id)
        away = stats[group_id].get(away_id)
        if home is None or away is None:
            continue

        home['played'] += 1
        away['played'] += 1
        home['goals_for'] += home_goals
        home['goals_against'] += away_goals
        away['goals_for'] += away_goals
        away['goals_against'] += home_goals

        if home_goals > away_goals:
            home['won'] += 1
            away['lost'] += 1
            home['points'] += 3
            h2h_points[group_id][home_id] += 3
        elif away_goals > home_goals:
            away['won'] += 1
            home['lost'] += 1
            away['points'] += 3
            h2h_points[group_id][away_id] += 3
        else:
            home['drawn'] += 1
            away['drawn'] += 1
            home['points'] += 1
            away['points'] += 1
            h2h_points[group_id][home_id] += 1
            h2h_points[group_id][away_id] += 1

    for group_id, teams in stats.items():
        for t in teams.values():
            t['goal_difference'] = t['goals_for'] - t['goals_against']

    output_groups = []
    for g in groups:
        group_id = g['id']
        team_rows = list(stats[group_id].values())
        team_rows.sort(key=lambda t: (
            -t['points'],
            -t['goal_difference'],
            -t['goals_for'],
            -h2h_points[group_id].get(t['team_id'], 0),
            t['team_id'],
        ))
        for i, row in enumerate(team_rows, start=1):
            row['position'] = i
        # reorder keys to match existing schema: position first
        ordered_rows = [
            {
                'position': r['position'],
                'team_id': r['team_id'],
                'played': r['played'],
                'won': r['won'],
                'drawn': r['drawn'],
                'lost': r['lost'],
                'goals_for': r['goals_for'],
                'goals_against': r['goals_against'],
                'goal_difference': r['goal_difference'],
                'points': r['points'],
            }
            for r in team_rows
        ]
        output_groups.append({'group_id': group_id, 'standings': ordered_rows})

    return {
        'competition_id': competition_id,
        'groups': output_groups,
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: compute_standings.py <path-to-competition-data-dir>", file=sys.stderr)
        sys.exit(1)

    competition_dir = Path(sys.argv[1])
    result = compute_standings(competition_dir)
    out_path = competition_dir / 'standings.json'
    save(out_path, result)
    print(f"Wrote {out_path}")


if __name__ == '__main__':
    main()
