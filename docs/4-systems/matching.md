# Product matching and ranking

## What it owns

Turning an in-stock product into a format, a lineage and a terpene list, then filtering and ranking it against the user's criteria.

## How it works

- `product_detail` reads the product's public Shopify record from cannacabana.com. Lineage comes from the `lineage:` tag. Terpenes are any of eleven known names found in the description or tags, ordered by where they first appear ([canna_find.py:96](../../skills/canna-stock-finder/scripts/canna_find.py#L96)).
- `fmt` sorts products into `aio`, `cart`, `caps`, `edible`, `infused`, `concentrate`, `flower` or `other` from the category, product type, tags and title, checked in that order ([canna_find.py:111](../../skills/canna-stock-finder/scripts/canna_find.py#L111)).
- `cmd_search` drops non-cannabis categories, grab bags and mystery boxes, then applies the format, lineage, price, CBD and terpene filters. The score is +3 when the first-named terpene is preferred, +1 for each later preferred one, −1 for each avoided one, plus 0.3 per store carrying it up to five ([canna_find.py:136](../../skills/canna-stock-finder/scripts/canna_find.py#L136)).

## Invariants

- `--avoid` only excludes a product when an avoided terpene is named **first**. A product that merely mentions pinene later stays in, with a score penalty.
- Grab bags are always excluded. A different product ships each time, which defeats choosing by effect.

## Traps

- Format matching is substring-based. "Roilty" contains "oil", so Roilty's shatter was classed as an oil until the oil check became whole-word.
- "First named" is not proof of dominance. Product copy is written by producers and the order is a convention, not a lab result.
- Many products name no terpenes. `--require-terps` drops them; without it they stay in with no profile, and the skill tells Claude to say so.
