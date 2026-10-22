---
name: canna-stock-finder
description: Find Canna Cabana cannabis products in stock near a postal code that match effect criteria (terpenes, lineage, format, CBD), and watch-list or re-check them.
---

# Canna Cabana stock finder

Use this skill when the user wants cannabis picks they can actually buy at a Canna Cabana near them, chosen by effect (sleep, focus, low anxiety, low nausea), or wants to re-check stock on products they already chose.

## Data sources

- Store stock comes from CannaScraper (https://ajw2003.github.io/CannaScraper/), a public site that publishes per-store Canna Cabana stock for a province at `data/<province>.json`, refreshed about hourly, plus `data/stores.json`. Report the file's `generated_at` time with every answer.
- Lineage and terpenes come from each product's own Canna Cabana record (`https://cannacabana.com/products/<handle>.json`). Terpenes are the ones named in the product description. The order is the order of mention, which usually but not always means dominance. Say this when it matters.
- If either download fails, say which one and stop rather than guessing.

## Step 1: find the script

The script is `scripts/canna_find.py` in this skill's folder. It needs only the Python standard library (Python 3.9 or newer). If the skill was installed without its `scripts/` folder, copy the script from https://github.com/Ajw2003/canna-stock-finder into a scratch folder.

Run it with `python3 -I`, and pass `--cache` a scratch folder. A first search downloads several hundred product records and takes about a minute. Later searches reuse the cache and take about a second.

## Step 2: settle the criteria

Ask only for what the request leaves open: the postal code (or a place), which formats, and the goal for each pick. Map goals to arguments like this:

| Goal | `--lineage` | `--prefer` | `--avoid` |
|---|---|---|---|
| Sleep, switch off, relax | `indica` | `myrcene,linalool,caryophyllene` | `pinene,terpinolene` |
| Focus, creativity, motivation without anxiety | `sativa,hybrid` | `limonene,caryophyllene,linalool` | `pinene,terpinolene` |
| Softer THC, anxiety-prone | (either) | as above | `pinene,terpinolene`, and add `--min-cbd 1` |

The basis for this mapping: a controlled human trial (Spindle et al., 2024, PMC article 38498958) found that vaporized d-limonene reduced THC-induced anxiety and paranoia. Myrcene and linalool are the terpenes most often linked to sedation. High-pinene and terpinolene-dominant products are the usual reports of racy, anxious highs. Present terpene effects as tendencies, not guarantees.

Formats are `flower`, `concentrate`, `cart`, `aio`, `edible`, `caps` and `infused`.

Add `--require-terps` when the user cares about avoiding specific terpenes, so products that name none are left out. Without it, products whose pages name no terpenes stay in, and you should say their profile is unknown.

## Step 3: run the search

Example, night picks in every format near a postal code:

```
python3 -I scripts/canna_find.py --cache <scratch>/cfcache --postal "T2P 1J9" search --lineage indica --prefer myrcene,linalool,caryophyllene --avoid pinene,terpinolene --require-terps --top 3
```

Location: `--postal` uses the centre of the stores sharing the first three postal characters (falling back to two). That can shift which stores count as nearest. When precision matters, look up the postal code's coordinates with web search and pass `--lat` and `--lng`. `--stores` sets how many nearest stores are searched (default 5). Always tell the user which stores were searched.

## Step 4: choose and present

From the script's JSON, pick one product per format and goal. Prefer, in order:

1. A first-named terpene in the preferred list and nothing from the avoid list.
2. Products from large producers or strain-specific extracts made from real flower (FSE, live resin, rosin), because restocks stay closer to the same recipe.
3. More stores carrying it, then lower price.

Grab bags and mystery boxes are always excluded (the script does this). Treat candy-flavoured liquid-diamond carts as a wildcard, because they often use non-cannabis terpenes.

For each pick, give the product name with its link, member price, the terpenes the page names, which nearby stores have it and how many, and the SKU. Say when the data was generated and when those stores were scanned. Canna Cabana's own pages often say out of stock for online orders even when store shelves have it, so suggest a call before going.

Do not give dosing protocols. If a heavy, daily user reports recurring nausea, mention once that it is worth raising with their doctor, then move on.

## Step 5: watch list and re-checks

To re-check chosen products, run `check` with their SKUs:

```
python3 -I scripts/canna_find.py --cache <scratch>/cfcache --postal "T2P 1J9" check --skus 293091,202656
```

It reports units at each nearby store and how many stores in the province have it. When a watched product has sold out nearby, run a new `search` with the same criteria and offer the closest replacement.

For ongoing watching, offer a scheduled task if the environment has one. Its prompt must stand alone: include the postal code, the SKUs with product names, the criteria used to choose them, and an instruction to use this skill to re-check and to suggest a replacement for anything sold out nearby. Ask the user how often they want it to run before creating it.
