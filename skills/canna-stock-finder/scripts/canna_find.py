#!/usr/bin/env python3
"""Find Canna Cabana products in stock near a postal code, filtered by effect
criteria, using the CannaScraper published data (ajw2003.github.io/CannaScraper).

Subcommands:
  search  -- rank in-stock products near a location against criteria
  check   -- re-check stock for specific SKUs near a location (watch list)

Data: data/alberta.json (per-store stock, refreshed hourly by the site),
data/stores.json, and each product's Shopify JSON from cannacabana.com for
lineage and the terpenes named in its description.
"""
import argparse, concurrent.futures as cf, html, json, math, os, re, sys, time
import urllib.request

SITE = "https://ajw2003.github.io/CannaScraper/data/"
SHOP = "https://cannacabana.com/products/"
TERPS = ["myrcene", "limonene", "caryophyllene", "linalool", "pinene", "terpinolene",
         "humulene", "ocimene", "bisabolol", "farnesene", "nerolidol"]
NON_CANNABIS = re.compile(r"access|rig|bong|pipe|paper|cone|grinder|batter|vaporizer|"
                          r"replacement|storage|clean|lighter|torch|rolling|mystery|"
                          r"apparel|tray|topical|cooking|lifestyle|screen|^$", re.I)


def fetch(url, path, max_age_s):
    """Download url to path unless a copy younger than max_age_s exists."""
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age_s:
        return path
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    last = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            with open(path, "wb") as f:
                f.write(data)
            return path
        except Exception as e:  # retried, then reported below
            last = e
            time.sleep(2)
    raise RuntimeError(f"could not download {url}: {last}")


def load_data(cache, province):
    os.makedirs(cache, exist_ok=True)
    slug = province.strip().lower().replace(" ", "-")
    stock = json.load(open(fetch(SITE + f"{slug}.json", f"{cache}/{slug}.json", 1800)))
    stores = json.load(open(fetch(SITE + "stores.json", f"{cache}/stores.json", 86400)))
    return stock, stores


def km(lat1, lng1, lat2, lng2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2)
         * math.sin(math.radians(lng2 - lng1) / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(a))


def locate(args, stores, province):
    """Return (lat, lng, how) from --lat/--lng, or from stores sharing the postal prefix."""
    if args.lat is not None and args.lng is not None:
        return args.lat, args.lng, "coordinates given"
    pc = (args.postal or "").upper().replace(" ", "")
    if not pc:
        sys.exit("give --postal or --lat and --lng")
    mine = [s for s in stores if s.get("province") == province and s.get("zip")]
    for n in (3, 2):
        hits = [s for s in mine if s["zip"].upper().replace(" ", "")[:n] == pc[:n]]
        if hits:
            lat = sum(s["latitude"] for s in hits) / len(hits)
            lng = sum(s["longitude"] for s in hits) / len(hits)
            return lat, lng, f"centre of {len(hits)} store(s) sharing postal prefix {pc[:n]}"
    sys.exit(f"no store shares a postal prefix with {pc}; pass --lat and --lng instead")


def nearest_stores(stock, lat, lng, n):
    ranked = sorted(stock["stores"], key=lambda s: km(lat, lng, s["lat"], s["lng"]))[:n]
    return {s["id"]: (s["name"], round(km(lat, lng, s["lat"], s["lng"]), 1), s["scraped_at"])
            for s in ranked}


def in_stock_here(stock, near):
    out = {}
    for sku, rows in stock["stock"].items():
        here = {near[r[0]][0]: r[1] for r in rows
                if r[0] in near and r[7] and (r[1] or 0) > 0}
        if here:
            # A row can lack both a tier price and a shelf price; skip those.
            prices = [(r[4] or r[2]) for r in rows if r[0] in near and r[7] and (r[1] or 0) > 0]
            prices = [x for x in prices if x is not None]
            out[sku] = dict(stores=here, price=min(prices) if prices else None,
                            thc=rows[0][5], cbd=rows[0][6])
    return out


def product_detail(cache, handle):
    os.makedirs(f"{cache}/products", exist_ok=True)
    path = f"{cache}/products/{handle}.json"
    fetch(f"{SHOP}{handle}.json", path, 86400)
    d = json.load(open(path))["product"]
    body = re.sub(r"<[^>]+>", " ", html.unescape(d["body_html"] or "")).strip()
    text = (body + " " + d["tags"]).lower()
    lin = re.search(r"lineage:(\w+)", d["tags"])
    return dict(
        lineage=lin.group(1).lower() if lin else "?",
        terps=sorted([t for t in TERPS if t in text], key=text.find),
        body=re.sub(r"\s+", " ", body),
        tags=d["tags"], ptype=d["product_type"])


def fmt(cat, ptype, tags, title):
    s = f"{cat} {ptype} {tags}".lower()
    t = title.lower()
    if "all-in-one" in s or "aio" in t or "disposable" in t: return "aio"
    if any(k in s for k in ("510", "cart", "liquid diamond", "vapes")): return "cart"
    # Whole-word "oil" so brand names like Roilty don't count as oils.
    if any(k in s for k in ("capsule", "soft gel", "softgel")) or re.search(r"\boils?\b", s): return "caps"
    if any(k in s for k in ("gumm", "chocolate", "candies", "edible", "beverage", "chew")): return "edible"
    if any(k in s for k in ("infused pre", "infused blunt")): return "infused"
    if any(k in s for k in ("concentrate", "resin", "rosin", "shatter", "hash", "diamond", "wax", "badder", "kief")): return "concentrate"
    if any(k in s for k in ("flower", "pre-roll", "joint")): return "flower"
    return "other"


def details_for(cache, stock, skus, workers=3):
    prods = stock["products"]
    def one(sku):
        try:
            return sku, product_detail(cache, prods[sku]["handle"])
        except Exception as e:
            return sku, {"error": str(e)}
    with cf.ThreadPoolExecutor(workers) as ex:
        return dict(ex.map(one, skus))


def cmd_search(args):
    stock, stores = load_data(args.cache, args.province)
    lat, lng, how = locate(args, stores, args.province)
    near = nearest_stores(stock, lat, lng, args.stores)
    here = in_stock_here(stock, near)
    prods = stock["products"]
    skus = [s for s in here if s in prods and not NON_CANNABIS.search(prods[s]["category"])]
    det = details_for(args.cache, stock, skus)
    want_fmt = set(args.formats.split(",")) if args.formats else None
    want_lin = set(args.lineage.split(",")) if args.lineage else None
    prefer = [t for t in (args.prefer or "").split(",") if t]
    avoid = [t for t in (args.avoid or "").split(",") if t]
    results, failed = [], 0
    for sku in skus:
        d = det[sku]
        if "error" in d:
            failed += 1
            continue
        p, h = prods[sku], here[sku]
        f = fmt(p["category"], d["ptype"], d["tags"], p["title"])
        if want_fmt and f not in want_fmt: continue
        if want_lin and d["lineage"] not in want_lin: continue
        if args.max_price and (h["price"] is None or h["price"] > args.max_price): continue
        if any(a in (p["title"] + " " + d["body"]).lower() for a in ("grab bag", "mystery")): continue
        if avoid and d["terps"] and d["terps"][0] in avoid: continue  # first-named terpene
        if args.require_terps and not d["terps"]: continue
        if args.min_cbd is not None:
            try:
                if float(h["cbd"]) < args.min_cbd: continue
            except (TypeError, ValueError):
                continue
        score = sum(3 if i == 0 else 1 for i, t in enumerate(d["terps"]) if t in prefer)
        score -= sum(1 for t in d["terps"] if t in avoid)
        score += min(len(h["stores"]), 5) * 0.3
        results.append(dict(sku=sku, format=f, lineage=d["lineage"], brand=p["brand"],
                            title=p["title"], size=p["size"], price=h["price"], thc=h["thc"],
                            cbd=h["cbd"], terps=d["terps"], stores=h["stores"],
                            url=SHOP + p["handle"], score=round(score, 1),
                            blurb=d["body"][:160]))
    results.sort(key=lambda r: (r["format"], -r["score"], r["price"] if r["price"] is not None else 1e9))
    if args.top:
        by, kept = {}, []
        for r in results:
            if by.setdefault(r["format"], 0) < args.top:
                kept.append(r); by[r["format"]] += 1
        results = kept
    out = dict(location=dict(lat=round(lat, 4), lng=round(lng, 4), how=how),
               data_generated=stock.get("generated_at"),
               stores={v[0]: dict(km=v[1], scanned=v[2]) for v in near.values()},
               searched=len(skus), detail_failures=failed, results=results)
    print(json.dumps(out, indent=1))


def cmd_check(args):
    stock, stores = load_data(args.cache, args.province)
    lat, lng, how = locate(args, stores, args.province)
    near = nearest_stores(stock, lat, lng, args.stores)
    prods = stock["products"]
    report = []
    for sku in args.skus.split(","):
        sku = sku.strip()
        p = prods.get(sku)
        rows = stock["stock"].get(sku, [])
        here = {near[r[0]][0]: r[1] for r in rows if r[0] in near and r[7] and (r[1] or 0) > 0}
        anywhere = sum(1 for r in rows if r[7] and (r[1] or 0) > 0)
        report.append(dict(sku=sku, product=(f"{p['brand']} - {p['title']} {p['size']}" if p else "not in the province index"),
                           nearby=here, in_stock_stores_in_province=anywhere,
                           url=(SHOP + p["handle"]) if p else None))
    print(json.dumps(dict(location=how, data_generated=stock.get("generated_at"),
                          stores=[v[0] for v in near.values()], watch=report), indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", default=os.path.expanduser("~/.cache/canna_find"))
    ap.add_argument("--province", default="Alberta")
    ap.add_argument("--postal"); ap.add_argument("--lat", type=float); ap.add_argument("--lng", type=float)
    ap.add_argument("--stores", type=int, default=5, help="how many nearest stores")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("--formats", help="flower,concentrate,cart,aio,edible,caps,infused")
    s.add_argument("--lineage", help="indica,sativa,hybrid,blend")
    s.add_argument("--prefer", help="terpenes to rank up, e.g. myrcene,linalool,caryophyllene")
    s.add_argument("--avoid", help="terpenes to exclude when named first, e.g. pinene,terpinolene")
    s.add_argument("--require-terps", action="store_true", help="only products that name terpenes")
    s.add_argument("--min-cbd", type=float)
    s.add_argument("--max-price", type=float)
    s.add_argument("--top", type=int, default=5, help="results kept per format")
    c = sub.add_parser("check")
    c.add_argument("--skus", required=True, help="comma-separated SKUs")
    args = ap.parse_args()
    {"search": cmd_search, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    main()
