# Decisions

Newest first. Entries are appended, never rewritten.

## 2026-10-21 — Bundle the script as a file, not embedded in SKILL.md

**Context.** The first version, saved from a chat, embedded the whole script inside `SKILL.md` so it could be saved from a single text card.

**Decision.** In this repository the script lives at `skills/canna-stock-finder/scripts/canna_find.py`, and `SKILL.md` points at it.

**Why.** One copy means the tests exercise exactly what the skill runs, and terminal users can run it directly. The embedded copy would drift.

**Status.** Standing.

## 2026-10-21 — Public, MIT licensed, skill plus standalone script

**Context.** aj asked for a repository so other people can use the skill, since CannaScraper is public.

**Decision.** Repository `Ajw2003/canna-stock-finder`, public, MIT licence, containing the skill and the script usable on its own. Chosen by aj from options on 21 October 2026.

**Why.** Public with a permissive licence is what lets others install and share it. Including the standalone script serves people who don't use Claude.

**Status.** Standing.

## 2026-10-21 — Use each product's own record for terpenes

**Context.** CannaScraper's data has stock and prices but no lineage or terpenes.

**Decision.** Read each in-stock product's public Shopify JSON from cannacabana.com, cached for a day.

**Why.** It is the only source naming terpenes for these exact products. Strain databases describe the strain in general, not this producer's batch.

**Status.** Standing.
