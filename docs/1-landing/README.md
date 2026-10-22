# canna-stock-finder: index

A Claude skill and a standalone Python script that find Canna Cabana products in stock at the stores nearest a postal code, ranked by effect criteria. Stock comes from CannaScraper's public JSON; lineage and terpenes come from each product's public cannacabana.com record.

## Moving parts

| Part | Where | One line |
|---|---|---|
| Skill | `skills/canna-stock-finder/SKILL.md` | Tells Claude how to turn a goal into a search, choose picks, and watch them |
| Script | `skills/canna-stock-finder/scripts/canna_find.py` | `search` and `check` subcommands; standard library only |
| Tests | `tests/test_canna_find.py` | Offline tests on made-up data (pending, see state) |

## Tiers

| Tier | Document |
|---|---|
| 1 Landing | this file |
| 2 Roadmap | [Roadmap.md](../2-roadmap/Roadmap.md) |
| 3 State | [ProjectState.md](../3-state/ProjectState.md) |
| 4 Systems | [Systems index](../4-systems/README.md) |
| 5 Today | [Today.md](../5-today/Today.md) |
| 6 Decisions | [Decisions.md](../6-decisions/Decisions.md) |

## Systems

| System | Owns |
|---|---|
| [Stock data and location](../4-systems/stock-data.md) | Downloading stock, placing the user, nearest stores |
| [Product matching and ranking](../4-systems/matching.md) | Format, lineage, terpenes; filtering and scoring |

## Conventions

- Claims about the code cite `file:line`.
- Decisions are appended to tier 6, never rewritten.
- Inert documents move to `docs/archive/`, never deleted.
