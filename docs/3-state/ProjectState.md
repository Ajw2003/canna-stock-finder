# Project state

**Headline: 40%.** Only M1 has had its acceptance check run.

| Milestone | Status |
|---|---|
| M1 — Search and re-check on live data | Done, 21 October 2026 |
| M2 — Offline tests pass | Not started: test file written but blocked from being saved until the build plan is approved |
| M3 — Skill installs from this repo | Not checked |
| M4 — Published | In progress: repository is public; first pull request not yet merged |

## M1

A night search from an empty cache near T3B searched 669 products in 54 seconds with zero detail failures. A day search on the warm cache took under a second. `check` reported Virtue Orange Velvet Underground Caviar at Bowness (6) and West Springs (3) and flagged SKU 999999 as not in the province index. Two bugs found in that run are fixed: missing prices crashed the search, and Roilty's shatter was classed as an oil.

## M3

A version of this skill with the script embedded in `SKILL.md` was saved to Claude from a review card on 21 October 2026. The repository version, which bundles the script as a separate file, has not been uploaded and run.

## The one thing that is not what it looks like

The skill reads as finished because it ran well in a chat, but that was the embedded-script version. The packaged folder in this repo has never been installed.

## Cross-cutting issues

- Correctness depends on CannaScraper's positional stock-row format staying the same. Nothing checks it.
