# canna-stock-finder

A Claude skill and Python script that finds Canna Cabana products in stock near you that match effect criteria (terpenes, lineage, format, CBD), using CannaScraper's public stock data.

It finds products that are **actually on the shelf at the Canna Cabana stores nearest you**, picked by the effect you want rather than whatever happens to be in stock. It works two ways:

- **As a Claude skill.** Tell Claude something like "find me a sleep indica and a focus sativa near T2P 1J9, no racy terpenes, in flower and carts". Claude runs the search, chooses one product per format, and can re-check your picks later or watch them on a schedule.
- **As a plain Python script.** Run it from a terminal and get the ranked matches as JSON.

It is not affiliated with Canna Cabana or High Tide Inc.

## Where the data comes from

| What | Source |
|---|---|
| Which store has how many units, and the price | [CannaScraper](https://ajw2003.github.io/CannaScraper/), a public site that re-reads every Alberta Canna Cabana about once an hour and publishes the results as JSON |
| Lineage (indica, sativa, hybrid) and terpenes | Each product's own public page on cannacabana.com |

Terpenes are the ones a product's description names. Many products don't name any, and the order they are named in usually, but not always, reflects which is dominant. Batches vary, so treat terpene effects as tendencies, not guarantees.

## Use it as a Claude skill

1. Download this repository (green **Code** button, then **Download ZIP**) and unzip it.
2. Zip the `skills/canna-stock-finder` folder on its own, so the zip contains `SKILL.md` and `scripts/`.
3. In Claude, open **Settings → Capabilities → Skills**, choose **Upload skill**, and pick that zip.
4. Ask Claude for picks, for example: *"Use canna-stock-finder: a sleep indica and a focus sativa in flower and carts near T2P 1J9, avoiding pinene and terpinolene."*

In Claude Code you can instead copy the `skills/canna-stock-finder` folder into `~/.claude/skills/`.

## Use it from a terminal

You need Python 3.9 or newer. There is nothing to install.

```bash
python3 skills/canna-stock-finder/scripts/canna_find.py --postal "T2P 1J9" \
  search --lineage indica --prefer myrcene,linalool,caryophyllene \
  --avoid pinene,terpinolene --require-terps --top 3
```

The first search downloads several hundred product records and takes about a minute. After that, results come from a local cache (`~/.cache/canna_find`) in about a second.

To re-check products you have chosen, pass their SKUs (every search result includes one):

```bash
python3 skills/canna-stock-finder/scripts/canna_find.py --postal "T2P 1J9" check --skus 293091,202656
```

### Options

| Option | What it does |
|---|---|
| `--postal` | Your postal code. The script centres on the stores that share its first three characters. |
| `--lat`, `--lng` | Exact coordinates instead of a postal code, when you want precise "nearest". |
| `--stores` | How many nearest stores to search (default 5). |
| `--province` | Province file to read from CannaScraper (default `Alberta`). |
| `--formats` | Any of `flower`, `concentrate`, `cart`, `aio`, `edible`, `caps`, `infused`. |
| `--lineage` | Any of `indica`, `sativa`, `hybrid`, `blend`. |
| `--prefer` | Terpenes that rank a product higher, strongest when named first. |
| `--avoid` | Leave out products whose first-named terpene is one of these. |
| `--require-terps` | Only keep products that name at least one terpene. |
| `--min-cbd`, `--max-price` | Simple limits. |
| `--top` | How many results to keep per format (default 5). |

Grab bags and mystery boxes are always left out, because the product inside changes every time.

### Goals as settings

| Goal | `--lineage` | `--prefer` | `--avoid` |
|---|---|---|---|
| Sleep, switch off | `indica` | `myrcene,linalool,caryophyllene` | `pinene,terpinolene` |
| Focus without anxiety | `sativa,hybrid` | `limonene,caryophyllene,linalool` | `pinene,terpinolene` |
| Softer, anxiety-prone | either | as above | as above, plus `--min-cbd 1` |

The limonene setting comes from a controlled trial in which vaporized d-limonene reduced THC-induced anxiety and paranoia ([Spindle et al., 2024](https://pmc.ncbi.nlm.nih.gov/articles/pmid/38498958)). The other mappings follow the terpenes most often reported as sedating or as racy.

## Things to know

- Canna Cabana's product pages often say "out of stock" for online ordering even when a store's shelf has it. Call the store before you go.
- Stock moves through the day. Every result says when the data was generated and when each store was last scanned.
- This is not medical advice. You must be of legal age in your province to buy cannabis (18 in Alberta).

## Running the tests

```bash
python3 -m unittest discover tests -v
```

The tests use small made-up data files and never touch the network.

## Licence

MIT. See [LICENSE](LICENSE).
