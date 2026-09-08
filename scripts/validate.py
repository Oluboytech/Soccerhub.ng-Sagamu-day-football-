#!/usr/bin/env python3
"""
Validate the competition data set before it gets published.

Checks:
  1. Every record in teams.json / matches.json / players.json / groups.json
     validates against its JSON Schema.
  2. Cross-file referential integrity: every team_id, group_id, venue_id
     referenced anywhere actually exists in its source-of-truth file.
  3. Fixture sanity: unique match IDs, no duplicate pairings within a group,
     each team plays the expected number of group-stage matches.

Exits non-zero on any failure, so this can be wired into CI (a GitHub Action)
to block a bad commit from ever reaching data.soccerhub.ng.
"""
import json
import sys
from pathlib import Path
from collections import Counter

try:
    from jsonschema import validate as js_validate, ValidationError
except ImportError:
    print("jsonschema package required: pip install jsonschema --break-system-packages", file=sys.stderr)
    sys.exit(2)


def load(path):
    with open(path) as f:
        return json.load(f)


def main():
    if len(sys.argv) != 2:
        print("Usage: validate.py <repo-root>", file=sys.stderr)
        sys.exit(1)

    root = Path(sys.argv[1])
    data_dir = root / 'data' / 'v1' / 'sagamu-day-2026'
    schema_dir = root / 'schema'

    errors = []

    def err(msg):
        errors.append(msg)

    # --- Load everything ---
    teams = load(data_dir / 'teams.json')['teams']
    groups = load(data_dir / 'groups.json')['groups']
    venues = load(data_dir / 'venues.json')['venues']
    matches = load(data_dir / 'matches.json')['matches']
    players = load(data_dir / 'players.json')['players']
    competition = load(data_dir / 'competition.json')

    team_schema = load(schema_dir / 'team.schema.json')
    group_schema = load(schema_dir / 'group.schema.json')
    match_schema = load(schema_dir / 'match.schema.json')
    player_schema = load(schema_dir / 'player.schema.json')
    competition_schema = load(schema_dir / 'competition.schema.json')
    venue_schema = load(schema_dir / 'venue.schema.json')

    # --- 1. Schema validation ---
    try:
        js_validate(competition, competition_schema)
    except ValidationError as e:
        err(f"competition.json failed schema: {e.message}")

    for t in teams:
        try:
            js_validate(t, team_schema)
        except ValidationError as e:
            err(f"team {t.get('id')} failed schema: {e.message}")

    for g in groups:
        try:
            js_validate(g, group_schema)
        except ValidationError as e:
            err(f"group {g.get('id')} failed schema: {e.message}")

    for m in matches:
        try:
            js_validate(m, match_schema)
        except ValidationError as e:
            err(f"match {m.get('id')} failed schema: {e.message}")

    for p in players:
        try:
            js_validate(p, player_schema)
        except ValidationError as e:
            err(f"player {p.get('id')} failed schema: {e.message}")

    for v in venues:
        try:
            js_validate(v, venue_schema)
        except ValidationError as e:
            err(f"venue {v.get('id')} failed schema: {e.message}")

    # --- 2. Referential integrity ---
    team_ids = {t['id'] for t in teams}
    group_ids = {g['id'] for g in groups}
    venue_ids = {v['id'] for v in venues}
    player_ids = {p['id'] for p in players}

    for t in teams:
        if t['group_id'] not in group_ids:
            err(f"team {t['id']} references unknown group_id {t['group_id']}")

    for g in groups:
        for tid in g['teams']:
            if tid not in team_ids:
                err(f"group {g['id']} references unknown team_id {tid}")

    for m in matches:
        if m['home_team_id'] not in team_ids:
            err(f"match {m['id']} has unknown home_team_id {m['home_team_id']}")
        if m['away_team_id'] not in team_ids:
            err(f"match {m['id']} has unknown away_team_id {m['away_team_id']}")
        if m['group_id'] and m['group_id'] not in group_ids:
            err(f"match {m['id']} references unknown group_id {m['group_id']}")
        if m.get('venue_id') and m['venue_id'] not in venue_ids:
            err(f"match {m['id']} references unknown venue_id {m['venue_id']}")

    for p in players:
        if p['team_id'] not in team_ids:
            err(f"player {p['id']} references unknown team_id {p['team_id']}")

    # --- 3. Fixture sanity ---
    match_ids = [m['id'] for m in matches]
    dupes = [mid for mid, c in Counter(match_ids).items() if c > 1]
    if dupes:
        err(f"duplicate match IDs: {dupes}")

    pairings = Counter()
    for m in matches:
        if m['group_id']:
            key = (m['group_id'], tuple(sorted([m['home_team_id'], m['away_team_id']])))
            pairings[key] += 1
    dup_pairings = {k: v for k, v in pairings.items() if v > 1}
    if dup_pairings:
        err(f"duplicate group-stage pairings: {dup_pairings}")

    expected_per_team = competition.get('teams_per_group', 4) - 1
    match_counts = Counter()
    for m in matches:
        if m['group_id']:
            match_counts[m['home_team_id']] += 1
            match_counts[m['away_team_id']] += 1
    wrong_counts = {tid: c for tid, c in match_counts.items() if c != expected_per_team}
    if wrong_counts:
        err(f"teams with unexpected group-stage match count (expected {expected_per_team}): {wrong_counts}")

    # --- Report ---
    if errors:
        print(f"VALIDATION FAILED — {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"Validation passed: {len(teams)} teams, {len(groups)} groups, "
              f"{len(venues)} venues, {len(matches)} matches, {len(players)} players.")


if __name__ == '__main__':
    main()
