# Stock data and location

## What it owns

Getting the store stock for a province, working out where the user is, and deciding which stores count as "nearest". Everything downstream only sees products that this system says are in stock at those stores.

## How it works

- `fetch` downloads a URL into the cache folder unless a fresh copy exists, retrying three times before raising ([canna_find.py:25](../../skills/canna-stock-finder/scripts/canna_find.py#L25)). The province file is reused for 30 minutes and the store list for a day ([canna_find.py:44](../../skills/canna-stock-finder/scripts/canna_find.py#L44)), because CannaScraper republishes about hourly.
- `locate` takes `--lat`/`--lng` when given. Otherwise it averages the coordinates of every store whose postal code shares the first three characters with the user's, falling back to two ([canna_find.py:59](../../skills/canna-stock-finder/scripts/canna_find.py#L59)).
- `nearest_stores` sorts the province's stores by great-circle distance and keeps `--stores` of them ([canna_find.py:76](../../skills/canna-stock-finder/scripts/canna_find.py#L76)).
- `in_stock_here` keeps a product when at least one of those stores reports it available with more than zero units, and records the lowest tier (member) price, falling back to shelf price ([canna_find.py:82](../../skills/canna-stock-finder/scripts/canna_find.py#L82)).

## Invariants

- A stock row is positional: `[store_id, units, shelf_price, tier_label, tier_price, thc, cbd, available, stock_text, time_index, carried]`. This is CannaScraper's export format; if its order changes, every count and price here is wrong without any error.
- Every answer must carry the province file's `generated_at`, so a reader can tell how stale it is.

## Traps

- Rows can have no tier price and no shelf price at all. The first live run crashed on `min()` over a list containing `None`; prices are now filtered first.
- Postal-prefix centring moves the "nearest" set. For T3B it centred between Bowness and Varsity and swapped Crowfoot for North Hill compared with a hand-placed point. The output always names the stores searched for this reason.
