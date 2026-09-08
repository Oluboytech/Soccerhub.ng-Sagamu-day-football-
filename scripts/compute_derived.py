#!/usr/bin/env python3
"""
Compute derived/convenience data files that save every frontend from having
to re-derive the same logic client-side:

    matches-upcoming.json   -- scheduled matches, soonest first
    matches-results.json    -- finished matches, most recent first
    top-scorers.json        -- scorers.json re-sorted/ranked (competition leaderboard)
    manifest.json           -- index of every endpoint with byte size + sha256,
                               so clients/CDNs can cheaply detect changes

Run this AFTER compute_standings.py, since manifest.json hashes the freshly
written standings.json too.
"""
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone


def load(path):
    with open(path) as f:
        return json.load(f)


def save(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def compute_matches_upcoming(matches):
    upcoming = [m for m in matches if m.get('status') == 'scheduled']
    upcoming.sort(key=lambda m: (m['date'], m['kickoff_time']))
    return upcoming


def compute_matches_results(matches):
    finished = [m for m in matches if m.get('status') == 'finished']
    finished.sort(key=lambda m: (m['date'], m['kickoff_time']), reverse=True)
    return finished


def compute_top_scorers(scorers_data):
    scorers = list(scorers_data.get('scorers', []))
    scorers.sort(key=lambda s: (-s.get('goals', 0), s.get('player_id', '')))
    for i, s in enumerate(scorers, start=1):
        s['rank'] = i
    return scorers


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def build_manifest(competition_dir: Path, competition_id: str, data_version: str):
    file_order = [
        'competition.json', 'groups.json', 'teams.json', 'venues.json',
        'players.json', 'matches.json', 'matches-upcoming.json',
        'matches-results.json', 'standings.json', 'scorers.json',
        'top-scorers.json', 'assists.json', 'cards.json', 'match-events.json',
        'lineups.json', 'statistics.json', 'knockout.json', 'awards.json',
    ]
    entries = []
    for fname in file_order:
        fpath = competition_dir / fname
        if not fpath.exists():
            continue
        entries.append({
            'file': fname,
            'path': f'/v1/{competition_id}/{fname}',
            'bytes': fpath.stat().st_size,
            'sha256': sha256_of_file(fpath),
        })
    return {
        'competition_id': competition_id,
        'data_version': data_version,
        'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'files': entries,
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: compute_derived.py <path-to-competition-data-dir>", file=sys.stderr)
        sys.exit(1)

    competition_dir = Path(sys.argv[1])

    matches_data = load(competition_dir / 'matches.json')
    matches = matches_data['matches']
    competition_id = matches_data['competition_id']

    upcoming = compute_matches_upcoming(matches)
    save(competition_dir / 'matches-upcoming.json', {
        'competition_id': competition_id,
        'count': len(upcoming),
        'matches': upcoming,
    })
    print(f"Wrote matches-upcoming.json ({len(upcoming)} matches)")

    results = compute_matches_results(matches)
    save(competition_dir / 'matches-results.json', {
        'competition_id': competition_id,
        'count': len(results),
        'matches': results,
    })
    print(f"Wrote matches-results.json ({len(results)} matches)")

    scorers_data = load(competition_dir / 'scorers.json')
    top_scorers = compute_top_scorers(scorers_data)
    save(competition_dir / 'top-scorers.json', {
        'competition_id': competition_id,
        'scorers': top_scorers,
    })
    print(f"Wrote top-scorers.json ({len(top_scorers)} scorers)")

    version_data = load(competition_dir.parent.parent.parent / 'meta' / 'version.json') \
        if (competition_dir.parent.parent.parent / 'meta' / 'version.json').exists() else {}
    data_version = version_data.get('data_version', 'unknown')

    manifest = build_manifest(competition_dir, competition_id, data_version)
    save(competition_dir / 'manifest.json', manifest)
    print(f"Wrote manifest.json ({len(manifest['files'])} files indexed)")


if __name__ == '__main__':
    main()
