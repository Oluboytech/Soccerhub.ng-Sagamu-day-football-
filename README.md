# SoccerHub — Sagamu Day Football Competition 2026

Official competition data repository for the **Sagamu Day Football Competition 2026**, in partnership with the **Sagamu Youth Association**.

SoccerHub is the official media partner and this repository is designed to provide one source of structured competition data for:

- SoccerHub.ng
- SoccerHub Android app
- Future SoccerHub competition products

## Current competition structure

- 32 teams
- 8 groups (A–H)
- 4 teams per group
- 48 group-stage matches (single round-robin) — **official fixture schedule confirmed**, 15 Sep – 7 Oct 2026
- Knockout stage structure is reserved for official qualification rules (quarter-finals, semi-finals, third-place playoff, final)

## Data layout

```text
data/v1/sagamu-day-2026/
├── competition.json         Competition metadata
├── groups.json               Group A–H membership
├── teams.json                 32 teams, crest, group assignment
├── venues.json                Match venues
├── players.json                Player registrations (populated once official squads are supplied)
├── matches.json                 All 48 group-stage fixtures (source of truth)
├── matches-upcoming.json         GENERATED — scheduled matches, soonest first
├── matches-results.json           GENERATED — finished matches, most recent first
├── standings.json                  GENERATED — group tables, computed from matches.json
├── scorers.json                     Top scorers (source data)
├── top-scorers.json                  GENERATED — scorers.json ranked
├── assists.json                       Assist leaders
├── cards.json                          Disciplinary record
├── match-events.json                    Goals/cards/subs timeline per match
├── lineups.json                          Starting XI + subs per match
├── statistics.json                        Per-match stats (possession, shots, etc.)
├── knockout.json                           Knockout bracket
├── awards.json                              Competition awards (MVP, golden boot, etc.)
└── manifest.json                            GENERATED — index of every file with size + sha256
```

Files marked **GENERATED** are produced by `scripts/build.sh` from the source files (mainly `matches.json`) — never hand-edit them directly, since the next build will overwrite your changes.

## API endpoints

Served as static files behind the SoccerHub data domain:

```text
https://data.soccerhub.ng/v1/sagamu-day-2026/manifest.json           <- start here: lists every file, size, hash
https://data.soccerhub.ng/v1/sagamu-day-2026/competition.json
https://data.soccerhub.ng/v1/sagamu-day-2026/groups.json
https://data.soccerhub.ng/v1/sagamu-day-2026/teams.json
https://data.soccerhub.ng/v1/sagamu-day-2026/venues.json
https://data.soccerhub.ng/v1/sagamu-day-2026/players.json
https://data.soccerhub.ng/v1/sagamu-day-2026/matches.json
https://data.soccerhub.ng/v1/sagamu-day-2026/matches-upcoming.json    <- next fixtures, pre-sorted
https://data.soccerhub.ng/v1/sagamu-day-2026/matches-results.json    <- completed matches, pre-sorted
https://data.soccerhub.ng/v1/sagamu-day-2026/standings.json         <- always in sync with match results
https://data.soccerhub.ng/v1/sagamu-day-2026/scorers.json
https://data.soccerhub.ng/v1/sagamu-day-2026/top-scorers.json      <- scorers.json, ranked
https://data.soccerhub.ng/v1/sagamu-day-2026/cards.json
https://data.soccerhub.ng/v1/sagamu-day-2026/knockout.json
https://data.soccerhub.ng/v1/sagamu-day-2026/awards.json
```

### Why a manifest?

`manifest.json` lists every published file with its byte size and SHA-256 hash. Clients (the website, the Android app) can poll this single small file on an interval and only re-fetch a data file when its hash changes, instead of re-downloading and re-parsing everything on every refresh.

### Why generated files instead of client-side computation?

`standings.json`, `matches-upcoming.json`, `matches-results.json`, and `top-scorers.json` are all derivable from `matches.json` / `scorers.json` — but computing them once at build time means every consumer (web, Android, any future product) gets identical, pre-sorted, pre-computed data without re-implementing tie-break or sort logic in three different codebases.

## Data pipeline

```text
Official competition information (Sagamu Youth Association / verified SoccerHub coverage)
        ↓
Edit source files: matches.json, teams.json, groups.json, players.json, scorers.json, ...
        ↓
scripts/build.sh          (validate → compute standings → compute derived files → validate again)
        ↓
GitHub commit + push
        ↓
GitHub Action re-runs the pipeline and auto-commits any drift
        ↓
GitHub Pages / CDN cache refresh
        ↓
SoccerHub.ng + Android app
```

Run the pipeline locally before committing:

```bash
pip install jsonschema
bash scripts/build.sh .
```

The script validates the source data against `schema/*.json`, recomputes every generated file, and validates again as a final gate — it exits non-zero if anything is inconsistent (bad schema, unknown team/group/venue reference, duplicate match ID, duplicate group pairing, wrong number of matches per team). The same script runs in CI on every push via `.github/workflows/build-and-validate.yml` and will auto-commit any regenerated files that drifted from what was pushed.

## Data rules

1. IDs are permanent and should not be changed after publication.
2. Do not identify teams or players by display name alone — always carry the `*_id` field.
3. Use `null` when information is unavailable; do not use `0` to mean unknown.
4. Do not invent official match data — dates, times, venues, scores, and events must come from the Sagamu Youth Association or verified SoccerHub match coverage.
5. Never hand-edit a GENERATED file (see the data layout table above) — edit the source file and re-run `scripts/build.sh`.
6. Keep API/schema versions backward compatible where possible; bump `schema_version` in `meta/version.json` on any breaking change.
7. Never store API keys, passwords, tokens, Firebase service accounts, or other secrets in this repository.

## Team groups

### Group A
Igbobi FC, Ayanperuwa FC, Ajaka FC, Ewuga FC

### Group B
Sonyindo FC, Sotubo FC, Ipoyin Ade FC, Idado FC

### Group C
Latawa FC, Apele FC, Aruba FC, Isote FC

### Group D
Ewuoliwo FC, Oba Orimadegbon FC, Iraye FC, Sabo FC

### Group E
Agura FC, Lalu FC, Agbele FC, Abafon FC

### Group F
Emuren FC, Isale Oko FC, Igbepa FC, Aladiye FC

### Group G
Agbowa FC, Isoso FC, Lowa Ibu FC, Ogijo FC

### Group H
Sabintu FC, Itunsokun FC, Apaken FC, Surulere FC

## Known gaps

- Crests missing for: Ipoyin Ade FC, Ewuoliwo FC, Isale Oko FC, Itunsokun FC (`logo: null` in `teams.json`).
- Only 2 venues confirmed so far (Ebedei Stadium, Sagamu High School) — 44 of 48 matches have `venue_id: null` pending confirmation.
- Player registrations, scorers, cards, lineups, and match-events are all empty pending official squad lists and match-day coverage.

## Versioning

Current schema version: `1.1.0`

Current data version: `2026.09.08.001`
