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
- 48 expected group-stage matches if each group uses a single round-robin
- Knockout stage structure is reserved for official qualification rules

## Important

The supplied group sheets establish the **group allocation**. They do not provide enough verified information to invent match dates, times, venues, or pairings.

Therefore `matches.json` is intentionally empty until the official fixture schedule is supplied.

## Data layout

```text
data/v1/sagamu-day-2026/
├── competition.json
├── groups.json
├── teams.json
├── players.json
├── venues.json
├── matches.json
├── standings.json
├── scorers.json
├── assists.json
├── cards.json
├── match-events.json
├── lineups.json
├── statistics.json
├── knockout.json
└── awards.json
```

## Suggested production endpoints

Once deployed behind the SoccerHub data domain:

```text
https://data.soccerhub.ng/v1/sagamu-day-2026/competition.json
https://data.soccerhub.ng/v1/sagamu-day-2026/groups.json
https://data.soccerhub.ng/v1/sagamu-day-2026/teams.json
https://data.soccerhub.ng/v1/sagamu-day-2026/players.json
https://data.soccerhub.ng/v1/sagamu-day-2026/matches.json
https://data.soccerhub.ng/v1/sagamu-day-2026/standings.json
https://data.soccerhub.ng/v1/sagamu-day-2026/scorers.json
https://data.soccerhub.ng/v1/sagamu-day-2026/knockout.json
```

These are the **planned API URLs**. The repository can initially be served using GitHub Pages/raw content, then moved behind a CDN/custom domain without changing the data model.

## Data rules

1. IDs are permanent and should not be changed after publication.
2. Do not identify teams or players by display name alone.
3. Use `null` when information is unavailable; do not use `0` to mean unknown.
4. Do not invent official match data.
5. Match scores and events should be updated from verified competition coverage.
6. Keep API/schema versions backward compatible where possible.
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

## Updating data

The recommended workflow is:

```text
Official competition information
        ↓
SoccerHub data update
        ↓
GitHub commit
        ↓
JSON/schema validation
        ↓
CDN cache refresh
        ↓
SoccerHub.ng + Android app
```

## Versioning

Current schema version: `1.0.0`

Current data version: `2026.09.05.001`
