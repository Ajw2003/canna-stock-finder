# Roadmap

## M1 — Search and re-check work against live data (40%)

**Contains:** `canna_find.py` with `search` and `check`, reading CannaScraper and cannacabana.com.

**Acceptance:** a `search` from an empty cache against live data returns ranked, in-stock results with no detail failures, and a `check` reports a real SKU's nearby stock and flags an unknown SKU.

## M2 — Offline tests pass (20%)

**Contains:** `tests/test_canna_find.py`, using made-up data files and no network.

**Acceptance:** `python3 -m unittest discover tests -v` passes, covering format sorting, postal-prefix location, filtering and ranking, missing prices, and `check`.

## M3 — The skill installs and runs from this repository (20%)

**Contains:** `skills/canna-stock-finder/SKILL.md` and its bundled script.

**Acceptance:** the zipped `skills/canna-stock-finder` folder uploads to Claude, and a request using it runs the bundled script and returns picks.

## M4 — Published for others (20%)

**Contains:** README with install and terminal instructions, MIT licence, the first pull request merged to `main`.

**Acceptance:** the repository is public, `main` contains everything above, and the README's terminal command runs as written from a fresh clone.
