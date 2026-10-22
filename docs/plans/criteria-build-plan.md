# Build plan: wider search criteria

Approved by aj on 21 October 2026 from [wider-criteria.html](wider-criteria.html) with the reply:
`Build plan approved: canna-stock-finder criteria 1A 2* 3* 4A`.

| Question | Answer |
|---|---|
| 1. Where descriptions come from | **A.** Each product's own page, cached for a day (unchanged from today). |
| 2. Which profiles | **aj's own answer:** labels specific to people's needs, while keeping the in-depth manual search the original skill had. |
| 3. Do effect descriptions count when terpenes are named | **aj's own answer:** both count; check that they match, and name it clearly when they don't. |
| 4. Description fallback default | **A.** On, with a switch to turn it off. |

All code is in `skills/canna-stock-finder/scripts/canna_find.py` and stays Python standard library only. Tests are in `tests/test_canna_find.py` and never touch the network.

## Part 1: terpenes and cannabinoids

**Terpenes.** Recognise these 26 names, matched as whole words (`\b...\b`), case-insensitive, ordered by first appearance in the description plus tags:

myrcene, limonene, caryophyllene, linalool, pinene, terpinolene, humulene, ocimene, bisabolol, farnesene, nerolidol, terpineol, valencene, guaiol, eucalyptol, geraniol, fenchol, cedrene, germacrene, phellandrene, carene, camphene, cymene, phytol, terpinene, selinadiene.

Map these misspellings and variants to the right name: caryopyllene, carophyllene, caryophylene, caryolphellene, caryopphyllene → caryophyllene; linolool → linalool; lumonene → limonene; franesene → farnesene; "beta-caryophyllene", "b-caryophyllene", "β-caryophyllene" → caryophyllene; "alpha-pinene", "beta-pinene", "α-pinene", "β-pinene" → pinene; "d-limonene" → limonene. `caryophyllene oxide` counts as caryophyllene.

Whole-word matching must fix both known bugs: "nerol" must not match inside "nerolidol", and "pinene" must not match inside "terpinene".

**Menthol** is reported in its own field (`flavour_menthol: true`), never in the terpene list.

**Percentages.** When a description gives a percentage next to a terpene name, in either order ("Limonene 0.8%", "limonene (0.8%)", "Limonene: 0.8 %", "0.8% limonene"), record it. When any percentages exist, the terpene order used for ranking is by percentage, highest first, and the result shows each percentage. A "total terpenes 2.1%" style figure is recorded as `terp_total` when present.

**Cannabinoids.** Detect CBD, CBG, CBN, CBC, THCV and THCA as whole words in the description and tags. New flags:

- `--cannabinoids cbg,thcv` keeps products that mention at least one of them.
- `--avoid-cannabinoids thcv` drops products that mention any of them.

THCA is shown but never used to rank, because it is the raw form of THC.

## Part 2: need-based profiles

`--profile` takes one or more comma-separated names. `--list-profiles` prints every profile with what it prefers, avoids and its evidence label, then exits.

| Profile | Prefer terpenes | Avoid terpenes | Want cannabinoids | Avoid cannabinoids | Lineage hint | Effect words | Opposite words | Evidence label |
|---|---|---|---|---|---|---|---|---|
| fall-asleep | myrcene, linalool, caryophyllene, terpineol | pinene, terpinolene | cbn | thcv | indica | sleep, bedtime, insomnia, drowsy, sedat, couch, knock out | energ, uplift, wake, invigor, daytime | Animal studies and user reports; weak human evidence for CBN |
| wind-down | linalool, caryophyllene, bisabolol, myrcene | pinene, terpinolene | cbd | | indica, hybrid | relax, calm, chill, mellow, unwind, soothing | energ, racy, intense | Animal studies and user reports |
| anxiety-safe | limonene, linalool, caryophyllene | pinene, terpinolene | cbd | | | calm, relax, balanced, stress, gentle | racy, paranoi, intense, heady | One controlled human trial (d-limonene with THC); mixed small human trials for CBD |
| nausea | limonene, caryophyllene | | cbd | | | nause, stomach, settle, queasy | | Strong for THC itself (approved prescription medicines for chemotherapy nausea); weak for terpenes. Warning: in heavy daily users, cannabis can itself cause recurring nausea (cannabinoid hyperemesis syndrome) |
| appetite | myrcene, caryophyllene, limonene | humulene | | thcv | | munchies, appetite, hungry | appetite suppress | Strong for THC itself (approved prescription medicine for appetite loss); small human studies for THCV suppressing appetite; animal only for humulene |
| focus-calm | limonene, caryophyllene, linalool | pinene, terpinolene | | | sativa, hybrid | focus, clear-headed, clear head, productiv, motivat | sedat, couch, sleep | User reports, plus the limonene anxiety trial |
| creative | limonene, terpinolene, ocimene, valencene | | | | sativa | creativ, inspir, imaginat | sedat, couch | User reports only. Warning: the profile most likely to cause anxiety |
| energy | limonene, pinene, terpinolene, ocimene | | thcv | | sativa | uplift, energ, invigor, wake | sleep, sedat, couch | User reports only. Warning: likely to cause anxiety in sensitive people |
| laugh-social | limonene, myrcene | | | | hybrid | giggl, laugh, euphori, happy, social, talkative | sedat | User reports only |
| body-pain | myrcene, caryophyllene, humulene | | cbg, cbd | | indica | pain, ache, body, inflamm, muscle | | Moderate human evidence for cannabis and chronic pain; animal studies for the terpenes |
| mild-daytime | caryophyllene, limonene | pinene, terpinolene | cbd, cbg | | | balanced, mild, gentle, microdose | intense, heavy-hitting, couch | Mixed small human trials for CBD |

**Combining profiles.** Prefer lists, want lists and effect words are unions. Avoid lists are unions. When one profile prefers what another avoids, the avoid wins, and the output lists it under `conflicts`. Lineage hints are a union, used only for ranking, never to filter.

**Manual flags stay.** `--prefer`, `--avoid`, `--lineage`, `--cannabinoids`, `--avoid-cannabinoids`, `--min-cbd`, `--max-price` and `--formats` work exactly as before, with or without `--profile`. A terpene named in `--prefer` is removed from the combined avoid list, because what the user types wins.

Every result carries `profile_evidence` (the labels of the profiles used) and `warnings` (any profile warnings).

## Part 3: effect descriptions, agreement, whole province

**Effect tags.** Each product's description is scanned for every profile's effect words and opposite words.

**Fallback (on by default).** A product that names no terpenes is scored on its effect words alone and marked `judged_by: "description"`. `--no-description-fallback` turns this off; then such products are kept only when no profile or `--prefer` is in use.

**Both count.** For a product that names terpenes, the score is the terpene score plus the effect-word score. Each matching effect word adds 1, up to 2. Each matching opposite word subtracts 1.

**Agreement.** Every result gets an `agreement` field:

- `agree`: terpenes and description both point to the requested goal.
- `terpenes only`: terpenes match; the description says nothing either way.
- `description only`: only the description matches, including fallback products.
- `mismatch`: the terpene score is positive but the description contains an opposite word, or the reverse. The result also gets `agreement_note`, naming both sides in plain words, for example: "Mismatch: terpenes suggest fall-asleep, description says energizing."

Mismatched products are kept but ranked after agreeing ones with the same score.

**Whole province.** `--stores all` searches every store in the province instead of the nearest N.

## Part 4: repository basics and tests

- `LICENSE` (MIT, Copyright (c) 2026 Ayden Wilkins) and `.gitignore` (Python caches, `.cache/`).
- `tests/test_canna_find.py` with the offline tests written on 21 October 2026, extended by each part above with: the two substring bugs, misspellings, percentages in both orders, cannabinoid filters, profile combination and conflict reporting, manual override of an avoid, fallback on and off, each agreement value, and `--stores all`.

## Part 5: documentation and live check

README, `SKILL.md`, `docs/4-systems/matching.md`, roadmap, state, today and decisions updated to match. A live search near T3B with `--profile fall-asleep,appetite` and one with `--profile focus-calm,anxiety-safe` run from an empty cache, with their output quoted in the state document.
