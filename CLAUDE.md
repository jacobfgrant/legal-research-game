# Legal Research Game

A web-based video game that captures the addictive detective work of legal research — chasing citations, connecting cases, building arguments.

## Repo Structure

This is a monorepo containing two independent games and shared docs:

```
legal-research-game/
  CLAUDE.md
  Caddyfile                      -- reverse proxy config (shared)
  docker-compose.yml             -- runs both games + Caddy
  docs/                          -- shared concept docs and beginner guides
    case-crawler-concept.md
    the-brief-concept.md
    beginners/
  case-crawler/                  -- puzzle/strategy game (independent)
    frontend/                    -- SvelteKit app
    backend/                     -- FastAPI server
  the-brief/                     -- narrative/branching game (independent)
    frontend/                    -- SvelteKit app
    backend/                     -- FastAPI server
```

Each game is fully independent — its own frontend, backend, and data. They share nothing except docs, deployment infrastructure, and this CLAUDE.md. Either can be developed and tested on its own.

## Game Concepts

See the concept docs before making design decisions:

- `docs/case-crawler-concept.md` — Puzzle/strategy game. Player searches a case database, builds arguments, manages billable hours.
- `docs/the-brief-concept.md` — Narrative/branching game. Research choices drive story paths and career outcomes.

Beginner onboarding guides (CLAUDE.md-style files for a non-technical user) are in `docs/beginners/`.

## Tech Stack

These are locked in — don't suggest alternatives unless there's a clear reason to reconsider:

- **SvelteKit (Svelte 5)** — frontend framework with built-in transitions, animations, and reactive state management. Game logic lives primarily client-side.
- **FastAPI** — backend API for game state persistence, serving legal research data, and auth. WebSocket support available for multiplayer later.
- **SQLite** — database (just a file, no server). Sufficient for a small VPS with a handful of concurrent players.
- **Docker** — deployment via `docker compose up` from the repo root
- **Caddy** — reverse proxy. Routes to both games from one VPS.

### Deployment

The root `docker-compose.yml` runs both games and a shared Caddy reverse proxy:

- **Both games:** `docker compose --profile case-crawler --profile the-brief up`
- **Just Case Crawler:** `docker compose --profile case-crawler up caddy case-crawler-frontend case-crawler-backend`
- **Just The Brief:** `docker compose --profile the-brief up caddy the-brief-frontend the-brief-backend`
- **Local dev:** Case Crawler at `localhost:8080`, The Brief at `localhost:8081`
- **Production:** Swap the port-based Caddyfile entries for subdomain-based routing (e.g., `casecrawler.yourdomain.com`). The commented example is in the Caddyfile.

### Architecture (per game)

- SvelteKit frontend and FastAPI backend are separate services
- Game logic lives client-side (single-player) — backend handles persistence and serves case/scenario data
- Game content (cases, statutes, scenarios, story branches) stays in structured data files, loaded by the backend
- Each game's backend data is persisted in a Docker volume

## Conventions

- **Games are independent.** Don't create shared libraries or cross-dependencies between the two games. If both need similar functionality, duplicate it — premature abstraction across games will create coupling.
- **Game content is data, not code.** Cases, statutes, scenarios, story branches, and other game content go in structured data files (JSON or YAML). A non-programmer should be able to author and edit game content without touching Python.
- **Keep it simple.** These are small web games. No microservices, no complex infrastructure, no unnecessary abstractions.
- **Flat project structure.** Don't create deep directory hierarchies within each game. One level of nesting is usually enough.
